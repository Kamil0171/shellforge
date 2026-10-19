const { test } = require("node:test");
const assert = require("node:assert/strict");
const fs = require("node:fs");
const vm = require("node:vm");

const sessionId = "12345678-1234-1234-1234-123456789abc";
const deferred = () => {
    let resolve, reject;
    const promise = new Promise((yes, no) => { resolve = yes; reject = no; });
    return { promise, resolve, reject };
};
const settle = () => new Promise(resolve => setImmediate(resolve));
const response = (data, status = 200) => ({ ok: status < 400, status, json: async () => data });
const failure = status => response({ detail: "Żądanie odrzucone." }, status);
const progress = (revision, extra = {}) => ({
    revision, status: "active", score: revision * 10, commands_used: revision,
    hints_used: 0, mission_complete: false, completed_objectives: revision,
    total_objectives: 3, objectives: [{ label: `Cel ${revision}`, completed: revision > 0 }], ...extra,
});
const view = (revision = 0, extra = {}) => ({
    progress: progress(revision), infrastructure: { nodes: [], links: [] },
    monitoring: { overall_status: revision ? "nominal" : "critical", signals: [] },
    incident: { title: "Incydent", difficulty: "easy" },
    revealed_hints: [], hint_limit: 3, shell: { prompt: `operator@host:/rev${revision}$` },
    support_center: { runbooks: [], operational_guidance: [] },
    game_map: { name: "NOC", theme: "noc", interactions: [], player_spawn: { x: 1, y: 1 }, sectors: [] },
    ...extra,
});
const result = (revision = 1, extra = {}) => ({
    success: true, output: "Potwierdzony wynik", progress: progress(revision),
    prompt: `operator@host:/rev${revision}$`, ...extra,
});

function harness(page = "scenario", initialFetch = () => response(view())) {
    const elements = new Map();
    const frames = new Map();
    const timers = new Map();
    let nextId = 0;
    let fetchImpl = initialFetch;
    const requests = [];
    let activeElement = null;
    function node() {
        const classes = new Set();
        const listeners = {};
        return {
            hidden: false, disabled: false, value: "", dataset: {}, children: [], attributes: {},
            classList: {
                add: name => classes.add(name), remove: name => classes.delete(name),
                contains: name => classes.has(name),
                toggle(name, force = !classes.has(name)) { if (force) classes.add(name); else classes.delete(name); },
            },
            set textContent(value) { this.text = String(value); this.children = []; },
            get textContent() { return (this.text || "") + this.children.map(child => child.textContent).join(""); },
            append(...children) { this.children.push(...children); },
            appendChild(child) { this.append(child); },
            replaceChildren(...children) { this.text = ""; this.children = children; },
            setAttribute(name, value) { this.attributes[name] = value; },
            focus() { activeElement = this; }, blur() { if (activeElement === this) activeElement = null; },
            scrollIntoView() {},
            addEventListener(name, callback) { (listeners[name] ||= []).push(callback); },
            emit(name, event = {}) {
                const defaults = { preventDefault() {}, stopPropagation() {} };
                return Promise.all((listeners[name] || []).map(callback => callback({ ...defaults, ...event })));
            },
        };
    }
    const html = fs.readFileSync(`app/templates/admin_duty/dynamic/${page}.html`, "utf8");
    for (const match of html.matchAll(/<[^>]*?\sid="([^"]+)"[^>]*>/g)) {
        const element = node();
        element.hidden = /\shidden(?:\s|>)/.test(match[0]);
        const classes = match[0].match(/class="([^"]*)"/);
        classes?.[1].split(" ").forEach(name => element.classList.add(name));
        elements.set(match[1], element);
    }
    const get = id => elements.get(id);
    if (page === "scenario") get("dynamic-session-workspace").dataset.sessionId = sessionId;
    const startButtons = page === "index" ? ["easy", "medium", "hard"].map(difficulty => {
        const button = get(`start-${difficulty}-button`);
        button.dataset.difficulty = difficulty;
        return button;
    }) : [];
    const document = Object.assign(node(), {
        body: node(), getElementById: get, createElement: node,
        querySelector: () => node(),
        querySelectorAll: selector => selector === ".start-incident-button" ? startButtons : [],
    });
    const window = Object.assign(node(), {
        innerWidth: 1440, matchMedia: () => ({ matches: false, addEventListener() {} }),
        scrollTo() {}, location: { replace(url) { window.destination = url; } },
        requestAnimationFrame(callback) { const id = ++nextId; frames.set(id, callback); return id; },
        cancelAnimationFrame: id => frames.delete(id),
        setTimeout(callback, ms) { const id = ++nextId; timers.set(id, { callback, ms }); return id; },
        clearTimeout: id => timers.delete(id),
        ShellForgeDynamicGame: {
            createGame(options) {
                window.gameCreations = (window.gameCreations || 0) + 1;
                window.gameOptions = options;
                return { destroy() {}, setInputLocked() {}, updateMonitoring(data) { window.monitoring = data; } };
            },
        },
    });
    const context = vm.createContext({
        window, document, AbortController, navigator: { userAgent: "Desktop", maxTouchPoints: 0 },
        fetch(url, options) { requests.push({ url, options }); return Promise.resolve(fetchImpl(url, options)); },
    });
    function run(file) {
        vm.runInContext(fs.readFileSync(`app/static/admin_duty/dynamic/${file}.js`, "utf8"), context);
    }
    run("request");
    if (page === "scenario") run("terminal");
    run(page);
    function framesNow() {
        for (const [id, callback] of [...frames]) { frames.delete(id); callback(); }
    }
    return {
        get, window, document, requests, timers, framesNow, run,
        setFetch: fn => { fetchImpl = fn; }, activeElement: () => activeElement,
        async ready() { await settle(); framesNow(); },
        async click(id) { await get(id).emit("click"); await settle(); },
        async command(command = "pwd") {
            window.gameOptions.onInteract({ type: "terminal" });
            get("terminal-input").value = command;
            await get("terminal-form").emit("submit");
            await settle();
        },
        async resize() { await window.emit("resize"); framesNow(); await settle(); },
        async expire(ms) {
            for (const [id, timer] of [...timers]) {
                if (timer.ms === ms) { timers.delete(id); timer.callback(); }
            }
            await settle();
        },
    };
}

