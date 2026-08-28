(() => {
    const root = document.getElementById("dynamic-lab");

    if (!root) {
        return;
    }

    const startButton = document.getElementById("start-easy-button");
    const retryButton = document.getElementById("retry-start-button");
    const errorPanel = document.getElementById("start-error");
    const errorMessage = document.getElementById("start-error-message");
    const overlay = document.getElementById("generation-overlay");
    const steps = Array.from(
        document.querySelectorAll("#generation-steps li"),
    );
    const progressBar = document.getElementById("generation-progress-bar");
    const reducedMotion = window.matchMedia(
        "(prefers-reduced-motion: reduce)",
    ).matches;
    let activeStep = 0;
    let stepTimer = null;
    let requestInProgress = false;

    function wait(duration) {
        return new Promise((resolve) => {
            window.setTimeout(resolve, duration);
        });
    }

    function setActiveStep(index) {
        activeStep = Math.min(index, steps.length - 1);

        steps.forEach((step, stepIndex) => {
            step.classList.toggle("is-complete", stepIndex < activeStep);
            step.classList.toggle("is-active", stepIndex === activeStep);
        });

        progressBar.style.width = `${
            ((activeStep + 1) / steps.length) * 100
        }%`;
    }

    function showPreparation() {
        errorPanel.hidden = true;
        overlay.hidden = false;
        overlay.setAttribute("aria-hidden", "false");
        document.body.classList.add("dynamic-generation-open");
        setActiveStep(0);

        stepTimer = window.setInterval(() => {
            if (activeStep < steps.length - 2) {
                setActiveStep(activeStep + 1);
            }
        }, reducedMotion ? 150 : 520);
    }

    function hidePreparation() {
        if (stepTimer !== null) {
            window.clearInterval(stepTimer);
            stepTimer = null;
        }

        overlay.hidden = true;
        overlay.setAttribute("aria-hidden", "true");
        document.body.classList.remove("dynamic-generation-open");
    }

    async function finishPreparation() {
        if (stepTimer !== null) {
            window.clearInterval(stepTimer);
            stepTimer = null;
        }

        const stepDelay = reducedMotion ? 40 : 170;

        while (activeStep < steps.length - 1) {
            setActiveStep(activeStep + 1);
            await wait(stepDelay);
        }

        await wait(reducedMotion ? 40 : 260);
    }

    async function readError(response) {
        try {
            const data = await response.json();

            if (typeof data.detail === "string") {
                return data.detail;
            }
        } catch {
            return null;
        }

        return null;
    }

    function getStartError(status, detail) {
        if (status === 503) {
            return "Wszystkie stanowiska są teraz zajęte. Spróbuj ponownie za chwilę.";
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

    async function startIncident() {
        if (requestInProgress) {
            return;
        }

        requestInProgress = true;
        startButton.disabled = true;
        retryButton.disabled = true;
        showPreparation();

        try {
            const response = await fetch("/admin-duty/dynamic/api/start", {
                method: "POST",
                headers: {
                    "Content-Type": "application/json",
                },
                body: JSON.stringify({ difficulty: "easy" }),
            });

            if (!response.ok) {
                const detail = await readError(response);
                throw {
                    kind: "api",
                    status: response.status,
                    detail,
                };
            }

            const data = await response.json();
            await finishPreparation();
            hidePreparation();
            window.location.replace(
                `/admin-duty/dynamic/sessions/${data.session_id}`,
            );
        } catch (error) {
            hidePreparation();

            if (error?.kind === "api") {
                showStartError(getStartError(error.status, error.detail));
            } else {
                showStartError(
                    "Nie udało się połączyć z laboratorium. Sprawdź połączenie i spróbuj ponownie.",
                );
            }

            requestInProgress = false;
            startButton.disabled = false;
            retryButton.disabled = false;
        }
    }

    startButton.addEventListener("click", () => {
        void startIncident();
    });

    retryButton.addEventListener("click", () => {
        void startIncident();
    });
})();
