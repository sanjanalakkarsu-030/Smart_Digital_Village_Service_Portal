/* =====================================================
   ADMIN COMPLAINT MANAGEMENT
===================================================== */


let complaints = [];

let selectedComplaint = null;


/* =====================================================
   LOAD COMPLAINTS
===================================================== */

async function loadComplaints() {

    const tableBody =
        document.getElementById(
            "complaintTableBody"
        );


    tableBody.innerHTML = `

        <tr>

            <td
                colspan="7"
                class="loading"
            >
                Loading complaints...
            </td>

        </tr>

    `;


    try {

        const response =
            await fetch(
                "/api/admin/complaints"
            );


        const data =
            await response.json();


        if (!data.success) {

            throw new Error(
                data.message
            );

        }


        complaints =
            data.complaints || [];


        updateStatistics();

        displayComplaints(
            complaints
        );


    }

    catch (error) {

        console.error(error);


        tableBody.innerHTML = `

            <tr>

                <td
                    colspan="7"
                    class="empty"
                >
                    Unable to load complaints.
                </td>

            </tr>

        `;

    }

}


/* =====================================================
   DISPLAY COMPLAINTS
===================================================== */

function displayComplaints(
    complaintList
) {

    const tableBody =
        document.getElementById(
            "complaintTableBody"
        );


    const count =
        document.getElementById(
            "complaintCount"
        );


    count.textContent =
        `${complaintList.length} complaint${
            complaintList.length !== 1
                ? "s"
                : ""
        }`;


    if (
        complaintList.length === 0
    ) {

        tableBody.innerHTML = `

            <tr>

                <td
                    colspan="7"
                    class="empty"
                >
                    No complaints found.
                </td>

            </tr>

        `;

        return;

    }


    tableBody.innerHTML = "";


    complaintList.forEach(
        function (complaint) {


            const row =
                document.createElement(
                    "tr"
                );


            row.innerHTML = `

                <td>

                    <strong>
                        ${escapeHTML(
                            complaint.complaint_id
                        )}
                    </strong>

                </td>


                <td>
                    ${escapeHTML(
                        complaint.category
                    )}
                </td>


                <td>
                    ${escapeHTML(
                        complaint.title
                    )}
                </td>


                <td>
                    ${escapeHTML(
                        complaint.location
                    )}
                </td>


                <td>
                    ${formatDate(
                        complaint.complaint_date
                    )}
                </td>


                <td>

                    ${getStatusBadge(
                        complaint.status
                    )}

                </td>


                <td>

                    <button
                        class="view-btn"
                        onclick="openComplaint(
                            '${escapeAttribute(
                                complaint.complaint_id
                            )}'
                        )"
                    >
                        View / Update
                    </button>

                </td>

            `;


            tableBody.appendChild(row);

        }
    );

}


/* =====================================================
   STATISTICS
===================================================== */

function updateStatistics() {

    document.getElementById(
        "totalComplaints"
    ).textContent =
        complaints.length;


    document.getElementById(
        "registeredComplaints"
    ).textContent =
        complaints.filter(
            c => c.status === "Registered"
        ).length;


    document.getElementById(
        "underReviewComplaints"
    ).textContent =
        complaints.filter(
            c => c.status === "Under Review"
        ).length;


    document.getElementById(
        "inProgressComplaints"
    ).textContent =
        complaints.filter(
            c => c.status === "In Progress"
        ).length;


    document.getElementById(
        "resolvedComplaints"
    ).textContent =
        complaints.filter(
            c => c.status === "Resolved"
        ).length;

}


/* =====================================================
   FILTER
===================================================== */

function filterComplaints() {

    const search =
        document.getElementById(
            "searchInput"
        ).value
            .trim()
            .toLowerCase();


    const status =
        document.getElementById(
            "statusFilter"
        ).value;


    const filtered =
        complaints.filter(
            function (complaint) {


                const matchesSearch =

                    complaint.complaint_id
                        .toLowerCase()
                        .includes(search)

                    ||

                    complaint.title
                        .toLowerCase()
                        .includes(search)

                    ||

                    complaint.location
                        .toLowerCase()
                        .includes(search);


                const matchesStatus =

                    status === "All"

                    ||

                    complaint.status === status;


                return (
                    matchesSearch &&
                    matchesStatus
                );

            }
        );


    displayComplaints(
        filtered
    );

}


/* =====================================================
   OPEN COMPLAINT
===================================================== */

