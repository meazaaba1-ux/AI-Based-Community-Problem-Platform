
const API_URL = "http://127.0.0.1:8000";

const form = document.getElementById("reportForm");
const message = document.getElementById("message");
const submitBtn = document.getElementById("submitBtn");

const imageInput = document.getElementById("image");

function showMessage(text, color = "red") {
    message.textContent = text;
    message.style.color = color;
}

// Submit report
form.addEventListener("submit", async (event) => {
    event.preventDefault();
    showMessage("");

    const title = document.getElementById("title").value.trim();
    const description =
        document.getElementById("description").value.trim();
    const location =
        document.getElementById("location").value.trim();
    const image = imageInput.files[0];

    if (!title || !description || !location) {
        showMessage("Please complete all required fields.");
        return;
    }

    // Validate image
    if (image) {
        const allowedTypes = [
            "image/jpeg",
            "image/png",
            "image/webp"
        ];

        if (!allowedTypes.includes(image.type)) {
            showMessage("Choose a JPG, PNG, or WEBP image.");
            return;
        }

        if (image.size > 5 * 1024 * 1024) {
            showMessage("The image must be 5 MB or smaller.");
            return;
        }
    }

    // Prepare report data without GPS coordinates
    const formData = new FormData();

    
const userId = localStorage.getItem("user_id");

if (!userId) {
    alert("Please login first.");
    window.location.href = "login.html";
    return;
}

formData.append("user_id", userId);



    formData.append("title", title);
    formData.append("description", description);
    formData.append("location", location);

    if (image) {
        formData.append("image", image);
    }

    submitBtn.disabled = true;
    submitBtn.textContent = "Submitting...";

    try {
        const response = await fetch(`${API_URL}/problems`, {
            method: "POST",
            body: formData
        });

        const responseText = await response.text();
        let data;

        try {
            data = JSON.parse(responseText);
        } catch {
            data = { detail: responseText };
        }

        console.log("POST /problems:", response.status, data);

        if (!response.ok) {
            const detail = data.detail;

            const errorText = Array.isArray(detail)
                ? detail.map(item => item.msg).join("; ")
                : detail || `Request failed: HTTP ${response.status}`;

            throw new Error(errorText);
        }

        showMessage(
    `Problem reported successfully! Report ID: ${data.id}`,
    "green"
);

message.style.display = "block";
message.style.padding = "10px";
message.style.marginTop = "15px";



form.reset();
    } catch (error) {
        console.error("Report submission error:", error);
        showMessage(
            error.message || "Unable to connect to the server."
        );
    } finally {
        submitBtn.disabled = false;
        submitBtn.textContent = "Submit Report";
    }
});
