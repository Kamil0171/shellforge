(() => {
    const root =
        document.getElementById(
            "admin-duty-level",
        );

    if (!root) {
        return;
    }

    document.body.classList.add(
        "admin-duty-playing",
    );

    let phaserGame = null;
    let activeScene = null;
    let activeStation = null;

    const navbar =
        document.querySelector(".navbar");

    function syncNavbarHeight() {
        const navbarHeight =
            navbar?.offsetHeight || 56;

        document.documentElement.style.setProperty(
            "--shellforge-nav-height",
            `${navbarHeight}px`,
        );
    }

    syncNavbarHeight();

    const sessionId =
        root.dataset.sessionId;

    const terminalOverlay =
        document.getElementById(
            "terminal-overlay",
        );

    const monitoringOverlay =
        document.getElementById(
            "monitoring-overlay",
        );

    const editorOverlay =
        document.getElementById(
            "editor-overlay",
        );

    const hintOverlay =
        document.getElementById(
            "hint-overlay",
        );

    const solutionOverlay =
        document.getElementById(
            "solution-overlay",
        );

    const leaveOverlay =
        document.getElementById(
            "leave-overlay",
        );

    const missionOverlay =
        document.getElementById(
            "mission-overlay",
        );

    const interactionPrompt =
        document.getElementById(
            "interaction-prompt",
        );

    const interactionText =
        document.getElementById(
            "interaction-text",
        );

    const terminalOutput =
        document.getElementById(
            "terminal-output",
        );

    const terminalForm =
        document.getElementById(
            "terminal-form",
        );

    const terminalPrompt =
        document.getElementById(
            "terminal-prompt",
        );

    const terminalInput =
        document.getElementById(
            "terminal-input",
        );

    const serviceEditor =
        document.getElementById(
            "service-editor",
        );

    const editorMessage =
        document.getElementById(
            "editor-message",
        );

    const applicationStatus =
        document.getElementById(
            "application-status",
        );

    const publicStatus =
        document.getElementById(
            "public-status",
        );

    const liveScore =
        document.getElementById(
            "live-score",
        );

    const hintsUsed =
        document.getElementById(
            "hints-used",
        );

    function gameKeyboardEnabled(
        enabled,
    ) {
        if (
            activeScene &&
            activeScene.input &&
            activeScene.input.keyboard
        ) {
            activeScene.input.keyboard.enabled =
                enabled;
        }
    }

    function hasOpenOverlay() {
        return Boolean(
            document.querySelector(
                ".duty-overlay.is-open",
            ),
        );
    }

    function openOverlay(element) {
        element.classList.add(
            "is-open",
        );

        element.setAttribute(
            "aria-hidden",
            "false",
        );

        gameKeyboardEnabled(
            false,
        );

        if (
            element === terminalOverlay
        ) {
            window.setTimeout(
                () => {
                    terminalInput.focus();
                },
                50,
            );
        }

        if (
            element === editorOverlay
        ) {
            window.setTimeout(
                () => {
                    serviceEditor.focus();
                },
                50,
            );
        }
    }

    function closeOverlay(element) {
        element.classList.remove(
            "is-open",
        );

        element.setAttribute(
            "aria-hidden",
            "true",
        );

        window.setTimeout(
            () => {
                if (!hasOpenOverlay()) {
                    gameKeyboardEnabled(
                        true,
                    );
                }
            },
            0,
        );
    }

    function closeAllOverlays() {
        document
            .querySelectorAll(
                ".duty-overlay.is-open",
            )
            .forEach((overlay) => {
                overlay.classList.remove(
                    "is-open",
                );

                overlay.setAttribute(
                    "aria-hidden",
                    "true",
                );
            });

        gameKeyboardEnabled(
            true,
        );
    }

    document
        .querySelectorAll(
            "[data-close-overlay]",
        )
        .forEach((button) => {
            button.addEventListener(
                "click",
                () => {
                    const overlay =
                        button.closest(
                            ".duty-overlay",
                        );

                    if (overlay) {
                        closeOverlay(
                            overlay,
                        );
                    }
                },
            );
        });

    document.addEventListener(
        "keydown",
        (event) => {
            if (
                event.key === "Escape" &&
                hasOpenOverlay()
            ) {
                closeAllOverlays();
            }
        },
    );

    [
        terminalInput,
        serviceEditor,
    ].forEach((element) => {
        element.addEventListener(
            "keydown",
            (event) => {
                if (event.key === "Escape") {
                    event.preventDefault();
                    closeAllOverlays();
                }

                event.stopPropagation();
            },
        );

        element.addEventListener(
            "keyup",
            (event) => {
                event.stopPropagation();
            },
        );
    });

    function appendLine(
        text,
        cssClass = "",
    ) {
        const line =
            document.createElement(
                "div",
            );

        line.textContent = text;

        if (cssClass) {
            line.className =
                cssClass;
        }

        terminalOutput.appendChild(
            line,
        );

        terminalOutput.scrollTop =
            terminalOutput.scrollHeight;
    }

    function renderTerminalPrompt(
        currentDirectory,
    ) {
        if (!currentDirectory) {
            return;
        }

        const promptPath =
            currentDirectory ===
            "/home/operator"
                ? "~"
                : currentDirectory;

        terminalPrompt.textContent =
            `operator@ops-01:${promptPath}$`;
    }

    function renderWelcome() {
        terminalOutput.innerHTML = "";

        appendLine(
            "IronVale Systems — Operations Console",
            "terminal-success",
        );

        appendLine(
            "INC-001 / Production incident",
            "terminal-command",
        );

        appendLine("");

        appendLine(
            "Wpisz 'help', aby zobaczyć dostępne polecenia.",
        );

        appendLine("");
    }

    async function postJson(
        url,
        payload,
    ) {
        const response = await fetch(
            url,
            {
                method: "POST",
                headers: {
                    "Content-Type":
                        "application/json",
                },
                body: JSON.stringify(
                    payload,
                ),
            },
        );

        if (!response.ok) {
            throw new Error(
                "Operacja nie powiodła się.",
            );
        }

        return response.json();
    }

    async function sendCommand(
        command,
    ) {
        return postJson(
            "/admin-duty/api/command",
            {
                session_id: sessionId,
                command,
            },
        );
    }

    async function saveServiceFile(
        content,
    ) {
        return postJson(
            "/admin-duty/api/service-file",
            {
                session_id: sessionId,
                content,
            },
        );
    }

    async function requestHint() {
        return postJson(
            "/admin-duty/api/hint",
            {
                session_id: sessionId,
            },
        );
    }

    async function requestSolution() {
        return postJson(
            "/admin-duty/api/solution",
            {
                session_id: sessionId,
            },
        );
    }

    async function endSession() {
        return postJson(
            "/admin-duty/api/end",
            {
                session_id:
                    sessionId,
            },
        );
    }

    function objectiveCompleted(
        progress,
        key,
    ) {
        return progress.objectives
            .find(
                (objective) =>
                    objective.key === key,
            )
            ?.completed;
    }

    function renderProgress(
        progress,
    ) {
        if (!progress) {
            return;
        }

        liveScore.textContent =
            progress.score;

        hintsUsed.textContent =
            progress.hints_used;

        progress.objectives.forEach(
            (objective) => {
                const row =
                    document.querySelector(
                        `[data-objective="${objective.key}"]`,
                    );

                if (!row) {
                    return;
                }

                const check =
                    row.querySelector(
                        ".objective-check",
                    );

                row.classList.toggle(
                    "is-complete",
                    objective.completed,
                );

                check.textContent =
                    objective.completed
                        ? "✓"
                        : "○";
            },
        );

        if (
            objectiveCompleted(
                progress,
                "restore_service",
            )
        ) {
            applicationStatus.textContent =
                "● active";

            applicationStatus.className =
                "service-ok";
        }

        if (
            objectiveCompleted(
                progress,
                "verify_portal",
            )
        ) {
            publicStatus.textContent =
                "OPERATIONAL";

            publicStatus.className =
                "status-badge status-success";
        }

        if (
            progress.mission_complete &&
            !missionOverlay.classList.contains(
                "is-open",
            )
        ) {
            document.getElementById(
                "score-value",
            ).textContent =
                progress.score;

            openOverlay(
                missionOverlay,
            );
        }
    }

    function renderCommandResult(
        result,
    ) {
        renderTerminalPrompt(
            result.cwd,
        );

        if (
            result.type === "editor"
        ) {
            serviceEditor.value =
                result.service_file;

            editorMessage.textContent =
                "";

            editorMessage.className =
                "";

            renderProgress(
                result.progress,
            );

            openOverlay(
                editorOverlay,
            );

            return;
        }

        if (result.output) {
            const classes = {
                error: "terminal-error",
                warning:
                    "terminal-warning",
                success:
                    "terminal-success",
            };

            appendLine(
                result.output,
                classes[result.type] || "",
            );
        }

        renderProgress(
            result.progress,
        );
    }

    terminalForm.addEventListener(
        "submit",
        async (event) => {
            event.preventDefault();

            const command =
                terminalInput.value.trim();

            if (!command) {
                return;
            }

            terminalInput.value = "";

            if (
                command === "clear"
            ) {
                terminalOutput.innerHTML =
                    "";

                terminalInput.focus();

                return;
            }

            appendLine(
                `${terminalPrompt.textContent} ${command}`,
                "terminal-command",
            );

            try {
                const result =
                    await sendCommand(
                        command,
                    );

                renderCommandResult(
                    result,
                );
            } catch (error) {
                appendLine(
                    error.message,
                    "terminal-error",
                );
            }

            terminalInput.focus();
        },
    );

    document
        .getElementById(
            "save-service-file",
        )
        .addEventListener(
            "click",
            async () => {
                try {
                    const result =
                        await saveServiceFile(
                            serviceEditor.value,
                        );

                    editorMessage.textContent =
                        result.message;

                    editorMessage.className =
                        result.configuration_fixed
                            ? "editor-message-success"
                            : "editor-message-warning";

                    renderTerminalPrompt(
                        result.cwd,
                    );

                    renderProgress(
                        result.progress,
                    );
                } catch (error) {
                    editorMessage.textContent =
                        error.message;

                    editorMessage.className =
                        "editor-message-error";
                }
            },
        );

    document
        .getElementById(
            "hint-button",
        )
        .addEventListener(
            "click",
            () => {
                document.getElementById(
                    "hint-title",
                ).textContent =
                    "Potrzebujesz pomocy?";

                document.getElementById(
                    "hint-text",
                ).textContent =
                    "Kolejna podpowiedź obniży wynik.";

                document.getElementById(
                    "hint-cost",
                ).textContent =
                    "";

                document.getElementById(
                    "request-hint-button",
                ).hidden =
                    false;

                openOverlay(
                    hintOverlay,
                );
            },
        );

    document
        .getElementById(
            "request-hint-button",
        )
        .addEventListener(
            "click",
            async (event) => {
                const button =
                    event.currentTarget;

                try {
                    const result =
                        await requestHint();

                    renderProgress(
                        result.progress,
                    );

                    if (
                        !result.available
                    ) {
                        document.getElementById(
                            "hint-title",
                        ).textContent =
                            "Brak kolejnych podpowiedzi";

                        document.getElementById(
                            "hint-text",
                        ).textContent =
                            result.message;

                        button.hidden = true;

                        return;
                    }

                    document.getElementById(
                        "hint-title",
                    ).textContent =
                        `Podpowiedź ${result.number}`;

                    document.getElementById(
                        "hint-text",
                    ).textContent =
                        result.text;

                    document.getElementById(
                        "hint-cost",
                    ).textContent =
                        `Koszt: -${result.cost} pkt`;

                    button.textContent =
                        "Następna podpowiedź";
                } catch (error) {
                    document.getElementById(
                        "hint-text",
                    ).textContent =
                        error.message;
                }
            },
        );

    document
        .getElementById(
            "solution-button",
        )
        .addEventListener(
            "click",
            () => {
                openOverlay(
                    solutionOverlay,
                );
            },
        );

    document
        .getElementById(
            "confirm-solution-button",
        )
        .addEventListener(
            "click",
            async () => {
                try {
                    const result =
                        await requestSolution();

                    renderProgress(
                        result.progress,
                    );

                    const list =
                        document.getElementById(
                            "solution-steps",
                        );

                    list.innerHTML = "";

                    result.steps.forEach(
                        (step, index) => {
                            const item =
                                document.createElement(
                                    "article",
                                );

                            item.className =
                                "solution-step";

                            const number =
                                document.createElement(
                                    "span",
                                );

                            number.className =
                                "solution-step-number";

                            number.textContent =
                                `Krok ${index + 1}`;

                            const command =
                                document.createElement(
                                    "pre",
                                );

                            command.className =
                                "solution-command";

                            const code =
                                document.createElement(
                                    "code",
                                );

                            code.textContent =
                                step.command;

                            command.appendChild(
                                code,
                            );

                            const purpose =
                                document.createElement(
                                    "p",
                                );

                            purpose.textContent =
                                step.purpose;

                            item.append(
                                number,
                                command,
                                purpose,
                            );

                            if (step.instruction) {
                                const instruction =
                                    document.createElement(
                                        "p",
                                    );

                                instruction.className =
                                    "solution-instruction";

                                instruction.textContent =
                                    step.instruction;

                                item.appendChild(
                                    instruction,
                                );
                            }

                            list.appendChild(
                                item,
                            );
                        },
                    );

                    document.getElementById(
                        "solution-warning",
                    ).hidden =
                        true;

                    document.getElementById(
                        "solution-content",
                    ).hidden =
                        false;
                } catch (error) {
                    window.alert(
                        error.message,
                    );
                }
            },
        );

    function requestLeaveDuty() {
        openOverlay(
            leaveOverlay,
        );
    }

    document
        .getElementById(
            "leave-duty-button",
        )
        .addEventListener(
            "click",
            requestLeaveDuty,
        );

    document
        .getElementById(
            "continue-duty-button",
        )
        .addEventListener(
            "click",
            () => {
                closeOverlay(
                    leaveOverlay,
                );
            },
        );

    async function leaveDuty() {
        try {
            await endSession();
        } catch (error) {
            window.alert(
                error.message,
            );

            return;
        }

        if (phaserGame) {
            phaserGame.destroy(
                true,
            );

            phaserGame = null;
        }

        window.location.href =
            "/admin-duty/?view=scenarios";
    }

    document
        .getElementById(
            "confirm-leave-button",
        )
        .addEventListener(
            "click",
            leaveDuty,
        );

    document
        .getElementById(
            "finish-mission-button",
        )
        .addEventListener(
            "click",
            leaveDuty,
        );

    class DutyScene extends Phaser.Scene {
        constructor() {
            super("DutyScene");

            this.player = null;
            this.playerParts = null;
            this.cursors = null;
            this.keys = null;
            this.stations = [];
            this.obstacles = [];
            this.walkTime = 0;
        }

        create() {
            activeScene = this;

            this.cameras.main
                .setBackgroundColor(
                    "#0b1120",
                );

            this.drawOperationsCenter();

            this.createPlayer();
            this.createControls();
            this.createStations();
            this.createCollisions();
        }

        createControls() {
            this.cursors =
                this.input.keyboard
                    .createCursorKeys();

            this.keys =
                this.input.keyboard
                    .addKeys({
                        up:
                            Phaser.Input.Keyboard
                                .KeyCodes.W,
                        down:
                            Phaser.Input.Keyboard
                                .KeyCodes.S,
                        left:
                            Phaser.Input.Keyboard
                                .KeyCodes.A,
                        right:
                            Phaser.Input.Keyboard
                                .KeyCodes.D,
                        interact:
                            Phaser.Input.Keyboard
                                .KeyCodes.E,
                    });
        }

        createPlayer() {
            const shadow =
                this.add.ellipse(
                    0,
                    18,
                    26,
                    9,
                    0x000000,
                    0.28,
                );

            const leftLeg =
                this.add.rectangle(
                    -6,
                    10,
                    7,
                    15,
                    0x1e293b,
                );

            const rightLeg =
                this.add.rectangle(
                    6,
                    10,
                    7,
                    15,
                    0x1e293b,
                );

            const body =
                this.add.rectangle(
                    0,
                    -5,
                    24,
                    27,
                    0x2563eb,
                );

            body.setStrokeStyle(
                2,
                0x60a5fa,
            );

            const leftArm =
                this.add.rectangle(
                    -16,
                    -4,
                    6,
                    22,
                    0xd9a178,
                );

            const rightArm =
                this.add.rectangle(
                    16,
                    -4,
                    6,
                    22,
                    0xd9a178,
                );

            const head =
                this.add.circle(
                    0,
                    -27,
                    11,
                    0xe3b38d,
                );

            const hair =
                this.add.rectangle(
                    0,
                    -35,
                    19,
                    6,
                    0x1e293b,
                );

            const badge =
                this.add.rectangle(
                    6,
                    -6,
                    5,
                    7,
                    0xe2e8f0,
                );

            this.playerParts = {
                shadow,
                leftLeg,
                rightLeg,
                body,
                leftArm,
                rightArm,
                head,
                hair,
                badge,
            };

            this.player =
                this.add.container(
                    590,
                    430,
                    [
                        shadow,
                        leftLeg,
                        rightLeg,
                        body,
                        leftArm,
                        rightArm,
                        head,
                        hair,
                        badge,
                    ],
                );

            this.player.setSize(
                30,
                42,
            );

            this.physics.add.existing(
                this.player,
            );

            this.player.body.setSize(
                26,
                38,
            );

            this.player.body
                .setCollideWorldBounds(
                    true,
                );

            this.add
                .text(
                    this.player.x,
                    this.player.y - 48,
                    "Operator",
                    {
                        fontFamily: "Arial",
                        fontSize: "11px",
                        color: "#bae6fd",
                        backgroundColor:
                            "rgba(15,23,42,0.70)",
                        padding: {
                            x: 5,
                            y: 2,
                        },
                    },
                )
                .setOrigin(0.5)
                .setName(
                    "player-label",
                );
        }

        drawOperationsCenter() {
            this.drawFloor();
            this.drawWalls();

            this.add.text(
                58,
                45,
                "IRONVALE SYSTEMS",
                {
                    fontFamily: "Arial",
                    fontSize: "13px",
                    color: "#60a5fa",
                    fontStyle: "bold",
                },
            );

            this.add.text(
                58,
                66,
                "Network Operations Center",
                {
                    fontFamily: "Arial",
                    fontSize: "20px",
                    color: "#f8fafc",
                    fontStyle: "bold",
                },
            );

            this.drawOpsDesk();
            this.drawMonitoringStation();
            this.drawIncidentDesk();
            this.drawNetworkDesk();
            this.drawRunbookStation();
            this.drawServerRacks();
            this.drawPlant();
        }

        drawFloor() {
            this.add.rectangle(
                480,
                270,
                900,
                484,
                0x172033,
            );

            const graphics =
                this.add.graphics();

            graphics.lineStyle(
                1,
                0x263449,
                0.5,
            );

            for (
                let x = 45;
                x <= 915;
                x += 32
            ) {
                graphics.lineBetween(
                    x,
                    28,
                    x,
                    512,
                );
            }

            for (
                let y = 28;
                y <= 512;
                y += 32
            ) {
                graphics.lineBetween(
                    45,
                    y,
                    915,
                    y,
                );
            }
        }

        drawWalls() {
            this.add.rectangle(
                480,
                22,
                920,
                18,
                0x334155,
            );

            this.add.rectangle(
                28,
                270,
                18,
                514,
                0x334155,
            );

            this.add.rectangle(
                932,
                270,
                18,
                514,
                0x334155,
            );

            this.add.rectangle(
                242,
                518,
                430,
                18,
                0x334155,
            );

            this.add.rectangle(
                718,
                518,
                430,
                18,
                0x334155,
            );

            this.add.rectangle(
                480,
                518,
                90,
                8,
                0x64748b,
            );

            this.add
                .text(
                    480,
                    501,
                    "WYJŚCIE",
                    {
                        fontFamily: "Arial",
                        fontSize: "9px",
                        color: "#94a3b8",
                    },
                )
                .setOrigin(0.5);
        }

        drawDesk(
            x,
            y,
            width,
            label,
        ) {
            this.add.rectangle(
                x + 5,
                y + 6,
                width,
                58,
                0x020617,
                0.35,
            );

            this.add
                .rectangle(
                    x,
                    y,
                    width,
                    58,
                    0x475569,
                )
                .setStrokeStyle(
                    2,
                    0x64748b,
                );

            this.add
                .text(
                    x,
                    y - 48,
                    label,
                    {
                        fontFamily: "Arial",
                        fontSize: "11px",
                        color: "#cbd5e1",
                        fontStyle: "bold",
                    },
                )
                .setOrigin(0.5);

            this.addObstacle(
                x,
                y,
                width,
                62,
            );
        }

        drawMonitor(
            x,
            y,
            color,
            text,
        ) {
            this.add
                .rectangle(
                    x,
                    y,
                    46,
                    30,
                    0x0f172a,
                )
                .setStrokeStyle(
                    2,
                    0x64748b,
                );

            this.add.rectangle(
                x,
                y,
                38,
                22,
                color,
            );

            this.add.rectangle(
                x,
                y + 20,
                5,
                10,
                0x64748b,
            );

            this.add.rectangle(
                x,
                y + 26,
                22,
                4,
                0x64748b,
            );

            this.add
                .text(
                    x,
                    y,
                    text,
                    {
                        fontFamily: "Arial",
                        fontSize: "8px",
                        color: "#f8fafc",
                        fontStyle: "bold",
                    },
                )
                .setOrigin(0.5);
        }

        drawChair(x, y) {
            this.add
                .circle(
                    x,
                    y,
                    14,
                    0x1e293b,
                )
                .setStrokeStyle(
                    2,
                    0x475569,
                );

            this.add.rectangle(
                x,
                y + 15,
                18,
                8,
                0x334155,
            );
        }

        drawOpsDesk() {
            this.drawDesk(
                160,
                175,
                180,
                "OPS-01",
            );

            this.drawMonitor(
                132,
                163,
                0x0c4a6e,
                ">_",
            );

            this.drawMonitor(
                186,
                163,
                0x075985,
                "OPS",
            );

            this.drawChair(
                160,
                225,
            );
        }

        drawMonitoringStation() {
            this.drawDesk(
                480,
                175,
                230,
                "MONITORING",
            );

            this.drawMonitor(
                420,
                160,
                0x14532d,
                "OK",
            );

            this.drawMonitor(
                480,
                160,
                0x7f1d1d,
                "502",
            );

            this.drawMonitor(
                540,
                160,
                0x14532d,
                "OK",
            );

            this.drawChair(
                480,
                225,
            );
        }

        drawIncidentDesk() {
            this.drawDesk(
                790,
                175,
                175,
                "INCIDENT DESK",
            );

            this.drawMonitor(
                762,
                163,
                0x422006,
                "P1",
            );

            this.add.rectangle(
                816,
                166,
                38,
                27,
                0xf8fafc,
            );

            this.add
                .text(
                    816,
                    166,
                    "INC\n001",
                    {
                        fontFamily: "Arial",
                        fontSize: "7px",
                        color: "#b91c1c",
                        align: "center",
                    },
                )
                .setOrigin(0.5);

            this.drawChair(
                790,
                225,
            );
        }

        drawNetworkDesk() {
            this.drawDesk(
                170,
                360,
                190,
                "NETWORK",
            );

            this.drawMonitor(
                140,
                350,
                0x064e3b,
                "NET",
            );

            this.drawMonitor(
                196,
                350,
                0x164e63,
                "DNS",
            );

            this.drawChair(
                170,
                407,
            );
        }

        drawRunbookStation() {
            this.drawDesk(
                780,
                360,
                190,
                "RUNBOOKS",
            );

            this.add.rectangle(
                750,
                350,
                40,
                28,
                0xf8fafc,
            );

            this.add.rectangle(
                795,
                350,
                40,
                28,
                0xe2e8f0,
            );

            this.add
                .text(
                    750,
                    350,
                    "OPS",
                    {
                        fontFamily: "Arial",
                        fontSize: "8px",
                        color: "#334155",
                    },
                )
                .setOrigin(0.5);

            this.add
                .text(
                    795,
                    350,
                    "DOC",
                    {
                        fontFamily: "Arial",
                        fontSize: "8px",
                        color: "#334155",
                    },
                )
                .setOrigin(0.5);

            this.drawChair(
                780,
                407,
            );
        }

        drawServerRacks() {
            this.drawRack(
                355,
                350,
                "EDGE-01",
                [
                    0x22c55e,
                    0x22c55e,
                    0x22c55e,
                ],
            );

            this.drawRack(
                420,
                350,
                "APP-01",
                [
                    0xef4444,
                    0xf59e0b,
                    0x22c55e,
                ],
            );

            this.drawRack(
                485,
                350,
                "DB-01",
                [
                    0x22c55e,
                    0x22c55e,
                    0x22c55e,
                ],
            );
        }

        drawRack(
            x,
            y,
            label,
            lights,
        ) {
            this.add
                .rectangle(
                    x,
                    y,
                    52,
                    110,
                    0x0f172a,
                )
                .setStrokeStyle(
                    2,
                    0x64748b,
                );

            for (
                let index = 0;
                index < 5;
                index += 1
            ) {
                this.add
                    .rectangle(
                        x,
                        y - 34 +
                            index * 17,
                        38,
                        10,
                        0x1e293b,
                    )
                    .setStrokeStyle(
                        1,
                        0x475569,
                    );
            }

            lights.forEach(
                (color, index) => {
                    this.add.circle(
                        x + 13,
                        y - 34 +
                            index * 17,
                        2,
                        color,
                    );
                },
            );

            this.add
                .text(
                    x,
                    y - 69,
                    label,
                    {
                        fontFamily: "Arial",
                        fontSize: "8px",
                        color: "#94a3b8",
                        fontStyle: "bold",
                    },
                )
                .setOrigin(0.5);

            this.addObstacle(
                x,
                y,
                56,
                114,
            );
        }

        drawPlant() {
            this.add.circle(
                875,
                450,
                18,
                0x14532d,
            );

            this.add.rectangle(
                875,
                471,
                16,
                18,
                0x78350f,
            );
        }

        addObstacle(
            x,
            y,
            width,
            height,
        ) {
            const obstacle =
                this.add.rectangle(
                    x,
                    y,
                    width,
                    height,
                    0x000000,
                    0,
                );

            this.physics.add.existing(
                obstacle,
                true,
            );

            this.obstacles.push(
                obstacle,
            );
        }

        createCollisions() {
            this.obstacles.forEach(
                (obstacle) => {
                    this.physics.add.collider(
                        this.player,
                        obstacle,
                    );
                },
            );
        }

        createStations() {
            this.stations = [
                {
                    x: 160,
                    y: 236,
                    radius: 72,
                    type: "terminal",
                    label:
                        "Otwórz terminal OPS-01",
                },
                {
                    x: 480,
                    y: 236,
                    radius: 75,
                    type: "monitoring",
                    label:
                        "Otwórz monitoring",
                },
                {
                    x: 480,
                    y: 492,
                    radius: 60,
                    type: "exit",
                    label:
                        "Opuść centrum operacyjne",
                },
            ];
        }

        animatePlayer(
            moving,
        ) {
            if (!moving) {
                this.walkTime = 0;

                this.playerParts
                    .leftLeg.y = 10;

                this.playerParts
                    .rightLeg.y = 10;

                this.playerParts
                    .leftArm.angle = 0;

                this.playerParts
                    .rightArm.angle = 0;

                return;
            }

            this.walkTime += 0.15;

            const walk =
                Math.sin(
                    this.walkTime,
                ) * 3;

            this.playerParts.leftLeg.y =
                10 + walk;

            this.playerParts.rightLeg.y =
                10 - walk;

            this.playerParts
                .leftArm.angle =
                    walk * 1.4;

            this.playerParts
                .rightArm.angle =
                    -walk * 1.4;
        }

        updateLabel() {
            const label =
                this.children.getByName(
                    "player-label",
                );

            if (!label) {
                return;
            }

            label.setPosition(
                this.player.x,
                this.player.y - 48,
            );
        }

        updateStations() {
            activeStation = null;

            for (
                const station
                of this.stations
            ) {
                const distance =
                    Phaser.Math.Distance
                        .Between(
                            this.player.x,
                            this.player.y,
                            station.x,
                            station.y,
                        );

                if (
                    distance <=
                    station.radius
                ) {
                    activeStation =
                        station;

                    break;
                }
            }

            if (activeStation) {
                interactionPrompt.hidden =
                    false;

                interactionText.textContent =
                    activeStation.label;
            } else {
                interactionPrompt.hidden =
                    true;
            }
        }

        handleInteraction() {
            if (
                !activeStation ||
                !Phaser.Input.Keyboard
                    .JustDown(
                        this.keys.interact,
                    )
            ) {
                return;
            }

            if (
                activeStation.type ===
                "terminal"
            ) {
                openOverlay(
                    terminalOverlay,
                );
            }

            if (
                activeStation.type ===
                "monitoring"
            ) {
                openOverlay(
                    monitoringOverlay,
                );
            }

            if (
                activeStation.type ===
                "exit"
            ) {
                requestLeaveDuty();
            }
        }

        update() {
            if (
                !this.input.keyboard.enabled
            ) {
                this.player.body
                    .setVelocity(
                        0,
                        0,
                    );

                return;
            }

            const speed = 165;

            this.player.body
                .setVelocity(
                    0,
                    0,
                );

            if (
                this.cursors.left.isDown ||
                this.keys.left.isDown
            ) {
                this.player.body
                    .setVelocityX(
                        -speed,
                    );
            } else if (
                this.cursors.right.isDown ||
                this.keys.right.isDown
            ) {
                this.player.body
                    .setVelocityX(
                        speed,
                    );
            }

            if (
                this.cursors.up.isDown ||
                this.keys.up.isDown
            ) {
                this.player.body
                    .setVelocityY(
                        -speed,
                    );
            } else if (
                this.cursors.down.isDown ||
                this.keys.down.isDown
            ) {
                this.player.body
                    .setVelocityY(
                        speed,
                    );
            }

            const velocity =
                this.player.body.velocity;

            if (
                velocity.x !== 0 ||
                velocity.y !== 0
            ) {
                velocity
                    .normalize()
                    .scale(speed);
            }

            this.animatePlayer(
                velocity.length() > 0,
            );

            this.updateLabel();
            this.updateStations();
            this.handleInteraction();
        }
    }

    function createGame() {
        phaserGame =
            new Phaser.Game({
                type: Phaser.AUTO,

                parent:
                    "admin-duty-game",

                width: 960,
                height: 540,

                pixelArt: true,
                roundPixels: true,

                backgroundColor:
                    "#0b1120",

                scale: {
                    mode:
                        Phaser.Scale.FIT,

                    autoCenter:
                        Phaser.Scale
                            .CENTER_BOTH,
                },

                physics: {
                    default: "arcade",

                    arcade: {
                        gravity: {
                            x: 0,
                            y: 0,
                        },

                        debug: false,
                    },
                },

                scene: DutyScene,
            });
    }

    window.addEventListener(
        "resize",
        () => {
            syncNavbarHeight();

            if (phaserGame) {
                phaserGame.scale.refresh();
            }
        },
    );

    renderWelcome();
    createGame();
})();
