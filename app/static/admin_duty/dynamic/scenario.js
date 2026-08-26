(() => {
    const root = document.getElementById("dynamic-session-workspace");

    if (!root) {
        return;
    }

    const sessionId = root.dataset.sessionId;
    const loadingPanel = document.getElementById("workspace-loading");
    const errorPanel = document.getElementById("workspace-error");
    const errorTitle = document.getElementById("workspace-error-title");
    const errorMessage = document.getElementById("workspace-error-message");
    const retryButton = document.getElementById("retry-session-button");
    const workspace = document.getElementById("workspace-content");
    const endSummary = document.getElementById("end-summary");
    const completionOverlay = document.getElementById("completion-overlay");
    const completionBanner = document.getElementById("completion-banner");
    const completionError = document.getElementById("completion-error");
    const terminalOutput = document.getElementById("terminal-output");
    const terminalForm = document.getElementById("terminal-form");
    const terminalInput = document.getElementById("terminal-input");
    const terminalSubmit = document.getElementById("terminal-submit");
    const terminalState = document.getElementById("terminal-state");
    const terminalConnection = document.getElementById("terminal-connection");
    const commandHistory = [];
    let historyIndex = 0;
    let currentIncident = null;
    let currentProgress = null;
    let commandPending = false;
    let sessionEnding = false;

    const statusLabels = {
        active: "Aktywny",
        completed: "Ukończony",
        ended: "Zakończony",
    };

    const difficultyLabels = {
        easy: "Łatwy",
        medium: "Średni",
        hard: "Trudny",
    };

    const interfaceLabels = {
        terminal: "Terminal systemd",
        monitoring: "Monitoring",
        ticket: "Zgłoszenie incydentu",
        file_editor: "Edytor plików",
    };

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
            const detail =
                typeof data?.detail === "string" ? data.detail : null;
            throw new ApiError(response.status, detail);
        }

        return data;
    }

    function appendTerminalEntry(type, text) {
        const entry = document.createElement("div");
        entry.className = `terminal-entry terminal-entry-${type}`;
        const content = document.createElement("pre");
        content.textContent = text;
        entry.appendChild(content);
        terminalOutput.appendChild(entry);
        terminalOutput.scrollTop = terminalOutput.scrollHeight;
    }

    function setTerminalEnabled(enabled, message = null) {
        const available = enabled && !commandPending && !sessionEnding;
        terminalInput.disabled = !available;
        terminalSubmit.disabled = !available;
        terminalForm.classList.toggle("is-disabled", !available);
        terminalConnection.textContent = available ? "CONNECTED" : "LOCKED";
        terminalConnection.classList.toggle("is-locked", !available);

        if (message !== null) {
            terminalState.textContent = message;
        }

        if (available) {
            terminalInput.focus({ preventScroll: true });
        }
    }

    function renderIncident(incident) {
        currentIncident = incident;
        document.getElementById("workspace-title").textContent = incident.title;
        document.getElementById("incident-title").textContent = incident.title;
        document.getElementById("incident-organization").textContent =
            incident.organization;
        document.getElementById("incident-environment").textContent =
            incident.environment_label;
        document.getElementById("incident-briefing").textContent =
            incident.briefing;
        document.getElementById("incident-difficulty").textContent =
            difficultyLabels[incident.difficulty] || incident.difficulty;
        document.getElementById("incident-main-objective").textContent =
            incident.main_objective;

        const tools = document.getElementById("incident-interfaces");
        tools.replaceChildren();

        incident.interfaces.forEach((interfaceId) => {
            const tool = document.createElement("span");
            tool.textContent = interfaceLabels[interfaceId] || "Narzędzie operacyjne";
            tools.appendChild(tool);
        });
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

        document.getElementById("objectives-counter").textContent =
            `${progress.completed_objectives} / ${progress.total_objectives}`;
    }

    function updateCompletionStats(progress) {
        const objectives =
            `${progress.completed_objectives} / ${progress.total_objectives}`;
        document.getElementById("completion-score").textContent = progress.score;
        document.getElementById("completion-commands").textContent =
            progress.commands_used;
        document.getElementById("completion-objectives").textContent = objectives;
    }

    function showCompletion(progress) {
        updateCompletionStats(progress);
        completionBanner.hidden = false;
        completionOverlay.hidden = false;
        document.body.classList.add("dynamic-modal-open");
        setTerminalEnabled(false, "Misja ukończona — terminal zablokowany");
        document.getElementById("end-session-button").focus();
    }

    function hideCompletion() {
        completionOverlay.hidden = true;
        document.body.classList.remove("dynamic-modal-open");
    }

    function renderSummary(progress) {
        hideCompletion();
        workspace.hidden = true;
        loadingPanel.hidden = true;
        errorPanel.hidden = true;
        endSummary.hidden = false;
        document.getElementById("summary-difficulty").textContent =
            difficultyLabels[currentIncident?.difficulty] || "—";
        document.getElementById("summary-score").textContent = progress.score;
        document.getElementById("summary-commands").textContent =
            progress.commands_used;
        document.getElementById("summary-objectives").textContent =
            `${progress.completed_objectives} / ${progress.total_objectives}`;
    }

    function renderProgress(progress, { showSuccess = true } = {}) {
        currentProgress = progress;
        renderObjectives(progress);

        const label = statusLabels[progress.status] || progress.status;
        const badge = document.getElementById("session-status-badge");
        badge.textContent = label;
        badge.dataset.status = progress.status;
        document.getElementById("header-score").textContent = progress.score;
        document.getElementById("progress-score").textContent = progress.score;
        document.getElementById("commands-used").textContent = progress.commands_used;
        document.getElementById("hints-used").textContent = progress.hints_used;
        document.getElementById("progress-status").textContent = label;
        document.getElementById("session-revision").textContent =
            `REV ${progress.revision}`;

        if (progress.status === "ended") {
            renderSummary(progress);
            return;
        }

        if (progress.status === "completed" || progress.mission_complete) {
            completionBanner.hidden = false;
            setTerminalEnabled(false, "Misja ukończona — terminal zablokowany");

            if (showSuccess) {
                showCompletion(progress);
            }
            return;
        }

        completionBanner.hidden = true;
        setTerminalEnabled(true, "Terminal gotowy");
    }

    function showWorkspace(data) {
        loadingPanel.hidden = true;
        errorPanel.hidden = true;
        endSummary.hidden = true;
        workspace.hidden = false;
        renderIncident(data.incident);
        renderProgress(data.progress);

        if (data.progress.status === "active") {
            appendTerminalEntry(
                "system",
                "Połączenie z bezpiecznym środowiskiem zostało ustanowione.\nWpisz polecenie, aby rozpocząć diagnostykę.",
            );
        }
    }

    function showLoadError(error) {
        hideCompletion();
        loadingPanel.hidden = true;
        workspace.hidden = true;
        endSummary.hidden = true;
        completionBanner.hidden = true;
        errorPanel.hidden = false;

        if (error instanceof ApiError && error.status === 404) {
            errorTitle.textContent = "Ta sesja wygasła lub nie istnieje";
            errorMessage.textContent =
                "Rozpocznij nowy incydent, aby wrócić do laboratorium.";
            retryButton.hidden = true;
            return;
        }

        errorTitle.textContent = "Nie udało się pobrać sesji";
        errorMessage.textContent =
            "Sprawdź połączenie i spróbuj ponownie. Twój postęp nie został zmieniony.";
        retryButton.hidden = false;
    }

    async function loadSession({ showLoading = true } = {}) {
        if (showLoading) {
            loadingPanel.hidden = false;
            errorPanel.hidden = true;
        }

        try {
            const data = await requestJson(
                `/admin-duty/dynamic/api/sessions/${sessionId}`,
            );
            showWorkspace(data);
        } catch (error) {
            showLoadError(error);
        }
    }

    function commandErrorMessage(error) {
        if (error instanceof ApiError && error.status === 400) {
            return error.message;
        }

        if (error instanceof ApiError && error.status === 422) {
            return "Polecenie ma nieprawidłowy format.";
        }

        return "Nie udało się wykonać polecenia. Możesz spróbować ponownie.";
    }

    async function executeCommand(command) {
        commandPending = true;
        setTerminalEnabled(false, "Wykonywanie polecenia...");
        appendTerminalEntry("command", `operator@incident:~$ ${command}`);

        try {
            const result = await requestJson(
                "/admin-duty/dynamic/api/command",
                {
                    method: "POST",
                    headers: { "Content-Type": "application/json" },
                    body: JSON.stringify({
                        session_id: sessionId,
                        command,
                    }),
                },
            );
            appendTerminalEntry("output", result.output);
            commandPending = false;
            renderProgress(result.progress);
        } catch (error) {
            commandPending = false;

            if (error instanceof ApiError && error.status === 404) {
                showLoadError(error);
                return;
            }

            if (error instanceof ApiError && error.status === 409) {
                appendTerminalEntry("error", error.message);
                setTerminalEnabled(false, "Sesja nie przyjmuje kolejnych poleceń");
                await loadSession({ showLoading: false });
                return;
            }

            appendTerminalEntry("error", commandErrorMessage(error));
            terminalInput.value = command;
            setTerminalEnabled(true, "Polecenie nie zostało wykonane");
        }
    }

    async function endSession() {
        if (sessionEnding) {
            return;
        }

        sessionEnding = true;
        completionError.hidden = true;
        document.getElementById("end-session-button").disabled = true;
        document.getElementById("banner-end-button").disabled = true;

        try {
            const result = await requestJson(
                "/admin-duty/dynamic/api/end",
                {
                    method: "POST",
                    headers: { "Content-Type": "application/json" },
                    body: JSON.stringify({ session_id: sessionId }),
                },
            );
            renderProgress(result.progress);
        } catch (error) {
            if (error instanceof ApiError && error.status === 404) {
                showLoadError(error);
                return;
            }

            if (error instanceof ApiError && error.status === 409) {
                sessionEnding = false;
                hideCompletion();
                await loadSession({ showLoading: false });
                return;
            }

            completionError.textContent =
                "Nie udało się zakończyć sesji. Spróbuj ponownie.";
            completionError.hidden = false;
            sessionEnding = false;
            document.getElementById("end-session-button").disabled = false;
            document.getElementById("banner-end-button").disabled = false;
        }
    }

    function submitCurrentCommand() {
        const command = terminalInput.value.trim();

        if (!command || commandPending || currentProgress?.status !== "active") {
            return;
        }

        commandHistory.push(command);
        historyIndex = commandHistory.length;
        terminalInput.value = "";
        void executeCommand(command);
    }

    terminalForm.addEventListener("submit", (event) => {
        event.preventDefault();
        submitCurrentCommand();
    });

    terminalInput.addEventListener("keydown", (event) => {
        if (event.key === "Enter") {
            event.preventDefault();
            submitCurrentCommand();
            return;
        }

        if (event.ctrlKey && event.key.toLowerCase() === "l") {
            event.preventDefault();
            terminalOutput.replaceChildren();
            return;
        }

        if (event.key === "ArrowUp") {
            event.preventDefault();

            if (historyIndex > 0) {
                historyIndex -= 1;
                terminalInput.value = commandHistory[historyIndex];
            }
        }

        if (event.key === "ArrowDown") {
            event.preventDefault();

            if (historyIndex < commandHistory.length - 1) {
                historyIndex += 1;
                terminalInput.value = commandHistory[historyIndex];
            } else {
                historyIndex = commandHistory.length;
                terminalInput.value = "";
            }
        }
    });

    retryButton.addEventListener("click", () => {
        void loadSession();
    });

    document.getElementById("continue-session-button").addEventListener(
        "click",
        hideCompletion,
    );
    document.getElementById("end-session-button").addEventListener(
        "click",
        () => void endSession(),
    );
    document.getElementById("banner-end-button").addEventListener(
        "click",
        () => void endSession(),
    );

    void loadSession();
})();
