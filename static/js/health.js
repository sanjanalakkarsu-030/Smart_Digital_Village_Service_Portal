// ==========================================
// SMART DIGITAL VILLAGE - HEALTH MODULE
// ENGLISH ONLY
// ==========================================


// ==========================================
// HOSPITAL CATEGORY
// ==========================================

let selectedCategory = "all";


// ==========================================
// CATEGORY BUTTON
// ==========================================

function filterCategory(category) {

    selectedCategory = category;


    const categoryContainer =
        document.querySelector(
            ".category-container"
        );


    const categorySection =
        categoryContainer
            ? categoryContainer.closest(
                ".wide-section"
            )
            : null;


    const searchBox =
        document.getElementById(
            "hospitalSearch"
        );


    const searchSection =
        searchBox
            ? searchBox.closest(
                ".wide-section"
            )
            : null;


    const hospitalTitle =
        document.getElementById(
            "hospitalListTitle"
        );


    const hospitalSection =
        hospitalTitle
            ? hospitalTitle.closest(
                ".wide-section"
            )
            : null;


    // ======================================
    // ALL HOSPITALS
    // ======================================

    if (category === "all") {

        if (categorySection) {
            categorySection.style.display =
                "block";
        }


        if (searchSection) {
            searchSection.style.display =
                "block";
        }


        if (hospitalSection) {
            hospitalSection.style.display =
                "block";
        }


        if (hospitalTitle) {

            hospitalTitle.innerText =
                "🏥 Hospitals";

        }


        filterHospitals();


        if (hospitalSection) {

            hospitalSection.scrollIntoView({
                behavior: "smooth",
                block: "start"
            });

        }

        return;
    }


    // ======================================
    // SPECIAL CATEGORY SELECTED
    // ======================================

    if (categorySection) {

        categorySection.style.display =
            "none";

    }


    if (searchSection) {

        searchSection.style.display =
            "none";

    }


    if (hospitalSection) {

        hospitalSection.style.display =
            "block";

    }


    // ======================================
    // CATEGORY TITLES
    // ======================================

    const categoryTitles = {

        adult:
            "👨 Adult Hospitals",

        children:
            "👶 Children Hospitals",

        eye:
            "👁️ Eye Hospitals",

        heart:
            "❤️ Heart Hospitals",

        skin:
            "🧴 Skin Hospitals",

        dental:
            "🦷 Dental Hospitals",

        kidney:
            "🫘 Kidney Hospitals",

        liver:
            "🫀 Liver Hospitals",

        veterinary:
            "🐄 Veterinary Hospitals"

    };


    if (hospitalTitle) {

        hospitalTitle.innerText =
            categoryTitles[category] ||
            "🏥 Hospitals";

    }


    // Filter hospitals

    filterHospitals();


    // ======================================
    // MOVE TO HOSPITAL RESULTS
    // ======================================

    if (hospitalSection) {

        hospitalSection.scrollIntoView({
            behavior: "smooth",
            block: "start"
        });

    }

}


// ==========================================
// FILTER HOSPITALS ONLY
// ==========================================

function filterHospitals() {

    const searchBox =
        document.getElementById(
            "hospitalSearch"
        );


    const searchText =
        searchBox
            ? searchBox.value
                .toLowerCase()
                .trim()
            : "";


    /*
     * Only hospital items having
     * data-category are selected.
     *
     * PHCs do NOT have data-category.
     *
     * Therefore PHCs remain visible.
     */

    const hospitals =
        document.querySelectorAll(
            ".hospital-item[data-category]"
        );


    let found = 0;


    hospitals.forEach(
        function(hospital) {

            const category =
                hospital.getAttribute(
                    "data-category"
                );


            const searchData =
                hospital.getAttribute(
                    "data-search"
                ) || "";


            const text =
                hospital.textContent
                    .toLowerCase();


            // Category matching

            const categoryMatch =
                selectedCategory === "all" ||
                category === selectedCategory;


            // Search matching

            const searchMatch =
                searchText === "" ||
                searchData
                    .toLowerCase()
                    .includes(searchText) ||
                text.includes(searchText);


            // Show matching hospital

            if (
                categoryMatch &&
                searchMatch
            ) {

                hospital.style.display =
                    "block";

                found++;

            } else {

                hospital.style.display =
                    "none";

            }

        }
    );


    // ======================================
    // NO RESULTS
    // ======================================

    const noResults =
        document.getElementById(
            "noResults"
        );


    if (noResults) {

        if (found === 0) {

            noResults.style.display =
                "block";

        } else {

            noResults.style.display =
                "none";

        }

    }

}


// ==========================================
// CATEGORY FROM URL
// ==========================================

document.addEventListener(
    "DOMContentLoaded",
    function() {

        const params =
            new URLSearchParams(
                window.location.search
            );


        const category =
            params.get("category");


        const validCategories = [

            "all",
            "adult",
            "children",
            "eye",
            "heart",
            "skin",
            "dental",
            "kidney",
            "liver",
            "veterinary"

        ];


        if (
            category &&
            validCategories.includes(
                category
            )
        ) {

            filterCategory(category);

        } else {

            selectedCategory =
                "all";

            filterHospitals();

        }

    }
);


// ==========================================
// ENTER KEY SEARCH
// ==========================================

document.addEventListener(
    "DOMContentLoaded",
    function() {

        const searchBox =
            document.getElementById(
                "hospitalSearch"
            );


        if (searchBox) {

            searchBox.addEventListener(
                "keydown",
                function(event) {

                    if (
                        event.key === "Enter"
                    ) {

                        filterHospitals();

                    }

                }
            );

        }

    }
);
function showHealthTips() {
    document.getElementById("healthTipsSection").style.display = "block";

    document.getElementById("healthTipsSection").scrollIntoView({
        behavior: "smooth",
        block: "start"
    });
}

function hideHealthTips() {
    document.getElementById("healthTipsSection").style.display = "none";

    window.scrollTo({
        top: 0,
        behavior: "smooth"
    });
}