const API_URL = "http://127.0.0.1:8000";

// =====================================
// Helper Function
// =====================================

async function handleResponse(response) {
  const data = await response.json();

  if (!response.ok) {
    throw new Error(data.detail || "Something went wrong.");
  }

  return data;
}

// =====================================
// CHAT
// =====================================

export async function search(question) {
  const response = await fetch(`${API_URL}/search`, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
    },
    body: JSON.stringify({
      question,
    }),
  });

  return handleResponse(response);
}

// =====================================
// DOCUMENTS
// =====================================

export async function uploadDocument(file) {
  const formData = new FormData();

  formData.append("file", file);

  const response = await fetch(`${API_URL}/upload`, {
    method: "POST",
    body: formData,
  });

  return handleResponse(response);
}

export async function getDocuments() {
  const response = await fetch(`${API_URL}/documents`);

  return handleResponse(response);
}

export async function deleteDocument(filename) {
  const response = await fetch(
    `${API_URL}/documents/${filename}`,
    {
      method: "DELETE",
    }
  );

  return handleResponse(response);
}

// =====================================
// MEMORIES
// =====================================

export async function getMemories() {
  const response = await fetch(`${API_URL}/memories`);

  return handleResponse(response);
}

export async function saveMemory(memory) {
  const response = await fetch(`${API_URL}/memory`, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
    },
    body: JSON.stringify(memory),
  });

  return handleResponse(response);
}

export async function deleteMemory(id) {
  const response = await fetch(`${API_URL}/memory/${id}`, {
    method: "DELETE",
  });

  return handleResponse(response);
}