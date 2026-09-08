(() => {
    const W = window.ShellForgeWorld;
    W.WorldEffects = class WorldEffects {
        constructor(scene) {
            this.scene = scene;
            if (!scene.textures.exists("soft-glow")) {
                const t = scene.textures.createCanvas("soft-glow", 128, 128);
                const g = t.context.createRadialGradient(64, 64, 0, 64, 64, 64);
                g.addColorStop(0, "#bddae855"); g.addColorStop(.4, "#aac8d522"); g.addColorStop(1, "#aac8d500");
                t.context.fillStyle = g; t.context.fillRect(0, 0, 128, 128);
            }
        }
        glow(x, y, width = 150, height = 110) {
            return this.scene.add.image(x, y, "soft-glow").setDisplaySize(width, height).setDepth(2).setAlpha(.4);
        }
    };
    W.AmbientAnimationSystem = class AmbientAnimationSystem {
        constructor(scene, bridge, objects, effects) {
            this.scene = scene; this.bridge = bridge; this.items = [];
            for (const object of objects) {
                if (!["server-rack", "operator-desk", "monitor-wall", "board"].includes(object.kind)) continue;
                const r = object.rect;
                const depth = 10 + r.y + r.height * .7;
                const led = scene.add.circle(r.x + r.width - 20, r.y + 24, 2.5, 0x7fae95).setDepth(depth + .1);
                const glow = effects.glow(r.x + r.width / 2, r.y + r.height * .65, r.width * 1.4, r.height * 1.5);
                let graph = null;
                if (object.kind === "monitor-wall") graph = scene.add.graphics().setDepth(depth + .1);
                this.items.push({ object, led, glow, graph, phase: this.items.length * 1.731 });
            }
            this.lastGraph = 0;
        }
        update(time) {
            const redraw = time - this.lastGraph > 90;
            for (const item of this.items) {
                const severity = this.bridge.severity(item.object.resource_id);
                const color = this.bridge.color(item.object.resource_id);
                item.led.setFillStyle(color).setAlpha(.45 + .5 * Math.abs(Math.sin(time / (severity === "ok" ? 370 : 920) + item.phase)));
                item.glow.setAlpha(.16 + .08 * Math.sin(time / 1500 + item.phase));
                if (!item.graph || !redraw) continue;
                const r = item.object.rect;
                item.graph.clear().lineStyle(1.4, color, .8);
                for (let screen = 0; screen < 4; screen++) {
                    const x = r.x + 15 + screen * (r.width - 25) / 4;
                    const width = (r.width - 70) / 4;
                    item.graph.beginPath();
                    for (let i = 0; i < 18; i++) {
                        const yy = r.y + 55 + Math.sin(i * .7 + time / 1400 + screen) * (severity === "ok" ? 8 : 17) + Math.cos(i * 1.6 + time / 2100) * 5;
                        if (i === 0) item.graph.moveTo(x, yy); else item.graph.lineTo(x + i * width / 17, yy);
                    }
                    item.graph.strokePath();
                    for (let bar = 0; bar < 6; bar++) {
                        item.graph.fillStyle(color, .2 + bar * .08);
                        item.graph.fillRect(x + bar * width / 6, r.y + r.height - 25, width / 6 - 4, 4 + 6 * Math.abs(Math.sin(time / 1900 + bar + screen)));
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
        constructor(scene, map, changed, interact) {
            this.scene = scene; this.changed = changed; this.interact = interact; this.current = null;
            this.items = map.interactions.map(item => {
                const highlight = scene.add.ellipse(item.position.x, item.position.y, 55, 22, 0xb3d5db, .07).setStrokeStyle(1, 0xc0dbe0, .25).setDepth(3).setAlpha(0);
                return { ...item, highlight };
            });
        }
        update(player) {
            const nearest = W.nearestInteraction(this.items, player);
            for (const item of this.items) {
                const distance = Math.hypot(player.x - item.position.x, player.y - item.position.y);
                item.highlight.setAlpha(Math.max(0, 1 - distance / (item.radius * 1.8)) * .7);
            }
            if (nearest?.id !== this.current?.id) { this.current = nearest; this.changed(nearest); }
        }
        trigger() { if (this.current) this.interact(this.current); }
    };
    W.PlayerController = class PlayerController {
        constructor(scene, map, obstacles) {
            this.scene = scene; this.facing = "down"; this.elapsed = 0;
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
            this.sprite.setScale(1, length ? 1 : 1 + Math.sin(time / 1400) * .008);
            this.sprite.setDepth(10 + this.sprite.y);
            this.shadow.setPosition(this.sprite.x, this.sprite.y + 3);
        }
    };
})();
