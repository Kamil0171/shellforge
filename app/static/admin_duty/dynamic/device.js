(() => {
    const pointerQuery = window.matchMedia("(pointer: coarse)");

    function isDesktopAllowed() {
        const tabletLike = pointerQuery.matches && navigator.maxTouchPoints > 0;
        const ipadDesktopUa = /Macintosh/i.test(navigator.userAgent) && navigator.maxTouchPoints > 1;
        return window.innerWidth >= 1024 && !tabletLike && !ipadDesktopUa
            && !/Android|iPad|iPhone|Mobile|Tablet|Silk/i.test(navigator.userAgent);
    }

    window.ShellForgeDynamicDevice = { isDesktopAllowed, pointerQuery };
})();
