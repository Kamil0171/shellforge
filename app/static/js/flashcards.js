document.addEventListener("DOMContentLoaded", () => {
    const dataElements = document.querySelectorAll("#flashcards-data div");

    if (!dataElements.length) {
        return;
    }

    const flashcards = Array.from(dataElements).map((element) => ({
        question: element.dataset.question,
        answer: element.dataset.answer,
    }));

    const card = document.querySelector("#flashcards-card");
    const scene = document.querySelector("#flashcards-scene");
    const label = document.querySelector("#flashcard-label");
    const question = document.querySelector("#flashcard-question");
    const answer = document.querySelector("#flashcard-answer");
    const current = document.querySelector("#flashcard-current");
    const progressBar = document.querySelector("#flashcards-progress-bar");
    const dots = document.querySelector("#flashcards-dots");
    const previousButton = document.querySelector("#flashcard-prev");
    const nextButton = document.querySelector("#flashcard-next");
    const reducedMotion = window.matchMedia("(prefers-reduced-motion: reduce)");

    let currentIndex = 0;
    let isFlipped = false;

    flashcards.forEach((_, index) => {
        const dot = document.createElement("button");
        dot.type = "button";
        dot.setAttribute("aria-label", `Przejdź do fiszki ${index + 1}`);
        dot.classList.add("flashcards-dot");

        if (index === 0) {
            dot.classList.add("is-active");
        }

        dot.addEventListener("click", () => {
            goToFlashcard(index);
        });

        dots.appendChild(dot);
    });

    function renderFlashcard() {
        const flashcard = flashcards[currentIndex];

        label.textContent = `Pytanie ${currentIndex + 1}`;
        question.textContent = flashcard.question;
        answer.textContent = flashcard.answer;
        current.textContent = currentIndex + 1;
        progressBar.style.width = `${Math.round(((currentIndex + 1) / flashcards.length) * 100)}%`;

        previousButton.disabled = currentIndex === 0;
        nextButton.disabled = currentIndex === flashcards.length - 1;

        document.querySelectorAll(".flashcards-dot").forEach((dot, index) => {
            dot.classList.toggle("is-active", index === currentIndex);
            dot.setAttribute("aria-current", String(index === currentIndex));
        });
        updateFlipState();
    }

    function updateFlipState() {
        card.classList.toggle("is-flipped", isFlipped);
        scene.setAttribute("aria-pressed", String(isFlipped));
        scene.setAttribute("aria-label", `Fiszka ${currentIndex + 1}. ${isFlipped ? "Pokaż pytanie" : "Pokaż odpowiedź"}`);
        scene.setAttribute("aria-describedby", isFlipped ? "flashcard-answer" : "flashcard-question");
        question.parentElement.setAttribute("aria-hidden", String(isFlipped));
        answer.parentElement.setAttribute("aria-hidden", String(!isFlipped));
    }

    function resetFlip() {
        isFlipped = false;
        updateFlipState();
    }

    function goToFlashcard(index) {
        if (index < 0 || index >= flashcards.length || index === currentIndex) {
            return;
        }

        if (isFlipped) {
            resetFlip();

            setTimeout(() => {
                currentIndex = index;
                renderFlashcard();
            }, reducedMotion.matches ? 0 : 250);

            return;
        }

        currentIndex = index;
        renderFlashcard();
    }

    scene.addEventListener("click", () => {
        isFlipped = !isFlipped;
        updateFlipState();
    });

    previousButton.addEventListener("click", () => {
        goToFlashcard(currentIndex - 1);
    });

    nextButton.addEventListener("click", () => {
        goToFlashcard(currentIndex + 1);
    });

    document.addEventListener("keydown", (event) => {
        if (event.defaultPrevented || event.altKey || event.ctrlKey || event.metaKey || event.repeat) return;
        if (event.target !== scene && event.target.closest("a, button, input, select, textarea, summary, audio[controls], video[controls], iframe, object, embed, [role='button'], [role='link'], [tabindex], [contenteditable]:not([contenteditable='false'])")) return;
        if (event.key === "ArrowLeft") {
            event.preventDefault();
            goToFlashcard(currentIndex - 1);
        }

        if (event.key === "ArrowRight") {
            event.preventDefault();
            goToFlashcard(currentIndex + 1);
        }

        if (event.key === " " || event.key === "Enter") {
            event.preventDefault();
            isFlipped = !isFlipped;
            updateFlipState();
        }
    });

    renderFlashcard();
});
