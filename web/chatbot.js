document.addEventListener("DOMContentLoaded", () => {
  const icon = document.getElementById("chatbot-icon");
  const box = document.getElementById("chatbot-box");
  const sendBtn = document.getElementById("chat-send");
  const input = document.getElementById("chat-input");
  const chatContent = document.getElementById("chat-content");

  // Toggle chat window
  icon.addEventListener("click", () => {
    box.classList.toggle("hidden");
  });

  // Send message
  sendBtn.addEventListener("click", sendMessage);
  input.addEventListener("keypress", (e) => {
    if (e.key === "Enter") sendMessage();
  });

  async function sendMessage() {
    
    const userMsg = input.value.trim();
    // print(userMsg);
    if (!userMsg) return;

    addMessage("You", userMsg);
    input.value = "";

    try {
      const res = await fetch("http://127.0.0.1:5000/api/ask", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ question: userMsg })
      });

      const data = await res.json();
      const reply = data.answer || "Sorry, I couldn’t find an answer.";
      addMessage("Bot", reply);
    } catch (err) {
      addMessage("System", "Error connecting to chatbot.");
      console.error(err);
    }
  }

  function addMessage(sender, text) {
    const msg = document.createElement("div");
    msg.classList.add("msg");
    msg.innerHTML = `<b>${sender}:</b> ${text}`;
    chatContent.appendChild(msg);
    chatContent.scrollTop = chatContent.scrollHeight;
  }
});
