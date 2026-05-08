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

    let currentIndex = 0;
    let isFlipped = false;

    flashcards.forEach((_, index) => {
        const dot = document.createElement("span");
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
        });
    }

    function resetFlip() {
        card.classList.remove("is-flipped");
        isFlipped = false;
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
            }, 250);

            return;
        }

        currentIndex = index;
        renderFlashcard();
    }

    scene.addEventListener("click", () => {
        isFlipped = !isFlipped;
        card.classList.toggle("is-flipped", isFlipped);
    });

    previousButton.addEventListener("click", () => {
        goToFlashcard(currentIndex - 1);
    });

    nextButton.addEventListener("click", () => {
        goToFlashcard(currentIndex + 1);
    });

    document.addEventListener("keydown", (event) => {
        if (event.key === "ArrowLeft") {
            goToFlashcard(currentIndex - 1);
        }

        if (event.key === "ArrowRight") {
            goToFlashcard(currentIndex + 1);
        }

        if (event.key === " " || event.key === "Enter") {
            event.preventDefault();
            isFlipped = !isFlipped;
            card.classList.toggle("is-flipped", isFlipped);
        }
    });

    renderFlashcard();
});