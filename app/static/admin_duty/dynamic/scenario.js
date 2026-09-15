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
        document.getElementById("game-sector-label").textContent = (state.current?.label || "Korytarz").toUpperCase();
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
        async onSaveFile(path, content) {
            const result = await requestJson("/admin-duty/dynamic/api/file", {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify({ session_id: sessionId, path, content }),
            });
            renderProgress(result.progress, { showSuccess: false });
            await refreshSessionProjection();
            return result;
        },
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
        const health = document.getElementById("infrastructure-health");
        const labels = { critical: "ALERT", improving: "POPRAWA", nominal: "NOMINAL" };
        health.textContent = labels[currentMonitoring.overall_status] || "ALERT";
        health.classList.toggle("is-alert", currentMonitoring.overall_status === "critical");
        health.classList.toggle("is-improving", currentMonitoring.overall_status === "improving");
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
        const visibleServiceIds = new Set([
            ...(resource?.type === "service" ? [resource.id] : []),
            ...linked.map((node) => node.id),
        ]);
        const dependencies = currentInfrastructure.links.filter(
            (link) => link.label === "zależy od" && (visibleServiceIds.has(link.source) || visibleServiceIds.has(link.target)),
        );
        const heading = document.createElement("div");
        heading.className = "rack-resource-heading";
        const name = document.createElement("strong");
        name.textContent = resource?.label || "Zasób infrastruktury";
        const status = document.createElement("span");
        status.textContent = resource?.status || "unknown";
        heading.append(name, status);
        container.appendChild(heading);
        const details = document.createElement("dl");
        [["Identyfikator", resource?.id || "—"], ["Typ", resourceTypeLabels[resource?.type] || resource?.type || "—"], ["Rola", resource?.role || "—"], ["Usługi w szafie", linked.length ? linked.map((node) => `${node.label} · ${node.health || node.status}`).join(", ") : "brak publicznych powiązań"], ["Zależności usług", dependencies.length ? dependencies.map((link) => `${link.source} → ${link.target} · ${link.protocol.toUpperCase()}/${link.port}`).join(", ") : "brak publicznych zależności"]].forEach(([term, value]) => {
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

    function renderReportList(containerId, values, formatter = (value) => value) {
        const container = document.getElementById(containerId);
        container.replaceChildren();
        values.forEach((value) => {
            const item = document.createElement("li");
            item.textContent = formatter(value);
            container.appendChild(item);
        });
    }

    function formatResolutionTime(seconds) {
        if (!Number.isFinite(seconds)) return "—";
        if (seconds < 60) return `${seconds} s`;
        const minutes = Math.floor(seconds / 60);
        const remainder = seconds % 60;
        return remainder ? `${minutes} min ${remainder} s` : `${minutes} min`;
    }

    function renderReportMetrics(report) {
        const efficiency = report.efficiency || {};
        const ratio = Number.isFinite(efficiency.diagnostic_efficiency)
            ? `${Math.round(efficiency.diagnostic_efficiency * 100)}%`
            : "Brak komend";
        const metrics = [
            ["Wszystkie komendy", efficiency.commands_total ?? 0],
            ["Diagnostyczne", efficiency.diagnostic_commands ?? 0],
            ["Naprawcze", efficiency.repair_commands ?? 0],
            ["Weryfikacyjne", efficiency.verification_commands ?? 0],
            ["Efektywność", ratio],
            ["Podpowiedzi", `${report.hints_used ?? 0} · koszt ${report.hint_cost ?? 0} pkt`],
            ["Czas rozwiązania", formatResolutionTime(efficiency.time_to_resolve_seconds)],
            ["Niezwiązane", efficiency.unnecessary_commands ?? 0],
        ];
        const container = document.getElementById("post-incident-efficiency");
        container.replaceChildren();
        metrics.forEach(([label, value]) => {
            const card = document.createElement("div");
            const term = document.createElement("span");
            const result = document.createElement("strong");
            term.textContent = label;
            result.textContent = value;
            card.append(term, result);
            container.appendChild(card);
        });
    }

    function renderCommandReview(report) {
        const classifications = {
            diagnostic: "Diagnostyka",
            repair: "Naprawa",
            verification: "Weryfikacja",
            navigation: "Nawigacja",
            unnecessary: "Niezwiązana",
        };
        const relevance = { direct: "Istotna", supporting: "Wspierająca", unrelated: "Niezwiązana" };
        const review = Array.isArray(report.command_review) ? report.command_review : [];
        const reviewPanel = document.getElementById("post-incident-command-review");
        reviewPanel.hidden = !review.length;
        document.getElementById("post-incident-command-count").textContent = `${review.length} komend`;
        const container = document.getElementById("post-incident-command-items");
        container.replaceChildren();
        if (!review.length) return;
        review.forEach((entry) => {
            const item = document.createElement("article");
            item.className = "command-review-item";
            const heading = document.createElement("div");
            const command = document.createElement("code");
            command.textContent = entry.command;
            const badges = document.createElement("div");
            const category = document.createElement("span");
            category.className = "command-badge";
            category.dataset.classification = entry.classification;
            category.textContent = classifications[entry.classification] || entry.classification;
            const relation = document.createElement("span");
            relation.className = "command-badge command-relevance";
            relation.textContent = relevance[entry.relevance] || entry.relevance;
            const status = document.createElement("span");
            status.className = "command-result";
            status.dataset.success = String(entry.success);
            status.textContent = entry.success ? "Sukces" : "Bez powodzenia";
            badges.append(category, relation, status);
            heading.append(command, badges);
            const context = document.createElement("p");
            context.className = "command-context";
            context.textContent = `#${entry.order} · ${entry.host}`;
            const explanation = document.createElement("p");
            explanation.textContent = entry.explanation;
            item.append(heading, context, explanation);
            container.appendChild(item);
        });
    }

    function renderPostIncidentReport(report) {
        document.getElementById("post-incident-score").textContent = report.score;
        document.getElementById("post-incident-summary").textContent = report.incident_summary;
        document.getElementById("post-incident-root-cause").textContent = report.root_cause;
        document.getElementById("post-incident-services").textContent = report.affected_services.join(", ");

        const rootChain = Array.isArray(report.root_cause_chain) ? report.root_cause_chain : [];
        const chain = document.getElementById("post-incident-chain-details");
        chain.hidden = rootChain.length < 2;
        document.getElementById("post-incident-root-chain").textContent = rootChain.join(" → ");
        if (!chain.hidden) {
            document.getElementById("post-incident-primary-fault").textContent = report.primary_fault || rootChain[0];
            document.getElementById("post-incident-secondary-fault").textContent = report.secondary_fault || rootChain[1];
        }

        const impactPath = Array.isArray(report.impact_path) ? report.impact_path : [];
        renderReportList("post-incident-impact-timeline", impactPath);
        document.getElementById("post-incident-impact-path").textContent = impactPath.join(" → ");

        const timeline = Array.isArray(report.repair_timeline)
            ? report.repair_timeline
            : (report.repair_sequence || []).map((description, index) => ({ order: index + 1, description, phase: "repair" }));
        const timelineContainer = document.getElementById("post-incident-repair-timeline");
        timelineContainer.replaceChildren();
        document.getElementById("post-incident-repair-section").hidden = !timeline.length;
        timeline.forEach((step) => {
            const item = document.createElement("li");
            item.dataset.phase = step.phase;
            const order = document.createElement("span");
            order.textContent = String(step.order).padStart(2, "0");
            const text = document.createElement("p");
            text.textContent = step.description;
            item.append(order, text);
            timelineContainer.appendChild(item);
        });
        document.getElementById("post-incident-repair-sequence").textContent = timeline.map((step) => step.description).join(" → ");
        renderReportList("post-incident-actions", report.repair_actions || []);

        const partial = document.getElementById("post-incident-partial");
        partial.hidden = !report.partial_recovery_explanation;
        if (!partial.hidden) document.getElementById("post-incident-partial-explanation").textContent = report.partial_recovery_explanation;

        renderReportMetrics(report);
        renderReportList("post-incident-key-signals", report.key_signals || [], (signal) => signal.signal);
        renderCommandReview(report);
        renderReportList("post-incident-learning-points", report.learning_points || []);
        renderReportList("post-incident-real-world", report.real_world_takeaways || []);
        document.getElementById("post-incident-learning-summary").textContent = report.learning_summary || "—";
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
        const report = sessionData?.post_incident;
        const reportPanel = document.getElementById("post-incident-report");
        reportPanel.hidden = !report;
        if (report) renderPostIncidentReport(report);
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
            sessionData = { ...sessionData, post_incident: result.post_incident };
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
