import { Link } from "react-router-dom";
import "./DashboardChart.css";
import Addreci from "./AddReci.jsx";
import ScanPantry from "./ScanPantry.jsx";
import GroceryButton from "./GroceryButton.jsx";


export default function Dashboard() {
  const username = "Osama"; // Replace with real user data from backend later

  return (
    <main className="dashboard">
      <section className="dash-section dash-hero">
        <h1 className="dash-title">Welcome back, {username} 👋</h1>
        <p className="dash-subtitle">
          Here's a quick look at your cooking world today.
        </p>

        <div className="dash-quick-actions">
           <div className="navbar__actions">
            <Link to="/recipes">
              <Addreci />
            </Link>
            </div>
            <div className="navbar__actions">
            <Link to="/pantry">
              <ScanPantry />
            </Link>
            </div>
            <div className="navbar__actions">
            <Link to="/grocery">
              <GroceryButton />
            </Link>
            </div>
         {/* <Link to="/recipes" className="dash-btn">+ Add Recipe</Link>
          <Link to="/pantry" className="dash-btn">Scan Pantry</Link>
          <Link to="/grocery" className="dash-btn">View Grocery List</Link>*/}
        </div>
      </section>

      {/* ===== Stats Section ===== */}
      <section className="dash-section dash-stats">
        <div className="dash-card">
          <h3>📘 Recipes</h3>
          <p className="dash-number">12 Saved</p>
        </div>

        <div className="dash-card">
          <h3>🧰 Pantry Items</h3>
          <p className="dash-number">27 Items</p>
        </div>

        <div className="dash-card">
          <h3>🛒 Grocery Needed</h3>
          <p className="dash-number">8 Items</p>
        </div>
      </section>

      {/* ===== Recent Recipes ===== */}
      <section className="dash-section">
        <h2 className="dash-heading">Recent Recipes</h2>

        <div className="dash-list">
          <div className="dash-list-item">
            <p>🍝 Creamy Alfredo Pasta</p>
            <Link to="/recipes/1" className="dash-link">View</Link>
          </div>

          <div className="dash-list-item">
            <p>🥗 Avocado Salad Bowl</p>
            <Link to="/recipes/2" className="dash-link">View</Link>
          </div>

          <div className="dash-list-item">
            <p>🍪 Soft Chocolate Chip Cookies</p>
            <Link to="/recipes/3" className="dash-link">View</Link>
          </div>
        </div>
      </section>

      {/* ===== Pantry Overview ===== */}
      <section className="dash-section">
        <h2 className="dash-heading">Pantry Overview</h2>

        <div className="dash-list">
          <div className="dash-list-item">
            <p>🍅 Tomato Sauce</p>
            <span className="dash-tag low">Low</span>
          </div>

          <div className="dash-list-item">
            <p>🥚 Eggs</p>
            <span className="dash-tag good">Good</span>
          </div>

          <div className="dash-list-item">
            <p>🥛 Milk</p>
            <span className="dash-tag expiring">Expiring Soon</span>
          </div>
        </div>
      </section>
    </main>
  );
}
