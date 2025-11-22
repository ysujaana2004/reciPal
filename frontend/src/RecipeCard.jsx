// import { useParams, Link } from "react-router-dom";
// import { useEffect, useState } from "react";
// import { getRecipeById, editRecipe } from "../api_funcs/recipes.js";

// export default function RecipeCard() {
//   const { id } = useParams();
//   const [recipe, setRecipe] = useState(null);
//   const [error, setError] = useState(null);
// //pip install requirements.txt
// //python manage.py runserver
//   useEffect(() => {
//     const ac = new AbortController();
//     (async () => {
//       try {
//         const data = await getRecipeById(id, { signal: ac.signal });
//         setRecipe({ ...data, author: "Mr. Robot" });
//       } catch (e) {
//         if (e.name !== "AbortError") setError(e);
//       }
//     })();
//     return () => ac.abort();
//   }, [id]);

//   if (error) return <main className="page container">Error: {String(error.message || error)}</main>;
//   if (!recipe) return <main className="page container">Loading…</main>;

//   return (
//     <main className="page container">
//       <Link to="/recipes" className="back-link">← Back to Recipes</Link>

//       <article className="recipe-detail card">
//         <header className="recipe-detail__head">
//           <h1 className="recipe-detail__title">{recipe.title}</h1>
//           <p className="recipe-detail__author">by {recipe.author}</p>
//         </header>

//         <p className="recipe-detail__transcript">{recipe.caption}</p>

//         <section className="recipe-detail__section">
//           <h2>Ingredients</h2>
//           <ul className="recipe-detail__list">
//             {(recipe.ingredients ?? []).map((item, i) => (
//               <li key={i}>{Array.isArray(item) ? item.join(" ") : String(item)}</li>
//             ))}
//           </ul>
//         </section>

//         <section className="recipe-detail__section">
//           <h2>Steps</h2>
//           <ol className="recipe-detail__list">
//             {(recipe.steps ?? []).map((step, i) => <li key={i}>{step}</li>)}
//           </ol>
//         </section>
//       </article>
//     </main>
//   );
// }

import { useParams, Link } from "react-router-dom";
import { useEffect, useState } from "react";
import { getRecipeById } from "../api_funcs/recipes.js";

export default function RecipeCard() {
  const { id } = useParams();
  const [recipe, setRecipe] = useState(null);
  const [error, setError] = useState(null);

  useEffect(() => {
    const ac = new AbortController();
    (async () => {
      try {
        const data = await getRecipeById(id, { signal: ac.signal });
        setRecipe({ ...data, author: "Mr. Robot" });
      } catch (e) {
        if (e.name !== "AbortError") setError(e);
      }
    })();
    return () => ac.abort();
  }, [id]);

  if (error) {
    return (
      <main className="page container">
        Error: {String(error.message || error)}
      </main>
    );
  }
  if (!recipe) {
    return <main className="page container">Loading…</main>;
  }

  // Split instructions into list items so we can render them like steps.
  const instructionLines =
    (recipe.instructions || "")
      .split(/\r?\n+/)
      .map((s) => s.trim())
      .filter(Boolean);

  return (
    <main className="page container">
      <Link to="/recipes" className="back-link">
        ← Back to Recipes
      </Link>

      <article className="recipe-detail card">
        <header className="recipe-detail__head">
          <h1 className="recipe-detail__title">{recipe.title}</h1>
          <p className="recipe-detail__author">by {recipe.author}</p>
        </header>

        <p className="recipe-detail__transcript">{recipe.caption}</p>

        <section className="recipe-detail__section">
          <h2>Ingredients</h2>
          <ul className="recipe-detail__list">
            {(recipe.ingredients ?? []).map((item, i) => (
              <li key={i}>
                {Array.isArray(item) ? item.join(" ") : String(item)}
              </li>
            ))}
          </ul>
        </section>

        <section className="recipe-detail__section">
          <h2>Instructions</h2>
          {instructionLines.length ? (
            <ol className="recipe-detail__list">
              {instructionLines.map((line, i) => (
                <li key={i}>{line}</li>
              ))}
            </ol>
          ) : (
            <p className="muted">No instructions provided.</p>
          )}
        </section>
      </article>
    </main>
  );
}