test("session load initializes one game and refresh does not initialize it again", async () => {
    const h = harness(); await h.ready();
    assert.equal(h.window.gameCreations, 1);
    assert.equal(h.get("workspace-content").hidden, false);
    assert.equal(h.get("workspace-error").hidden, true);
    await h.resize(); await h.click("refresh-session-button");
    assert.equal(h.window.gameCreations, 1);
});

for (const unavailablePhaser of [false, true]) {
    test(`game initialization failure remains accessible (unavailable Phaser: ${unavailablePhaser})`, async () => {
        const initial = deferred();
        const h = harness("scenario", () => initial.promise);
        const createGame = h.window.ShellForgeDynamicGame.createGame;
        let attempts = 0;
        let initializationError;
        if (unavailablePhaser) {
            h.window.ShellForgeWorld = {
                MapLoader: { load: map => map }, visualProfile: () => ({}),
                MotionPreference: class {}, RuntimeBridge: class {},
            };
            h.run("game");
        }
        const failingCreate = h.window.ShellForgeDynamicGame.createGame;
        h.window.ShellForgeDynamicGame.createGame = options => {
            attempts++;
            if (unavailablePhaser) {
                try {
                    return failingCreate(options);
                } catch (error) {
                    initializationError = error;
                    throw error;
                }
            }
            throw new Error("Game initialization failed");
        };
        initial.resolve(response(view())); await h.ready();
        if (unavailablePhaser) assert.match(initializationError.message, /Phaser/);
        assert.equal(attempts, 1);
        assert.equal(h.get("workspace-content").hidden, true);
        assert.equal(h.get("workspace-error").hidden, false);
        assert.equal(h.get("session-sync-warning").hidden, true);
        assert.match(h.get("workspace-error-title").textContent, /uruchomić gry/);
        assert.equal(h.get("retry-session-button").hidden, false);
        assert.equal(h.activeElement(), h.get("workspace-error-title"));
        await h.resize();
        assert.equal(attempts, 1);
        h.setFetch(() => failure(503)); await h.click("retry-session-button");
        assert.equal(h.get("workspace-error").hidden, false);
        assert.equal(h.get("workspace-loading").hidden, true);
        assert.equal(attempts, 1);
        h.window.ShellForgeDynamicGame.createGame = createGame;
        h.setFetch(() => response(view())); await h.click("retry-session-button");
        assert.equal(h.window.gameCreations, 1);
        assert.equal(h.get("workspace-error").hidden, true);
        assert.equal(h.get("workspace-content").hidden, false);
    });
}

