(() => {
    const root = document.getElementById("dynamic-session-workspace");
    if (!root) return;

    const sessionId = root.dataset.sessionId;
    const loadingPanel = document.getElementById("workspace-loading");
    const errorPanel = document.getElementById("workspace-error");
    const workspace = document.getElementById("workspace-content");
    const desktopGate = document.getElementById("desktop-gate");
    const endSummary = document.getElementById("end-summary");
    const completionOverlay = document.getElementById("completion-overlay");
    const completionBanner = document.getElementById("completion-banner");
    const exitOverlay = document.getElementById("exit-confirmation");
    const hintButton = document.getElementById("request-hint-button");
    const hintError = document.getElementById("hint-error");
    const interactionPrompt = document.getElementById("interaction-prompt");
    const interactionPromptLabel = document.getElementById("interaction-prompt-label");
    const mobilePattern = /Android|iPad|iPhone|Mobile|Tablet|Silk/i;
    const pointerQuery = window.matchMedia("(pointer: coarse)");
    const commandHistoryMessage = "Połączenie z bezpiecznym środowiskiem zostało ustanowione.\nZnajdź stanowisko OPS-01 i naciśnij E.";
    let sessionData = null;
    let currentProgress = null;
    let currentInfrastructure = { nodes: [], links: [] };
    let currentMonitoring = { title: "Monitoring", signals: [] };
    let gameController = null;
    let activeOverlay = null;
    let hintPending = false;
    let sessionEnding = false;
    let terminalAnnounced = false;
    let currentInteraction = null;
    let announcementTimer = null;

    const statusLabels = { active: "Aktywny", completed: "Ukończony", ended: "Zakończony" };
    const difficultyLabels = { easy: "Łatwy", medium: "Średni", hard: "Trudny" };
    const resourceTypeLabels = { host: "Host", service: "Usługa", file: "Plik", process: "Proces", listener: "Port", endpoint: "Endpoint", domain: "Domena" };

    class ApiError extends Error {
        constructor(status, detail) {
            super(detail || "Żądanie nie powiodło się.");
            this.status = status;
        }
    }

    async function requestJson(url, options = {}) {
        const response = await fetch(url, options);
        let data = null;
        try {
            data = await response.json();
        } catch {
            data = null;
        }
        if (!response.ok) {
            throw new ApiError(response.status, typeof data?.detail === "string" ? data.detail : null);
        }
        return data;
    }

    function isDesktopAllowed() {
        const tabletLike = pointerQuery.matches && navigator.maxTouchPoints > 0;
        const ipadDesktopUa = /Macintosh/i.test(navigator.userAgent) && navigator.maxTouchPoints > 1;
        return window.innerWidth >= 1024 && !tabletLike && !ipadDesktopUa && !mobilePattern.test(navigator.userAgent);
    }

    function destroyGame() {
        gameController?.destroy();
        gameController = null;
    }

    function createGameIfReady() {
        if (!sessionData || gameController || !isDesktopAllowed() || currentProgress?.status === "ended") return;
        try {
            gameController = window.ShellForgeDynamicGame.createGame({
                parent: "game-canvas",
                map: sessionData.game_map,
                monitoring: currentMonitoring,
                onInteractionChange: renderInteractionPrompt,
                onInteract: handleGameInteraction,
                onSectorChange: renderSectorState,
                onPlayerState: reportPlayerState,
            });
            gameController.setInputLocked(Boolean(activeOverlay));
        } catch (error) {
            showLoadError(error);
        }
    }

    function applyDeviceGate() {
        const allowed = isDesktopAllowed();
        desktopGate.hidden = allowed;
        workspace.inert = !allowed;
        workspace.setAttribute("aria-hidden", String(!allowed));
        document.body.classList.toggle("dynamic-device-blocked", !allowed);
        if (!allowed) {
            destroyGame();
            interactionPrompt.hidden = true;
            return;
        }
        window.scrollTo({ top: 0, left: 0, behavior: "instant" });
        createGameIfReady();
        if (sessionData) void refreshSessionProjection();
    }

    function renderInteractionPrompt(interaction) {
        currentInteraction = interaction;
        interactionPrompt.hidden = !interaction;
        if (interaction) interactionPromptLabel.textContent = interaction.label;
    }

    function reportPlayerState(state) {
        root.dataset.playerX = state.x;
        root.dataset.playerY = state.y;
        root.dataset.playerSector = state.sector || "unknown";
        root.dataset.discoveredSectors = state.discovered;
    }

    function renderSectorState(state) {
        document.getElementById("game-sector-label").textContent = state.current.label.toUpperCase();
        if (!state.newlyDiscovered || state.discovered === 1) return;
        const announcement = document.getElementById("game-announcement");
        announcement.textContent = `Odkryto sektor: ${state.current.label}`;
        announcement.classList.add("is-visible");
        window.clearTimeout(announcementTimer);
        announcementTimer = window.setTimeout(() => announcement.classList.remove("is-visible"), 2200);
    }

    function lockGame(locked) {
        gameController?.setInputLocked(locked);
    }

    function openOverlay(element, focusTarget = null) {
        if (activeOverlay && activeOverlay !== element) activeOverlay.hidden = true;
        activeOverlay = element;
        element.hidden = false;
        document.body.classList.add("dynamic-modal-open");
        lockGame(true);
        focusTarget?.focus({ preventScroll: true });
    }

    function closeOverlay(element) {
        if (element.hidden) return;
        element.hidden = true;
        if (activeOverlay === element) activeOverlay = null;
        document.body.classList.remove("dynamic-modal-open");
        lockGame(false);
    }

    const terminal = window.ShellForgeDynamicTerminal.createTerminalController({
        async onSubmit(command) {
            try {
                const result = await requestJson("/admin-duty/dynamic/api/command", {
                    method: "POST",
                    headers: { "Content-Type": "application/json" },
                    body: JSON.stringify({ session_id: sessionId, command }),
                });
                renderProgress(result.progress, { showSuccess: false });
                await refreshSessionProjection();
                if (result.progress.mission_complete) {
                    window.setTimeout(() => {
                        terminal.close();
                        showCompletion(result.progress);
                    }, 0);
                }
                return result;
            } catch (error) {
                if (error instanceof ApiError && error.status === 404) showLoadError(error);
                if (error instanceof ApiError && error.status === 409) void loadSession(false);
                throw new Error(commandErrorMessage(error));
            }
        },
        onOpenChange(open) {
            if (open) {
                activeOverlay = document.getElementById("terminal-overlay");
                document.body.classList.add("dynamic-modal-open");
                lockGame(true);
            } else {
                activeOverlay = null;
                document.body.classList.remove("dynamic-modal-open");
                lockGame(false);
            }
        },
    });

    function handleGameInteraction(interaction) {
        if (interaction.type === "terminal") {
            terminal.open();
            return;
        }
        if (interaction.type === "monitoring") {
            renderMonitoring();
            openOverlay(document.getElementById("monitoring-overlay"), document.querySelector("#monitoring-overlay .overlay-close"));
            return;
        }
        if (interaction.type === "support") {
            renderSupportCenter();
            openOverlay(document.getElementById("support-overlay"), document.querySelector("#support-overlay .overlay-close"));
            return;
        }
        renderRackDetails(interaction.resource_id);
        openOverlay(document.getElementById("rack-overlay"), document.querySelector("#rack-overlay .overlay-close"));
    }

    function renderIncident(incident) {
        document.getElementById("workspace-title").textContent = incident.title;
        document.getElementById("incident-title").textContent = incident.title;
        document.getElementById("incident-briefing").textContent = incident.briefing;
        document.getElementById("incident-organization").textContent = incident.organization;
        document.getElementById("incident-environment").textContent = incident.environment_label;
        document.getElementById("incident-main-objective").textContent = incident.main_objective;
        document.getElementById("incident-difficulty").textContent = difficultyLabels[incident.difficulty] || incident.difficulty;
    }

    function renderObjectives(progress) {
        const list = document.getElementById("objectives-list");
        list.replaceChildren();
        progress.objectives.forEach((objective) => {
            const item = document.createElement("div");
            item.className = "objective-item";
            item.classList.toggle("is-complete", objective.completed);
            const marker = document.createElement("span");
            marker.className = "objective-marker";
            marker.textContent = objective.completed ? "✓" : "○";
            const content = document.createElement("div");
            const label = document.createElement("strong");
            label.textContent = objective.label;
            const state = document.createElement("span");
            state.textContent = objective.completed ? "Ukończony" : "Do wykonania";
            content.append(label, state);
            item.append(marker, content);
            list.appendChild(item);
        });
        document.getElementById("objectives-counter").textContent = `${progress.completed_objectives} / ${progress.total_objectives}`;
    }

    function renderHints(revealedHints, hintLimit, progress) {
        const list = document.getElementById("revealed-hints");
        list.replaceChildren();
        revealedHints.forEach((hint) => {
            const item = document.createElement("li");
            const text = document.createElement("p");
            const cost = document.createElement("span");
            text.textContent = hint.text;
            cost.textContent = `Koszt: ${hint.cost} pkt`;
            item.append(text, cost);
            list.appendChild(item);
        });
        document.getElementById("hints-counter").textContent = `${progress.hints_used} / ${hintLimit}`;
        hintButton.disabled = hintPending || progress.status !== "active" || progress.hints_used >= hintLimit;
        hintButton.textContent = progress.hints_used >= hintLimit ? "Wykorzystano limit" : "Pobierz podpowiedź";
    }

    function renderMonitoring() {
        const container = document.getElementById("monitoring-signals");
        container.replaceChildren();
        currentMonitoring.signals.forEach((signal) => {
            const card = document.createElement("article");
            card.className = `monitoring-signal is-${signal.severity}`;
            const heading = document.createElement("div");
            const dot = document.createElement("i");
            const name = document.createElement("strong");
            name.textContent = signal.label;
            heading.append(dot, name);
            const status = document.createElement("span");
            status.textContent = signal.status;
            card.append(heading, status);
            container.appendChild(card);
        });
        const critical = currentMonitoring.signals.filter((signal) => signal.severity === "critical").length;
        const health = document.getElementById("infrastructure-health");
        health.textContent = critical ? `${critical} ALERT` : "NOMINAL";
        health.classList.toggle("is-alert", critical > 0);
    }

    function renderSupportCenter() {
        const runbooks = document.getElementById("support-runbooks");
        const guidance = document.getElementById("operational-guidance");
        runbooks.replaceChildren();
        guidance.replaceChildren();
        sessionData.support_center.runbooks.forEach((runbook) => {
            const details = document.createElement("details");
            const summary = document.createElement("summary");
            const title = document.createElement("strong");
            const description = document.createElement("span");
            const steps = document.createElement("ol");
            title.textContent = runbook.title;
            description.textContent = runbook.summary;
            summary.append(title, description);
            runbook.steps.forEach((step) => {
                const item = document.createElement("li");
                item.textContent = step;
                steps.appendChild(item);
            });
            details.append(summary, steps);
            runbooks.appendChild(details);
        });
        sessionData.support_center.operational_guidance.forEach((tip) => {
            const item = document.createElement("li");
            item.textContent = tip;
            guidance.appendChild(item);
        });
    }

    function renderRackDetails(resourceId) {
        const container = document.getElementById("rack-details");
        container.replaceChildren();
        const resource = currentInfrastructure.nodes.find((node) => node.id === resourceId) || currentInfrastructure.nodes.find((node) => node.type === "host");
        const linked = currentInfrastructure.nodes.filter((node) => node.parent_id === resource?.id);
        const heading = document.createElement("div");
        heading.className = "rack-resource-heading";
        const name = document.createElement("strong");
        name.textContent = resource?.label || "Zasób infrastruktury";
        const status = document.createElement("span");
        status.textContent = resource?.status || "unknown";
        heading.append(name, status);
        container.appendChild(heading);
        const details = document.createElement("dl");
        [["Identyfikator", resource?.id || "—"], ["Typ", resourceTypeLabels[resource?.type] || resource?.type || "—"], ["Rola", resource?.role || "—"], ["Usługi w szafie", linked.length ? linked.map((node) => `${node.label} · ${node.status}`).join(", ") : "brak publicznych powiązań"]].forEach(([term, value]) => {
            const row = document.createElement("div");
            const dt = document.createElement("dt");
            const dd = document.createElement("dd");
            dt.textContent = term;
            dd.textContent = value;
            row.append(dt, dd);
            details.appendChild(row);
        });
        container.appendChild(details);
    }

    function renderProgress(progress, { showSuccess = true } = {}) {
        currentProgress = progress;
        renderObjectives(progress);
        const label = statusLabels[progress.status] || progress.status;
        const badge = document.getElementById("session-status-badge");
        badge.textContent = label;
        badge.dataset.status = progress.status;
        document.getElementById("header-score").textContent = progress.score;
        document.getElementById("progress-status").textContent = label;
        document.getElementById("commands-used").textContent = progress.commands_used;
        document.getElementById("hints-used").textContent = progress.hints_used;
        document.getElementById("session-revision").textContent = progress.revision;
        document.getElementById("exit-session-button").hidden = progress.status === "ended";
        terminal.setAvailable(progress.status === "active", progress.status === "active" ? "Terminal gotowy" : "Terminal zablokowany");
        completionBanner.hidden = !progress.mission_complete || progress.status === "ended";
        if (progress.status === "ended") renderSummary(progress);
        if (showSuccess && progress.mission_complete && progress.status === "completed") showCompletion(progress);
    }

    function showCompletion(progress) {
        document.getElementById("completion-score").textContent = progress.score;
        document.getElementById("completion-commands").textContent = progress.commands_used;
        document.getElementById("completion-objectives").textContent = `${progress.completed_objectives} / ${progress.total_objectives}`;
        openOverlay(completionOverlay, document.getElementById("end-session-button"));
    }

    function renderSummary(progress) {
        destroyGame();
        if (activeOverlay) activeOverlay.hidden = true;
        activeOverlay = null;
        workspace.hidden = true;
        loadingPanel.hidden = true;
        errorPanel.hidden = true;
        endSummary.hidden = false;
        document.body.classList.remove("dynamic-modal-open");
        document.getElementById("summary-difficulty").textContent = difficultyLabels[sessionData?.incident.difficulty] || "—";
        document.getElementById("summary-score").textContent = progress.score;
        document.getElementById("summary-commands").textContent = progress.commands_used;
        document.getElementById("summary-objectives").textContent = `${progress.completed_objectives} / ${progress.total_objectives}`;
    }

    function showWorkspace(data) {
        sessionData = data;
        currentInfrastructure = data.infrastructure;
        currentMonitoring = data.monitoring;
        loadingPanel.hidden = true;
        errorPanel.hidden = true;
        endSummary.hidden = true;
        workspace.hidden = false;
        renderIncident(data.incident);
        renderHints(data.revealed_hints, data.hint_limit, data.progress);
        renderSupportCenter();
        renderMonitoring();
        renderProgress(data.progress);
        terminal.setPrompt(data.shell.prompt);
        document.getElementById("game-map-name").textContent = data.game_map.name;
        document.getElementById("game-sector-label").textContent = "WEJŚCIE NOC";
        if (!terminalAnnounced) {
            terminal.append("system", commandHistoryMessage);
            terminalAnnounced = true;
        }
        createGameIfReady();
    }

    function showLoadError(error) {
        destroyGame();
        loadingPanel.hidden = true;
        workspace.hidden = true;
        endSummary.hidden = true;
        errorPanel.hidden = false;
        const expired = error instanceof ApiError && error.status === 404;
        document.getElementById("workspace-error-title").textContent = expired ? "Ta sesja wygasła lub nie istnieje" : "Nie udało się pobrać sesji";
        document.getElementById("workspace-error-message").textContent = expired ? "Rozpocznij nowy incydent, aby wrócić do laboratorium." : "Sprawdź połączenie i spróbuj ponownie. Twój postęp nie został zmieniony.";
        document.getElementById("retry-session-button").hidden = expired;
    }

    async function loadSession(showLoading = true) {
        if (showLoading) {
            loadingPanel.hidden = false;
            errorPanel.hidden = true;
        }
        try {
            const data = await requestJson(`/admin-duty/dynamic/api/sessions/${sessionId}`);
            showWorkspace(data);
        } catch (error) {
            showLoadError(error);
        }
    }

    async function refreshSessionProjection() {
        if (!sessionData) return;
        const data = await requestJson(`/admin-duty/dynamic/api/sessions/${sessionId}`);
        sessionData = { ...sessionData, ...data };
        currentInfrastructure = data.infrastructure;
        currentMonitoring = data.monitoring;
        renderHints(data.revealed_hints, data.hint_limit, data.progress);
        renderMonitoring();
        renderProgress(data.progress, { showSuccess: false });
        terminal.setPrompt(data.shell.prompt);
        gameController?.updateMonitoring(currentMonitoring);
    }

    async function requestHint() {
        if (hintPending || currentProgress?.status !== "active") return;
        hintPending = true;
        hintButton.disabled = true;
        hintButton.textContent = "Pobieranie...";
        hintError.hidden = true;
        try {
            const result = await requestJson("/admin-duty/dynamic/api/hint", {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify({ session_id: sessionId }),
            });
            hintPending = false;
            renderProgress(result.progress, { showSuccess: false });
            renderHints(result.revealed_hints, result.hint_limit, result.progress);
        } catch (error) {
            hintPending = false;
            hintError.textContent = error instanceof ApiError ? error.message : "Nie udało się pobrać podpowiedzi.";
            hintError.hidden = false;
            if (error instanceof ApiError && [404, 409].includes(error.status)) {
                await loadSession(false);
            } else {
                hintButton.disabled = false;
                hintButton.textContent = "Pobierz podpowiedź";
            }
        }
    }

    function commandErrorMessage(error) {
        if (error instanceof ApiError && error.status === 400) return error.message;
        if (error instanceof ApiError && error.status === 422) return "Polecenie ma nieprawidłowy format.";
        if (error instanceof ApiError && error.status === 409) return error.message;
        return "Nie udało się wykonać polecenia. Możesz spróbować ponownie.";
    }

    function showExitConfirmation() {
        if (!currentProgress || currentProgress.status === "ended") return;
        const completed = currentProgress.status === "completed";
        document.getElementById("exit-confirmation-title").textContent = completed ? "Zakończyć ukończony incydent?" : "Opuścić aktywny incydent?";
        document.getElementById("exit-confirmation-message").textContent = completed ? "Sesja zostanie zakończona, a wynik pozostanie dostępny do czasu wygaśnięcia." : "Sesja zostanie oznaczona jako zakończona. Zmiana viewportu nigdy nie wykonuje tej operacji.";
        document.getElementById("confirm-exit-button").textContent = completed ? "Zakończ incydent" : "Opuść incydent";
        document.getElementById("exit-error").hidden = true;
        openOverlay(exitOverlay, document.getElementById("confirm-exit-button"));
    }

    async function endSession({ redirectAfterEnd = false } = {}) {
        if (sessionEnding) return;
        sessionEnding = true;
        ["end-session-button", "banner-end-button", "confirm-exit-button"].forEach((id) => {
            document.getElementById(id).disabled = true;
        });
        try {
            const result = await requestJson("/admin-duty/dynamic/api/end", {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify({ session_id: sessionId }),
            });
            if (redirectAfterEnd) {
                window.location.replace("/admin-duty/dynamic/");
                return;
            }
            renderProgress(result.progress);
        } catch (error) {
            sessionEnding = false;
            const message = error instanceof ApiError ? error.message : "Nie udało się zakończyć sesji.";
            document.getElementById("exit-error").textContent = message;
            document.getElementById("exit-error").hidden = exitOverlay.hidden;
            document.getElementById("completion-error").textContent = message;
            document.getElementById("completion-error").hidden = completionOverlay.hidden;
            ["end-session-button", "banner-end-button", "confirm-exit-button"].forEach((id) => {
                document.getElementById(id).disabled = false;
            });
        }
    }

    document.getElementById("retry-session-button").addEventListener("click", () => void loadSession());
    hintButton.addEventListener("click", () => void requestHint());
    document.getElementById("exit-session-button").addEventListener("click", showExitConfirmation);
    document.getElementById("cancel-exit-button").addEventListener("click", () => closeOverlay(exitOverlay));
    document.getElementById("confirm-exit-button").addEventListener("click", () => void endSession({ redirectAfterEnd: currentProgress?.status === "active" }));
    document.getElementById("continue-session-button").addEventListener("click", () => closeOverlay(completionOverlay));
    document.getElementById("end-session-button").addEventListener("click", () => void endSession());
    document.getElementById("banner-end-button").addEventListener("click", () => showCompletion(currentProgress));
    function setMissionDrawer(open) {
        const panel = document.getElementById("mission-drawer");
        const toggle = document.getElementById("toggle-briefing-button");
        panel.classList.toggle("is-collapsed", !open);
        panel.setAttribute("aria-hidden", String(!open));
        toggle.setAttribute("aria-expanded", String(open));
        lockGame(open);
        if (open) document.getElementById("close-briefing-button").focus({ preventScroll: true });
    }

    document.getElementById("toggle-briefing-button").addEventListener("click", () => setMissionDrawer(true));
    document.getElementById("close-briefing-button").addEventListener("click", () => setMissionDrawer(false));
    document.querySelectorAll("[data-close-overlay]").forEach((button) => {
        button.addEventListener("click", () => closeOverlay(document.getElementById(button.dataset.closeOverlay)));
    });

    document.addEventListener("keydown", (event) => {
        const missionDrawer = document.getElementById("mission-drawer");
        if (event.key.toLowerCase() === "e" && currentInteraction && !activeOverlay && missionDrawer.classList.contains("is-collapsed")) {
            event.preventDefault();
            handleGameInteraction(currentInteraction);
            return;
        }
        if (event.key === "Escape" && !missionDrawer.classList.contains("is-collapsed") && !activeOverlay) {
            event.preventDefault();
            setMissionDrawer(false);
            return;
        }
        if (event.key !== "Escape" || terminal.isOpen() || !activeOverlay) return;
        event.preventDefault();
        if (activeOverlay === completionOverlay) return;
        closeOverlay(activeOverlay);
    });

    let resizeFrame = null;
    window.addEventListener("resize", () => {
        window.cancelAnimationFrame(resizeFrame);
        resizeFrame = window.requestAnimationFrame(applyDeviceGate);
    });
    pointerQuery.addEventListener?.("change", applyDeviceGate);

    applyDeviceGate();
    void loadSession();
})();
