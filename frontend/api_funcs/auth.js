const API_BASE = import.meta.env.VITE_API_URL || "http://127.0.0.1:8000";
const BASE = `${API_BASE.replace(/\/$/, "")}/auth`;
const ACCESS_KEY = "access_token";

function getJsonOrThrow(res, fallback = "Request failed") {
  return res.json().then((data) => {
    if (!res.ok) {
      const detail = data?.detail || data?.error || res.statusText;
      throw new Error(detail || fallback);
    }
    return data;
  });
}

export function getAccessToken() {
  return localStorage.getItem(ACCESS_KEY);
}

export function clearAccessToken() {
  localStorage.removeItem(ACCESS_KEY);
}

export function getSessionUser() {
  const token = getAccessToken();
  if (!token) return null;
  try {
    const payload = JSON.parse(atob(token.split(".")[1] || ""));
    return {
      email: payload.email || payload.user_metadata?.email,
      uid: payload.sub,
    };
  } catch {
    return null;
  }
}

export async function me() {
  const user = getSessionUser();
  if (!user) {
    throw new Error("Unauthorized");
  }
  return user;
}

export async function signup({ username, email, password }) {
  const res = await fetch(`${BASE}/signup`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ username, email, password }),
  });
  return getJsonOrThrow(res, "Signup failed");
}

export async function login({ email, password }) {
  const res = await fetch(`${BASE}/login`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ email, password }),
  });
  const data = await getJsonOrThrow(res, "Login failed");
  if (data?.access_token) {
    localStorage.setItem(ACCESS_KEY, data.access_token);
  }
  return data;
}

export function logout() {
  clearAccessToken();
}