test("failed controller setup destroys the controller before explicit retry", async () => {
    const initial = deferred();
    const h = harness("scenario", () => initial.promise);
    const createGame = h.window.ShellForgeDynamicGame.createGame;
    let destroyed = 0;
    h.window.ShellForgeDynamicGame.createGame = () => ({
        setInputLocked() { throw new Error("Controller setup failed"); },
        destroy() { destroyed++; },
    });
    initial.resolve(response(view())); await h.ready();
    assert.equal(destroyed, 1);
    assert.equal(h.get("workspace-error").hidden, false);
    h.window.ShellForgeDynamicGame.createGame = createGame;
    h.setFetch(() => response(view())); await h.click("retry-session-button");
    assert.equal(h.window.gameCreations, 1);
    assert.equal(destroyed, 1);
    assert.equal(h.get("workspace-content").hidden, false);
});

for (const previousWarning of [false, true]) {
    test(`confirmed end presents report and clears obsolete warning (previous warning: ${previousWarning})`, async () => {
        const completed = view(1, { progress: progress(1, { status: "completed", mission_complete: true }) });
        const h = harness("scenario", () => response(completed)); await h.ready();
        if (previousWarning) {
            h.setFetch(() => failure(503)); await h.resize();
            assert.equal(h.get("session-sync-warning").hidden, false);
        }
        h.get("hint-error").textContent = "Istniejący komunikat podpowiedzi";
        h.get("hint-error").hidden = false;
        h.setFetch(() => response({
            progress: progress(2, { status: "ended", mission_complete: true }),
            post_incident: { score: 20, incident_summary: "Raport incydentu", root_cause: "Przyczyna", affected_services: [] },
        }));
        await h.click("end-session-button");
        assert.equal(h.get("end-summary").hidden, false);
        assert.equal(h.get("post-incident-report").hidden, false);
        assert.equal(h.get("post-incident-summary").textContent, "Raport incydentu");
        assert.equal(h.get("session-sync-warning").hidden, true);
        assert.equal(h.get("hint-error").hidden, false);
        assert.equal(h.requests.filter(r => r.options.method === "POST").length, 1);
    });
}

for (const mode of ["rejected", "uncertain-read-fails", "uncertain-read-succeeds"]) {
    test(`end preserves applicable warning information: ${mode}`, async () => {
        const completed = view(1, { progress: progress(1, { status: "completed", mission_complete: true }) });
        const h = harness("scenario", () => response(completed)); await h.ready();
        h.setFetch(() => failure(503)); await h.resize();
        assert.equal(h.get("session-sync-warning").hidden, false);
        h.setFetch((url, options) => {
            if (options.method === "POST") return mode === "rejected" ? failure(400) : new Promise(() => {});
            return mode === "uncertain-read-succeeds" ? response(completed) : failure(503);
        });
        await h.click("end-session-button");
        if (mode !== "rejected") await h.expire(20000);
        assert.equal(h.get("end-summary").hidden, true);
        assert.equal(h.get("completion-overlay").hidden, false);
        assert.equal(h.get("completion-error").hidden, false);
        assert.equal(h.get("session-sync-warning").hidden, mode === "uncertain-read-succeeds");
        if (mode !== "rejected") assert.match(h.get("completion-error").textContent, /Mogła zostać wykonana/);
        assert.equal(h.get("end-session-button").disabled, false);
        assert.equal(h.requests.filter(r => r.options.method === "POST").length, 1);
    });
}

