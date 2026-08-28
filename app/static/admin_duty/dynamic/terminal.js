(() => {
    function createTerminalController({ onSubmit, onOpenChange }) {
        const overlay = document.getElementById("terminal-overlay");
        const form = document.getElementById("terminal-form");
        const input = document.getElementById("terminal-input");
        const submit = document.getElementById("terminal-submit");
        const output = document.getElementById("terminal-output");
        const state = document.getElementById("terminal-state");
        const closeButton = document.getElementById("terminal-close");
        const promptElement = document.getElementById("terminal-prompt");
        const history = [];
        let historyIndex = 0;
        let pending = false;
        let available = true;
        let prompt = "operator@incident:~$";

        function append(type, text) {
            const entry = document.createElement("div");
            entry.className = `terminal-entry terminal-entry-${type}`;
            const content = document.createElement("pre");
            content.textContent = text;
            entry.appendChild(content);
            output.appendChild(entry);
            output.scrollTop = output.scrollHeight;
        }

        function sync() {
            const enabled = available && !pending;
            input.disabled = !enabled;
            submit.disabled = !enabled;
            form.classList.toggle("is-disabled", !enabled);
            if (enabled && !overlay.hidden) {
                window.requestAnimationFrame(() => input.focus({ preventScroll: true }));
            }
        }

        function open() {
            if (!overlay.hidden) return;
            overlay.hidden = false;
            document.body.classList.add("dynamic-modal-open");
            onOpenChange(true);
            sync();
            input.focus({ preventScroll: true });
        }

        function close() {
            if (overlay.hidden) return;
            overlay.hidden = true;
            document.body.classList.remove("dynamic-modal-open");
            input.blur();
            onOpenChange(false);
        }

        function setAvailable(nextAvailable, message = null) {
            available = nextAvailable;
            if (message !== null) state.textContent = message;
            sync();
        }

        function setPrompt(nextPrompt) {
            if (!nextPrompt) return;
            prompt = nextPrompt;
            promptElement.textContent = nextPrompt;
        }

        async function submitCommand() {
            const command = input.value.trim();
            if (!command || pending || !available) return;
            input.value = "";
            if (["clear", "cls"].includes(command.toLowerCase())) {
                history.push(command);
                historyIndex = history.length;
                output.replaceChildren();
                state.textContent = "Historia terminala wyczyszczona";
                sync();
                return;
            }
            pending = true;
            history.push(command);
            historyIndex = history.length;
            append("command", `${prompt} ${command}`);
            state.textContent = "Wykonywanie polecenia...";
            sync();
            try {
                const result = await onSubmit(command);
                setPrompt(result.prompt);
                if (result.output) append("output", result.output);
                state.textContent = "Terminal gotowy";
            } catch (error) {
                append("error", error.message || "Nie udało się wykonać polecenia.");
                state.textContent = "Polecenie nie zostało wykonane";
            } finally {
                pending = false;
                sync();
            }
        }

        form.addEventListener("submit", (event) => {
            event.preventDefault();
            void submitCommand();
        });

        input.addEventListener("keydown", (event) => {
            event.stopPropagation();
            if (event.key === "Enter") {
                event.preventDefault();
                void submitCommand();
                return;
            }
            if (event.key === "Escape") {
                event.preventDefault();
                close();
                return;
            }
            if (event.ctrlKey && event.key.toLowerCase() === "l") {
                event.preventDefault();
                output.replaceChildren();
                return;
            }
            if (event.key === "ArrowUp") {
                event.preventDefault();
                if (historyIndex > 0) {
                    historyIndex -= 1;
                    input.value = history[historyIndex];
                }
            }
            if (event.key === "ArrowDown") {
                event.preventDefault();
                if (historyIndex < history.length - 1) {
                    historyIndex += 1;
                    input.value = history[historyIndex];
                } else {
                    historyIndex = history.length;
                    input.value = "";
                }
            }
        });

        closeButton.addEventListener("click", close);

        return { open, close, append, setAvailable, setPrompt, isOpen: () => !overlay.hidden };
    }

    window.ShellForgeDynamicTerminal = { createTerminalController };
})();
