(() => {
    const W = window.ShellForgeWorld;
    W.WorldManager = class WorldManager {
        constructor(options) {
            const map = W.MapLoader.load(options.map);
            this.bridge = new W.RuntimeBridge(options.monitoring);
            this.locked = false;
            const manager = this;
            class WorldScene extends Phaser.Scene {
                create() {
                    manager.scene = this;
                    this.physics.world.setBounds(0, 0, map.width, map.height);
                    W.drawFloors(this, map);
                    this.effects = new W.WorldEffects(this);
                    const obstacles = this.physics.add.staticGroup();
                    for (const r of map.collision_zones) {
                        const body = this.add.rectangle(r.x + r.width / 2, r.y + r.height / 2, r.width, r.height, 0, 0);
                        this.physics.add.existing(body, true); obstacles.add(body);
                    }
                    for (const object of map.objects.filter(item => item.kind !== "floor-zone")) {
                        const r = object.rect;
                        const floor = ["light-strip", "floor-marking", "cable-tray"].includes(object.kind);
                        if (!floor) this.add.ellipse(r.x + r.width / 2 + 6, r.y + r.height + 2, r.width + 10, 17, 0x07141b, .18).setDepth(2);
                        this.add.image(r.x, r.y, W.textureObject(this, object)).setOrigin(0).setDepth(floor ? 2 : 10 + r.y + r.height * .7);
                    }
                    this.operator = new W.PlayerController(this, map, obstacles);
                    this.cameraController = new W.CameraController(this, this.operator.sprite, map);
                    this.discovery = new W.DiscoverySystem(this, map, options.onSectorChange);
                    this.interactions = new W.InteractionSystem(this, map, options.onInteractionChange, options.onInteract);
                    this.ambient = new W.AmbientAnimationSystem(this, manager.bridge, map.objects, this.effects);
                    this.scale.on("resize", () => this.cameraController.resize());
                    this.lastReport = 0;
                    this.discovery.update(this.operator.sprite.x, this.operator.sprite.y);
                    this.cameras.main.fadeIn(350, 15, 24, 32);
                }
                update(time, delta) {
                    if (!this.operator) return;
                    this.operator.update(time, delta, manager.locked);
                    this.ambient.update(time);
                    const player = this.operator.sprite;
                    if (!manager.locked) {
                        this.discovery.update(player.x, player.y);
                        this.interactions.update(player);
                        if (Phaser.Input.Keyboard.JustDown(this.operator.keys.E)) this.interactions.trigger();
                    }
                    if (time - this.lastReport > 100) {
                        this.lastReport = time;
                        this.game.canvas.dataset.fps = String(Math.round(this.game.loop.actualFps));
                        options.onPlayerState({ x: Math.round(player.x), y: Math.round(player.y), sector: this.discovery.current?.id || null, discovered: this.discovery.state.discovered.size });
                    }
                }
            }
            this.game = new Phaser.Game({
                type: Phaser.CANVAS, parent: options.parent, backgroundColor: "#172631",
                scale: { mode: Phaser.Scale.RESIZE, width: "100%", height: "100%" },
                physics: { default: "arcade", arcade: { debug: false } },
                render: { antialias: true, pixelArt: false, roundPixels: false },
                scene: WorldScene,
            });
            this.options = options;
        }
        setInputLocked(locked) {
            this.locked = locked;
            const scene = this.scene;
            if (!scene?.input?.keyboard) return;
            scene.input.keyboard.enabled = !locked;
            scene.input.keyboard.resetKeys();
            if (locked) scene.operator.sprite.body.setVelocity(0, 0);
            else { this.game.canvas.setAttribute("tabindex", "-1"); this.game.canvas.focus({ preventScroll: true }); }
        }
        updateMonitoring(monitoring) { this.bridge.update(monitoring); }
        destroy() { this.options.onInteractionChange(null); this.game.destroy(true); this.scene = null; }
    };
    window.ShellForgeDynamicGame = { createGame: options => new W.WorldManager(options) };
})();
