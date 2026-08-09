(() => {
    const root =
        document.getElementById("admin-duty");

    if (!root) {
        return;
    }

    const menuScreen =
        document.getElementById("duty-menu-screen");

    const scenarioScreen =
        document.getElementById("scenario-screen");

    const briefingScreen =
        document.getElementById("briefing-screen");

    const controlsScreen =
        document.getElementById("controls-screen");

    const aboutGameScreen =
        document.getElementById("about-game-screen");

    const transition =
        document.getElementById("duty-transition");

    const transitionTitle =
        document.getElementById("transition-title");

    const transitionContext =
        document.getElementById("transition-context");

    const transitionStatus =
        document.getElementById("transition-status");

    const bootStorageKey =
        "shellforge:admin-duty:booted";

    const screens = [
        menuScreen,
        scenarioScreen,
        briefingScreen,
        controlsScreen,
        aboutGameScreen,
    ];

    function wait(duration) {
        return new Promise((resolve) => {
            window.setTimeout(
                resolve,
                duration,
            );
        });
    }

    function showScreen(
        screen,
        smoothScroll = true,
    ) {
        screens.forEach((item) => {
            item.hidden = true;
            item.classList.remove(
                "is-active",
            );
        });

        screen.hidden = false;
        void screen.offsetWidth;
        screen.classList.add(
            "is-active",
        );

        window.scrollTo({
            top: 0,
            behavior: smoothScroll
                ? "smooth"
                : "auto",
        });
    }

    function showTransition({
        title,
        context,
        status,
    }) {
        transitionTitle.textContent =
            title;

        transitionContext.textContent =
            context;

        transitionStatus.textContent =
            status;

        transition.classList.add(
            "is-visible",
        );

        transition.setAttribute(
            "aria-hidden",
            "false",
        );
    }

    function hideTransition() {
        transition.classList.remove(
            "is-visible",
        );

        transition.setAttribute(
            "aria-hidden",
            "true",
        );
    }

    function changeTransitionStatus(
        text,
    ) {
        transitionStatus.textContent =
            text;
    }

    function getReferrerPath() {
        if (!document.referrer) {
            return null;
        }

        try {
            const referrer =
                new URL(document.referrer);

            if (
                referrer.origin !==
                window.location.origin
            ) {
                return null;
            }

            return referrer.pathname;
        } catch {
            return null;
        }
    }

    function hasModuleBooted() {
        try {
            return (
                window.sessionStorage
                    .getItem(
                        bootStorageKey,
                    ) === "true"
            );
        } catch {
            return false;
        }
    }

    function markModuleAsBooted() {
        try {
            window.sessionStorage.setItem(
                bootStorageKey,
                "true",
            );
        } catch {
            return;
        }
    }

    function shouldShowModuleBoot(view) {
        if (view === "scenarios") {
            return false;
        }

        const navigationEntry =
            window.performance
                .getEntriesByType(
                    "navigation",
                )[0];

        if (
            navigationEntry?.type ===
            "reload"
        ) {
            return false;
        }

        const referrerPath =
            getReferrerPath();

        if (
            referrerPath?.startsWith(
                "/admin-duty",
            )
        ) {
            return false;
        }

        const cameFromShellForge =
            referrerPath !== null;

        return (
            cameFromShellForge ||
            !hasModuleBooted()
        );
    }

    async function runModuleBoot() {
        markModuleAsBooted();

        showTransition({
            title:
                "Uruchamianie symulatora",
            context:
                "OPERATIONS SIMULATOR // NOC",
            status:
                "Ładowanie środowiska...",
        });

        await wait(280);

        changeTransitionStatus(
            "Inicjalizacja scenariuszy...",
        );

        await wait(290);

        changeTransitionStatus(
            "Łączenie z centrum operacyjnym...",
        );

        await wait(330);
        hideTransition();
        showScreen(menuScreen, false);
    }

    async function startScenario(
        scenarioId,
    ) {
        const response = await fetch(
            "/admin-duty/api/start",
            {
                method: "POST",
                headers: {
                    "Content-Type":
                        "application/json",
                },
                body: JSON.stringify({
                    scenario_id: scenarioId,
                }),
            },
        );

        if (!response.ok) {
            throw new Error(
                "Nie udało się rozpocząć scenariusza.",
            );
        }

        return response.json();
    }

    document
        .getElementById("play-button")
        .addEventListener(
            "click",
            () => {
                showScreen(
                    scenarioScreen,
                );
            },
        );

    document
        .getElementById("controls-button")
        .addEventListener(
            "click",
            () => {
                showScreen(
                    controlsScreen,
                );
            },
        );

    document
        .getElementById("about-game-button")
        .addEventListener(
            "click",
            () => {
                showScreen(
                    aboutGameScreen,
                );
            },
        );

    document
        .querySelectorAll(".back-to-menu")
        .forEach((button) => {
            button.addEventListener(
                "click",
                () => {
                    showScreen(
                        menuScreen,
                    );
                },
            );
        });

    document
        .querySelectorAll(".select-scenario")
        .forEach((button) => {
            button.addEventListener(
                "click",
                () => {
                    showScreen(
                        briefingScreen,
                    );
                },
            );
        });

    document
        .getElementById(
            "briefing-back-button",
        )
        .addEventListener(
            "click",
            () => {
                showScreen(
                    scenarioScreen,
                );
            },
        );

    document
        .getElementById(
            "start-duty-button",
        )
        .addEventListener(
            "click",
            async (event) => {
                const button =
                    event.currentTarget;

                const scenarioId =
                    button.dataset.scenarioId;

                button.disabled = true;

                showTransition({
                    title:
                        "Rozpoczynanie dyżuru",
                    context:
                        button.dataset
                            .scenarioContext,
                    status:
                        "Tworzenie sesji operacyjnej...",
                });

                try {
                    const data =
                        await startScenario(
                            scenarioId,
                        );

                    await wait(350);

                    changeTransitionStatus(
                        "Łączenie z centrum operacyjnym...",
                    );

                    await wait(550);

                    window.location.href =
                        data.redirect_url;
                } catch (error) {
                    hideTransition();
                    button.disabled = false;

                    window.alert(
                        error.message,
                    );
                }
            },
        );

    const view =
        new URLSearchParams(
            window.location.search,
        ).get("view");

    if (view === "scenarios") {
        showScreen(
            scenarioScreen,
            false,
        );
    } else {
        showScreen(
            menuScreen,
            false,
        );
    }

    if (shouldShowModuleBoot(view)) {
        void runModuleBoot();
    }
})();
