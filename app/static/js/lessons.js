document.addEventListener("DOMContentLoaded", () => {
    const searchInput = document.querySelector("#lesson-search");
    const levelFilter = document.querySelector("#lesson-level-filter");
    const moduleFilter = document.querySelector("#lesson-module-filter");
    const resetButton = document.querySelector("#lesson-filters-reset");
    const visibleCount = document.querySelector("#lesson-visible-count");
    const emptyState = document.querySelector("#lessons-empty-state");
    const lessonCards = Array.from(document.querySelectorAll("[data-lesson-card]"));

    if (!searchInput || !levelFilter || !moduleFilter || !visibleCount) {
        return;
    }

    const normalize = (value) => {
        return value
            .toLowerCase()
            .trim()
            .normalize("NFD")
            .replace(/[\u0300-\u036f]/g, "");
    };

    const updateLessons = () => {
        const searchValue = normalize(searchInput.value);
        const selectedLevel = normalize(levelFilter.value);
        const selectedModule = normalize(moduleFilter.value);

        let visibleLessons = 0;

        lessonCards.forEach((card) => {
            const title = normalize(card.dataset.title || "");
            const description = normalize(card.dataset.description || "");
            const level = normalize(card.dataset.level || "");
            const module = normalize(card.dataset.module || "");

            const searchableText = `${title} ${description} ${level} ${module}`;

            const matchesSearch =
                !searchValue || searchableText.includes(searchValue);

            const matchesLevel = !selectedLevel || level === selectedLevel;
            const matchesModule = !selectedModule || module === selectedModule;
            const isVisible = matchesSearch && matchesLevel && matchesModule;

            card.classList.toggle("is-hidden", !isVisible);
            card.hidden = !isVisible;

            if (isVisible) {
                visibleLessons += 1;
            }
        });

        visibleCount.textContent = String(visibleLessons);

        if (emptyState) {
            emptyState.classList.toggle("d-none", visibleLessons !== 0);
        }
    };

    const resetFilters = () => {
        searchInput.value = "";
        levelFilter.value = "";
        moduleFilter.value = "";
        updateLessons();
        searchInput.focus();
    };

    searchInput.addEventListener("input", updateLessons);
    levelFilter.addEventListener("change", updateLessons);
    moduleFilter.addEventListener("change", updateLessons);

    if (resetButton) {
        resetButton.addEventListener("click", resetFilters);
    }

    updateLessons();
});