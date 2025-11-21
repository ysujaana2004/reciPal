// grocery.js
// grocery API logic from app/grocery.py

// const BASE = "http://127.0.0.1:8000/grocery";

const API_BASE = import.meta.env.VITE_API_URL; // e.g. https://your-backend.onrender.com
const BASE = `${API_BASE.replace(/\/$/, "")}/grocery`;

// GET /grocery/recommendations -> returns recommended grocery items based on user's recipes and pantry
export async function getRecommendations() {
  const res = await fetch(`${BASE}/recommendations`);
  if (!res.ok) throw new Error("Failed to load grocery list");
  return res.json(); // expect [{ id, label }] or whatever the backend returns
}

