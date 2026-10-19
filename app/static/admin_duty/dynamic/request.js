(() => {
    class ApiError extends Error {
        constructor(status, detail) {
            super(detail || "Żądanie nie powiodło się.");
            this.status = status;
            this.uncertain = status >= 500;
        }
    }

    async function requestJson(url, options = {}, timeoutMs = 15000) {
        const controller = new AbortController();
        let timer;
        let response;
        const timeout = new Promise((_, reject) => {
            timer = window.setTimeout(() => {
                reject(new Error("Przekroczono czas oczekiwania na odpowiedź."));
                controller.abort();
            }, timeoutMs);
        });
        const request = async () => {
            response = await fetch(url, { ...options, signal: controller.signal });
            let data = null;
            try {
                data = await response.json();
            } catch (error) {
                if (response.ok) throw error;
            }
            if (!response.ok) {
                throw new ApiError(response.status, typeof data?.detail === "string" ? data.detail : null);
            }
            if (!data || typeof data !== "object") throw new Error("Brak odpowiedzi JSON.");
            return data;
        };
        try {
            return await Promise.race([request(), timeout]);
        } catch (error) {
            if (response && !response.ok) {
                throw error instanceof ApiError ? error : new ApiError(response.status);
            }
            error.uncertain = options.method === "POST";
            throw error;
        } finally {
            window.clearTimeout(timer);
        }
    }

    window.ShellForgeDynamicApi = { ApiError, requestJson };
})();
