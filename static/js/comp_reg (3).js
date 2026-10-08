/* =====================================================
   SMART DIGITAL VILLAGE SERVICE PORTAL
   UPDATED JAVASCRIPT
===================================================== */


/* =====================================================
   CONFIGURATION
===================================================== */

const STORAGE_KEY = "complaints";

const VALID_STATUSES = [
    "Registered",
    "Under Review",
    "In Progress",
    "Resolved"
];

const MAX_IMAGE_SIZE = 2 * 1024 * 1024;


/* =====================================================
   DOM ELEMENTS
===================================================== */

const complaintForm =
    document.getElementById("complaintForm");

const complaintIdInput =
    document.getElementById("complaintId");

const mobileInput =
    document.getElementById("mobile");

const photoInput =
    document.getElementById("photo");

const photoPreview =
    document.getElementById("photoPreview");

const trackComplaintId =
    document.getElementById("trackComplaintId");

const trackBtn =
    document.getElementById("trackBtn");

const statusResult =
    document.getElementById("statusResult");

const registeredComplaints =
    document.getElementById("registeredComplaints");


/* =====================================================
   GET COMPLAINTS
===================================================== */

function getComplaints() {

    try {

        return JSON.parse(
            localStorage.getItem(STORAGE_KEY)
        ) || [];

    } catch (error) {

        console.error(
            "Unable to read complaints:",
            error
        );

        return [];

    }

}


/* =====================================================
   SAVE COMPLAINTS
===================================================== */

function saveComplaints(complaints) {

    localStorage.setItem(
        STORAGE_KEY,
        JSON.stringify(complaints)
    );

}


/* =====================================================
   ESCAPE HTML
===================================================== */