for (const refreshFails of [false, true]) {
    test(`confirmed command POST survives GET ${refreshFails ? "failure" : "success"}`, async () => {
        const h = harness(); await h.ready();
        h.setFetch(url => url.endsWith("/command") ? response(result()) : refreshFails ? failure(503) : response(view(1)));
        await h.command();
        assert.match(h.get("terminal-output").textContent, /Potwierdzony wynik/);
        assert.doesNotMatch(h.get("terminal-output").textContent, /Operacja została odrzucona/);
        assert.equal(h.get("session-sync-warning").hidden, !refreshFails);
        assert.equal(h.get("workspace-content").hidden, false);
        assert.equal(h.get("terminal-input").disabled, false);
        assert.equal(h.requests.filter(r => r.options.method === "POST").length, 1);
    });
}

test("confirmed POST rejection is reported and never retried", async () => {
    const h = harness(); await h.ready(); h.setFetch(() => failure(400));
    await h.command();
    assert.match(h.get("terminal-state").textContent, /odrzucona/);
    assert.equal(h.get("terminal-input").disabled, false);
    assert.equal(h.requests.length, 2);
});

test("confirmed command output is visible while GET waits and survives its timeout", async () => {
    const h = harness(); await h.ready();
    h.setFetch(url => url.endsWith("/command") ? response(result()) : new Promise(() => {}));
    await h.command();
    assert.match(h.get("terminal-output").textContent, /Potwierdzony wynik/);
    assert.equal(h.get("terminal-input").disabled, true);
    await h.expire(15000);
    assert.match(h.get("terminal-output").textContent, /Potwierdzony wynik/);
    assert.match(h.get("terminal-output").textContent, /nie zostanie powtórzona/);
    assert.equal(h.get("terminal-input").disabled, false);
});

test("successful command followed by 404 GET retains output and recovery focus", async () => {
    const h = harness(); await h.ready();
    h.setFetch(url => url.endsWith("/command") ? response(result()) : failure(404));
    await h.command(); h.framesNow();
    assert.match(h.get("terminal-output").textContent, /Potwierdzony wynik/);
    assert.equal(h.get("workspace-error").hidden, false);
    assert.equal(h.get("terminal-overlay").hidden, true);
    assert.equal(h.activeElement(), h.get("workspace-error-title"));
});

for (const mode of ["network", "timeout", "server", "invalid-json", "body-timeout"]) {
    test(`uncertain command (${mode}) reconciles with GET without repeating POST`, async () => {
        const h = harness(); await h.ready();
        const waiting = deferred();
        h.setFetch(url => {
            if (!url.endsWith("/command")) return response(view(1));
            if (mode === "timeout") return waiting.promise;
            if (mode === "body-timeout") return { ok: true, status: 200, json: () => waiting.promise };
            if (mode === "server") return failure(503);
            if (mode === "invalid-json") return { ok: true, status: 200, json: async () => { throw new Error("JSON"); } };
            return Promise.reject(new Error("network"));
        });
        await h.command();
        if (mode.includes("timeout")) {
            assert.equal(h.get("terminal-input").disabled, true);
            await h.command("whoami");
            assert.equal(h.requests.filter(r => r.options.method === "POST").length, 1);
            await h.expire(20000);
        }
        assert.match(h.get("terminal-state").textContent, /niepotwierdzony/);
        assert.match(h.get("terminal-output").textContent, /Mogła zostać wykonana/);
        assert.equal(h.get("session-revision").textContent, "1");
        assert.equal(h.get("terminal-input").disabled, false);
        assert.equal(h.requests.filter(r => r.options.method === "POST").length, 1);
        if (mode.includes("timeout")) assert.equal(h.requests[1].options.signal.aborted, true);
    });
}

