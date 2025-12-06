import { getAccessToken } from "./auth";

const API_BASE = import.meta.env.VITE_API_URL || "http://127.0.0.1:8000";
const BASE = `${API_BASE.replace(/\/$/, "")}/pantry`;

async function request(
  path,
  { method = "GET", headers = {}, body, signal } = {}
) {
  const url = `${BASE}${path}`;
  const authHeaders = { ...headers };

  const token = getAccessToken();
  if (token) {
    authHeaders.Authorization = `Bearer ${token}`;
  }

  if (body && !authHeaders["Content-Type"]) {
    authHeaders["Content-Type"] = "application/json";
    body = JSON.stringify(body);
  }

  const res = await fetch(url, { method, headers: authHeaders, body, signal });
  const text = await res.text();

  let data = null;
  try {
    data = text ? JSON.parse(text) : null;
  } catch {
    data = text;
  }

  if (!res.ok) {
    const msg =
      (data && (data.detail || data.error || JSON.stringify(data))) ||
      res.statusText;
    const err = new Error(msg);
    err.status = res.status;
    err.data = data;
    throw err;
  }
  return data;
}

/**
 * Get all pantry items for the authenticated user
 */
export async function getPantryItems(opts = {}) {
  return request("/", { method: "GET", ...opts });
}

/**
 * Add or update a pantry item (upsert)
 */
export async function addPantryItem({ ingredient_name, quantity, unit = "pieces" }) {
  return request("/", {
    method: "POST",
    body: { ingredient_name, quantity, unit },
  });
}

/**
 * Update a pantry item's quantity
 */
export async function updatePantryItem(itemId, { quantity, unit }) {
  return request(`/${itemId}`, {
    method: "PUT",
    body: { quantity, unit },
  });
}

/**
 * Delete a pantry item
 */
export async function deletePantryItem(itemId) {
  return request(`/${itemId}`, { method: "DELETE" });
}

/**
 * Check which recipe ingredients are available
 */
export async function checkIngredients(ingredients) {
  return request("/check", {
    method: "POST",
    body: { ingredients },
  });
}
