(() => {
    const W = window.ShellForgeWorld;
    W.MotionPreference = class MotionPreference {
        constructor() {
            this.query = window.matchMedia?.("(prefers-reduced-motion: reduce)");
            this.reduced = Boolean(this.query?.matches);
            this.changed = event => { this.reduced = event.matches; };
            this.query?.addEventListener("change", this.changed);
        }
        destroy() { this.query?.removeEventListener("change", this.changed); }
    };
    W.WorldEffects = class WorldEffects {
        constructor(scene, profile = "noc") {
            this.scene = scene;
            this.key = profile === "industrial" ? "industrial-glow" : "soft-glow";
            if (!scene.textures.exists(this.key)) {
                const t = scene.textures.createCanvas(this.key, 128, 128);
                const g = t.context.createRadialGradient(64, 64, 0, 64, 64, 64);
                if (profile === "industrial") {
                    g.addColorStop(0, "#e1e5cd35"); g.addColorStop(.4, "#c3d2c618"); g.addColorStop(1, "#c3d2c600");
                } else {
                    g.addColorStop(0, "#bddae855"); g.addColorStop(.4, "#aac8d522"); g.addColorStop(1, "#aac8d500");
                }
                t.context.fillStyle = g; t.context.fillRect(0, 0, 128, 128);
            }
        }
        glow(x, y, width = 150, height = 110) {
            return this.scene.add.image(x, y, this.key).setDisplaySize(width, height).setDepth(2).setAlpha(.4);
        }
    };
    W.AmbientAnimationSystem = class AmbientAnimationSystem {
        constructor(scene, bridge, objects, effects, profile = "noc", motion = { reduced: false }) {
            this.scene = scene; this.bridge = bridge; this.items = [];
            this.industrial = profile === "industrial"; this.motion = motion; this.decorations = []; this.lastUpdate = -Infinity;
            if (this.industrial && !scene.textures.exists("dc-fan")) {
                const t = scene.textures.createCanvas("dc-fan", 80, 80), c = t.context;
                for (let blade = 0; blade < 6; blade++) {
                    c.save(); c.translate(40, 40); c.rotate(blade * Math.PI / 3);
                    c.fillStyle = "#657674"; c.beginPath(); c.moveTo(3, -8); c.lineTo(15, -30); c.lineTo(4, -34); c.lineTo(-5, -15); c.closePath(); c.fill(); c.restore();
                }
                c.fillStyle = "#939f94"; c.beginPath(); c.arc(40, 40, 7, 0, Math.PI * 2); c.fill();
            }
            for (const object of objects) {
                const r = object.rect;
                const depth = 10 + r.y + r.height * .7;
                if (this.industrial && object.kind === "light-strip") effects.glow(r.x + r.width / 2, r.y + r.height / 2, r.width + 100, r.height + 100).setAlpha(.65);
                if (this.industrial && object.kind === "cooling-unit") {
                    const fan = scene.add.image(r.x + r.width / 2, r.y + r.height * .31, "dc-fan").setDisplaySize(r.width * .66, r.width * .66).setDepth(depth + .1);
                    const air = scene.add.rectangle(r.x + r.width / 2, r.y + r.height * .74, r.width * .5, 2, 0xa0b9b5).setDepth(depth + .1).setAlpha(.3);
                    effects.glow(r.x + r.width / 2, r.y + r.height, r.width * 1.4, 90).setAlpha(.35);
                    this.decorations.push({ object, fan, air, phase: this.decorations.length * 1.73 });
                }
                if (this.industrial && object.kind === "cable-tray" && object.id === "tray-network") {
                    const pulse = scene.add.rectangle(r.x, r.y + r.height / 2, 14, 2, 0xc0cdc0).setDepth(2.1).setAlpha(.5);
                    this.decorations.push({ object, pulse, phase: .5 });
                }
                if (!["server-rack", "network-rack", "operator-desk", "monitor-wall", "board", "ups-unit", "access-panel", ...(this.industrial ? ["patch-panel"] : [])].includes(object.kind)) continue;
                const led = scene.add.circle(r.x + r.width - 20, r.y + 24, 2.5, 0x7fae95).setDepth(depth + .1);
                const glow = effects.glow(r.x + r.width / 2, r.y + r.height * .65, r.width * 1.4, r.height * 1.5);
                const leds = [];
                if (this.industrial) {
                    led.setRadius(1.7);
                    const rack = ["server-rack", "network-rack"].includes(object.kind);
                    for (let i = 0; i < (rack ? 3 : object.kind === "patch-panel" ? 4 : 0); i++) {
                        const x = rack ? r.x + r.width - 25 : r.x + 20 + i * (r.width - 40) / 4;
                        const y = rack ? r.y + 23 + i * (r.height - 40) / (object.kind === "network-rack" ? 6 : object.variant === "storage" ? 5 : 8) : r.y + 12;
                        leds.push(scene.add.circle(x, y, 1.3, 0x9db99b).setDepth(depth + .1));
                    }
                }
                let graph = null;
                if (object.kind === "monitor-wall") graph = scene.add.graphics().setDepth(depth + .1);
                this.items.push({ object, led, leds, glow, graph, phase: this.items.length * 1.731 });
            }
            this.lastGraph = 0;
        }
        update(time) {
            if (this.industrial && time - this.lastUpdate < 50 && this.lastReduced === this.motion.reduced) return;
            this.lastUpdate = time;
            const motionChanged = this.lastReduced !== this.motion.reduced;
            this.lastReduced = this.motion.reduced;
            const tick = this.motion.reduced ? 0 : time;
            const redraw = !this.motion.reduced && time - this.lastGraph > (this.industrial ? 150 : 90);
            for (const item of this.decorations) {
                const r = item.object.rect;
                if (item.fan) {
                    item.fan.setRotation(this.motion.reduced ? 0 : tick / 5000 + item.phase);
                    item.air.setY(r.y + r.height * (.65 + (this.motion.reduced ? .4 : (tick / 4500 + item.phase) % 1) * .18));
                }
                if (item.pulse) item.pulse.setVisible(!this.motion.reduced).setX(r.x + 10 + ((tick / 5000 + item.phase) % 1) * (r.width - 20));
            }
            for (const item of this.items) {
                const severity = this.bridge.severity(item.object.resource_id);
                const color = this.bridge.color(item.object.resource_id);
                item.led.setFillStyle(color).setAlpha(this.motion.reduced ? .8 : this.industrial ? .7 + .15 * Math.sin(tick / 1300 + item.phase) : .45 + .5 * Math.abs(Math.sin(tick / (severity === "ok" ? 370 : 920) + item.phase)));
                item.glow.setAlpha(this.industrial ? .12 : this.motion.reduced ? .16 : .16 + .08 * Math.sin(tick / 1500 + item.phase));
                const period = item.object.kind === "network-rack" || item.object.kind === "patch-panel" ? 210 : item.object.variant === "storage" ? 900 : 470;
                item.leds.forEach((led, i) => led.setAlpha(this.motion.reduced || i === 0 ? .75 : .35 + .5 * Math.abs(Math.sin(tick / (period + i * 137) + item.phase + i * 2.31))));
                if (!item.graph || !(redraw || motionChanged || item.lastColor !== color)) continue;
                item.lastColor = color;
                const r = item.object.rect;
                item.graph.clear().lineStyle(1.4, color, .8);
                for (let screen = 0; screen < 4; screen++) {
                    const x = r.x + 15 + screen * (r.width - 25) / 4;
                    const width = (r.width - 70) / 4;
                    item.graph.beginPath();
                    for (let i = 0; i < 18; i++) {
                        const yy = this.industrial ? r.y + r.height * .46 + Math.sin(i * .7 + tick / 1400 + screen) * r.height * .09 + Math.cos(i * 1.6 + tick / 2100) * 2 : r.y + 55 + Math.sin(i * .7 + tick / 1400 + screen) * (severity === "ok" ? 8 : 17) + Math.cos(i * 1.6 + tick / 2100) * 5;
                        if (i === 0) item.graph.moveTo(x, yy); else item.graph.lineTo(x + i * width / 17, yy);
                    }
                    item.graph.strokePath();
                    for (let bar = 0; bar < 6; bar++) {
                        item.graph.fillStyle(color, .2 + bar * .08);
                        item.graph.fillRect(x + bar * width / 6, r.y + r.height - 25, width / 6 - 4, 4 + 6 * Math.abs(Math.sin(tick / 1900 + bar + screen)));
                    }
                    if (this.industrial && !this.motion.reduced) {
                        item.graph.fillStyle(0xc3d0c5, .16);
                        item.graph.fillRect(x, r.y + 26 + ((tick / 6000 + screen / 4) % 1) * (r.height - 59), width, 1);
                    }
                    if (this.industrial && severity !== "ok") {
                        item.graph.fillStyle(color, this.motion.reduced ? .65 : .45 + .2 * Math.max(0, Math.sin(tick / 2400)));
                        item.graph.fillRect(x + width - 5, r.y + 15, 4, 4);
                    }
                }
            }
            if (redraw) this.lastGraph = time;
        }
    };
    W.DiscoverySystem = class DiscoverySystem {
        constructor(scene, map, report) {
            this.scene = scene; this.map = map; this.report = report;
            this.state = new W.DiscoveryState(map);
            this.texture = scene.textures.createCanvas("exploration-fog", Math.ceil(map.width / 2), Math.ceil(map.height / 2));
            const c = this.texture.context;
            c.fillStyle = "#0b1723"; c.fillRect(0, 0, this.texture.width, this.texture.height);
            scene.add.image(0, 0, "exploration-fog").setOrigin(0).setScale(2).setDepth(20000).setAlpha(.94);
            this.last = { x: -1000, y: -1000 }; this.current = null;
        }
        update(x, y) {
            if (Math.hypot(x - this.last.x, y - this.last.y) > 8) {
                const c = this.texture.context;
                const radius = (this.map.ambience?.fog_radius || 230) / 2;
                const g = c.createRadialGradient(x / 2, y / 2, 18, x / 2, y / 2, radius);
                g.addColorStop(0, "#000"); g.addColorStop(.45, "#000e"); g.addColorStop(1, "#0000");
                c.globalCompositeOperation = "destination-out";
                c.fillStyle = g;
                c.fillRect(x / 2 - radius, y / 2 - radius, radius * 2, radius * 2);
                c.globalCompositeOperation = "source-over";
                this.last = { x, y };
            }
            const state = this.state.visit(x, y);
            if (state.newlyDiscovered || state.current?.id !== this.current?.id) { this.current = state.current; this.report(state); }
        }
    };
    W.InteractionSystem = class InteractionSystem {
        constructor(scene, map, changed, interact, motion = { reduced: false }) {
            this.scene = scene; this.changed = changed; this.interact = interact; this.current = null;
            this.industrial = map.theme === "datacenter-hall"; this.motion = motion; this.time = 0;
            this.items = map.interactions.map(item => {
                const highlight = scene.add.ellipse(item.position.x, item.position.y, 55, 22, 0xb3d5db, .07).setStrokeStyle(1, 0xc0dbe0, .25).setDepth(3).setAlpha(0);
                const r = map.objects.find(object => object.id === item.object_id)?.rect;
                const outline = this.industrial && r ? scene.add.rectangle(r.x + r.width / 2, r.y + r.height / 2, r.width + 6, r.height + 6).setStrokeStyle(1, 0xd1c7a0, .8).setDepth(10 + r.y + r.height * .7 + .2).setAlpha(0) : null;
                return { ...item, highlight, outline, proximity: 0, entered: -Infinity, activated: -Infinity };
            });
        }
        update(player) {
            const nearest = W.nearestInteraction(this.items, player);
            for (const item of this.items) {
                const distance = Math.hypot(player.x - item.position.x, player.y - item.position.y);
                item.highlight.setAlpha(Math.max(0, 1 - distance / (item.radius * 1.8)) * .7);
                item.proximity = Math.max(0, 1 - distance / (item.radius * 1.8));
            }
            if (nearest?.id !== this.current?.id) { this.current = nearest; if (nearest) nearest.entered = this.time; this.changed(nearest); }
        }
        feedback(time) {
            this.time = time;
            if (!this.industrial) return;
            for (const item of this.items) {
                const selected = item.id === this.current?.id;
                const pulse = this.motion.reduced ? 0 : Math.max(0, 1 - (time - Math.max(item.entered, item.activated)) / 450);
                item.outline?.setAlpha(selected ? .42 + pulse * .35 : 0);
                item.highlight.setAlpha(item.proximity * (selected ? .65 + pulse * .25 : .3));
            }
        }
        trigger() { if (this.current) { this.current.activated = this.time; this.interact(this.current); } }
    };
    W.PlayerController = class PlayerController {
        constructor(scene, map, obstacles, motion = { reduced: false }) {
            this.scene = scene; this.facing = "down"; this.elapsed = 0;
            this.motion = motion;
            this.shadow = scene.add.ellipse(map.player_spawn.x, map.player_spawn.y + 3, 25, 10, 0x07121a, .3).setDepth(3);
            for (const direction of ["down", "up", "left", "right"]) for (let frame = 0; frame < 4; frame++) {
                const key = "operator-" + direction + "-" + frame;
                const t = scene.textures.createCanvas(key, 44, 66), c = t.context;
                const side = ["left", "right"].includes(direction), sign = direction === "left" ? -1 : 1;
                const stride = Math.sin(frame / 4 * Math.PI * 2) * 4;
                c.translate(22, 0);
                const shape = (x, y, w, h, color) => { c.fillStyle = color; c.beginPath(); c.roundRect(x, y, w, h, Math.min(4, w / 2)); c.fill(); };
                shape(-9, 44 + stride, 7, 16, "#26323c"); shape(2, 44 - stride, 7, 16, "#35404a");
                shape(-10, 57 + stride, 9, 5, "#15212a"); shape(1, 57 - stride, 10, 5, "#1a2730");
                shape(side ? -8 : -12, 25, side ? 17 : 24, 23, "#768d9c");
                shape(side ? sign * 6 - 3 : -17, 28 + stride / 2, 6, 21, "#c79f86");
                if (!side) shape(12, 28 - stride / 2, 6, 21, "#c79f86");
                shape(-7, 18, 14, 12, "#c9a68c");
                c.fillStyle = "#d3af91"; c.beginPath(); c.ellipse(side ? sign * 2 : 0, 15, 10, 12, 0, 0, Math.PI * 2); c.fill();
                shape(-10, 4, 20, direction === "up" ? 19 : 9, "#443e39");
                if (direction !== "up") { shape(side ? sign * 9 : -5, 15, 2, 2, "#343b3e"); if (!side) shape(4, 15, 2, 2, "#343b3e"); }
                if (direction === "down") { shape(4, 31, 5, 7, "#dce0d8"); shape(5, 31, 3, 2, "#568696"); }
            }
            this.sprite = scene.add.sprite(map.player_spawn.x, map.player_spawn.y, "operator-down-0").setOrigin(.5, .94);
            scene.physics.add.existing(this.sprite);
            this.sprite.body.setSize(20, 12).setOffset(12, 51).setCollideWorldBounds(true);
            scene.physics.add.collider(this.sprite, obstacles);
            this.keys = scene.input.keyboard.addKeys("W,A,S,D,E,UP,DOWN,LEFT,RIGHT");
            this.pulseUntil = {};
            for (const [name, key] of Object.entries(this.keys)) {
                if (name !== "E") key.on("down", () => { this.pulseUntil[name] = scene.time.now + 80; });
            }
        }
        update(time, delta, locked) {
            const k = this.keys;
            if (locked) this.pulseUntil = {};
            const down = name => k[name].isDown || time < (this.pulseUntil[name] || 0);
            let x = locked ? 0 : Number(down("D") || down("RIGHT")) - Number(down("A") || down("LEFT"));
            let y = locked ? 0 : Number(down("S") || down("DOWN")) - Number(down("W") || down("UP"));
            const length = Math.hypot(x, y);
            if (length) { x /= length; y /= length; this.facing = Math.abs(x) > Math.abs(y) ? (x < 0 ? "left" : "right") : (y < 0 ? "up" : "down"); }
            this.sprite.body.setVelocity(x * 235, y * 235);
            this.elapsed += delta;
            const frame = length ? Math.floor(this.elapsed / 130) % 4 : 0;
            this.sprite.setTexture("operator-" + this.facing + "-" + frame);
            this.sprite.setScale(1, length || this.motion.reduced ? 1 : 1 + Math.sin(time / 1400) * .008);
            this.sprite.setDepth(10 + this.sprite.y);
            this.shadow.setPosition(this.sprite.x, this.sprite.y + 3);
        }
    };
})();