function openComplaint(
    complaintId
) {

    selectedComplaint =
        complaints.find(
            function (complaint) {

                return (
                    complaint.complaint_id ===
                    complaintId
                );

            }
        );


    if (!selectedComplaint) {

        alert(
            "Complaint not found."
        );

        return;

    }


    const details =
        document.getElementById(
            "complaintDetails"
        );


    details.innerHTML = `

        <div class="detail-row">

            <div class="detail-label">
                Complaint ID
            </div>

            <div class="detail-value">
                ${escapeHTML(
                    selectedComplaint.complaint_id
                )}
            </div>

        </div>


        <div class="detail-row">

            <div class="detail-label">
                Mobile Number
            </div>

            <div class="detail-value">
                ${escapeHTML(
                    selectedComplaint.mobile
                )}
            </div>

        </div>


        <div class="detail-row">

            <div class="detail-label">
                Category
            </div>

            <div class="detail-value">
                ${escapeHTML(
                    selectedComplaint.category
                )}
            </div>

        </div>


        <div class="detail-row">

            <div class="detail-label">
                Complaint Title
            </div>

            <div class="detail-value">
                ${escapeHTML(
                    selectedComplaint.title
                )}
            </div>

        </div>


        <div class="detail-row">

            <div class="detail-label">
                Description
            </div>

            <div class="detail-value">
                ${escapeHTML(
                    selectedComplaint.description
                )}
            </div>

        </div>


        <div class="detail-row">

            <div class="detail-label">
                Location
            </div>

            <div class="detail-value">
                ${escapeHTML(
                    selectedComplaint.location
                )}
            </div>

        </div>


        <div class="detail-row">

            <div class="detail-label">
                Registered Date
            </div>

            <div class="detail-value">
                ${formatDate(
                    selectedComplaint.complaint_date
                )}
            </div>

        </div>


        <div class="detail-row">

            <div class="detail-label">
                Current Status
            </div>

            <div class="detail-value">

                ${getStatusBadge(
                    selectedComplaint.status
                )}

            </div>

        </div>


        ${
            selectedComplaint.image_path

                ? `

                    <div class="detail-row">

                        <div class="detail-label">
                            Complaint Photo
                        </div>

                        <div class="detail-value">

                            <img
                                src="${escapeAttribute(
                                    selectedComplaint.image_path
                                )}"
                                class="complaint-image"
                                alt="Complaint Photo"
                            >

                        </div>

                    </div>

                `

                : ""

        }


        <div class="status-update-box">

            <h3>
                Update Complaint Status
            </h3>


            <select
                id="newStatus"
            >

                <option value="Registered">
                    Registered
                </option>

                <option value="Under Review">
                    Under Review
                </option>

                <option value="In Progress">
                    In Progress
                </option>

                <option value="Resolved">
                    Resolved
                </option>

            </select>


            <button
                class="update-btn"
                onclick="updateStatus()"
            >
                Update Status
            </button>

        </div>

    `;


    document.getElementById(
        "newStatus"
    ).value =
        selectedComplaint.status;


    document.getElementById(
        "complaintModal"
    ).style.display =
        "block";

}


/* =====================================================
   UPDATE STATUS
===================================================== */

async function updateStatus() {

    if (!selectedComplaint) {

        return;

    }


    const newStatus =
        document.getElementById(
            "newStatus"
        ).value;


    if (
        newStatus ===
        selectedComplaint.status
    ) {

        alert(
            "Please select a different status."
        );

        return;

    }


    try {

        const response =
            await fetch(
                `/api/admin/complaints/${
                    encodeURIComponent(
                        selectedComplaint.complaint_id
                    )
                }/status`,
                {

                    method: "PUT",

                    headers: {
                        "Content-Type":
                            "application/json"
                    },

                    body: JSON.stringify({

                        status: newStatus

                    })

                }
            );


        const data =
            await response.json();


        if (!data.success) {

            alert(
                data.message ||
                "Unable to update status."
            );

            return;

        }


        alert(
            "Complaint status updated successfully."
        );


        closeModal();


        await loadComplaints();


    }

    catch (error) {

        console.error(error);

        alert(
            "Server error. Please try again."
        );

    }

}


/* =====================================================
   CLOSE MODAL
===================================================== */

function closeModal() {

    document.getElementById(
        "complaintModal"
    ).style.display =
        "none";

    selectedComplaint = null;

}


/* =====================================================
   STATUS BADGE
===================================================== */

function getStatusBadge(
    status
) {

    let className =
        "status-registered";


    if (
        status === "Under Review"
    ) {

        className =
            "status-review";

    }

    else if (
        status === "In Progress"
    ) {

        className =
            "status-progress";

    }

    else if (
        status === "Resolved"
    ) {

        className =
            "status-resolved";

    }


    return `

        <span
            class="status-badge ${className}"
        >
            ${escapeHTML(status)}
        </span>

    `;

}


/* =====================================================
   FORMAT DATE
===================================================== */

function formatDate(
    date
) {

    if (!date) {

        return "-";

    }


    const d =
        new Date(date);


    if (
        isNaN(d.getTime())
    ) {

        return escapeHTML(
            String(date)
        );

    }


    return d.toLocaleString(
        "en-IN",
        {
            dateStyle: "medium",
            timeStyle: "short"
        }
    );

}


/* =====================================================
   ESCAPE HTML
===================================================== */

function escapeHTML(
    value
) {

    return String(
        value ?? ""
    )

        .replace(
            /&/g,
            "&amp;"
        )

        .replace(
            /</g,
            "&lt;"
        )

        .replace(
            />/g,
            "&gt;"
        )

        .replace(
            /"/g,
            "&quot;"
        )

        .replace(
            /'/g,
            "&#039;"
        );

}


/* =====================================================
   ESCAPE ATTRIBUTE
===================================================== */

function escapeAttribute(
    value
) {

    return escapeHTML(value);

}


/* =====================================================
   CLOSE MODAL WHEN CLICKING OUTSIDE
===================================================== */

window.addEventListener(
    "click",
    function (event) {

        const modal =
            document.getElementById(
                "complaintModal"
            );


        if (
            event.target === modal
        ) {

            closeModal();

        }

    }
);


/* =====================================================
   INITIALIZE
===================================================== */

document.addEventListener(
    "DOMContentLoaded",
    function () {

        loadComplaints();

    }
);