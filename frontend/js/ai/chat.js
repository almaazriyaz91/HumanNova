/**
 * HumanNova — OctSem AI Learning Assistant
 * Handles context-aware anatomical inquiries, session-only chat history, and rich markdown rendering.
 */

window.OctSemChat = (function() {
  let sidebarEl, toggleTabEl, messagesContainer, chatInput, sendBtn;
  let contextBannerEl, contextTextEl, clearContextBtn;
  let activeContext = null;
  const sessionId = "session_" + Math.random().toString(36).substring(2, 9);
  
  // Base API URL (fallback to origin or local 8000)
  const API_BASE = window.location.origin.includes(":8000") || window.location.origin.includes(":5500")
    ? window.location.origin
    : "http://localhost:8000";

  function init() {
    sidebarEl = document.getElementById("atlas-ai-sidebar");
    toggleTabEl = document.getElementById("sidebar-toggle-tab");
    messagesContainer = document.getElementById("ai-messages-scroll");
    chatInput = document.getElementById("chat-input-field");
    sendBtn = document.getElementById("chat-send-btn");
    
    contextBannerEl = document.getElementById("ai-context-banner");
    contextTextEl = document.getElementById("ai-context-text");
    clearContextBtn = document.getElementById("clear-context-btn");

    if (!sidebarEl) return;

    // Toggle sidebar collapse
    if (toggleTabEl) {
      toggleTabEl.addEventListener("click", () => {
        sidebarEl.classList.toggle("collapsed");
      });
    }

    // Clear context
    if (clearContextBtn) {
      clearContextBtn.addEventListener("click", clearContext);
    }

    // Input submission
    const form = document.getElementById("ai-input-form");
    if (form) {
      form.addEventListener("submit", (e) => {
        e.preventDefault();
        sendMessage();
      });
    }

    // Quick suggestion pills
    const pills = document.querySelectorAll(".suggestion-pill");
    pills.forEach(pill => {
      pill.addEventListener("click", () => {
        const query = pill.dataset.prompt || pill.textContent;
        promptQuickQuestion(query);
      });
    });

    // Add initial greeting
    addMessage("ai", 
      "👋 Hello! I am **OctSem AI**, your anatomical study assistant.\n\n" +
      "Click any structure on the **3D Atlas** to load its context, then ask me about its origin, insertion, physiology, or clinical relevance."
    );
  }

  function setActiveContext(structure) {
    if (!structure) {
      clearContext();
      return;
    }

    activeContext = {
      structure_id: structure.id,
      structure_name: structure.name,
      system: structure.system,
      model_type: AtlasModelLoader ? AtlasModelLoader.getCurrentGender() : "male"
    };

    if (contextTextEl) {
      contextTextEl.innerHTML = `<i class="fa-solid fa-crosshairs"></i> ${structure.name} <small>(${structure.system})</small>`;
    }
    if (contextBannerEl) {
      contextBannerEl.style.display = "flex";
    }
  }

  function clearContext() {
    activeContext = null;
    if (contextBannerEl) {
      contextBannerEl.style.display = "none";
    }
  }

  function openSidebar() {
    if (sidebarEl && sidebarEl.classList.contains("collapsed")) {
      sidebarEl.classList.remove("collapsed");
    }
  }

  function promptQuickQuestion(text) {
    openSidebar();
    if (chatInput) {
      chatInput.value = text;
      sendMessage();
    }
  }

  async function sendMessage() {
    const text = chatInput.value.trim();
    if (!text) return;

    // 1. Add user message
    addMessage("user", text);
    chatInput.value = "";

    // 2. Add loading bubble
    const loadingId = "loading_" + Date.now();
    addLoadingMessage(loadingId);

    try {
      const resp = await fetch(`${API_BASE}/api/chat`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          message: text,
          context: activeContext,
          session_id: sessionId
        })
      });

      removeLoadingMessage(loadingId);

      if (resp.ok) {
        const data = await resp.json();
        addMessage("ai", data.answer);
      } else {
        // Fallback local response
        const fallbackText = generateLocalFallback(text, activeContext);
        addMessage("ai", fallbackText);
      }
    } catch (err) {
      console.warn("[OctSemChat] Server fetch error. Generating local anatomical response.", err);
      removeLoadingMessage(loadingId);
      const fallbackText = generateLocalFallback(text, activeContext);
      addMessage("ai", fallbackText);
    }
  }

  function addMessage(sender, rawText) {
    if (!messagesContainer) return;
    const bubble = document.createElement("div");
    bubble.className = `chat-bubble chat-bubble-${sender}`;
    bubble.innerHTML = formatMarkdown(rawText);
    messagesContainer.appendChild(bubble);
    messagesContainer.scrollTop = messagesContainer.scrollHeight;
  }

  function addLoadingMessage(id) {
    if (!messagesContainer) return;
    const bubble = document.createElement("div");
    bubble.id = id;
    bubble.className = "chat-bubble chat-bubble-ai";
    bubble.innerHTML = `<span style="display: flex; align-items: center; gap: 8px;"><div class="spinner" style="width: 14px; height: 14px; border-width: 2px;"></div> OctSem AI is analyzing anatomical context...</span>`;
    messagesContainer.appendChild(bubble);
    messagesContainer.scrollTop = messagesContainer.scrollHeight;
  }

  function removeLoadingMessage(id) {
    const el = document.getElementById(id);
    if (el) el.remove();
  }

  function formatMarkdown(text) {
    if (!text) return "";
    let html = text
      .replace(/### (.*?)\n/g, '<h3>$1</h3>')
      .replace(/#### (.*?)\n/g, '<h4>$1</h4>')
      .replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>')
      .replace(/\*(.*?)\*/g, '<em>$1</em>')
      .replace(/> (.*?)\n/g, '<blockquote>$1</blockquote>')
      .replace(/\n\n/g, '<br><br>')
      .replace(/\n/g, '<br>');
    return html;
  }

  function generateLocalFallback(question, context) {
    if (context && context.structure_id) {
      const s = window.HumanNovaAnatomy.structures[context.structure_id];
      if (s) {
        return (
          `### 🩺 **${s.name}** (${s.system})\n\n` +
          `**Inquiry:** *"${question}"*\n\n` +
          `#### 📍 **Position & Landmarks**\n${s.location || "Standard anatomical location."}\n\n` +
          `#### ⚙️ **Function**\n${s.function || "Supports systemic physiological balance."}\n\n` +
          `#### 💡 **Clinical Notes**\n${s.clinical_notes || "Clinical pathology available in course curriculum."}\n\n` +
          `> *Tip: Rotate the 3D model or toggle adjacent layers to examine anatomical relationships.*`
        );
      }
    }
    return (
      `### 🧠 **OctSem AI Anatomy Guide**\n\n` +
      `**Question:** *"${question}"*\n\n` +
      `To receive specific anatomical guidance, select an organ, muscle, vein, or bone on the 3D canvas.`
    );
  }

  return {
    init,
    setActiveContext,
    clearContext,
    openSidebar,
    promptQuickQuestion
  };
})();
