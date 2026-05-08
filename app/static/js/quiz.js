document.addEventListener("DOMContentLoaded", () => {
    const quizForm = document.querySelector(".quiz-form");

    if (quizForm) {
        quizForm.addEventListener("submit", (event) => {
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

        setTimeout(() => {
            progressFill.style.width = `${progressValue}%`;
        }, 250);
    }
});