test("editor save preserves confirmed success when refresh fails", async () => {
    const h = harness(); await h.ready();
    h.setFetch(url => url.endsWith("/command")
        ? response(result(1, { editor: { path: "/etc/example.conf", content: "old" } }))
        : response(view(1)));
    await h.command("nano /etc/example.conf");
    assert.equal(h.get("virtual-editor").hidden, false);
    h.get("virtual-editor-content").value = "new";
    h.setFetch(url => url.endsWith("/file") ? response(result(2, { output: "Zapisano plik" })) : failure(503));
    await h.click("virtual-editor-save");
    assert.equal(h.get("virtual-editor").hidden, true);
    assert.match(h.get("terminal-output").textContent, /Zapisano plik/);
    assert.match(h.get("terminal-output").textContent, /nie zostanie powtórzona/);
    assert.equal(h.get("terminal-input").disabled, false);
});

test("uncertain editor save retains text, reconciles and never repeats save", async () => {
    const h = harness(); await h.ready();
    h.setFetch(url => url.endsWith("/command")
        ? response(result(1, { editor: { path: "/etc/example.conf", content: "old" } }))
        : response(view(1)));
    await h.command("nano /etc/example.conf");
    h.get("virtual-editor-content").value = "unsaved or saved";
    h.setFetch(url => url.endsWith("/file") ? new Promise(() => {}) : response(view(2)));
    void h.get("virtual-editor-save").emit("click"); await settle();
    await h.expire(20000);
    assert.equal(h.get("virtual-editor").hidden, false);
    assert.equal(h.get("virtual-editor-content").value, "unsaved or saved");
    assert.match(h.get("terminal-state").textContent, /Mogła zostać wykonana/);
    assert.equal(h.get("virtual-editor-save").disabled, false);
    assert.equal(h.requests.filter(r => r.url.endsWith("/file")).length, 1);
});

for (const overlay of ["terminal", "support", "monitoring", "rack"]) {
    test(`expired session closes ${overlay} and restores recovery focus`, async () => {
        const h = harness(); await h.ready();
        h.window.gameOptions.onInteract({ type: overlay });
        h.setFetch(() => failure(404));
        await h.resize(); h.framesNow();
        assert.equal(h.get(`${overlay}-overlay`).hidden, true);
        assert.equal(h.get("workspace-error").hidden, false);
        assert.equal(h.get("retry-session-button").hidden, true);
        assert.equal(h.document.body.classList.contains("dynamic-modal-open"), false);
        assert.equal(h.activeElement(), h.get("workspace-error-title"));
    });
}

for (const action of ["command", "hint"]) {
    test(`404 during ${action} shows recovery directly`, async () => {
        const h = harness(); await h.ready(); h.setFetch(() => failure(404));
        if (action === "command") await h.command();
        else {
            h.window.gameOptions.onInteract({ type: "support" });
            await h.click("request-hint-button");
        }
        h.framesNow();
        assert.equal(h.get("workspace-error").hidden, false);
        assert.equal(h.get("terminal-overlay").hidden, true);
        assert.equal(h.get("support-overlay").hidden, true);
        assert.equal(h.activeElement(), h.get("workspace-error-title"));
        assert.equal(h.get("terminal-input").disabled, true);
    });
}

test("late successful GET cannot resurrect an expired session", async () => {
    const h = harness(); await h.ready(); const old = deferred();
    h.setFetch(() => old.promise); await h.resize();
    h.setFetch(() => failure(404)); await h.resize();
    old.resolve(response(view(2))); await settle();
    assert.equal(h.get("workspace-content").hidden, true);
    assert.equal(h.get("workspace-error").hidden, false);
});

test("transient resize failure preserves terminal and GET-only recovery", async () => {
    const h = harness(); await h.ready();
    h.window.gameOptions.onInteract({ type: "terminal" });
    h.setFetch(() => Promise.reject(new Error("network"))); await h.resize();
    assert.equal(h.get("terminal-overlay").hidden, false);
    assert.equal(h.get("workspace-content").hidden, false);
    h.setFetch(() => response(view(2))); await h.click("refresh-session-button");
    assert.equal(h.get("session-sync-warning").hidden, true);
    assert.equal(h.get("session-revision").textContent, "2");
    assert.equal(h.requests.some(r => r.options.method === "POST"), false);
});

