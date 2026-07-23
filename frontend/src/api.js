const BASE = import.meta.env.VITE_API_BASE || "/api";

function authHeaders() {
  const token = localStorage.getItem("saarthi_token");
  return token ? { Authorization: `Bearer ${token}` } : {};
}

export async function signup(payload) {
  const res = await fetch(`${BASE}/auth/signup`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(payload),
  });
  if (!res.ok) throw new Error((await res.json()).detail || "Signup failed");
  return res.json();
}

export async function login(payload) {
  const res = await fetch(`${BASE}/auth/login`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(payload),
  });
  if (!res.ok) throw new Error((await res.json()).detail || "Login failed");
  return res.json();
}

export async function createSession() {
  const res = await fetch(`${BASE}/chat/session`, {
    method: "POST",
    headers: authHeaders(),
  });
  return res.json();
}

export async function listSessions() {
  const res = await fetch(`${BASE}/chat/sessions`, { headers: authHeaders() });
  return res.json();
}

export async function getMessages(sessionId) {
  const res = await fetch(`${BASE}/chat/session/${sessionId}/messages`, {
    headers: authHeaders(),
  });
  return res.json();
}

export async function getLevel(sessionId) {
  const res = await fetch(`${BASE}/chat/session/${sessionId}/level`, {
    headers: authHeaders(),
  });
  return res.json();
}

export async function sendMessageStream(sessionId, content, onChunk) {
  const res = await fetch(`${BASE}/chat/message`, {
    method: "POST",
    headers: { "Content-Type": "application/json", ...authHeaders() },
    body: JSON.stringify({ session_id: sessionId, content }),
  });

  if (!res.ok || !res.body) throw new Error("Message failed to send");

  const reader = res.body.getReader();
  const decoder = new TextDecoder();
  while (true) {
    const { done, value } = await reader.read();
    if (done) break;
    onChunk(decoder.decode(value, { stream: true }));
  }
}
