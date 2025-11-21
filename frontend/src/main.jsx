import React from "react";
import ReactDOM from "react-dom/client";
import { BrowserRouter } from "react-router-dom";
import App from "./App/App.jsx";
import "./Home/index.css";

ReactDOM.createRoot(document.getElementById("root")).render(
  <React.StrictMode>
    <BrowserRouter>
      <App />
    </BrowserRouter>
  </React.StrictMode>
);

// ... existing React import/setup code in main.jsx ...

// Add this block below your ReactDOM.createRoot(...) call
document.addEventListener('DOMContentLoaded', () => {
    const cursorDot = document.getElementById('cursor-dot');
    const cursorRing = document.getElementById('cursor-ring');

    if (cursorDot && cursorRing) {
        document.addEventListener('mousemove', (e) => {
            // Update the dot position immediately
            cursorDot.style.transform = `translate(${e.clientX}px, ${e.clientY}px)`;
            
            // Update the ring position
            cursorRing.style.transform = `translate(${e.clientX}px, ${e.clientY}px)`;
        });
    }
});
