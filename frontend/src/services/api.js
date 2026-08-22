const API_URL = "https://ai-memory-search-engine.onrender.com";

// Helper Functions

function getAuthHeaders() {
  const token = localStorage.getItem("access_token");

  return {
    Authorization: `Bearer ${token}`,
  };
}

async function handleResponse(response) {
  const data = await response.json();

  if (!response.ok) {
    throw new Error(data.detail || "Something went wrong.");
  }

  return data;
}

// CHAT

export async function search(question) {
  const response = await fetch(`${API_URL}/search`, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
      ...getAuthHeaders(),
    },
    body: JSON.stringify({
      question,
    }),
  });

  return handleResponse(response);
}
export async function getChatHistory() {
  const response = await fetch(
    `${API_URL}/chat/history`,
    {
      headers: {
        ...getAuthHeaders(),
      },
    }
  );

  return handleResponse(response);
}
export async function clearChatHistory() {
  const response = await fetch(
    `${API_URL}/chat/history`,
    {
      method: "DELETE",
      headers: {
        ...getAuthHeaders(),
      },
    }
  );

  return handleResponse(response);
}

// DOCUMENTS

export async function uploadDocument(file) {
  const formData = new FormData();

  formData.append("file", file);

  const response = await fetch(`${API_URL}/upload`, {
    method: "POST",
    headers: {
      ...getAuthHeaders(),
    },
    body: formData,
  });

  return handleResponse(response);
}

export async function getDocuments() {
  const response = await fetch(`${API_URL}/documents`, {
    headers: {
      ...getAuthHeaders(),
    },
  });

  return handleResponse(response);
}

export async function deleteDocument(filename) {
  const response = await fetch(
    `${API_URL}/documents/${filename}`,
    {
      method: "DELETE",
      headers: {
        ...getAuthHeaders(),
      },
    }
  );

  return handleResponse(response);
}

// MEMORIES

export async function getMemories() {
  const response = await fetch(`${API_URL}/memories`, {
    headers: {
      ...getAuthHeaders(),
    },
  });

  return handleResponse(response);
}

export async function saveMemory(memory) {
  const response = await fetch(`${API_URL}/memory`, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
      ...getAuthHeaders(),
    },
    body: JSON.stringify(memory),
  });

  return handleResponse(response);
}

export async function deleteMemory(id) {
  const response = await fetch(`${API_URL}/memory/${id}`, {
    method: "DELETE",
    headers: {
      ...getAuthHeaders(),
    },
  });

  return handleResponse(response);
}

export async function updateMemory(id, memory) {
  const response = await fetch(
    `${API_URL}/memory/${id}`,
    {
      method: "PUT",
      headers: {
        "Content-Type": "application/json",
        ...getAuthHeaders(),
      },
      body: JSON.stringify(memory),
    }
  );

  return handleResponse(response);
}