import { Link } from "react-router-dom";
import { useEffect, useState } from "react";
import { getAllRecipes } from "../../api_funcs/recipes.js";
import "./Recipes.css"
import Addreci from "../Buttons/AddReci.jsx";
import Footer from "../Footer/Footer.jsx";


export default function Recipes() {
  const [recipes, setRecipes] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    const ac = new AbortController();
    (async () => {
      try {
        const data = await getAllRecipes();
        setRecipes(Array.isArray(data) ? data : []);
      } catch (e) {
        if (e.name !== "AbortError") setError(e);
      } finally {
        setLoading(false);
      }
    })();
    return () => ac.abort();
  }, []);

  return (
    <main className="page">
      {/* Page header and Search combined */}
      <div
        className="page__head container">
        {/* LEFT SIDE: Title, Subtitle, and CTA Button */}

        <div>
          <h1 className="page__title">Recipe Collection</h1>
          <p className="page__subtitle">
            Discover and share recipes transcribed from your audio/video.
          </p>
        </div>
          <div className="navbar__actions">
            <Link to="/recipes/new">
              <Addreci />
            </Link>
            </div>
             <div className="searchbar">
                <input
                  className="searchbar__input"
                  placeholder="Search recipe titles…"
                />
            </div>
        {/* RIGHT SIDE: Search bar */}
        <section
          style={{ width: '250px', padding: 0, marginTop: '8.0rem' }} // Align search bar visually
        >
        </section>
      </div>

    

      {/* Grid */}
      <section className="grid grid--recipes">
        {loading ? (
          <p className="muted">Loading…</p>
        ) : error ? (
          <p className="muted">Failed to load: {String(error.message || error)}</p>
        ) : recipes.length ? (
          recipes.map((r) => <RecipeTitleCard key={r.id ?? r.title} recipe={r} />)
        ) : (
          <p className="muted">No recipes yet.</p>
        )}
      </section>
    </main>
  );
}

function RecipeTitleCard({ recipe }) {
  return (
    <article className="card recipe recipe--minimal">
      <h3 className="recipe__title">{recipe.title}</h3>
      <div className="recipe__actions">
        <Link to={`/recipes/${recipe.id}`} className="btn btn--ghost sm">
          View Recipe
        </Link>
      </div>
    </article>
  );
}
