document.addEventListener("DOMContentLoaded", function () {


    /* =========================================
       CURRENT DATE
    ========================================= */

    const dateElement =
        document.getElementById("currentDate");

    if (dateElement) {

        const today = new Date();

        dateElement.innerText =
            today.toLocaleDateString(
                "en-IN",
                {
                    weekday: "long",
                    day: "numeric",
                    month: "long",
                    year: "numeric"
                }
            );

    }


    /* =========================================
       MOBILE SIDEBAR
    ========================================= */

    const toggle =
        document.getElementById("sidebarToggle");

    const sidebar =
        document.getElementById("adminSidebar");

    const overlay =
        document.getElementById("sidebarOverlay");


    if (toggle) {

        toggle.addEventListener("click", function () {

            sidebar.classList.toggle("open");

            overlay.classList.toggle("show");

        });

    }


    if (overlay) {

        overlay.addEventListener("click", function () {

            sidebar.classList.remove("open");

            overlay.classList.remove("show");

        });

    }


    /* =========================================
       NAVIGATION
    ========================================= */

    const navLinks =
        document.querySelectorAll(".admin-nav-link");

    navLinks.forEach(function (link) {

        link.addEventListener("click", function () {

            navLinks.forEach(function (item) {

                item.classList.remove("active");

            });

            if (!link.classList.contains("logout-link")) {

                link.classList.add("active");

            }

        });

    });


    /* =========================================
       QUICK ACTION BUTTONS
    ========================================= */

    const quickButtons =
        document.querySelectorAll(".quick-actions button");

    quickButtons.forEach(function (button) {

        button.addEventListener("click", function () {

            const title =
                button.querySelector("strong");

            if (title) {

                alert(
                    title.innerText +
                    " page will be connected later."
                );

            }

        });

    });


    /* =========================================
       COMPLAINT VIEW BUTTON
    ========================================= */

    const viewButtons =
        document.querySelectorAll(".view-btn");

    viewButtons.forEach(function (button) {

        button.addEventListener("click", function () {

            alert(
                "Complaint details will be connected later."
            );

        });

    });

});