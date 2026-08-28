(() => {
    const toneColors = {
        cyan: 0x38bdf8,
        blue: 0x3b82f6,
        amber: 0xf59e0b,
        green: 0x22c55e,
        neutral: 0x64748b,
        danger: 0xef4444,
    };

    const severityColors = {
        ok: 0x22c55e,
        warning: 0xf59e0b,
        critical: 0xef4444,
    };

    function colorHex(color) {
        return `#${color.toString(16).padStart(6, "0")}`;
    }

    function createGame({
        parent,
        map,
        monitoring,
        onInteractionChange,
        onInteract,
        onSectorChange,
        onPlayerState,
    }) {
        if (!window.Phaser) {
            throw new Error("Silnik mapy nie został załadowany.");
        }

        let scene = null;
        let inputLocked = false;
        let monitoringState = monitoring;

        class ModernNocScene extends Phaser.Scene {
            constructor() {
                super("modern-noc");
                this.nearestInteraction = null;
                this.currentSector = null;
                this.discoveredSectors = new Set();
                this.fogLayers = new Map();
                this.lastPlayerReport = 0;
                this.walkTime = 0;
                this.keyPulse = null;
            }

            create() {
                scene = this;
                this.cameras.main.setBackgroundColor("#080d16");
                this.physics.world.setBounds(0, 0, map.width, map.height);
                this.drawEnvironment();
                this.createCollisions();
                this.createInteractions();
                this.createPlayer();
                this.createInput();
                this.renderInfrastructureLights();
                this.createFogOfWar();
                this.configureCamera();
                this.updateExploration(true);
                this.cameras.main.fadeIn(380, 2, 6, 14);
                this.scale.on("resize", () => this.configureCamera());
            }

            drawEnvironment() {
                const floor = this.add.graphics().setDepth(0);
                floor.fillStyle(0x111827, 1);
                floor.fillRect(0, 0, map.width, map.height);
                floor.lineStyle(1, 0x263449, 0.42);
                for (let x = 42; x < map.width; x += 36) {
                    floor.lineBetween(x, 42, x, map.height - 42);
                }
                for (let y = 42; y < map.height; y += 36) {
                    floor.lineBetween(42, y, map.width - 42, y);
                }

                map.objects.forEach((object) => this.drawObject(object));

                const walls = this.add.graphics().setDepth(5);
                walls.fillStyle(0x334155, 1);
                walls.fillRect(0, 0, map.width, 42);
                walls.fillRect(0, map.height - 42, map.width, 42);
                walls.fillRect(0, 0, 42, map.height);
                walls.fillRect(map.width - 42, 0, 42, map.height);
                walls.lineStyle(3, 0x64748b, 0.8);
                walls.strokeRect(42, 42, map.width - 84, map.height - 84);

            }

            drawObject(object) {
                const { x, y, width, height } = object.rect;
                const color = toneColors[object.tone] || toneColors.neutral;
                const graphics = this.add.graphics().setDepth(2);

                if (object.kind === "floor-zone") {
                    graphics.fillStyle(color, 0.035);
                    graphics.fillRect(x, y, width, height);
                    graphics.lineStyle(1, color, 0.13);
                    graphics.strokeRect(x, y, width, height);
                }

                if (object.kind === "server-rack") {
                    graphics.fillStyle(0x020617, 0.38);
                    graphics.fillRoundedRect(x + 7, y + 8, width, height, 5);
                    graphics.fillStyle(0x0f172a, 1);
                    graphics.fillRoundedRect(x, y, width, height, 5);
                    graphics.lineStyle(2, 0x64748b, 0.9);
                    graphics.strokeRoundedRect(x, y, width, height, 5);
                    for (let slot = 0; slot < 8; slot += 1) {
                        const slotY = y + 17 + slot * 18;
                        graphics.fillStyle(0x1e293b, 1);
                        graphics.fillRect(x + 11, slotY, width - 22, 11);
                        graphics.lineStyle(1, 0x475569, 0.8);
                        graphics.strokeRect(x + 11, slotY, width - 22, 11);
                        graphics.fillStyle(slot === 3 ? color : 0x22c55e, 0.9);
                        graphics.fillCircle(x + width - 19, slotY + 5, 2.5);
                    }
                }

                if (object.kind === "operator-desk") {
                    graphics.fillStyle(0x020617, 0.34);
                    graphics.fillRoundedRect(x + 7, y + 8, width, height, 7);
                    graphics.fillStyle(0x475569, 1);
                    graphics.fillRoundedRect(x, y, width, height, 7);
                    graphics.lineStyle(2, 0x64748b, 0.9);
                    graphics.strokeRoundedRect(x, y, width, height, 7);
                    const monitorCount = width > 245 ? 3 : 2;
                    const monitorWidth = Math.min(62, (width - 34) / monitorCount - 8);
                    for (let index = 0; index < monitorCount; index += 1) {
                        const monitorX = x + 20 + monitorWidth / 2 + index * (monitorWidth + 10);
                        graphics.fillStyle(0x0f172a, 1);
                        graphics.fillRoundedRect(monitorX - monitorWidth / 2, y + 13, monitorWidth, 38, 3);
                        graphics.lineStyle(2, 0x94a3b8, 0.7);
                        graphics.strokeRoundedRect(monitorX - monitorWidth / 2, y + 13, monitorWidth, 38, 3);
                        graphics.fillStyle(color, 0.32 + index * 0.08);
                        graphics.fillRect(monitorX - monitorWidth / 2 + 5, y + 18, monitorWidth - 10, 28);
                        graphics.fillStyle(0x64748b, 1);
                        graphics.fillRect(monitorX - 2, y + 51, 4, 10);
                    }
                }

                if (object.kind === "monitor-wall") {
                    graphics.fillStyle(0x020617, 0.5);
                    graphics.fillRoundedRect(x + 8, y + 9, width, height, 5);
                    graphics.fillStyle(0x0f172a, 1);
                    graphics.fillRoundedRect(x, y, width, height, 5);
                    graphics.lineStyle(3, 0x64748b, 0.85);
                    graphics.strokeRoundedRect(x, y, width, height, 5);
                    for (let screen = 0; screen < 4; screen += 1) {
                        const screenWidth = (width - 50) / 4;
                        const screenX = x + 10 + screen * (screenWidth + 10);
                        graphics.fillStyle(0x0c4a6e, 0.7);
                        graphics.fillRect(screenX, y + 13, screenWidth, height - 26);
                        graphics.lineStyle(1, color, 0.55);
                        graphics.strokeRect(screenX, y + 13, screenWidth, height - 26);
                        graphics.lineBetween(screenX + 10, y + height - 27, screenX + screenWidth * 0.45, y + 31);
                        graphics.lineBetween(screenX + screenWidth * 0.45, y + 31, screenX + screenWidth - 10, y + height - 40);
                    }
                }

                if (object.kind === "chair") {
                    graphics.fillStyle(0x020617, 0.25);
                    graphics.fillEllipse(x + width / 2 + 5, y + height / 2 + 7, width, height * 0.7);
                    graphics.fillStyle(0x1e293b, 1);
                    graphics.fillEllipse(x + width / 2, y + height / 2, width - 8, height - 12);
                    graphics.lineStyle(2, 0x475569, 1);
                    graphics.strokeEllipse(x + width / 2, y + height / 2, width - 8, height - 12);
                }

                if (object.kind === "partition" || object.kind === "wall-panel") {
                    graphics.fillStyle(0x334155, 1);
                    graphics.fillRect(x, y, width, height);
                    graphics.lineStyle(2, 0x64748b, 0.75);
                    graphics.strokeRect(x, y, width, height);
                }

                if (object.kind === "door") {
                    graphics.fillStyle(0x14532d, 0.5);
                    graphics.fillRect(x, y, width, height);
                    graphics.lineStyle(2, color, 0.85);
                    graphics.strokeRect(x, y, width, height);
                    graphics.lineBetween(x + width / 2, y, x + width / 2, y + height);
                }

                if (object.kind === "cable-tray") {
                    graphics.fillStyle(0x111827, 1);
                    graphics.fillRect(x, y, width, height);
                    graphics.lineStyle(2, color, 0.35);
                    for (let cable = 0; cable < 4; cable += 1) {
                        graphics.lineBetween(x + 10, y + 5 + cable * 5, x + width - 10, y + 5 + cable * 5);
                    }
                }

                if (object.kind === "light-strip" || object.kind === "floor-marking") {
                    graphics.fillStyle(color, object.kind === "light-strip" ? 0.58 : 0.22);
                    graphics.fillRect(x, y, width, height);
                }

                if (object.kind === "plant") {
                    graphics.fillStyle(0x78350f, 1);
                    graphics.fillRect(x + width * 0.28, y + height * 0.6, width * 0.44, height * 0.38);
                    graphics.fillStyle(color, 0.72);
                    graphics.fillCircle(x + width * 0.34, y + height * 0.42, width * 0.24);
                    graphics.fillCircle(x + width * 0.62, y + height * 0.35, width * 0.25);
                    graphics.fillCircle(x + width * 0.5, y + height * 0.18, width * 0.22);
                }

                if (object.label && ["operator-desk", "door"].includes(object.kind)) {
                    this.add.text(x + width / 2, y + height - 10, object.label, {
                        color: colorHex(color),
                        fontFamily: "Arial",
                        fontSize: "9px",
                        fontStyle: "bold",
                        letterSpacing: 0.5,
                    }).setOrigin(0.5).setAlpha(0.58).setDepth(3);
                }
            }

            createCollisions() {
                this.obstacles = this.physics.add.staticGroup();
                map.collision_zones.forEach((zone) => {
                    const obstacle = this.add.rectangle(
                        zone.x + zone.width / 2,
                        zone.y + zone.height / 2,
                        zone.width,
                        zone.height,
                        0x000000,
                        0,
                    );
                    this.physics.add.existing(obstacle, true);
                    this.obstacles.add(obstacle);
                });
            }

            createInteractions() {
                this.interactions = map.interactions.map((interaction) => {
                    const color = interaction.type === "terminal"
                        ? toneColors.blue
                        : interaction.type === "monitoring"
                            ? toneColors.cyan
                            : interaction.type === "support"
                                ? toneColors.green
                                : toneColors.amber;
                    const offsets = {
                        terminal: { x: 58, y: 28 },
                        monitoring: { x: 64, y: 26 },
                        support: { x: 60, y: 28 },
                        rack: { x: -42, y: 36 },
                    };
                    const offset = offsets[interaction.type] || { x: 0, y: 32 };
                    const marker = this.add.container(
                        interaction.position.x + offset.x,
                        interaction.position.y + offset.y,
                    ).setDepth(7).setAlpha(0);
                    const halo = this.add.circle(0, 0, 18, color, 0.05).setStrokeStyle(1, color, 0.46);
                    const glyphs = { terminal: ">_", monitoring: "◫", support: "?", rack: "▤" };
                    const glyph = this.add.text(0, 0, glyphs[interaction.type] || "·", {
                        color: colorHex(color),
                        fontFamily: "monospace",
                        fontSize: "12px",
                        fontStyle: "bold",
                    }).setOrigin(0.5);
                    marker.add([halo, glyph]);
                    this.tweens.add({ targets: halo, scale: 1.16, alpha: 0.18, duration: 1250, yoyo: true, repeat: -1 });
                    return { ...interaction, marker };
                });
            }

            createPlayer() {
                const shadow = this.add.ellipse(0, 18, 28, 10, 0x000000, 0.3);
                const leftLeg = this.add.rectangle(-6, 11, 7, 15, 0x1e293b);
                const rightLeg = this.add.rectangle(6, 11, 7, 15, 0x1e293b);
                const body = this.add.rectangle(0, -5, 25, 28, 0x2563eb).setStrokeStyle(2, 0x60a5fa);
                const leftArm = this.add.rectangle(-16, -4, 6, 22, 0xd9a178);
                const rightArm = this.add.rectangle(16, -4, 6, 22, 0xd9a178);
                const head = this.add.circle(0, -27, 11, 0xe3b38d);
                const hair = this.add.rectangle(0, -35, 19, 6, 0x1e293b);
                const badge = this.add.rectangle(6, -6, 5, 7, 0xe2e8f0);
                this.playerParts = { leftLeg, rightLeg, leftArm, rightArm };
                this.player = this.add.container(map.player_spawn.x, map.player_spawn.y, [shadow, leftLeg, rightLeg, body, leftArm, rightArm, head, hair, badge]).setDepth(30);
                this.physics.add.existing(this.player);
                this.player.body.setSize(28, 40).setOffset(-14, -20);
                this.player.body.setCollideWorldBounds(true);
                this.physics.add.collider(this.player, this.obstacles);
                this.playerLabel = this.add.text(this.player.x, this.player.y - 50, "Operator", {
                    color: "#bae6fd",
                    backgroundColor: "rgba(15,23,42,0.78)",
                    fontFamily: "Arial",
                    fontSize: "11px",
                    padding: { x: 6, y: 3 },
                }).setOrigin(0.5).setDepth(31);
            }

            createInput() {
                this.cursors = this.input.keyboard.createCursorKeys();
                this.keys = this.input.keyboard.addKeys({
                    up: Phaser.Input.Keyboard.KeyCodes.W,
                    down: Phaser.Input.Keyboard.KeyCodes.S,
                    left: Phaser.Input.Keyboard.KeyCodes.A,
                    right: Phaser.Input.Keyboard.KeyCodes.D,
                    interact: Phaser.Input.Keyboard.KeyCodes.E,
                });
                this.input.keyboard.on("keydown", (event) => {
                    const pulses = {
                        ArrowUp: { x: 0, y: -1 },
                        KeyW: { x: 0, y: -1 },
                        ArrowDown: { x: 0, y: 1 },
                        KeyS: { x: 0, y: 1 },
                        ArrowLeft: { x: -1, y: 0 },
                        KeyA: { x: -1, y: 0 },
                        ArrowRight: { x: 1, y: 0 },
                        KeyD: { x: 1, y: 0 },
                    };
                    const direction = pulses[event.code];
                    if (direction) {
                        this.keyPulse = { ...direction, expiresAt: this.time.now + 95 };
                    }
                });
            }

            createFogOfWar() {
                map.sectors.forEach((sector) => {
                    const fog = this.add.graphics().setDepth(20);
                    fog.fillStyle(0x01040a, 0.91);
                    fog.fillRect(sector.rect.x, sector.rect.y, sector.rect.width, sector.rect.height);
                    fog.lineStyle(2, 0x334155, 0.24);
                    fog.strokeRect(sector.rect.x, sector.rect.y, sector.rect.width, sector.rect.height);
                    this.fogLayers.set(sector.id, fog);
                });
            }

            configureCamera() {
                const camera = this.cameras.main;
                const zoom = Math.max(0.96, Math.min(1.12, camera.height / 620));
                camera.setBounds(0, 0, map.width, map.height);
                camera.setZoom(zoom);
                camera.startFollow(this.player, true, 0.1, 0.1);
            }

            renderInfrastructureLights() {
                this.statusLayer?.destroy(true);
                this.statusLayer = this.add.container(0, 0).setDepth(6);
                const signals = monitoringState?.signals || [];
                const serviceSignal = signals.find((signal) => signal.id.includes("service")) || signals[0];
                const serviceColor = severityColors[serviceSignal?.severity] || severityColors.warning;
                const wallStatus = this.add.container(1100, 238);
                const wallLight = this.add.circle(0, 0, 7, serviceColor, 1);
                wallStatus.add(wallLight);
                wallStatus.add(this.add.text(-14, -7, serviceSignal?.status?.toUpperCase() || "UNKNOWN", {
                    color: colorHex(serviceColor),
                    fontFamily: "monospace",
                    fontSize: "10px",
                    fontStyle: "bold",
                }).setOrigin(1, 0));
                this.statusLayer.add(wallStatus);
                this.tweens.add({ targets: wallLight, alpha: 0.48, duration: 820, yoyo: true, repeat: -1 });
                signals.slice(0, 6).forEach((signal, index) => {
                    const color = severityColors[signal.severity] || severityColors.warning;
                    const row = Math.floor(index / 3);
                    const column = index % 3;
                    const light = this.add.circle(1320 + column * 130, 720 + row * 32, 5, color, 1);
                    this.statusLayer.add(light);
                    this.tweens.add({ targets: light, alpha: 0.5, duration: 900 + index * 95, yoyo: true, repeat: -1 });
                    this.statusLayer.add(this.add.text(1333 + column * 130, 713 + row * 32, signal.label.slice(0, 12), {
                        color: "#94a3b8",
                        fontFamily: "monospace",
                        fontSize: "9px",
                    }));
                });
            }

            sectorAt(x, y) {
                return map.sectors.find((sector) => (
                    x >= sector.rect.x
                    && x <= sector.rect.x + sector.rect.width
                    && y >= sector.rect.y
                    && y <= sector.rect.y + sector.rect.height
                )) || null;
            }

            revealSector(sector, instant = false) {
                if (!sector || this.discoveredSectors.has(sector.id)) return;
                this.discoveredSectors.add(sector.id);
                const fog = this.fogLayers.get(sector.id);
                if (fog) {
                    if (instant) {
                        fog.setAlpha(0.04);
                    } else {
                        this.tweens.add({ targets: fog, alpha: 0.04, duration: 520, ease: "Sine.easeOut" });
                    }
                }
                onSectorChange({
                    current: sector,
                    discovered: this.discoveredSectors.size,
                    total: map.sectors.length,
                    newlyDiscovered: true,
                });
            }

            updateExploration(instant = false) {
                const sector = this.sectorAt(this.player.x, this.player.y);
                this.revealSector(sector, instant);
                if (sector?.id !== this.currentSector?.id) {
                    this.currentSector = sector;
                    if (sector && this.discoveredSectors.has(sector.id)) {
                        onSectorChange({
                            current: sector,
                            discovered: this.discoveredSectors.size,
                            total: map.sectors.length,
                            newlyDiscovered: false,
                        });
                    }
                }
            }

            movementVector() {
                let x = 0;
                let y = 0;
                if (this.cursors.left.isDown || this.keys.left.isDown) x -= 1;
                if (this.cursors.right.isDown || this.keys.right.isDown) x += 1;
                if (this.cursors.up.isDown || this.keys.up.isDown) y -= 1;
                if (this.cursors.down.isDown || this.keys.down.isDown) y += 1;
                if (x === 0 && y === 0 && this.keyPulse && this.time.now < this.keyPulse.expiresAt) {
                    x = this.keyPulse.x;
                    y = this.keyPulse.y;
                }
                return new Phaser.Math.Vector2(x, y);
            }

            animatePlayer(moving) {
                if (!moving) {
                    this.walkTime = 0;
                    this.playerParts.leftLeg.y = 11;
                    this.playerParts.rightLeg.y = 11;
                    this.playerParts.leftArm.angle = 0;
                    this.playerParts.rightArm.angle = 0;
                    return;
                }
                this.walkTime += 0.16;
                const walk = Math.sin(this.walkTime) * 3;
                this.playerParts.leftLeg.y = 11 + walk;
                this.playerParts.rightLeg.y = 11 - walk;
                this.playerParts.leftArm.angle = walk * 1.3;
                this.playerParts.rightArm.angle = -walk * 1.3;
            }

            findNearestInteraction() {
                let nearest = null;
                let nearestDistance = Number.POSITIVE_INFINITY;
                this.interactions.forEach((interaction) => {
                    const distance = Phaser.Math.Distance.Between(this.player.x, this.player.y, interaction.position.x, interaction.position.y);
                    if (distance <= interaction.radius && distance < nearestDistance) {
                        nearest = interaction;
                        nearestDistance = distance;
                    }
                });
                return nearest;
            }

            updateInteractionMarkers(nearest) {
                this.interactions.forEach((interaction) => {
                    const distance = Phaser.Math.Distance.Between(
                        this.player.x,
                        this.player.y,
                        interaction.position.x,
                        interaction.position.y,
                    );
                    const visible = distance <= interaction.radius * 1.6;
                    interaction.marker.setAlpha(
                        visible ? (nearest?.id === interaction.id ? 0.92 : 0.34) : 0,
                    );
                });
            }

            update() {
                if (!this.player?.body) return;
                if (inputLocked) {
                    this.player.body.setVelocity(0, 0);
                    this.animatePlayer(false);
                    return;
                }

                const movement = this.movementVector();
                const moving = movement.lengthSq() > 0;
                const velocity = movement.normalize().scale(235);
                this.player.body.setVelocity(velocity.x, velocity.y);
                if (velocity.x !== 0) this.player.setScale(velocity.x < 0 ? -1 : 1, 1);
                this.animatePlayer(moving);
                this.playerLabel.setPosition(this.player.x, this.player.y - 50);
                this.updateExploration();

                const nearest = this.findNearestInteraction();
                this.updateInteractionMarkers(nearest);
                if (nearest?.id !== this.nearestInteraction?.id) {
                    this.nearestInteraction = nearest;
                    onInteractionChange(nearest);
                }
                if (nearest && Phaser.Input.Keyboard.JustDown(this.keys.interact)) {
                    onInteract(nearest);
                }

                if (this.time.now - this.lastPlayerReport >= 100) {
                    this.lastPlayerReport = this.time.now;
                    onPlayerState({
                        x: Math.round(this.player.x),
                        y: Math.round(this.player.y),
                        sector: this.currentSector?.id || null,
                        discovered: this.discoveredSectors.size,
                    });
                }
            }
        }

        const game = new Phaser.Game({
            type: Phaser.CANVAS,
            parent,
            backgroundColor: "#080d16",
            scale: { mode: Phaser.Scale.RESIZE, width: "100%", height: "100%" },
            physics: { default: "arcade", arcade: { debug: false } },
            render: { antialias: true, pixelArt: false },
            scene: ModernNocScene,
        });

        return {
            destroy() {
                onInteractionChange(null);
                game.destroy(true);
                scene = null;
            },
            setInputLocked(locked) {
                inputLocked = locked;
                if (!scene?.input?.keyboard) return;
                scene.input.keyboard.enabled = !locked;
                if (locked) {
                    scene.input.keyboard.resetKeys();
                    scene.player?.body?.setVelocity(0, 0);
                } else {
                    game.canvas.setAttribute("tabindex", "-1");
                    game.canvas.focus({ preventScroll: true });
                }
            },
            updateMonitoring(nextMonitoring) {
                monitoringState = nextMonitoring;
                scene?.renderInfrastructureLights();
            },
        };
    }

    window.ShellForgeDynamicGame = { createGame };
})();
