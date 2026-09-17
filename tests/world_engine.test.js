const { test } = require("node:test");
const assert = require("node:assert/strict");
const fs = require("node:fs");
const vm = require("node:vm");
const context = { window: {} };
vm.createContext(context);
vm.runInContext(fs.readFileSync("app/static/admin_duty/dynamic/world-core.js", "utf8"), context);
vm.runInContext(fs.readFileSync("app/static/admin_duty/dynamic/world-renderers.js", "utf8"), context);
vm.runInContext(fs.readFileSync("app/static/admin_duty/dynamic/world-systems.js", "utf8"), context);
const W = context.window.ShellForgeWorld;
const source = JSON.parse(fs.readFileSync("app/admin_duty/components/maps/modern_noc.json", "utf8"));
const datacenter = JSON.parse(fs.readFileSync("app/admin_duty/components/maps/datacenter_hall.json", "utf8"));

test("MapLoader loads JSON, rejects duplicate ids and invalid geometry", () => {
    assert.equal(W.MapLoader.load(source), source);
    assert.equal(W.MapLoader.load(datacenter), datacenter);
    const invalid = structuredClone(source);
    invalid.objects.push(invalid.objects[0]);
    assert.throws(() => W.MapLoader.load(invalid));
    invalid.objects.pop();
    invalid.player_spawn.x = -1;
    assert.throws(() => W.MapLoader.load(invalid));
    invalid.player_spawn.x = 100;
    invalid.interactions[0].radius = 0;
    assert.throws(() => W.MapLoader.load(invalid));
    const missingObject = structuredClone(datacenter);
    missingObject.interactions[0].object_id = "missing-object";
    assert.throws(() => W.MapLoader.load(missingObject));
});

test("Both worlds expose bounded spawn, sectors and reachable interaction data", () => {
    for (const world of [source, datacenter]) {
        assert.ok(world.sectors.length >= 5);
        assert.ok(world.player_spawn.x <= world.width);
        assert.ok(world.player_spawn.y <= world.height);
        assert.ok(world.interactions.every(item => item.position.x <= world.width && item.position.y <= world.height));
    }
});

test("Discovery remembers visits without revealing other sectors", () => {
    const discovery = new W.DiscoveryState(source);
    const first = source.sectors[0];
    const visit = discovery.visit(first.rect.x + 1, first.rect.y + 1);
    assert.equal(visit.newlyDiscovered, true);
    assert.equal(visit.discovered, 1);
    assert.equal(discovery.visit(first.rect.x + 2, first.rect.y + 2).newlyDiscovered, false);
    discovery.visit(-1, -1);
    assert.equal(discovery.discovered.size, 1);
    assert.equal(new W.DiscoveryState(source).discovered.size, 0);
});

test("Datacenter discovery starts in Operations and reveals sectors independently", () => {
    const discovery = new W.DiscoveryState(datacenter);
    const start = discovery.visit(datacenter.player_spawn.x, datacenter.player_spawn.y);
    assert.equal(start.current.id, "operations-entry");
    assert.equal(start.discovered, 1);
    const compute = datacenter.sectors.find(item => item.id === "compute-hall");
    const next = discovery.visit(compute.rect.x + 50, compute.rect.y + 50);
    assert.equal(next.current.id, "compute-hall");
    assert.equal(next.discovered, 2);
});

test("Interactions select nearest in radius, distant player has no prompt", () => {
    const item = source.interactions[0];
    assert.equal(W.nearestInteraction(source.interactions, item.position).id, item.id);
    assert.equal(W.nearestInteraction(source.interactions, { x: -999, y: -999 }), null);
    const near = { ...item, id: "near", position: { x: item.position.x + 1, y: item.position.y } };
    assert.equal(W.nearestInteraction([item, near], near.position).id, "near");
});

test("RuntimeBridge changes color using only public severity", () => {
    const bridge = new W.RuntimeBridge({ signals: [{ resource_id: "service", severity: "critical" }] });
    const critical = bridge.color("service");
    bridge.update({ signals: [{ resource_id: "service", severity: "ok" }] });
    assert.notEqual(bridge.color("service"), critical);
    assert.equal(bridge.severity("unknown"), "ok");
});

