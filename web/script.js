// ===============================
// Global Config
// ===============================
const CONFIG = {
  powerBIEmbedUrl: "https://app.powerbi.com/view?r=YOUR_EMBED_LINK_HERE", // <-- Paste your Power BI embed URL
  apiBase: "" // leave empty to use same server (http://localhost:5000)
};

// ===============================
// Navbar Items
// ===============================
const NAV_ITEMS = [
  { text: "Home", href: "index.html" },
  { text: "About Us", href: "about.html" },
  { text: "Experiments", href: "experiments.html" },
  { text: "Dashboard", href: "dashboard.html" }
];

function isActive(href){
  const path = location.pathname.split("/").pop();
  return path === href || (path === "" && href === "index.html");
}

function renderNav(){
  const navContainer = document.getElementById("navbar-placeholder");
  if(!navContainer) return;

  const itemsHTML = NAV_ITEMS.map(item => {
    const active = isActive(item.href) ? 'aria-current="page" class="active"' : "";
    return `<li><a href="${item.href}" ${active}>${item.text}</a></li>`;
  }).join("");

  navContainer.innerHTML = `
    <nav class="nav" role="navigation">
      <div class="nav-inner container">
        <a class="brand" href="index.html">NASA Bioscience</a>
        <button id="nav-toggle" class="nav-toggle" aria-expanded="false" aria-controls="nav-links">
          <span class="sr-only">Toggle menu</span>
          <span class="hamburger" aria-hidden="true"></span>
        </button>
        <ul id="nav-links" class="nav-links">
          ${itemsHTML}
        </ul>
      </div>
    </nav>
  `;

  // Mobile toggle
  const toggle = document.getElementById("nav-toggle");
  const navLinks = document.getElementById("nav-links");
  if(toggle && navLinks){
    toggle.addEventListener("click", () => {
      const open = navLinks.classList.toggle("open");
      toggle.setAttribute("aria-expanded", open);
    });
  }
}

// ===============================
// Helpers
// ===============================
function api(path) {
  if (CONFIG.apiBase && CONFIG.apiBase.length) {
    return CONFIG.apiBase + path;
  }
  return path; // relative
}

function escapeHtml(s){ 
  return (s||'')
    .replace(/&/g,'&amp;')
    .replace(/</g,'&lt;')
    .replace(/>/g,'&gt;'); 
}

// ===============================
// Chatbot Functions
// ===============================
async function askServer(){
  const qEl = document.getElementById('userInput');
  if(!qEl) return; // not on dashboard
  const q = qEl.value.trim();
  if(!q) return;
  appendChatMessage('You', q);
  qEl.value = '';
  try {
    const res = await fetch(api('/api/ask'), {
      method: 'POST',
      headers: {'Content-Type':'application/json'},
      body: JSON.stringify({ question: q })
    });
    const data = await res.json();
    appendChatMessage('Bot', data.answer, data.sources);
  } catch(err) {
    appendChatMessage('System', 'Error: ' + err.message);
  }
}

function appendChatMessage(who, text, sources){
  const chat = document.getElementById('chat');
  if(!chat) return;
  const container = document.createElement('div');
  container.style.padding = '8px 0';
  container.innerHTML = `<div style="font-weight:600">${who}:</div>
                         <pre style="white-space:pre-wrap;margin:6px 0">${escapeHtml(text)}</pre>`;
  if (sources && sources.length) {
    const srcHtml = sources.map(s => {
      const url = s.url ? ` <a href="${s.url}" target="_blank">[pdf]</a>` : '';
      return `<div style="font-size:13px">• <b>${s.id}</b> — ${escapeHtml(s.title)} ${url}</div>`;
    }).join('');
    const srcDiv = document.createElement('div');
    srcDiv.style.marginTop = '6px';
    srcDiv.innerHTML = `<div style="font-weight:600">Sources:</div>${srcHtml}`;
    container.appendChild(srcDiv);
  }
  chat.appendChild(container);
  chat.scrollTop = chat.scrollHeight;
}

