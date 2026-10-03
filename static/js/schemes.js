// Search Function
function searchScheme() {
    let input = document.getElementById("search").value.toUpperCase();
    let cards = document.getElementsByClassName("card");

    for (let i = 0; i < cards.length; i++) {
        let title = cards[i].getElementsByTagName("h2")[0];

        if (title.innerHTML.toUpperCase().indexOf(input) > -1) {
            cards[i].style.display = "";
        } else {
            cards[i].style.display = "none";
        }
    }
}

// Automatically fill selected scheme in Apply Form
window.onload = function () {

    const params = new URLSearchParams(window.location.search);

    const scheme = params.get("scheme");

    const schemeField = document.getElementById("schemeName");

    if (schemeField && scheme) {
        schemeField.value = scheme;
    }

};