test("Interaction highlights use one HUD prompt and trigger once", () => {
    const changes = [];
    const triggered = [];
    const scene = { add: { ellipse: () => ({
        alpha: 0,
        setStrokeStyle() { return this; },
        setDepth() { return this; },
        setAlpha(value) { this.alpha = value; return this; },
    }) } };
    const system = new W.InteractionSystem(scene, source, item => changes.push(item?.id || null), item => triggered.push(item.id));
    const target = source.interactions[0];
    system.update(target.position);
    system.update(target.position);
    assert.deepEqual(changes, [target.id]);
    assert.ok(system.items[0].highlight.alpha > 0);
    system.trigger();
    assert.deepEqual(triggered, [target.id]);
    system.update({ x: -999, y: -999 });
    system.trigger();
    assert.deepEqual(changes, [target.id, null]);
    assert.deepEqual(triggered, [target.id]);
    assert.equal(system.items[0].highlight.alpha, 0);
});

test("Camera uses smooth bounded follow and resize", () => {
    for (const world of [source, datacenter]) {
        const calls = [];
        const camera = { height: 720, setBounds: (...args) => calls.push(["bounds", ...args]), setZoom: value => calls.push(["zoom", value]), startFollow: (...args) => calls.push(["follow", ...args]) };
        const player = {};
        new W.CameraController({ cameras: { main: camera } }, player, world);
        assert.deepEqual(calls[0], ["bounds", 0, 0, world.width, world.height]);
        assert.deepEqual(calls[2], ["follow", player, false, 0.075, 0.075]);
    }
});

function visualScene() {
    const canvases = new Map(), nodes = [], calls = [];
    const canvas = () => new Proxy({}, {
        get(target, key) {
            if (key in target) return target[key];
            if (["createLinearGradient", "createRadialGradient"].includes(key)) return () => ({ addColorStop: (...args) => calls.push(["stop", ...args]) });
            return (...args) => {
                assert.ok(args.filter(value => typeof value === "number").every(Number.isFinite));
                if (["roundRect", "fillRect", "strokeRect", "rect"].includes(key)) assert.ok(args[2] >= 0 && args[3] >= 0, `${key}: ${args}`);
                calls.push([key, ...args]);
            };
        },
        set(target, key, value) { calls.push([key, value]); target[key] = value; return true; },
    });
    const node = (kind, ...args) => {
        const item = { kind, args, alpha: 1, rotation: 0, visible: true, clears: 0 };
        for (const method of ["setDepth", "setDisplaySize", "setOrigin", "setScale", "setStrokeStyle", "setRadius", "lineStyle", "beginPath", "moveTo", "lineTo", "strokePath", "fillStyle", "fillRect"]) item[method] = () => item;
        for (const [method, field] of [["setAlpha", "alpha"], ["setRotation", "rotation"], ["setVisible", "visible"], ["setX", "x"], ["setY", "y"], ["setFillStyle", "color"]]) item[method] = value => { item[field] = value; return item; };
        item.clear = () => { item.clears++; return item; };
        nodes.push(item); return item;
    };
    return {
        calls, nodes, canvases,
        textures: {
            exists: key => canvases.has(key),
            createCanvas: (key, width, height) => {
                assert.ok(!canvases.has(key), `duplicate texture ${key}`);
                const texture = { key, width, height, context: canvas() }; canvases.set(key, texture); return texture;
            },
        },
        add: Object.fromEntries(["image", "circle", "rectangle", "ellipse", "graphics"].map(kind => [kind, (...args) => node(kind, ...args)])),
    };
}

test("Map profiles are isolated from logical component ids and default to NOC", () => {
    assert.equal(W.visualProfile(datacenter), "industrial");
    assert.equal(W.visualProfile(source), "noc");
    assert.equal(W.visualProfile({ ...datacenter, id: "web-operations-room" }), "industrial");
    assert.equal(W.visualProfile({}), "noc");
});