function escapeHTML(value) {

    return String(value ?? "")
        .replace(/&/g, "&amp;")
        .replace(/</g, "&lt;")
        .replace(/>/g, "&gt;")
        .replace(/"/g, "&quot;")
        .replace(/'/g, "&#039;");

}


/* =====================================================
   GENERATE UNIQUE COMPLAINT ID
===================================================== */

function generateComplaintID() {

    const complaints =
        getComplaints();

    let id;

    do {

        id =
            "CMP" +
            Math.floor(
                1000 + Math.random() * 9000
            );

    } while (
        complaints.some(
            complaint =>
                complaint.id === id
        )
    );

    complaintIdInput.value = id;

    return id;

}


/* =====================================================
   FORMAT DATE
===================================================== */

function getCurrentDate() {

    return new Date().toLocaleString(
        "en-IN",
        {
            dateStyle: "medium",
            timeStyle: "short"
        }
    );

}


/* =====================================================
   FILE TO BASE64
===================================================== */

function fileToBase64(file) {

    return new Promise(
        function (resolve, reject) {

            const reader =
                new FileReader();

            reader.onload =
                function () {

                    resolve(
                        reader.result
                    );

                };

            reader.onerror =
                function () {

                    reject(
                        new Error(
                            "Unable to read image."
                        )
                    );

                };

            reader.readAsDataURL(file);

        }
    );

}


/* =====================================================
   PHOTO PREVIEW
===================================================== */

photoInput.addEventListener(
    "change",
    function () {

        photoPreview.innerHTML = "";

        const file =
            photoInput.files[0];

        if (!file) {

            return;

        }


        if (!file.type.startsWith("image/")) {

            alert(
                "Please select a valid image."
            );

            photoInput.value = "";

            return;

        }


        if (file.size > MAX_IMAGE_SIZE) {

            alert(
                "Photo size must be less than 2 MB."
            );

            photoInput.value = "";

            return;

        }


        const image =
            document.createElement("img");

        image.alt =
            "Selected complaint photo";


        const reader =
            new FileReader();

        reader.onload =
            function (event) {

                image.src =
                    event.target.result;

                photoPreview.appendChild(
                    image
                );

            };

        reader.readAsDataURL(file);

    }
);


/* =====================================================
   MOBILE NUMBER INPUT
===================================================== */

mobileInput.addEventListener(
    "input",
    function () {

        this.value =
            this.value
                .replace(/\D/g, "")
                .slice(0, 10);

    }
);


/* =====================================================
   TRACK ID INPUT
===================================================== */

trackComplaintId.addEventListener(
    "input",
    function () {

        this.value =
            this.value
                .toUpperCase()
                .replace(/[^A-Z0-9]/g, "")
                .slice(0, 7);

    }
);


/* =====================================================
   FORM SUBMISSION
===================================================== */

complaintForm.addEventListener(
    "submit",
    async function (event) {

        event.preventDefault();


        /* ================= VALUES ================= */

        const complaintId =
            complaintIdInput.value;

        const mobile =
            mobileInput.value.trim();

        const category =
            document
                .getElementById("category")
                .value;

        const title =
            document
                .getElementById("title")
                .value.trim();

        const description =
            document
                .getElementById("description")
                .value.trim();

        const location =
            document
                .getElementById("location")
                .value.trim();


        /* ================= VALIDATION ================= */

        if (!/^[0-9]{10}$/.test(mobile)) {

            alert(
                "Please enter a valid 10-digit mobile number."
            );

            mobileInput.focus();

            return;

        }


        if (!category) {

            alert(
                "Please select a complaint category."
            );

            return;

        }


        if (title.length < 3) {

            alert(
                "Complaint title must contain at least 3 characters."
            );

            return;

        }


        if (description.length < 10) {

            alert(
                "Complaint description must contain at least 10 characters."
            );

            return;

        }


        if (location.length < 3) {

            alert(
                "Please enter a valid location or landmark."
            );

            return;

        }


        /* =================================================
           PHOTO
        ================================================= */

        let photo = "";

        const file =
            photoInput.files[0];


        if (file) {

            if (!file.type.startsWith("image/")) {

                alert(
                    "Please select a valid image file."
                );

                return;

            }


            if (file.size > MAX_IMAGE_SIZE) {

                alert(
                    "Photo size must be less than 2 MB."
                );

                return;

            }


            try {

                photo =
                    await fileToBase64(file);

            } catch (error) {

                alert(
                    "Unable to process the selected photo."
                );

                return;

            }

        }


        /* =================================================
           CREATE COMPLAINT
        ================================================= */

        const date =
            getCurrentDate();


        const complaint = {

            id: complaintId,

            mobile: mobile,

            category: category,

            title: title,

            description: description,

            location: location,

            photo: photo,

            status: "Registered",

            date: date,

            statusHistory: [

                {
                    status: "Registered",
                    date: date
                }

            ]

        };


        /* =================================================
           SAVE
        ================================================= */

        const complaints =
            getComplaints();


        complaints.push(
            complaint
        );


        saveComplaints(
            complaints
        );


        /* =================================================
           SAVE INDIVIDUAL RECORD
        ================================================= */

        localStorage.setItem(
            complaintId,
            JSON.stringify(complaint)
        );


        /* =================================================
           SUCCESS
        ================================================= */

        alert(

            "Complaint Registered Successfully!\n\n" +

            "Complaint ID: " +
            complaintId +

            "\n\n" +

            "Status: Registered\n\n" +

            "Please save your Complaint ID " +
            "for future tracking."

        );


        /* =================================================
           RESET
        ================================================= */

        complaintForm.reset();

        photoPreview.innerHTML = "";


        /* =================================================
           NEW ID
        ================================================= */

        generateComplaintID();


        /* =================================================
           UPDATE LIST
        ================================================= */

        displayRegisteredComplaints();

    }
);


/* =====================================================
   TRACK COMPLAINT
===================================================== */

function trackComplaint() {

    const complaintId =
        trackComplaintId.value
            .trim()
            .toUpperCase();


    /* ================= EMPTY ================= */

    if (!complaintId) {

        showStatusMessage(

            "Complaint ID Required",

            "Please enter a Complaint ID."

        );

        return;

    }


    /* ================= FORMAT ================= */

    if (!/^CMP[0-9]{4}$/.test(complaintId)) {

        showStatusMessage(

            "Invalid Complaint ID",

            "Please enter an ID such as CMP4821."

        );

        return;

    }


    /* ================= SEARCH ================= */

    const complaints =
        getComplaints();


    const complaint =
        complaints.find(
            item =>
                item.id === complaintId
        );


    /* ================= NOT FOUND ================= */

    if (!complaint) {

        showStatusMessage(

            "Complaint Not Found",

            `
            No complaint was found with ID:
            <strong>
                ${escapeHTML(complaintId)}
            </strong>

            <br><br>

            Please check your Complaint ID
            and try again.
            `

        );

        return;

    }


    /* ================= DISPLAY ================= */

    displayComplaintStatus(
        complaint
    );

}


/* =====================================================
   SHOW STATUS MESSAGE
===================================================== */

function showStatusMessage(
    heading,
    message
) {

    statusResult.style.display =
        "block";

    statusResult.innerHTML = `

        <h3>
            ${heading}
        </h3>

        <p>
            ${message}
        </p>

    `;

}


/* =====================================================
   DISPLAY COMPLAINT STATUS
===================================================== */

function displayComplaintStatus(
    complaint
) {

    statusResult.style.display =
        "block";


    statusResult.innerHTML = `

        <h3>
            Complaint Details
        </h3>


        <p>
            <strong>Complaint ID:</strong>
            ${escapeHTML(complaint.id)}
        </p>


        <p>
            <strong>Mobile Number:</strong>
            ${maskMobile(complaint.mobile)}
        </p>


        <p>
            <strong>Category:</strong>
            ${escapeHTML(complaint.category)}
        </p>


        <p>
            <strong>Title:</strong>
            ${escapeHTML(complaint.title)}
        </p>


        <p>
            <strong>Description:</strong>
            ${escapeHTML(complaint.description)}
        </p>


        <p>
            <strong>Location:</strong>
            ${escapeHTML(complaint.location)}
        </p>


        <p>
            <strong>Registered Date:</strong>
            ${escapeHTML(complaint.date)}
        </p>


        <p>
            <strong>Current Status:</strong>
            <span class="status-badge">
                ${escapeHTML(complaint.status)}
            </span>
        </p>


        ${
            complaint.photo
                ? `

                    <p>
                        <strong>
                            Uploaded Photo:
                        </strong>
                    </p>

                    <img
                        class="track-photo"
                        src="${complaint.photo}"
                        alt="Complaint Photo"
                    >

                  `
                : ""
        }


        ${createStatusTimeline(complaint)}

    `;

}


/* =====================================================
   MASK MOBILE NUMBER
===================================================== */

function maskMobile(mobile) {

    const value =
        String(mobile || "");

    if (value.length !== 10) {

        return "**********";

    }

    return "******" +
        value.slice(-4);

}


/* =====================================================
   CREATE STATUS TIMELINE
===================================================== */

function createStatusTimeline(
    complaint
) {

    const currentIndex =
        VALID_STATUSES.indexOf(
            complaint.status
        );


    let html = `

        <div class="status-timeline">

    `;


    VALID_STATUSES.forEach(
        function (status, index) {

            let className =
                "status-step";


            if (index < currentIndex) {

                className +=
                    " completed";

            }


            if (index === currentIndex) {

                className +=
                    " active";

            }


            let icon = "○";


            if (index < currentIndex) {

                icon = "✓";

            }


            if (index === currentIndex) {

                icon = "●";

            }


            html += `

                <div class="${className}">

                    ${icon}

                    ${escapeHTML(status)}

                </div>

            `;

        }
    );


    html += `

        </div>

    `;


    return html;

}


/* =====================================================
   DISPLAY REGISTERED COMPLAINTS
===================================================== */

function displayRegisteredComplaints() {

    const complaints =
        getComplaints();


    /* ================= EMPTY ================= */

    if (complaints.length === 0) {

        registeredComplaints.innerHTML = `

            <p class="no-complaints">

                No complaints registered yet.

            </p>

        `;

        return;

    }


    registeredComplaints.innerHTML =
        "";


    /* ================= NEWEST FIRST ================= */

    const sortedComplaints =
        [...complaints].reverse();


    sortedComplaints.forEach(
        function (complaint) {

            const card =
                document.createElement(
                    "div"
                );


            card.className =
                "complaint-card";


            card.innerHTML = `

                <h3>

                    🆔
                    ${escapeHTML(
                        complaint.id
                    )}

                </h3>


                <p>

                    <strong>
                        Category:
                    </strong>

                    ${escapeHTML(
                        complaint.category
                    )}

                </p>


                <p>

                    <strong>
                        Title:
                    </strong>

                    ${escapeHTML(
                        complaint.title
                    )}

                </p>


                <p>

                    <strong>
                        Description:
                    </strong>

                    ${escapeHTML(
                        complaint.description
                    )}

                </p>


                <p>

                    <strong>
                        Location:
                    </strong>

                    ${escapeHTML(
                        complaint.location
                    )}

                </p>


                <p>

                    <strong>
                        Registered On:
                    </strong>

                    ${escapeHTML(
                        complaint.date
                    )}

                </p>


                <span class="status-badge">

                    ${escapeHTML(
                        complaint.status
                    )}

                </span>


                ${
                    complaint.photo
                        ? `

                            <div style="margin-top:15px;">

                                <strong>
                                    Uploaded Photo:
                                </strong>

                                <br>

                                <img
                                    class="complaint-photo"
                                    src="${complaint.photo}"
                                    alt="Complaint Photo"
                                >

                            </div>

                          `
                        : ""
                }

            `;


            registeredComplaints
                .appendChild(card);

        }
    );

}


/* =====================================================
   UPDATE COMPLAINT STATUS
   ADMIN FUNCTION

   Example:

   updateComplaintStatus(
       "CMP4821",
       "In Progress"
   );

===================================================== */

function updateComplaintStatus(
    complaintId,
    newStatus
) {

    const id =
        String(complaintId)
            .trim()
            .toUpperCase();


    /* ================= VALIDATE STATUS ================= */

    if (
        !VALID_STATUSES.includes(
            newStatus
        )
    ) {

        console.error(
            "Invalid complaint status."
        );

        return false;

    }


    /* ================= GET DATA ================= */

    const complaints =
        getComplaints();


    const index =
        complaints.findIndex(
            complaint =>
                complaint.id === id
        );


    /* ================= NOT FOUND ================= */

    if (index === -1) {

        console.error(
            "Complaint not found:",
            id
        );

        return false;

    }


    /* ================= UPDATE ================= */

    const date =
        getCurrentDate();


    complaints[index].status =
        newStatus;


    if (
        !Array.isArray(
            complaints[index].statusHistory
        )
    ) {

        complaints[index].statusHistory =
            [];

    }


    complaints[index]
        .statusHistory
        .push({

            status: newStatus,

            date: date

        });


    /* ================= SAVE ================= */

    saveComplaints(
        complaints
    );


    localStorage.setItem(
        id,
        JSON.stringify(
            complaints[index]
        )
    );


    /* ================= REFRESH ================= */

    displayRegisteredComplaints();


    if (
        trackComplaintId.value
            .trim()
            .toUpperCase() === id
    ) {

        displayComplaintStatus(
            complaints[index]
        );

    }


    return true;

}


/* =====================================================
   RESET BUTTON
===================================================== */

complaintForm.addEventListener(
    "reset",
    function () {

        setTimeout(
            function () {

                photoPreview.innerHTML =
                    "";

                statusResult.style.display =
                    "none";

                generateComplaintID();

            },
            0
        );

    }
);


/* =====================================================
   TRACK BUTTON
===================================================== */

trackBtn.addEventListener(
    "click",
    trackComplaint
);


/* =====================================================
   ENTER KEY FOR TRACKING
===================================================== */

trackComplaintId.addEventListener(
    "keydown",
    function (event) {

        if (
            event.key === "Enter"
        ) {

            event.preventDefault();

            trackComplaint();

        }

    }
);


/* =====================================================
   CLEAR ALL COMPLAINTS
   DEVELOPMENT / TESTING ONLY
===================================================== */

function clearAllComplaints() {

    const confirmed =
        confirm(
            "Delete all locally stored complaints?"
        );


    if (!confirmed) {

        return;

    }


    const complaints =
        getComplaints();


    complaints.forEach(
        function (complaint) {

            localStorage.removeItem(
                complaint.id
            );

        }
    );


    localStorage.removeItem(
        STORAGE_KEY
    );


    displayRegisteredComplaints();

    generateComplaintID();

    statusResult.style.display =
        "none";


    alert(
        "All complaints have been deleted."
    );

}


/* =====================================================
   INITIALIZE
===================================================== */

generateComplaintID();

displayRegisteredComplaints();
