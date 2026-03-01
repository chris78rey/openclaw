const collectionList = document.getElementById("collection-list");
const chatCollections = document.getElementById("chat-collections");
const uploadCollection = document.getElementById("upload-collection");
const modelSelect = document.getElementById("model-select");
const uploadStatus = document.getElementById("upload-status");
const chatStatus = document.getElementById("chat-status");
const messages = document.getElementById("messages");
const sources = document.getElementById("sources");

const selectedCollections = new Set();

function setStatus(node, text) {
  node.textContent = text;
}

function addMessage(role, text) {
  const article = document.createElement("article");
  article.className = `message ${role}`;
  const paragraph = document.createElement("p");
  paragraph.textContent = text;
  article.appendChild(paragraph);
  messages.appendChild(article);
  messages.scrollTop = messages.scrollHeight;
}

function renderCollections(collections) {
  collectionList.innerHTML = "";
  chatCollections.innerHTML = "";
  uploadCollection.innerHTML = "";

  if (!collections.length) {
    collectionList.innerHTML = '<span class="tag">Sin colecciones</span>';
    chatCollections.innerHTML = '<span class="tag">Sube un documento primero</span>';
    return;
  }

  for (const collection of collections) {
    const option = document.createElement("option");
    option.value = collection;
    option.textContent = collection;
    uploadCollection.appendChild(option);

    const summaryTag = document.createElement("span");
    summaryTag.className = "tag";
    summaryTag.textContent = collection;
    collectionList.appendChild(summaryTag);

    const pickerTag = document.createElement("button");
    pickerTag.type = "button";
    pickerTag.className = "tag selectable";
    pickerTag.textContent = collection;
    pickerTag.addEventListener("click", () => {
      if (selectedCollections.has(collection)) {
        selectedCollections.delete(collection);
        pickerTag.classList.remove("active");
      } else {
        selectedCollections.add(collection);
        pickerTag.classList.add("active");
      }
    });
    chatCollections.appendChild(pickerTag);
  }
}

function renderSources(items) {
  sources.innerHTML = "";
  if (!items.length) {
    sources.innerHTML = '<div class="source-card"><p class="source-text">Sin fuentes para mostrar.</p></div>';
    return;
  }

  for (const item of items) {
    const card = document.createElement("article");
    card.className = "source-card";

    const meta = document.createElement("p");
    meta.className = "source-meta";
    meta.textContent = `${item.collection} | ${item.source} | score ${item.score.toFixed(3)}`;

    const text = document.createElement("p");
    text.className = "source-text";
    text.textContent = item.text;

    card.append(meta, text);
    sources.appendChild(card);
  }
}

async function loadCollections() {
  const response = await fetch("/api/collections");
  const payload = await response.json();
  renderCollections(payload.collections || []);
}

async function loadModels() {
  const response = await fetch("/api/models");
  const payload = await response.json();
  modelSelect.innerHTML = "";

  for (const model of payload.models || []) {
    const option = document.createElement("option");
    option.value = model;
    option.textContent = model;
    if (model === payload.default) {
      option.selected = true;
    }
    modelSelect.appendChild(option);
  }
}

document.getElementById("collection-form").addEventListener("submit", async (event) => {
  event.preventDefault();
  const input = document.getElementById("collection-name");
  const name = input.value.trim();
  if (!name) return;

  setStatus(uploadStatus, "Creando...");
  const response = await fetch("/api/collections", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ name }),
  });

  if (!response.ok) {
    setStatus(uploadStatus, "Error");
    return;
  }

  input.value = "";
  await loadCollections();
  setStatus(uploadStatus, "Coleccion creada");
});

document.getElementById("upload-form").addEventListener("submit", async (event) => {
  event.preventDefault();
  const fileInput = document.getElementById("upload-file");
  const file = fileInput.files[0];
  const collection = uploadCollection.value;
  if (!file || !collection) return;

  const formData = new FormData();
  formData.append("collection", collection);
  formData.append("file", file);

  setStatus(uploadStatus, "Subiendo...");
  const response = await fetch("/api/upload", {
    method: "POST",
    body: formData,
  });

  const payload = await response.json();
  if (!response.ok) {
    setStatus(uploadStatus, payload.detail || "Error");
    return;
  }

  fileInput.value = "";
  setStatus(uploadStatus, `Listo: ${payload.chunks} fragmentos`);
  await loadCollections();
});

document.getElementById("chat-form").addEventListener("submit", async (event) => {
  event.preventDefault();
  const input = document.getElementById("chat-input");
  const question = input.value.trim();
  if (!question) return;

  addMessage("user", question);
  input.value = "";
  setStatus(chatStatus, "Consultando...");

  const response = await fetch("/api/chat", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({
      question,
      collections: Array.from(selectedCollections),
      model: modelSelect.value || null,
    }),
  });

  const payload = await response.json();
  if (!response.ok) {
    addMessage("assistant", payload.detail || "No pude responder.");
    setStatus(chatStatus, "Error");
    return;
  }

  addMessage("assistant", payload.answer);
  renderSources(payload.sources || []);
  setStatus(chatStatus, "Listo");
});

Promise.all([loadCollections(), loadModels()]).catch(() => {
  setStatus(chatStatus, "Error");
  setStatus(uploadStatus, "Error");
});