test("Every existing visual variant renders valid canvas geometry in both profiles", () => {
    for (const map of [source, datacenter]) {
        const before = JSON.stringify(map), scene = visualScene();
        W.drawFloors(scene, map);
        for (const object of map.objects.filter(item => item.kind !== "floor-zone")) W.textureObject(scene, object, W.visualProfile(map));
        assert.equal(JSON.stringify(map), before);
        assert.ok(scene.canvases.size <= map.objects.length + 1);
        assert.ok(!scene.calls.some(call => call.includes(undefined)));
    }
});

test("Texture cache isolates style and printed labels but reuses identical decoration", () => {
    const scene = visualScene(), rack = datacenter.objects.find(item => item.kind === "server-rack");
    const key = W.textureObject(scene, rack, "industrial");
    assert.equal(W.textureObject(scene, rack, "industrial"), key);
    assert.notEqual(W.textureObject(scene, rack), key);
    assert.notEqual(W.textureObject(scene, { ...rack, id: "rack-other" }, "industrial"), key);
    const light = datacenter.objects.find(item => item.kind === "light-strip");
    assert.equal(W.textureObject(scene, light, "industrial"), W.textureObject(scene, { ...light, id: "another-light" }, "industrial"));
    const panel = datacenter.objects.find(item => item.kind === "patch-panel");
    assert.notEqual(W.textureObject(scene, panel), W.textureObject(scene, { ...panel, label: "INNY PANEL" }));
});

test("Default Modern NOC drawing retains its palette and explicit NOC output", () => {
    const implicit = visualScene(), explicit = visualScene();
    for (const object of source.objects.filter(item => item.kind !== "floor-zone")) {
        W.textureObject(implicit, object); W.textureObject(explicit, object, "noc");
    }
    assert.equal(JSON.stringify(implicit.calls), JSON.stringify(explicit.calls));
    W.drawFloors(implicit, source);
    assert.ok(implicit.calls.some(call => call[0] === "fillStyle" && call[1] === "#34434b"));
    assert.ok(implicit.calls.some(call => call[0] === "stop" && call[2] === "#78848b"));
});

test("Modern NOC definition remains unchanged", () => {
    const { createHash } = require("node:crypto");
    assert.equal(createHash("sha256").update(JSON.stringify(source)).digest("hex"), "e59b9cbd9382c32ba3af825e5f4194eae50da07617eab13bb5f6e3740192346d");
});

