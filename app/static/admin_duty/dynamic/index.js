(() => {
    const root = document.getElementById("dynamic-lab");

    if (!root) {
        return;
    }

    const startButtons = Array.from(document.querySelectorAll(".start-incident-button"));
    const retryButton = document.getElementById("retry-start-button");
    const errorPanel = document.getElementById("start-error");
    const errorMessage = document.getElementById("start-error-message");
    const overlay = document.getElementById("generation-overlay");
    const statusText = document.getElementById("generation-status");
    const deviceNotice = document.getElementById("desktop-start-notice");
    const { isDesktopAllowed, pointerQuery } = window.ShellForgeDynamicDevice;
    const reducedMotion = window.matchMedia("(prefers-reduced-motion: reduce)").matches;
    let requestInProgress = false;
    let selectedDifficulty = "easy";
    const { requestJson, ApiError } = window.ShellForgeDynamicApi;

    function updateDeviceAvailability() {
        const allowed = isDesktopAllowed();
        startButtons.forEach(button => { button.disabled = requestInProgress || !allowed; });
        retryButton.disabled = requestInProgress || !allowed;
        deviceNotice.textContent = allowed
            ? "Rozgrywka wymaga komputera, klawiatury i okna o szerokości co najmniej 1024 px."
            : "Nie można rozpocząć incydentu na tym urządzeniu lub przy tej szerokości okna. Użyj komputera z klawiaturą i okna o szerokości co najmniej 1024 px.";
    }

    function showPreparation() {
        errorPanel.hidden = true;
        overlay.hidden = false;
        overlay.setAttribute("aria-hidden", "false");
        overlay.setAttribute("aria-busy", "true");
        statusText.textContent = "Trwa przygotowywanie i sprawdzanie incydentu. To może potrwać kilkadziesiąt sekund.";
        document.body.classList.add("dynamic-generation-open");
    }

    function hidePreparation() {
        overlay.hidden = true;
        overlay.setAttribute("aria-hidden", "true");
        overlay.setAttribute("aria-busy", "false");
        document.body.classList.remove("dynamic-generation-open");
    }

    function getStartError(status, detail) {
        if (status === 503) {
            const messages = {
                "Limit aktywnych sesji został osiągnięty.": "Wszystkie stanowiska są teraz zajęte. Spróbuj ponownie za chwilę.",
                "Trwały zapis sesji jest chwilowo niedostępny.": "Zapis sesji jest chwilowo niedostępny. Spróbuj ponownie za chwilę.",
                "Nie udało się przygotować poprawnego incydentu.": "Nie udało się przygotować incydentu. Spróbuj ponownie za chwilę.",
            };
            return Object.hasOwn(messages, detail) ? messages[detail] : "Laboratorium jest chwilowo niedostępne. Spróbuj ponownie za chwilę.";
        }

        if (status === 400 || status === 422) {
            return detail || "Nie udało się przygotować wybranego poziomu.";
        }

        return "Nie udało się uruchomić laboratorium. Spróbuj ponownie.";
    }

    function showStartError(message) {
        errorMessage.textContent = message;
        errorPanel.hidden = false;
        errorPanel.scrollIntoView({
            behavior: reducedMotion ? "auto" : "smooth",
            block: "center",
        });
    }

    async function startIncident(difficulty = selectedDifficulty) {
        if (!isDesktopAllowed()) {
            updateDeviceAvailability();
            deviceNotice.focus({ preventScroll: true });
            return;
        }
        if (requestInProgress) {
            return;
        }

        requestInProgress = true;
        selectedDifficulty = difficulty;
        startButtons.forEach((button) => { button.disabled = true; });
        retryButton.disabled = true;
        showPreparation();

        try {
            const data = await requestJson("/admin-duty/dynamic/api/start", {
                method: "POST",
                headers: {
                    "Content-Type": "application/json",
                },
                body: JSON.stringify({ difficulty }),
            }, 90000);
            if (typeof data.session_id !== "string" || !/^[0-9a-f-]{36}$/i.test(data.session_id)) {
                throw new Error("Brak identyfikatora sesji.");
            }
            statusText.textContent = "Sesja gotowa. Otwieranie laboratorium…";
            overlay.setAttribute("aria-busy", "false");
            window.location.replace(
                `/admin-duty/dynamic/sessions/${data.session_id}`,
            );
        } catch (error) {
            hidePreparation();

            if (error instanceof ApiError) {
                const knownRejection = error.status === 503 && [
                    "Limit aktywnych sesji został osiągnięty.",
                    "Nie udało się przygotować poprawnego incydentu.",
                ].includes(error.message);
                const uncertainty = error.uncertain && !knownRejection
                    ? " Wynik utworzenia sesji jest niepewny. Żądanie nie zostanie ponowione automatycznie; kolejna próba może utworzyć nową sesję."
                    : "";
                showStartError(getStartError(error.status, error.message) + uncertainty);
            } else {
                showStartError(
                    "Nie otrzymano potwierdzenia utworzenia sesji. Sesja mogła powstać. Żądanie nie zostanie ponowione automatycznie. Kolejna próba może utworzyć nową sesję.",
                );
            }

            requestInProgress = false;
            updateDeviceAvailability();
        }
    }

    startButtons.forEach((button) => button.addEventListener("click", () => {
        void startIncident(button.dataset.difficulty || "easy");
    }));

    retryButton.addEventListener("click", () => {
        void startIncident();
    });
    window.addEventListener("resize", updateDeviceAvailability);
    pointerQuery.addEventListener?.("change", updateDeviceAvailability);
    updateDeviceAvailability();
})();
