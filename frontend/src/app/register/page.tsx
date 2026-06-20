"use client";

import { useState } from "react";
import { motion } from "framer-motion";
import Link from "next/link";
import { useAuth } from "@/lib/auth-context";

export default function RegisterPage() {
  const { register } = useAuth();
  const [name, setName] = useState("");
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(false);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError("");
    setLoading(true);
    try {
      await register(email, password, name);
    } catch (err: any) {
      setError(err.response?.data?.detail || "Registration failed");
    } finally {
      setLoading(false);
    }
  };

  return (
    <main className="min-h-screen flex items-center justify-center px-6">
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.5 }}
        className="glass-card p-8 w-full max-w-md"
      >
        <h1 className="text-2xl font-semibold mb-1 gradient-text">Create your account</h1>
        <p className="text-gray-400 text-sm mb-6">Start exploring research papers with AI</p>

        {error && (
          <div className="mb-4 p-3 bg-red-500/10 border border-red-500/30 rounded-lg text-red-400 text-sm">
            {error}
          </div>
        )}

        <form onSubmit={handleSubmit} className="space-y-4">
          <div>
            <label className="text-sm text-gray-400">Full Name</label>
            <input
              type="text"
              required
              value={name}
              onChange={(e) => setName(e.target.value)}
              className="w-full mt-1 px-4 py-2.5 bg-white/5 border border-white/10 rounded-lg focus:outline-none focus:border-accent transition"
              placeholder="Jane Doe"
            />
          </div>
          <div>
            <label className="text-sm text-gray-400">Email</label>
            <input
              type="email"
              required
              value={email}
              onChange={(e) => setEmail(e.target.value)}
              className="w-full mt-1 px-4 py-2.5 bg-white/5 border border-white/10 rounded-lg focus:outline-none focus:border-accent transition"
              placeholder="you@example.com"
            />
          </div>
          <div>
            <label className="text-sm text-gray-400">Password</label>
            <input
              type="password"
              required
              minLength={8}
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              className="w-full mt-1 px-4 py-2.5 bg-white/5 border border-white/10 rounded-lg focus:outline-none focus:border-accent transition"
              placeholder="At least 8 characters"
            />
          </div>
          <button
            type="submit"
            disabled={loading}
            className="w-full py-2.5 bg-accent hover:bg-accent-dark rounded-lg font-medium transition disabled:opacity-50"
          >
            {loading ? "Creating account..." : "Create Account"}
          </button>
        </form>

        <p className="text-center text-sm text-gray-400 mt-6">
          Already have an account?{" "}
          <Link href="/login" className="text-accent-light hover:underline">
            Sign in
          </Link>
        </p>
      </motion.div>
    </main>
  );
}