test("Datacenter preserves protected geometry and bindings with the approved Operations console offset", () => {
    assert.equal(datacenter.id, "datacenter-hall");
    assert.equal(datacenter.theme, "datacenter-hall");
    assert.deepEqual([datacenter.width, datacenter.height], [2200, 1400]);
    assert.deepEqual(datacenter.player_spawn, { x: 1100, y: 1290 });
    assert.deepEqual(datacenter.ambience, { fog_radius: 250 });
    assert.deepEqual(datacenter.sectors, [
        {"id":"operations-entry","label":"Operations / wejście","rect":{"x":700,"y":1000,"width":800,"height":340}},
        {"id":"compute-hall","label":"Hala obliczeniowa","rect":{"x":60,"y":60,"width":900,"height":880}},
        {"id":"network-core","label":"Rdzeń sieci","rect":{"x":1000,"y":60,"width":520,"height":420}},
        {"id":"storage-services","label":"Storage i usługi","rect":{"x":1000,"y":520,"width":520,"height":420}},
        {"id":"power-cooling","label":"Zasilanie i chłodzenie","rect":{"x":1560,"y":60,"width":580,"height":880}},
    ]);
    assert.deepEqual(datacenter.interactions, [
        {"type":"terminal","id":"admin-terminal","label":"Otwórz terminal administracyjny","position":{"x":920,"y":1230},"radius":86,"role":"primary","object_id":"desk-admin"},
        {"type":"monitoring","id":"monitoring-station","label":"Sprawdź monitoring hali","position":{"x":1260,"y":1145},"radius":88,"role":"support","object_id":"monitor-wall-dc"},
        {"type":"terminal","id":"network-console","label":"Otwórz konsolę sieciową","position":{"x":1260,"y":475},"radius":92,"role":"support","object_id":"network-console"},
        {"type":"rack","id":"service-inspection","label":"Sprawdź rack usługowy","position":{"x":680,"y":720},"radius":90,"role":"primary","object_id":"compute-rack-c4"},
        {"type":"support","id":"infrastructure-status","label":"Sprawdź status infrastruktury","position":{"x":2045,"y":880},"radius":92,"role":"support","object_id":"infrastructure-panel"},
    ]);
    const expected = [
        {"id":"compute-rack-a1","kind":"server-rack","rect":{"x":130,"y":150,"width":86,"height":170},"label":"A01 · COMPUTE","tone":"cyan","variant":"compute","binding_slot":"host-1"},
        {"id":"compute-rack-a2","kind":"server-rack","rect":{"x":330,"y":150,"width":86,"height":170},"label":"A02 · COMPUTE","tone":"blue","variant":"compute","binding_slot":"host-2"},
        {"id":"compute-rack-a3","kind":"server-rack","rect":{"x":530,"y":150,"width":86,"height":170},"label":"A03 · PROD","tone":"amber","variant":"prod","binding_slot":"service-1"},
        {"id":"compute-rack-a4","kind":"server-rack","rect":{"x":730,"y":150,"width":86,"height":170},"label":"A04 · COMPUTE","tone":"cyan","variant":"compute","binding_slot":"host-3"},
        {"id":"compute-rack-b1","kind":"server-rack","rect":{"x":130,"y":390,"width":86,"height":170},"label":"B01 · COMPUTE","tone":"blue","variant":"compute","binding_slot":"host-4"},
        {"id":"compute-rack-b2","kind":"server-rack","rect":{"x":330,"y":390,"width":86,"height":170},"label":"B02 · PROD","tone":"amber","variant":"prod","binding_slot":"service-2"},
        {"id":"compute-rack-b3","kind":"server-rack","rect":{"x":530,"y":390,"width":86,"height":170},"label":"B03 · COMPUTE","tone":"cyan","variant":"compute","binding_slot":"host-5"},
        {"id":"compute-rack-c1","kind":"server-rack","rect":{"x":130,"y":630,"width":86,"height":170},"label":"C01 · COMPUTE","tone":"blue","variant":"compute","binding_slot":"host-6"},
        {"id":"compute-rack-c2","kind":"server-rack","rect":{"x":330,"y":630,"width":86,"height":170},"label":"C02 · PROD","tone":"amber","variant":"prod","binding_slot":"service-3"},
        {"id":"compute-rack-c4","kind":"server-rack","rect":{"x":730,"y":630,"width":86,"height":170},"label":"C04 · SPARE","tone":"neutral","variant":"spare"},
        {"id":"network-rack-n1","kind":"network-rack","rect":{"x":1050,"y":120,"width":72,"height":190},"label":"N01 · EDGE","tone":"green","variant":"edge","binding_slot":"support-host"},
        {"id":"network-console","kind":"operator-desk","rect":{"x":1130,"y":400,"width":260,"height":62},"label":"KONSOLA SIECIOWA","tone":"green","variant":"default"},
        {"id":"storage-rack-s1","kind":"server-rack","rect":{"x":1060,"y":590,"width":100,"height":130},"label":"S01 · STORAGE","tone":"green","variant":"storage","binding_slot":"service-4"},
        {"id":"storage-rack-s2","kind":"server-rack","rect":{"x":1210,"y":590,"width":100,"height":130},"label":"S02 · STORAGE","tone":"green","variant":"storage","binding_slot":"service-5"},
        {"id":"storage-rack-s4","kind":"server-rack","rect":{"x":1060,"y":780,"width":100,"height":130},"label":"S04 · SERVICES","tone":"blue","variant":"prod","binding_slot":"service-6"},
        {"id":"infrastructure-panel","kind":"access-panel","rect":{"x":1980,"y":790,"width":130,"height":52},"label":"STATUS","tone":"amber","variant":"status"},
        {"id":"monitor-wall-dc","kind":"monitor-wall","rect":{"x":1080,"y":1025,"width":360,"height":82},"label":"MONITORING INFRASTRUKTURY","tone":"cyan","variant":"default","binding_slot":"primary-service"},
        {"id":"desk-admin","kind":"operator-desk","rect":{"x":710,"y":1100,"width":300,"height":92},"label":"ADMIN TERMINAL","tone":"blue","variant":"default"},
    ];
    const targets = new Set(datacenter.interactions.map(item => item.object_id));
    const actual = datacenter.objects.filter(item => item.binding_slot || item.binding_role || item.resource_id || targets.has(item.id));
    assert.deepEqual(actual, expected);
    for (const object of actual) assert.ok(datacenter.collision_zones.some(rect => JSON.stringify(rect) === JSON.stringify(object.rect)));
});

