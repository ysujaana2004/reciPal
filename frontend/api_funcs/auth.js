// const BASE = "http://127.0.0.1:8000";
const BASE = import.meta.env.VITE_API_URL;

export async function signup({ username, email, password }) {
  const res = await fetch(`${BASE}/api/auth/signup/`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ username, email, password }),
  });
  if (!res.ok) throw new Error("Signup failed");
  return res.json();
}

export async function signin({ login, password }) {
  const res = await fetch(`${BASE}/api/auth/signin/`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ login, password }),
  });
  if (!res.ok) throw new Error("Signin failed");
  const data = await res.json();
  // store tokens (you can use httpOnly cookies in prod; localStorage is simple for dev)
  localStorage.setItem("access", data.access);
  localStorage.setItem("refresh", data.refresh);
  return data.user; // { username, email }
}

export async function me() {
  const access = localStorage.getItem("access");
  const res = await fetch(`${BASE}/api/auth/me/`, {
    headers: { Authorization: `Bearer ${access}` },
  });
  if (res.status === 401) throw new Error("Unauthorized");
  return res.json(); // { username, email }
}

export async function refreshToken() {
  const refresh = localStorage.getItem("refresh");
  const res = await fetch(`${BASE}/api/auth/refresh/`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ refresh }),
  });
  if (!res.ok) throw new Error("Refresh failed");
  const data = await res.json();
  localStorage.setItem("access", data.access);
  return data.access;
}