test("concurrent resize GETs discard revision 1 arriving after revision 2", async () => {
    const h = harness(); await h.ready(); const first = deferred(); const second = deferred();
    h.setFetch(() => first.promise); await h.resize();
    h.setFetch(() => second.promise); await h.resize();
    second.resolve(response(view(2))); await settle();
    first.resolve(response(view(1))); await settle();
    assert.equal(h.get("session-revision").textContent, "2");
    assert.equal(h.get("header-score").textContent, "20");
    assert.match(h.get("objectives-list").textContent, /Cel 2/);
    assert.equal(h.get("infrastructure-health").textContent, "NOMINAL");
    assert.match(h.get("terminal-prompt").textContent, /rev2/);
    assert.equal(h.window.monitoring.overall_status, "nominal");
});

test("GET started before command cannot overwrite confirmed POST progress or prompt", async () => {
    const h = harness(); await h.ready(); const old = deferred();
    h.setFetch(() => old.promise); await h.resize();
    h.setFetch(url => url.endsWith("/command") ? response(result(2)) : failure(503));
    await h.command(); old.resolve(response(view(1))); await settle();
    assert.equal(h.get("session-revision").textContent, "2");
    assert.match(h.get("terminal-prompt").textContent, /rev2/);
});

test("newer GET prompt survives delayed older command response", async () => {
    const h = harness(); await h.ready(); const command = deferred();
    h.setFetch(url => url.endsWith("/command") ? command.promise : response(view(2)));
    await h.command(); await h.resize();
    command.resolve(response(result(1))); await settle();
    assert.equal(h.get("session-revision").textContent, "2");
    assert.match(h.get("terminal-prompt").textContent, /rev2/);
    assert.match(h.get("terminal-output").textContent, /Potwierdzony wynik/);
});

test("older rejected GET does not replace a newer successful read", async () => {
    const h = harness(); await h.ready(); const old = deferred();
    h.setFetch(() => old.promise); await h.resize();
    h.setFetch(() => response(view(2))); await h.resize();
    old.reject(new Error("offline")); await settle();
    assert.equal(h.get("session-revision").textContent, "2");
    assert.equal(h.get("session-sync-warning").hidden, true);
});

test("late active revision cannot undo completed mission state", async () => {
    const h = harness(); await h.ready(); const old = deferred();
    h.setFetch(() => old.promise); await h.resize();
    h.setFetch(() => response(view(2, { progress: progress(2, { status: "completed", mission_complete: true }) })));
    await h.resize(); old.resolve(response(view(1))); await settle();
    assert.equal(h.get("session-status-badge").textContent, "Ukończony");
    assert.equal(h.get("completion-banner").hidden, false);
    assert.equal(h.get("terminal-input").disabled, true);
});

test("stale successful hint response cannot overwrite newer hints or score", async () => {
    const h = harness(); await h.ready(); const hint = deferred();
    h.setFetch(url => url.endsWith("/hint") ? hint.promise : response(view(2, {
        progress: progress(2, { hints_used: 2 }), revealed_hints: [{ text: "Nowsza podpowiedź", cost: 5 }],
    })));
    await h.click("request-hint-button"); await h.resize();
    hint.resolve(response({ progress: progress(1, { hints_used: 1 }), revealed_hints: [], hint_limit: 3 }));
    await settle();
    assert.match(h.get("revealed-hints").textContent, /Nowsza podpowiedź/);
    assert.equal(h.get("header-score").textContent, "20");
    assert.equal(h.get("hints-counter").textContent, "2 / 3");
});

test("both mutation and reconciliation deadlines restore control with a warning", async () => {
    const h = harness(); await h.ready(); h.setFetch(() => new Promise(() => {}));
    await h.command(); await h.expire(20000); await h.expire(15000);
    assert.equal(h.get("terminal-input").disabled, false);
    assert.equal(h.get("session-sync-warning").hidden, false);
    assert.match(h.get("terminal-state").textContent, /niepotwierdzony/);
    assert.equal(h.requests.filter(r => r.options.method === "POST").length, 1);
    assert.equal(h.timers.size, 0);
});