test("Composition removes seven props and replaces four with small static variants", () => {
    const removed = ["compute-rack-b4", "compute-rack-c3", "network-rack-n2", "network-rack-n4", "storage-rack-s3", "storage-rack-s6", "ups-2"];
    const oldIds = ["desk-operations", "network-rack-n3", "storage-rack-s5", "ups-3"];
    assert.ok([...removed, ...oldIds].every(id => !datacenter.objects.some(item => item.id === id)));
    assert.equal(datacenter.objects.length, 59);
    assert.equal(datacenter.objects.filter(item => ["server-rack", "network-rack"].includes(item.kind)).length, 14);
    assert.equal(datacenter.objects.filter(item => item.kind === "ups-unit").length, 1);
    for (const [id, kind, variant, width, height] of [
        ["maintenance-cart", "cabinet", "maintenance-cart", 110, 58],
        ["fiber-distribution-frame", "wall-panel", "fiber-frame", 72, 88],
        ["service-crate", "cabinet", "service-crate", 90, 52],
        ["power-distribution-panel", "wall-panel", "power-distribution", 150, 54],
    ]) {
        const object = datacenter.objects.find(item => item.id === id);
        assert.equal(object.kind, kind); assert.equal(object.variant, variant);
        assert.deepEqual([object.rect.width, object.rect.height], [width, height]);
        const scene = visualScene();
        W.textureObject(scene, object, "industrial");
        assert.ok(scene.calls.some(call => call[0] === (variant === "fiber-frame" ? "bezierCurveTo" : "roundRect")));
        const ambient = new W.AmbientAnimationSystem(scene, new W.RuntimeBridge({ signals: [] }), [object], new W.WorldEffects(scene, "industrial"), "industrial");
        assert.equal(ambient.items.length, 0); assert.equal(ambient.decorations.length, 0);
    }
});

test("Industrial floors keep sector identity when objects are reordered", () => {
    const first = visualScene(), reordered = visualScene();
    W.drawFloors(first, datacenter);
    W.drawFloors(reordered, { ...datacenter, objects: [...datacenter.objects].reverse() });
    const labels = scene => scene.calls.filter(call => call[0] === "fillText").map(call => JSON.stringify(call)).sort();
    assert.deepEqual(labels(first), labels(reordered));
});

test("Datacenter wayfinding is baked into the floor without additional scene objects", () => {
    const scene = visualScene();
    W.drawFloors(scene, datacenter);
    assert.equal(scene.nodes.length, datacenter.sectors.length + 1);
    const labels = scene.calls.filter(call => call[0] === "fillText").map(call => call[1]);
    for (const label of ["HALA", "F01 / ŚWIATŁOWÓD", "PRZEPŁYW POWIETRZA"]) assert.ok(labels.includes(label));
    const noc = visualScene(); W.drawFloors(noc, source);
    assert.ok(!noc.calls.some(call => call[0] === "fillText" && call[1] === "HALA"));
});

test("Motion preference handles live changes, cleanup and missing matchMedia", () => {
    let callback, removed;
    context.window.matchMedia = query => {
        assert.equal(query, "(prefers-reduced-motion: reduce)");
        return { matches: true, addEventListener: (event, handler) => { callback = handler; }, removeEventListener: (event, handler) => { removed = handler; } };
    };
    const preference = new W.MotionPreference();
    assert.equal(preference.reduced, true);
    callback({ matches: false }); assert.equal(preference.reduced, false);
    preference.destroy(); assert.equal(removed, callback);
    delete context.window.matchMedia;
    const fallback = new W.MotionPreference(); assert.equal(fallback.reduced, false); fallback.destroy();
});

