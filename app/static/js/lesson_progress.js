(() => {
    "use strict";

    const STORAGE_KEY = "shellforge.lessonProgress";
    const STORAGE_VERSION = 1;

    const isValidLessonId = (lessonId) => {
        return Number.isInteger(lessonId) && lessonId > 0;
    };

    const getLessonId = (element) => {
        const lessonId = Number(element?.dataset.lessonId);
        return isValidLessonId(lessonId) ? lessonId : null;
    };

    const readCompletedLessonIds = () => {
        try {
            const storedProgress = window.localStorage.getItem(STORAGE_KEY);

            if (!storedProgress) {
                return new Set();
            }

            const progress = JSON.parse(storedProgress);

            if (
                !progress
                || progress.version !== STORAGE_VERSION
                || !Array.isArray(progress.completedLessonIds)
            ) {
                return new Set();
            }

            return new Set(
                progress.completedLessonIds.filter(isValidLessonId),
            );
        } catch {
            return new Set();
        }
    };

    const writeCompletedLessonIds = (completedLessonIds) => {
        const progress = {
            version: STORAGE_VERSION,
            completedLessonIds: Array.from(completedLessonIds).sort(
                (firstId, secondId) => firstId - secondId,
            ),
        };

        try {
            window.localStorage.setItem(STORAGE_KEY, JSON.stringify(progress));
        } catch {
            return false;
        }

        return true;
    };

    document.addEventListener("DOMContentLoaded", () => {
        const lessonCards = Array.from(
            document.querySelectorAll("[data-lesson-card][data-lesson-id]"),
        );
        const lessonDetail = document.querySelector(
            "[data-lesson-progress-detail][data-lesson-id]",
        );
        const completionButton = document.querySelector(
            "[data-lesson-completion-toggle]",
        );
        const completedCount = document.querySelector(
            "#lesson-completed-count",
        );
        const totalCount = document.querySelector("#lesson-total-count");

        let completedLessonIds = readCompletedLessonIds();

        const updateLessonCard = (card) => {
            const lessonId = getLessonId(card);
            const isCompleted = completedLessonIds.has(lessonId);
            const cardElement = card.querySelector(".lesson-card");
            const status = card.querySelector(
                "[data-lesson-completed-status]",
            );

            cardElement?.classList.toggle("is-completed", isCompleted);

            if (status) {
                status.hidden = !isCompleted;
            }
        };

        const updateCompletionButton = () => {
            if (!lessonDetail || !completionButton) {
                return;
            }

            const lessonId = getLessonId(lessonDetail);
            const isCompleted = completedLessonIds.has(lessonId);
            const label = completionButton.querySelector(
                "[data-lesson-completion-label]",
            );
            const icon = completionButton.querySelector(
                "[data-lesson-completion-icon]",
            );

            completionButton.classList.toggle("is-completed", isCompleted);
            completionButton.setAttribute("aria-pressed", String(isCompleted));
            completionButton.setAttribute(
                "aria-label",
                isCompleted
                    ? "Cofnij oznaczenie ukończenia lekcji"
                    : "Oznacz lekcję jako ukończoną",
            );

            if (label) {
                label.textContent = isCompleted
                    ? "Ukończono"
                    : "Oznacz jako ukończoną";
            }

            if (icon) {
                icon.hidden = !isCompleted;
            }
        };

        const updateProgressCount = () => {
            if (!completedCount || !totalCount) {
                return;
            }

            const completedRenderedLessons = lessonCards.filter((card) => {
                return completedLessonIds.has(getLessonId(card));
            }).length;

            completedCount.textContent = String(completedRenderedLessons);
            totalCount.textContent = String(lessonCards.length);
        };

        const renderProgress = () => {
            lessonCards.forEach(updateLessonCard);
            updateCompletionButton();
            updateProgressCount();
        };

        if (lessonDetail && completionButton) {
            const lessonId = getLessonId(lessonDetail);

            if (lessonId === null) {
                completionButton.disabled = true;
            } else {
                completionButton.addEventListener("click", () => {
                    const updatedLessonIds = new Set(completedLessonIds);

                    if (updatedLessonIds.has(lessonId)) {
                        updatedLessonIds.delete(lessonId);
                    } else {
                        updatedLessonIds.add(lessonId);
                    }

                    completedLessonIds = updatedLessonIds;
                    writeCompletedLessonIds(completedLessonIds);
                    renderProgress();
                });
            }
        }

        window.addEventListener("storage", (event) => {
            if (event.key !== STORAGE_KEY && event.key !== null) {
                return;
            }

            completedLessonIds = readCompletedLessonIds();
            renderProgress();
        });

        renderProgress();
    });
})();
