# ReciPal (Refactored)

ReciPal is a full‑stack cooking assistant that turns short‑form cooking videos into structured recipes and auto‑builds the grocery list you need to cook them.

At a high level the app:

- Lets a user drop an Instagram/TikTok/YouTube link, downloads the audio, and sends it to Gemini to extract the recipe title, instructions, and ingredients.
- Stores the resulting recipe data in a FastAPI + SQLAlchemy backend so it is accessible from any device.
- Seeds a demo user and sample recipes so the UI works immediately (no sign‑in required).
- Computes personalized grocery recommendations by comparing your pantry to the ingredients across your saved recipes.
- Surfaces all of that through a Vite/React frontend with dedicated pages for recipes, adding new ones, pantry, and grocery planning.

## Repository Layout

```
app/
  main.py          # FastAPI app, routes include routers
  auth.py          # signup/signin/me
  recipes.py       # recipe CRUD + extraction endpoint
  grocery.py       # recommender endpoint
  models.py        # SQLAlchemy models
  db.py            # engine/session
  services/        # gemini.py (extraction + substitutions), downloader.py
.env
requirements.txt
```

## Backend Modules (app/)

### `app/main.py`
- Think of this as the “power button” for the backend. It creates the FastAPI server, makes sure the database tables exist, loads demo data, and connects every feature module.
- It also flips on CORS so the React frontend can talk to the backend from `http://localhost:5173`.
- When the app starts, four mini-apps are mounted:
  - `/auth` → handles sign-up/sign-in
  - `/recipes` → handles recipe extraction and listing
  - `/grocery` → generates grocery suggestions
  - `/pantry` → stores what’s inside your pantry
- Bonus: `GET /health` is a quick “ping” endpoint that simply returns `{"status": "ok"}` so you can confirm the backend is running.

### `app/auth.py`
- Provides the ultra-simple login system used for demos. Instead of passwords + JWTs, we issue tokens shaped like `user-<id>`.
- Endpoints (all accept/return plain JSON or form data):
  - `POST /auth/signup` → create a basic account (email + password).
  - `POST /auth/signin` → verify the email/password and return the `user-<id>` token.
- Helper `get_current_user` looks for the `Authorization: Bearer user-<id>` header. If it’s missing, we automatically log people in as the pre-seeded demo user so the site still works during testing.
- Future frontend login screens would call these endpoints, but the current UI piggybacks on the demo user.

### `app/recipes.py`
- This is the heart of the product: it’s where reels get turned into structured recipes and where the frontend fetches them.
- Key endpoints:
  - `POST /recipes/from_video` → accepts JSON `{ "video_url": "..." }`, downloads the audio (`services/downloader.py`), calls Gemini to extract the recipe (`services/gemini.py`), saves it, and returns both the stored record plus Gemini's raw output. (`/recipes/extract?url=` still works for legacy callers.)
  - `GET /recipes/` → returns every recipe for the logged-in user. The Recipes page calls this on load.
  - `GET /recipes/{id}` → returns a single recipe (useful for a detail page).
  - `DELETE /recipes/{id}` → removes a recipe (handy for future “delete” buttons).
- Each response includes the recipe title, instructions, source URL, and ingredient list so the frontend can render cards or detailed views without extra calls.

### `app/grocery.py`
- Implements the grocery recommender logic described earlier: “What ingredient should I buy to unlock the most of my saved recipes?”
- Endpoint:
  - `GET /grocery/recommendations` → compares your pantry items and recipe ingredients, then returns suggestions like `{"ingredient": "butter", "unlocks": 2}` meaning “buy butter to unlock two more meals.”
- The Grocery List page calls this endpoint directly; everything else (math + sorting) happens server-side so the frontend stays simple.

### `app/pantry.py`
- Keeps track of what the user already has in the kitchen.
- Endpoints:
  - `POST /pantry/add` with `name=<ingredient>` → adds a new pantry item for the user.
  - `GET /pantry/` → returns all stored items (plain list of strings).
- These endpoints aren’t wired into the UI yet, but they will drive future features like barcode scanning or manual pantry updates, and they are already used indirectly by the grocery recommender.

### `app/models.py`
- Defines the database tables using SQLAlchemy.
- Tables (and why they matter):
  - `User` → stores login info and links to everything else.
  - `Recipe` → stores title, instructions, and who owns it.
  - `RecipeIngredient` → each row is one ingredient tied to a recipe.
  - `PantryItem` → tracks what the user already has on hand.
- These models are imported throughout the project so every endpoint is speaking the same data language.

