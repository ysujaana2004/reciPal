import { Routes, Route } from "react-router-dom";
import Navbar from "../Navbar/Navbar.jsx";
import Home from "../Home/Home.jsx";
import Recipes from "../Recipes/Recipes.jsx";
import Pantry from "../Pantry/Pantry.jsx";
import GroceryList from "../Grocery List/GroceryList.jsx";
import RecipeCard from "../RecipeCard.jsx";
import Login from "../Login/Login.jsx";
import Signup from "../Signup.jsx";
import NewRecipe from "../NewRecipe.jsx";
import User from "../User.jsx";
import Dashboard from "../Dashboard/DashboardChart.jsx";


function App() {
  return (
    <>
      <Navbar />
      <Routes>
        <Route path="/" element={<Home />} />
        <Route path="/recipes" element={<Recipes />} />
        {/* support both /recipes/new (new recipe form) and /recipes/:id (view) */}
        <Route path="/recipes/new" element={<NewRecipe />} />
        <Route path="/recipes/:id" element={<RecipeCard />} />
        <Route path="/pantry" element={<Pantry />} />
        <Route path="/grocery" element={<GroceryList />} />
        <Route path="/login" element={<Login />} />
        <Route path="/signup" element={<Signup />} />
        <Route path="/user" element={<User />} />
        <Route path="/dashboard" element={<Dashboard />} />

        {/* Optional placeholders for links shown on Home */}
        {/* Optional placeholders for links shown on Home */}
        {/* Optional placeholders for links shown on Home */}
        <Route
          path="*"
          element={
            <div className="container" style={{ padding: "32px 20px" }}>
              Page not found.
            </div>
          }
        />
      </Routes>
    </>
  );
}

export default App;
