(() => {
    function createTerminalController({ onSubmit, onSaveFile, onOpenChange }) {
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
        const editor = document.getElementById("virtual-editor");
        const editorText = document.getElementById("virtual-editor-content");
        const editorPath = document.getElementById("virtual-editor-path");
        const editorSave = document.getElementById("virtual-editor-save");
        let editingPath = null;

        function closeEditor() {
            if (pending) return;
            editor.hidden = true;
            form.hidden = false;
            editingPath = null;
            sync();
        }

        document.getElementById("virtual-editor-cancel").addEventListener("click", closeEditor);
        editor.addEventListener("keydown", (event) => {
            event.stopPropagation();
            if (event.key === "Escape") {
                event.preventDefault();
                closeEditor();
            }
        });
        editorSave.addEventListener("click", async () => {
            if (pending || !editingPath) return;
            pending = true;
            editorSave.disabled = true;
            try {
                const result = await onSaveFile(editingPath, editorText.value);
                append(result.success ? "output" : "error", result.output);
                pending = false;
                if (result.success) closeEditor();
            } catch (error) {
                state.textContent = error.message;
            } finally {
                pending = false;
                editorSave.disabled = false;
                sync();
            }
        });

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
            if (enabled && !overlay.hidden && !editingPath) {
                window.requestAnimationFrame(() => input.focus({ preventScroll: true }));
            }
        }

        function open() {
            if (!overlay.hidden) return;
            overlay.hidden = false;
            document.body.classList.add("dynamic-modal-open");
            onOpenChange(true);
            sync();
            (available ? input : closeButton).focus({ preventScroll: true });
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
                if (result.editor) {
                    editingPath = result.editor.path;
                    editorPath.textContent = editingPath;
                    editorText.value = result.editor.content;
                    editor.hidden = false;
                    form.hidden = true;
                    editorText.focus();
                }
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

        document.addEventListener("keydown", (event) => {
            if (event.key !== "Escape" || overlay.hidden || editingPath) return;
            event.preventDefault();
            close();
        });

        return { open, close, append, setAvailable, setPrompt, isOpen: () => !overlay.hidden };
    }

    window.ShellForgeDynamicTerminal = { createTerminalController };
})();
