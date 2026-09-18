const BASE_URL = "http://127.0.0.1:8000";


function formatResponse(text) {
  return text
    .replace(/\*\*(.*?)\*\*/g, "<b>$1</b>")
    .replace(/\n/g, "<br>");
}


function addMessage(text, type) {

  const chatBox = document.getElementById("chatBox");

  const msg = document.createElement("div");
  msg.className = "message " + type;

  const avatar = document.createElement("div");

  avatar.className =
    "avatar " +
    (type === "user" ? "user-avatar" : "bot-avatar");

  avatar.innerHTML =
    type === "user"
      ? '<i class="fa-solid fa-user"></i>'
      : '<i class="fa-solid fa-robot"></i>';

  const bubble = document.createElement("div");

  bubble.className = "bubble";

  bubble.innerHTML = formatResponse(text);

  msg.appendChild(avatar);
  msg.appendChild(bubble);

  chatBox.appendChild(msg);

  chatBox.scrollTop = chatBox.scrollHeight;

  return bubble;
}


async function uploadFile() {

  const fileInput = document.getElementById("fileInput");
  const uploadStatus = document.getElementById("uploadStatus");

  const file = fileInput.files[0];

  if (!file) {

    uploadStatus.className = "status error";

    uploadStatus.innerHTML =
      '<i class="fa-solid fa-circle-xmark"></i> Please select a file first.';

    return;
  }

  const formData = new FormData();

  formData.append("file", file);

  uploadStatus.className = "status";

  uploadStatus.innerHTML =
    '<i class="fa-solid fa-spinner fa-spin"></i> Uploading document...';

  try {

    console.log("BASE_URL =", BASE_URL);
    console.log("About to fetch...");

    const res = await fetch(BASE_URL + "/upload-doc", {
      method: "POST",
      body: formData
    });

    console.log("Response Status:", res.status);

    const data = await res.json();

    console.log("Response:", data);

    if (!res.ok || data.error) {

      uploadStatus.className = "status error";

      uploadStatus.innerHTML =
        '<i class="fa-solid fa-circle-xmark"></i> Upload failed.';

      return;
    }

    uploadStatus.className = "status success";

    uploadStatus.innerHTML =
      '<i class="fa-solid fa-circle-check"></i> Document uploaded successfully.';

    addMessage(
      "Document uploaded successfully. Now you can ask questions from it.",
      "bot"
    );

  } catch (error) {

    console.error(error);

    uploadStatus.className = "status error";

    uploadStatus.innerHTML =
      '<i class="fa-solid fa-circle-xmark"></i> Backend connection failed.';
  }
}


async function askQuestion() {

  const input = document.getElementById("questionInput");

  const question = input.value.trim();

  if (!question) return;

  addMessage(question, "user");

  input.value = "";

  const loadingBubble = addMessage("Thinking...", "bot");

  try {

    const res = await fetch(BASE_URL + "/ask", {

      method: "POST",

      headers: {
        "Content-Type": "application/json"
      },

      body: JSON.stringify({
        question: question
      })
    });

    const data = await res.json();

    if (data.answer) {

      loadingBubble.innerHTML =
        formatResponse(data.answer);

    } else if (data.error) {

      loadingBubble.innerHTML =
        formatResponse(data.error);

    } else {

      loadingBubble.innerHTML =
        "No response from backend.";
    }

  } catch (error) {

    console.log(error);

    loadingBubble.innerHTML =
      "Unable to connect with backend.";
  }
}


function handleEnter(event) {

  if (event.key === "Enter") {
    askQuestion();
  }
}