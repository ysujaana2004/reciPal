import { useState } from "react";
import { Link } from "react-router-dom";
import {signup} from "../api_funcs/auth.js";

export default function Signup() {
  const [form, setForm] = useState({ email: "", username: "", password: "" });

  const handleChange = (e) =>
    setForm({ ...form, [e.target.name]: e.target.value });

  const handleSubmit = async(e) => {
    e.preventDefault();
    try {
      await signup({
        username: form.username,
        email: form.email,
        password: form.password,
      });
      console.log("Signing up:", form);
    } catch (err) {
      console.error("Signup failed:", err);
    }
  };

  return (
    <main className="page container" style={{ maxWidth: 480 }}>
      <h1 className="page__title">Sign Up</h1>
      <p className="page__subtitle">Create a new account to get started.</p>

      <form className="card auth-form" onSubmit={handleSubmit}>
        <label className="auth-label">
          Email
          <input
            type="email"
            name="email"
            className="auth-input"
            value={form.email}
            onChange={handleChange}
            required
          />
        </label>

        <label className="auth-label">
          Username
          <input
            type="text"
            name="username"
            className="auth-input"
            value={form.username}
            onChange={handleChange}
            required
          />
        </label>

        <label className="auth-label">
          Password
          <input
            type="password"
            name="password"
            className="auth-input"
            value={form.password}
            onChange={handleChange}
            required
          />
        </label>

        <button type="submit" className="btn btn--solid" style={{ width: "100%" }}>
          Sign Up
        </button>

        <p style={{ fontSize: 14, color: "var(--muted)", marginTop: 14 }}>
          Already have an account?{" "}
          <Link to="/login" style={{ color: "var(--accent)", fontWeight: 600 }}>
            Log in
          </Link>
        </p>
      </form>
    </main>
  );
}
