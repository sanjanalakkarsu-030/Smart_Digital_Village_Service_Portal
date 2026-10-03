// ============================
// Search Announcements
// ============================

function searchAnnouncements(){

    let input = document
    .getElementById("searchInput")
    .value
    .toLowerCase();


    let cards = document
    .querySelectorAll(".announcement-card");


    cards.forEach(card=>{

        let text = card.innerText.toLowerCase();

        if(text.includes(input)){
            card.style.display="block";
        }
        else{
            card.style.display="none";
        }

    });

}


// ============================
// Language Translation
// ============================

function changeLanguage(){

    let language = document
    .getElementById("language")
    .value;


    let titles=document.querySelectorAll(".title");

    let descriptions=document.querySelectorAll(".description");


    titles.forEach(title=>{

        if(title.dataset[language]){

            title.innerText=title.dataset[language];

        }

    });


    descriptions.forEach(description=>{

        if(description.dataset[language]){

            description.innerText=
            description.dataset[language];

        }

    });

}


// ============================
// Category Filter
// ============================

function filterCategory(){

    let category =
    document.getElementById("categoryFilter").value;


    let cards =
    document.querySelectorAll(".announcement-card");


    cards.forEach(card=>{


        if(category=="all"){

            card.style.display="block";

        }

        else if(card.dataset.category==category){

            card.style.display="block";

        }

        else{

            card.style.display="none";

        }


    });

}



// ============================
// Open Details Page
// ============================

function openDetails(title,description,date,time,postedBy,venue){


    let announcement={

        title:title,

        description:description,

        date:date,

        time:time,

        postedBy:postedBy,

        venue:venue

    };


    localStorage.setItem(

        "selectedAnnouncement",

        JSON.stringify(announcement)

    );


    window.location.href=
    "announcement_details.html";


}
function showForm(){

let form=document.getElementById("addForm");

if(form.style.display==="block")
{
form.style.display="none";
}
else
{
form.style.display="block";
}

}



function showForm() {

    const form = document.getElementById("addForm");

    if (form.style.display === "none" ||
        form.style.display === "") {

        form.style.display = "block";

        form.scrollIntoView({
            behavior: "smooth"
        });

    } else {

        form.style.display = "none";
    }
}
function showForm() {

    const form = document.getElementById("addForm");
    const button = document.querySelector(".add-announcement-btn");

    if (form.style.display === "block") {

        form.style.display = "none";

        button.innerHTML = "＋ Add Announcement";

    } else {

        form.style.display = "block";

        button.innerHTML = "✕ Close Form";

        form.scrollIntoView({
            behavior: "smooth",
            block: "start"
        });
    }
}