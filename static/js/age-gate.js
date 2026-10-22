(() => {
    "use strict";

    const dialog = document.getElementById("age-gate");
    if (!dialog) return;

    const page = document.querySelector(".page");
    const title = document.getElementById("age-gate-title");
    const error = document.getElementById("age-gate-error");
    const cookieName = encodeURIComponent(dialog.dataset.cookieName);
    const cookieValue = encodeURIComponent(dialog.dataset.ageLimit);

    const isConfirmed = () => {
        try {
            return document.cookie.split(";").some(
                (cookie) => cookie.trim() === `${cookieName}=${cookieValue}`
            );
        } catch {
            // Storage may be disabled. Keep the dialog visible instead of failing silently.
            return false;
        }
    };

    const unlock = () => {
        document.documentElement.classList.remove("age-gate-pending");
        if (page) page.inert = false;
        if (dialog.open) dialog.close();
    };

    const checkAge = () => {
        if (isConfirmed()) {
            unlock();
            return;
        }

        document.documentElement.classList.add("age-gate-pending");
        if (page) page.inert = true;
        if (!dialog.open) dialog.showModal();
        title?.focus();
    };

    // The backdrop should not be dismissible using Escape.
    dialog.addEventListener("cancel", (event) => event.preventDefault());

    document.getElementById("age-gate-confirm")?.addEventListener("click", () => {
        try {
            const secure = location.protocol === "https:" ? "; Secure" : "";
            // Session cookie, not a permanent age-verification mechanism.
            document.cookie = `${cookieName}=${cookieValue}; Path=/; SameSite=Lax${secure}`;
        } catch {
            error.hidden = false;
            return;
        }

        if (!isConfirmed()) {
            error.hidden = false;
            return;
        }
        error.hidden = true;
        unlock();
        document.querySelector(".site-name")?.focus();
    });

    document.getElementById("age-gate-leave")?.addEventListener("click", () => {
        location.replace("about:blank");
    });

    // The page may return from the back/forward cache after the cookie changed.
    window.addEventListener("pageshow", checkAge);
    checkAge();
})();
