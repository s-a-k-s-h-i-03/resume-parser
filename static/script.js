const resumeInput = document.getElementById("resumeFile");
const fileNameSpan = document.getElementById("fileName");

if (resumeInput) {
    resumeInput.addEventListener("change", function () {
        const file = this.files[0];

        if (!file) {
            fileNameSpan.textContent = "No file chosen";
            return;
        }

        const allowedExtensions = ["pdf", "docx"];
        const fileExt = file.name.split(".").pop().toLowerCase();

        if (!allowedExtensions.includes(fileExt)) {
            alert("Invalid file type. Please upload a PDF or DOCX file only.");

            // reset input
            this.value = "";
            fileNameSpan.textContent = "No file chosen";
            return;
        }

        // valid file
        fileNameSpan.textContent = file.name;
    });
}
function openTextModal(text, title) {
    console.log("Modal opened:", title);

    document.getElementById("textModalTitle").innerText = title;
    document.getElementById("textModalBody").innerText =
        text && text.trim() ? text : "No data available";

    document.getElementById("textModal").style.display = "block";
}
document.addEventListener("DOMContentLoaded", function () {
    const closeBtn = document.querySelector(".close");
    const modal = document.getElementById("textModal");

    if (closeBtn && modal) {
        closeBtn.addEventListener("click", function () {
            modal.style.display = "none";
        });
    }
});
