let isRecognizing = false;

function sendMessage() {
    let userInput = document.getElementById("user-input").value.trim();
    if (userInput === "") return;

    let chatBox = document.getElementById("chat-box");

    // Create user message container
    let userMessageContainer = document.createElement("div");
    userMessageContainer.classList.add("message-container", "user-align");

    // User avatar
    let userAvatar = document.createElement("img");
    userAvatar.classList.add("chat-avatar");
    userAvatar.src = "icon-5359553_640.webp";

    // User message bubble
    let userMessage = document.createElement("div");
    userMessage.classList.add("user-message");
    userMessage.textContent = userInput;

    userMessageContainer.appendChild(userMessage);
    userMessageContainer.appendChild(userAvatar);
    chatBox.appendChild(userMessageContainer);

    chatBox.scrollTop = chatBox.scrollHeight;

    // ✅ Send request to FastAPI backend
    fetch("http://127.0.0.1:8000/chat", {
        method: "POST",
        headers: {
            "Content-Type": "application/json"
        },
        body: JSON.stringify({ query: userInput })
    })
    .then(response => response.json())
    .then(data => {
        let botMessageContainer = document.createElement("div");
        botMessageContainer.classList.add("message-container", "bot-align");

        let botAvatar = document.createElement("img");
        botAvatar.classList.add("chat-avatar");
        botAvatar.src = "istockphoto-1221348467-612x612 (1).jpg";

        let botMessage = document.createElement("div");
        botMessage.classList.add("bot-message");

        let formattedResponse = formatBotAnswer(data.response);

        botMessage.innerHTML = `${formattedResponse} <span class="source">(from RAG)</span>`;

        botMessageContainer.appendChild(botAvatar);
        botMessageContainer.appendChild(botMessage);
        chatBox.appendChild(botMessageContainer);

        chatBox.scrollTop = chatBox.scrollHeight;

        // 🔊 Text-to-Speech
        speakBotResponse(data.response);
    })
    .catch(error => {
        console.error("Error:", error);
    });

    // Clear input
    document.getElementById("user-input").value = "";
}

// 🔊 Speak the bot’s response
function speakBotResponse(text) {
    const synth = window.speechSynthesis;
    synth.cancel();
    const utterance = new SpeechSynthesisUtterance(text);
    utterance.lang = "en-IN";
    synth.speak(utterance);
}

function stopSpeaking() {
    const synth = window.speechSynthesis;
    if (synth.speaking || synth.pending) {
        synth.cancel();
    }
}

// 📄 Format bot's long answers with line breaks
function formatBotAnswer(text) {
    if (!text) return "";

    text = text.replace(/</g, "&lt;").replace(/>/g, "&gt;");

    text = text.replace(/(\d+)\.\s+/g, "<br><strong>$1.</strong> ");

    if ((/variet(y|ies)|include|consist/i).test(text) && text.includes(",")) {
        text = text.replace(/(variet(y|ies).*?:)/i, "<br><strong>$1</strong><ul>");
        text = text.replace(/,\s*/g, "</li><li>");
        text = text + "</li></ul>";
        text = text.replace("<ul></li>", "<ul><li>");
    }

    text = text.replace(/(?:^|<br>)[\-•]\s*(.*?)(?=<br>|$)/g, "<br>• $1");

    text = text.replace(/\. (?=[A-Z])/g, ".<br><br>");

    text = text.replace(/(Note:)/gi, "<br><strong>$1</strong>");

    text = text.replace(/(Source:.*?)($|<br>)/gi, "<br><em>$1</em>");

    text = text.replace(/(<br>\s*){2,}/g, "<br><br>");

    return text.trim();
}

// 🎤 Speech-to-Text function
function startDictation() {
    const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
    if (!SpeechRecognition) {
        alert("Speech Recognition not supported in this browser.");
        return;
    }

    const recognition = new SpeechRecognition();
    recognition.lang = "en-IN";
    recognition.interimResults = false;
    recognition.maxAlternatives = 1;

    recognition.onresult = function (event) {
        const speechResult = event.results[0][0].transcript;
        document.getElementById("user-input").value = speechResult;
    };

    recognition.onerror = function (event) {
        console.error("Speech recognition error:", event.error);
    };

    recognition.start();
}

// 🧹 Clear the chat box
function clearChat() {
    document.getElementById("chat-box").innerHTML = "";
    window.speechSynthesis.cancel();
}