test("Ambient effects share textures, stagger LEDs and freeze cleanly in reduced motion", () => {
    const scene = visualScene(), motion = { reduced: false }, bridge = new W.RuntimeBridge({ signals: [] });
    const ambient = new W.AmbientAnimationSystem(scene, bridge, datacenter.objects, new W.WorldEffects(scene, "industrial"), "industrial", motion);
    ambient.update(1000);
    assert.equal(scene.canvases.size, 2);
    const fans = ambient.decorations.filter(item => item.fan);
    assert.equal(fans.length, 4);
    assert.ok(fans.some(item => item.fan.rotation !== 0));
    const rack = ambient.items.find(item => item.leds.length === 3);
    assert.notEqual(rack.leds[1].alpha, rack.leds[2].alpha);
    assert.equal(rack.leds[0].alpha, .75);
    const graph = ambient.items.find(item => item.graph).graph;
    const count = graph.clears;
    ambient.update(1010); assert.equal(graph.clears, count);
    motion.reduced = true; ambient.update(1020);
    const reducedCount = graph.clears;
    const snapshot = () => JSON.stringify(scene.nodes.map(({ alpha, rotation, visible, x, y }) => ({ alpha, rotation, visible, x, y })));
    const still = snapshot(); ambient.update(5000);
    assert.equal(snapshot(), still); assert.equal(graph.clears, reducedCount);
    assert.ok(fans.every(item => item.fan.rotation === 0));
    assert.ok(ambient.decorations.filter(item => item.pulse).every(item => !item.pulse.visible));
    motion.reduced = false; ambient.update(5100);
    assert.ok(fans.some(item => item.fan.rotation !== 0));
});

test("Reduced motion monitoring still responds to public severity without reading hidden state", () => {
    const scene = visualScene(), bridge = new W.RuntimeBridge({ signals: [] }), motion = { reduced: true };
    const map = structuredClone(datacenter);
    const monitor = map.objects.find(item => item.kind === "monitor-wall"); monitor.resource_id = "public-monitor";
    for (const object of map.objects) for (const key of ["fault_category", "root_cause", "repair_order", "hidden_dependency", "reference_solution"]) Object.defineProperty(object, key, { get() { throw new Error(`Hidden field read: ${key}`); } });
    const system = new W.AmbientAnimationSystem(scene, bridge, map.objects, new W.WorldEffects(scene, "industrial"), "industrial", motion);
    system.update(0);
    const item = system.items.find(item => item.graph), count = item.graph.clears;
    bridge.update({ signals: [{ resource_id: "public-monitor", severity: "critical" }] }); system.update(200);
    assert.equal(item.led.color, 0xd86e66); assert.equal(item.graph.clears, count + 1);
    system.update(400); assert.equal(item.graph.clears, count + 1);
    for (const object of map.objects.filter(item => item.kind !== "floor-zone")) W.textureObject(scene, object, "industrial");
});

test("Industrial interaction feedback preserves range, target and single activation", () => {
    const scene = visualScene(), motion = { reduced: true }, triggered = [];
    const system = new W.InteractionSystem(scene, datacenter, () => {}, item => triggered.push(item.id), motion);
    const target = datacenter.interactions[0];
    system.update(target.position); system.feedback(1000);
    const selected = system.current;
    assert.ok(selected.outline.alpha > 0);
    const alpha = selected.outline.alpha; system.feedback(2000); assert.equal(selected.outline.alpha, alpha);
    system.trigger(); system.feedback(2100); assert.equal(selected.outline.alpha, alpha);
    assert.deepEqual(triggered, [target.id]);
    system.update({ x: -1000, y: -1000 }); system.feedback(2200);
    assert.equal(selected.outline.alpha, 0); system.trigger(); assert.equal(triggered.length, 1);
    assert.equal(selected.radius, target.radius);
});
