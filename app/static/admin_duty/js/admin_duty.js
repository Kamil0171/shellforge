(() => {
    const root = document.getElementById("admin-duty");
    if (!root) return;
    const screens = [...root.querySelectorAll(".duty-screen")];
    function show(id) {
        for (const screen of screens) {
            screen.hidden = screen.id !== id;
            screen.classList.toggle("is-active", screen.id === id);
        }
        window.scrollTo({ top: 0, behavior: "instant" });
    }
    for (const [button, screen] of [
        ["play-button", "scenario-screen"],
        ["controls-button", "controls-screen"],
        ["about-game-button", "about-game-screen"],
    ]) document.getElementById(button).addEventListener("click", () => show(screen));
    root.querySelectorAll(".back-to-menu").forEach(button => button.addEventListener("click", () => show("duty-menu-screen")));
    show(new URLSearchParams(window.location.search).get("view") === "scenarios" ? "scenario-screen" : "duty-menu-screen");
})();