### `app/db.py`
- Centralizes the code that opens and closes database connections.
- Exposes `get_db()`, a helper that every endpoint can “depend” on so FastAPI automatically hands them a ready-to-use database session and cleans it up afterward.
- Defaults to a local SQLite file (`app.db`) but honors the `DATABASE_URL` env var for Postgres/Supabase deployments.

### `app/startup_data.py`
- Populates the database with a demo user, four starter recipes, and a small pantry the first time you run the app.
- This is why you can open the frontend and immediately see recipes and grocery recommendations even if you never signed up.

### `app/services/downloader.py`
- Small utility that accepts a video URL and uses `yt-dlp` to grab just the audio track.
- It saves the audio as a temporary `.mp3` and returns the file path so the recipe extraction step can analyze the spoken instructions.

### `app/services/gemini.py`
- Handles all communication with the Gemini API.
- Given a path to an audio file, it sends a clear prompt, receives structured JSON (title, ingredient list, instructions), validates it, and hands the clean dict back to `recipes.py`.
- If anything goes wrong (missing API key, invalid JSON, network hiccup) you get detailed exceptions instead of silent failures.

## How the App Flows (Step by Step)

Below is the typical journey from opening the site to generating grocery suggestions.

1. **User visits the React frontend (Vite `npm run dev`)**
   - The browser loads the UI, pulls shared styles/assets, and shows the Navbar.
   - No login is required because the backend auto-signs visitors in as the demo user if they don’t send a token.

2. **Clicking “Recipes”**
   - Frontend calls `getAllRecipes()` (from `frontend/api_funcs/recipes.js`), which fetches `GET http://127.0.0.1:8000/recipes/`.
   - FastAPI routes that request to `app/recipes.py:list_recipes`, which loads all recipes for the (demo) user from the database and returns them as JSON.
   - React maps the JSON into cards, each linking to `/recipes/<id>`.

3. **Adding a new recipe**
   - On the “Add Recipe” page the user pastes a reel URL and hits submit.
   - Frontend calls `createRecipeFromReel(url)` → `POST http://127.0.0.1:8000/recipes/from_video` with body `{ video_url: url }`.
   - `app/recipes.py:create_recipe_from_video` takes over:
     1. `services/downloader.py` pulls the video audio.
     2. `services/gemini.py` turns the audio into structured recipe data.
     3. The recipe and its ingredients are saved via `models.py` + `db.py`.
   - The newly created recipe is returned to the UI, and the list can be refreshed to show it.

4. **Viewing grocery recommendations**
   - On the Grocery page the frontend calls `getRecommendations()` → `GET http://127.0.0.1:8000/grocery/recommendations`.
   - `app/grocery.py:recommend_ingredients` compares the user’s pantry (`app/pantry.py` data) with all their recipe ingredients, calculates which missing ingredients unlock the most recipes, and returns a sorted list.
   - React converts the response into checklist items with unlock counts and renders them with animated checkboxes.

5. **Pantry updates (future flow)**
   - When a pantry UI is added, it will call `POST /pantry/add` and `GET /pantry/` so the backend keeps track of what the user owns; these entries automatically feed into the grocery recommender.

6. **Health + maintenance**
   - Any monitoring or deployment scripts can hit `GET /health` to make sure the backend is still running.

## Local Setup

Follow these steps to run the entire stack locally (Mac/Linux; Windows users can adapt commands accordingly).

### 1. Clone and install backend dependencies

```bash
git clone <repo-url>
cd reciPal-refactored
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

Copy `.env.example` to `.env` (if provided) and make sure you set:

```
GOOGLE_API_KEY=your_gemini_api_key
DATABASE_URL=sqlite:///./app.db   # optional; defaults to this value
```

### 2. Start the FastAPI backend

```bash
uvicorn app.main:app --reload
```

This creates/updates `app.db`, seeds demo data (if empty), and serves the API on `http://127.0.0.1:8000`.

### 3. Install frontend dependencies

```bash
cd frontend
npm install
```

### 4. Run the Vite dev server

```bash
npm run dev
```

Vite will print something like `http://localhost:5173`. Open that URL in your browser—the frontend will automatically talk to the FastAPI backend running on port 8000.

### 5. Optional: run tests / lint

Currently the repo relies on manual testing, but you can add Pytest or React Testing Library suites as needed. For now, validate changes by:

- Hitting `http://127.0.0.1:8000/health` to confirm the backend is alive.
- Visiting the Recipes and Grocery pages to ensure data loads.