test("late timed-out mutation response is ignored after reconciliation", async () => {
    const h = harness(); await h.ready(); const late = deferred();
    h.setFetch(url => url.endsWith("/command") ? late.promise : response(view(2)));
    await h.command(); await h.expire(20000);
    late.resolve(response(result(1, { output: "Late output" }))); await settle();
    assert.equal(h.get("session-revision").textContent, "2");
    assert.doesNotMatch(h.get("terminal-output").textContent, /Late output/);
    assert.equal(h.requests.filter(r => r.options.method === "POST").length, 1);
});

test("initial load deadline releases loading screen and supports retry", async () => {
    const h = harness("scenario", () => new Promise(() => {})); await h.ready();
    await h.expire(15000);
    assert.equal(h.get("workspace-loading").hidden, true);
    assert.equal(h.get("workspace-error").hidden, false);
    assert.equal(h.requests[0].options.signal.aborted, true);
    h.setFetch(() => response(view())); await h.click("retry-session-button");
    assert.equal(h.get("workspace-content").hidden, false);
    assert.equal(h.timers.size, 0);
});

for (const action of ["hint", "end"]) {
    test(`${action} timeout keeps double-submit protection through reconciliation`, async () => {
        const h = harness(); await h.ready(); const read = deferred();
        h.setFetch((url, options) => options.method === "POST" ? new Promise(() => {}) : read.promise);
        const button = action === "hint" ? "request-hint-button" : "end-session-button";
        void h.get(button).emit("click"); await settle();
        await h.expire(20000);
        void h.get(button).emit("click"); await settle();
        assert.equal(h.requests.filter(r => r.options.method === "POST").length, 1);
        read.resolve(response(view(1))); await settle();
        assert.equal(h.get(button).disabled, false);
        const message = h.get(action === "hint" ? "hint-error" : "completion-error").textContent;
        assert.match(message, /Mogła zostać wykonana/);
        assert.equal(h.timers.size, 0);
    });
}

test("generation timeout closes overlay and does not restart automatically", async () => {
    const h = harness("index", () => new Promise(() => {}));
    await h.click("start-easy-button"); await h.click("start-hard-button");
    assert.equal(h.requests.length, 1);
    await h.expire(90000);
    assert.equal(h.get("generation-overlay").hidden, true);
    assert.equal(h.get("generation-overlay").attributes["aria-busy"], "false");
    assert.equal(h.get("start-easy-button").disabled, false);
    assert.equal(h.get("retry-start-button").disabled, false);
    assert.match(h.get("start-error-message").textContent, /Sesja mogła powstać/);
    assert.equal(h.requests.length, 1);
    assert.equal(h.requests[0].options.signal.aborted, true);
});

for (const [detail, expected] of [
    ["Limit aktywnych sesji został osiągnięty.", /stanowiska.*zajęte/],
    ["Trwały zapis sesji jest chwilowo niedostępny.", /Zapis sesji jest chwilowo niedostępny/],
    ["Nie udało się przygotować poprawnego incydentu.", /Nie udało się przygotować incydentu/],
    ["sqlite internal secret", /Laboratorium jest chwilowo niedostępne/],
    ["__proto__", /Laboratorium jest chwilowo niedostępne/],
    [null, /Laboratorium jest chwilowo niedostępne/],
]) {
    test(`503 explains only recognized causes: ${detail}`, async () => {
        const h = harness("index", () => response({ detail }, 503));
        await h.click("start-easy-button");
        assert.match(h.get("start-error-message").textContent, expected);
        assert.doesNotMatch(h.get("start-error-message").textContent, /sqlite|internal|secret/);
        assert.equal(h.get("generation-overlay").hidden, true);
    });
}

test("generation success redirects once and clears deadline", async () => {
    const h = harness("index", () => response({ session_id: sessionId }));
    await h.click("start-hard-button");
    assert.equal(h.window.destination, `/admin-duty/dynamic/sessions/${sessionId}`);
    assert.equal(h.timers.size, 0);
    assert.equal(h.requests.length, 1);
});
