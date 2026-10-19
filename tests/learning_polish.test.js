const { test } = require("node:test");
const assert = require("node:assert/strict");
const fs = require("node:fs");
const vm = require("node:vm");

function matchesSelector(node, selector) {
    const exclusion = selector.match(/:not\(([^()]+)\)$/);
    if (exclusion) {
        return matchesSelector(node, selector.slice(0, exclusion.index)) && !matchesSelector(node, exclusion[1]);
    }
    const match = selector.match(/^([a-z][\w-]*)?(?:\[([\w-]+)(?:=(?:'([^']*)'|"([^"]*)"|([^\]\s]+)))?\])?$/i);
    assert.ok(match && (match[1] || match[2]), `Unsupported mock selector: ${selector}`);
    const [, tag, attribute, singleQuoted, doubleQuoted, unquoted] = match;
    const value = singleQuoted ?? doubleQuoted ?? unquoted;
    return (!tag || node.tagName.toLowerCase() === tag.toLowerCase())
        && (!attribute || (Object.hasOwn(node.attributes, attribute)
            && (value === undefined || node.attributes[attribute] === value)));
}

function element(tag = "div", attributes = {}) {
    const listeners = {};
    const classes = new Set();
    return {
        tagName: tag, dataset: {}, style: {}, attributes: { ...attributes }, children: [], disabled: false,
        classList: {
            add: name => classes.add(name), remove: name => classes.delete(name),
            contains: name => classes.has(name),
            toggle(name, force) { if (force) classes.add(name); else classes.delete(name); },
        },
        setAttribute(name, value) { this.attributes[name] = value; },
        appendChild(child) { child.parentElement = this; this.children.push(child); },
        closest(selector) {
            const selectors = selector.split(",").map(part => part.trim());
            for (let node = this; node; node = node.parentElement) {
                if (selectors.some(part => matchesSelector(node, part))) return node;
            }
            return null;
        },
        addEventListener(name, fn) { (listeners[name] ||= []).push(fn); },
        emit(name, values = {}) {
            const event = { target: this, defaultPrevented: false, preventDefault() { this.defaultPrevented = true; }, ...values };
            for (const fn of listeners[name] || []) fn(event);
            return event;
        },
    };
}

function learningHarness(file, { reducedMotion = false, blockedRead = false, blockedWrite = false, savedIds = [], transformSource = source => source } = {}) {
    const nodes = new Map();
    const get = selector => {
        if (!nodes.has(selector)) nodes.set(selector, element());
        return nodes.get(selector);
    };
    const document = element();
    document.querySelector = get;
    document.querySelectorAll = selector => {
        if (selector === "#flashcards-data div") return [1, 2, 3].map(index => ({ dataset: { question: `Pytanie ${index}`, answer: `Odpowiedź ${index}` } }));
        if (selector === ".flashcards-dot") return get("#flashcards-dots").children;
        return [];
    };
    document.createElement = element;
    get("#flashcard-question").parentElement = element();
    get("#flashcard-answer").parentElement = element();
    get("[data-lesson-progress-detail][data-lesson-id]").dataset.lessonId = "1";
    const label = element();
    const button = get("[data-lesson-completion-toggle]");
    button.querySelector = selector => selector === "[data-lesson-completion-label]" ? label : element();
    const timers = [];
    const writes = [];
    const window = element();
    window.matchMedia = () => ({ matches: reducedMotion });
    window.localStorage = {
        getItem() {
            if (blockedRead) throw new Error("Storage blocked");
            return JSON.stringify({ version: 1, completedLessonIds: savedIds });
        },
        setItem(key, value) {
            if (blockedWrite) throw new Error("Quota exceeded");
            writes.push(JSON.parse(value));
        },
    };
    window.scrollTo = options => { window.scrolled = options; };
    const context = vm.createContext({ document, window, setTimeout: fn => timers.push(fn) });
    vm.runInContext(transformSource(fs.readFileSync(`app/static/js/${file}.js`, "utf8")), context);
    document.emit("DOMContentLoaded");
    return { get, document, window, label, button, writes, timers, flush() { while (timers.length) timers.shift()(); } };
}

test("closest respects selectors and returns the nearest matching element or ancestor", () => {
    const outer = element("button");
    const inner = element("div", { role: "button" });
    const child = element("span");
    outer.appendChild(inner);
    inner.appendChild(child);
    assert.equal(child.closest("span"), child);
    assert.equal(child.closest("button, [role='button']"), inner);
    assert.equal(child.closest("button"), outer);
    assert.equal(child.closest("a, [role='link']"), null);
    assert.equal(inner.closest('[role="button"]'), inner);
    assert.equal(inner.closest("[role=link]"), null);
    assert.equal(element("BUTTON").closest("button")?.tagName, "BUTTON");
});

function assertFlashcardIgnoresKey(h, target, key) {
    const event = h.document.emit("keydown", { target, key });
    assert.equal(event.defaultPrevented, false, "native control key must not be intercepted");
    assert.equal(h.get("#flashcards-scene").attributes["aria-pressed"], "false");
    assert.equal(h.get("#flashcard-current").textContent, 1);
}

const interactiveElements = [
    ...["a", "button", "input", "select", "textarea", "summary", "iframe", "object", "embed"].map(tag => [tag, {}]),
    ["audio", { controls: "" }], ["video", { controls: "" }],
    ["div", { role: "button" }], ["div", { role: "link" }],
    ["div", { tabindex: "0" }], ["div", { contenteditable: "" }], ["div", { contenteditable: "true" }],
];

for (const [tag, attributes] of interactiveElements) {
    for (const key of ["Enter", " ", "ArrowRight"]) {
        test(`flashcards do not intercept ${key} on ${tag} ${JSON.stringify(attributes)} or its descendants`, () => {
            for (const nested of [false, true]) {
                const target = element(tag, attributes);
                const child = element("span");
                const grandchild = element("span");
                target.appendChild(child);
                child.appendChild(grandchild);
                assertFlashcardIgnoresKey(learningHarness("flashcards"), nested ? grandchild : target, key);
            }
        });
    }
}

test("non-interactive attributes do not suppress flashcard keyboard handling", () => {
    for (const target of [element("div", { contenteditable: "false" }), element("div", { role: "note" }), element("audio"), element("video")]) {
        const h = learningHarness("flashcards");
        const event = h.document.emit("keydown", { target, key: "Enter" });
        assert.equal(event.defaultPrevented, true);
        assert.equal(h.get("#flashcards-scene").attributes["aria-pressed"], "true");
    }
});

test("keyboard regression assertion detects an incorrect production closest selector", () => {
    const button = element("button");
    const child = element("span");
    button.appendChild(child);
    assertFlashcardIgnoresKey(learningHarness("flashcards"), child, "Enter");
    const h = learningHarness("flashcards", {
        transformSource(source) {
            const mutated = source.replace(/event\.target\.closest\("[^"]+"\)/, 'event.target.closest("a")');
            assert.notEqual(mutated, source, "mutation must replace the production closest selector");
            return mutated;
        },
    });
    assert.throws(() => assertFlashcardIgnoresKey(h, child, "Enter"), {
        code: "ERR_ASSERTION",
        actual: true,
        expected: false,
    });
    assert.equal(h.get("#flashcards-scene").attributes["aria-pressed"], "true");
});

test("flashcard keyboard activation updates its state and hides the reverse face from accessibility", () => {
    const h = learningHarness("flashcards");
    const scene = h.get("#flashcards-scene");
    const event = h.document.emit("keydown", { target: scene, key: "Enter" });
    assert.equal(event.defaultPrevented, true);
    assert.equal(scene.attributes["aria-pressed"], "true");
    assert.equal(scene.attributes["aria-describedby"], "flashcard-answer");
    assert.equal(h.get("#flashcard-question").parentElement.attributes["aria-hidden"], "true");
    h.document.emit("keydown", { target: scene, key: " " });
    assert.equal(scene.attributes["aria-pressed"], "false");
    h.document.emit("keydown", { target: scene, key: "ArrowRight" });
    assert.equal(h.get("#flashcard-current").textContent, 2);
    const dots = h.get("#flashcards-dots").children;
    assert.equal(dots[1].tagName, "button");
    assert.equal(dots[1].attributes["aria-current"], "true");
    assert.equal(dots[2].attributes["aria-label"], "Przejdź do fiszki 3");
    dots[2].emit("click");
    assert.equal(h.get("#flashcard-current").textContent, 3);
    assert.equal(h.get("#flashcard-next").disabled, true);
});

test("failed progress write keeps previous completion and announces failure", () => {
    const h = learningHarness("lesson_progress", { blockedWrite: true });
    h.button.emit("click");
    assert.equal(h.button.attributes["aria-pressed"], "false");
    assert.equal(h.label.textContent, "Oznacz jako ukończoną");
    assert.match(h.get("[data-lesson-progress-status]").textContent, /Nie udało się zapisać.*pozostaje bez zmian/);
    assert.equal(h.writes.length, 0);
});

test("failed removal of saved completion does not clear the saved state", () => {
    const h = learningHarness("lesson_progress", { blockedWrite: true, savedIds: [1] });
    h.button.emit("click");
    assert.equal(h.button.attributes["aria-pressed"], "true");
    assert.equal(h.label.textContent, "Ukończono");
});

test("unavailable storage read is explicit and does not claim saved progress", () => {
    const h = learningHarness("lesson_progress", { blockedRead: true, blockedWrite: true });
    assert.match(h.get("[data-lesson-progress-status]").textContent, /Nie można odczytać/);
    h.button.emit("click");
    assert.equal(h.button.attributes["aria-pressed"], "false");
});

test("successful progress write persists before displaying completion", () => {
    const h = learningHarness("lesson_progress");
    h.button.emit("click");
    assert.deepEqual(h.writes, [{ version: 1, completedLessonIds: [1] }]);
    assert.equal(h.button.attributes["aria-pressed"], "true");
    assert.match(h.get("[data-lesson-progress-status]").textContent, /Postęp zapisany/);
    h.button.emit("click");
    assert.equal(h.button.attributes["aria-pressed"], "false");
    assert.deepEqual(h.writes[1].completedLessonIds, []);
});

for (const reducedMotion of [true, false]) {
    test(`quiz submission respects reduced motion: ${reducedMotion}`, () => {
        const h = learningHarness("quiz", { reducedMotion });
        let submitted = false;
        h.get(".quiz-form").submit = () => { submitted = true; };
        const event = h.get(".quiz-form").emit("submit");
        assert.equal(event.defaultPrevented, !reducedMotion);
        if (reducedMotion) {
            assert.equal(h.window.scrolled, undefined);
            assert.equal(h.timers.length, 0);
        } else {
            assert.equal(h.window.scrolled.behavior, "smooth");
            h.flush();
            assert.equal(submitted, true);
        }
    });
}