// ===============================
// Search Functions
// ===============================
async function doSearch(){
  const qEl = document.getElementById('searchInput');
  if(!qEl) return; // not on dashboard
  const q = qEl.value.trim();
  if (!q) return;
  const resultsDiv = document.getElementById('searchResults');
  resultsDiv.innerHTML = 'Searching...';
  try {
    const res = await fetch(api('/api/search?q=' + encodeURIComponent(q)));
    const data = await res.json();
    if (!data.results || data.results.length === 0) {
      resultsDiv.innerHTML = 'No results found.';
      return;
    }
    const html = data.results.map(r => {
      return `<div style="padding:8px;border-bottom:1px solid #eee">
        <div style="font-weight:700">${escapeHtml(r.title)} 
            <span style="color:#666;font-weight:400">(${r.year || ''})</span></div>
        <div style="font-size:13px;margin-top:6px">
            ${escapeHtml((r.abstract||'').slice(0,200))}
            ${(r.abstract||'').length > 200 ? '...' : '' }
        </div>
        <div style="margin-top:6px">
          <a href="${r.pdf_url || '#'}" target="_blank">Open PDF</a>
        </div>
      </div>`;
    }).join('');
    resultsDiv.innerHTML = html;
  } catch (err) {
    resultsDiv.innerHTML = 'Error: ' + err.message;
  }
}

// ===============================
// Graph Functions
// ===============================
async function drawGraph(){
  const container = document.getElementById('graph');
  if(!container) return; // not on dashboard
  container.innerHTML = 'Loading graph...';
  try {
    const res = await fetch(api('/api/graph'));
    const data = await res.json();
    container.innerHTML = '';
    const nodes = new vis.DataSet(data.nodes.map(n => ({ 
      id: n.id, 
      label: n.label, 
      title: n.title || n.label, 
      group: n.group 
    })));
    const edges = new vis.DataSet(data.edges.map(e => ({ from: e.from, to: e.to })));
    const network = new vis.Network(container, { nodes, edges }, {
      nodes: { shape: 'dot', size: 16, font: { size: 14 } },
      edges: { arrows: { to: false } },
      physics: { stabilization: false, barnesHut: { gravitationalConstant: -800 } },
      interaction: { hover: true, tooltipDelay: 100 }
    });
    network.on("click", params => {
      if (params.nodes && params.nodes.length === 1) {
        const nodeId = params.nodes[0];
        const node = nodes.get(nodeId);
        appendChatMessage('Graph', `Clicked node: ${node.label}`);
      }
    });
  } catch(err) {
    container.innerHTML = 'Graph load error: ' + err.message;
  }
}

// ===============================
// DOM Ready
// ===============================
document.addEventListener("DOMContentLoaded", () => {
  renderNav();

  // Footer year
  const yearEl = document.getElementById("year");
  if(yearEl) yearEl.textContent = new Date().getFullYear();

  // Set Power BI iframe if exists
  const pbIframe = document.getElementById("powerbi-embed");
  if(pbIframe && CONFIG.powerBIEmbedUrl){
    pbIframe.src = CONFIG.powerBIEmbedUrl;
  }

  // If dashboard page → init graph
  if (document.getElementById('graph')) {
    drawGraph();
  }
});

// async function sendMessage() {
//   const userInput = document.getElementById("chat-input").value.trim();
//   if (!userInput) return;

//   // Display user message
//   addMessage("user", userInput);

//   // Send to Flask backend
//   try {
//     const response = await fetch("http://127.0.0.1:5000/ask", {
//       method: "POST",
//       headers: { "Content-Type": "application/json" },
//       body: JSON.stringify({ query: userInput })
//     });

//     const data = await response.json();
//     const botReply = data.answer || "Sorry, I couldn’t find an answer.";

//     // Display bot reply
//     addMessage("bot", botReply);
//   } catch (error) {
//     addMessage("bot", "Error connecting to chatbot server.");
//     console.error("Chatbot error:", error);
//   }

//   document.getElementById("chat-input").value = "";
// }

// function addMessage(sender, text) {
//   const chatBox = document.getElementById("chat-box");
//   const msgDiv = document.createElement("div");
//   msgDiv.classList.add(sender === "user" ? "user-msg" : "bot-msg");
//   msgDiv.textContent = text;
//   chatBox.appendChild(msgDiv);
//   chatBox.scrollTop = chatBox.scrollHeight;
// }

