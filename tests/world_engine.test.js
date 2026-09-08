const { test } = require("node:test");
const assert = require("node:assert/strict");
const fs = require("node:fs");
const vm = require("node:vm");
const context = { window: {} };
vm.createContext(context);
vm.runInContext(fs.readFileSync("app/static/admin_duty/dynamic/world-core.js", "utf8"), context);
vm.runInContext(fs.readFileSync("app/static/admin_duty/dynamic/world-systems.js", "utf8"), context);
const W = context.window.ShellForgeWorld;
const source = JSON.parse(fs.readFileSync("app/admin_duty/components/maps/modern_noc.json", "utf8"));

test("MapLoader loads JSON, rejects duplicate ids and invalid geometry", () => {
    assert.equal(W.MapLoader.load(source), source);
    const invalid = structuredClone(source);
    invalid.objects.push(invalid.objects[0]);
    assert.throws(() => W.MapLoader.load(invalid));
    invalid.objects.pop();
    invalid.player_spawn.x = -1;
    assert.throws(() => W.MapLoader.load(invalid));
    invalid.player_spawn.x = 100;
    invalid.interactions[0].radius = 0;
    assert.throws(() => W.MapLoader.load(invalid));
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
    const calls = [];
    const camera = { height: 720, setBounds: (...args) => calls.push(["bounds", ...args]), setZoom: value => calls.push(["zoom", value]), startFollow: (...args) => calls.push(["follow", ...args]) };
    const player = {};
    new W.CameraController({ cameras: { main: camera } }, player, source);
    assert.deepEqual(calls[0], ["bounds", 0, 0, source.width, source.height]);
    assert.deepEqual(calls[2], ["follow", player, false, 0.075, 0.075]);
});
