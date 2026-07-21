const log = document.getElementById("chat-log");
const form = document.getElementById("chat-form");
const input = document.getElementById("chat-input");

function appendMessage(role, content) {
  const el = document.createElement("div");
  el.className = `chat-msg ${role}`;
  el.textContent = content;
  log.appendChild(el);
  log.scrollTop = log.scrollHeight;
}

async function loadHistory() {
  const res = await fetch("/chat/history");
  const messages = await res.json();
  log.innerHTML = "";
  messages.forEach((m) => appendMessage(m.role, m.content));
}

form.addEventListener("submit", async (e) => {
  e.preventDefault();
  const message = input.value.trim();
  if (!message) return;
  appendMessage("user", message);
  input.value = "";
  try {
    const res = await fetch("/chat", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ message }),
    });
    if (!res.ok) {
      const err = await res.json();
      appendMessage("assistant", `Error: ${err.detail || res.statusText}`);
      return;
    }
    const data = await res.json();
    appendMessage("assistant", data.reply);
  } catch (err) {
    appendMessage("assistant", `Error: ${err.message}`);
  }
});

document.getElementById("sync-btn").addEventListener("click", async () => {
  const btn = document.getElementById("sync-btn");
  btn.disabled = true;
  btn.textContent = "Syncing...";
  try {
    const res = await fetch("/plaid/sync", { method: "POST" });
    if (res.ok) {
      location.reload();
    } else {
      const err = await res.json();
      alert(err.detail || "Sync failed");
    }
  } finally {
    btn.disabled = false;
    btn.textContent = "Sync bank";
  }
});

loadHistory();
