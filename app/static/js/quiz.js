document.addEventListener("DOMContentLoaded", () => {
    const reducedMotion = window.matchMedia("(prefers-reduced-motion: reduce)").matches;
    const quizForm = document.querySelector(".quiz-form");

    if (quizForm) {
        quizForm.addEventListener("submit", (event) => {
            if (reducedMotion) return;
            event.preventDefault();

            window.scrollTo({
                top: 0,
                behavior: "smooth",
            });

            setTimeout(() => {
                quizForm.submit();
            }, 700);
        });
    }

    const progressFill = document.querySelector(".quiz-modern-fill");

    if (progressFill) {
        const progressValue = progressFill.dataset.progress || "0";

        const showProgress = () => {
            progressFill.style.width = `${progressValue}%`;
        };
        if (reducedMotion) showProgress();
        else setTimeout(showProgress, 250);
    }
});
