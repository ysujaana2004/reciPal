// FastAPI mounts the recipes router at /recipes (see app/main.py)
const BASE = "http://127.0.0.1:8000/recipes";

async function request(
  path,
  { method = "GET", headers = {}, body, signal } = {}
) {
  const url = `${BASE}${path}`;

  // If body is a plain object, send JSON
  const isFormData =
    typeof FormData !== "undefined" && body instanceof FormData;
  if (body && !isFormData && !headers["Content-Type"]) {
    headers["Content-Type"] = "application/json";
    body = JSON.stringify(body);
  }

  const res = await fetch(url, { method, headers, body, signal });
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

// ---------- Endpoints (no auth) ----------

// GET /recipes/<id>  -> returns full recipe record with its ingredients
export function getRecipeById(id, opts) {
  return request(`/${encodeURIComponent(id)}`, opts);
}

// Placeholder: backend search endpoint hasn't been implemented yet
export function searchRecipesByTitle(query, opts) {
  return request(`/search/${encodeURIComponent(query)}`, opts);
}

// GET /recipes/ -> returns all recipes for the authenticated user
export function getAllRecipes(opts) {
  return request(`/`, opts);
}

// POST /recipes/extract?url=<video_url>
export function createRecipeFromReel(reelUrl, opts) {
  const urlParam = encodeURIComponent(reelUrl);
  return request(`/extract?url=${urlParam}`, { method: "POST", ...opts });
}

// POST /recipes/edit -> placeholder for compatibility with older UI pieces
export function editRecipe(id, dataObj, opts) {
  return request(`/edit`, {
    method: "POST",
    body: { id: id, data: dataObj },
    ...opts,
  });
}
