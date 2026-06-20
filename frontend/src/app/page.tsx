"use client";

import { motion } from "framer-motion";
import Link from "next/link";
import { Sparkles, FileSearch, MessageSquare, Network } from "lucide-react";
import { GlassCard } from "@/components/ui/GlassCard";

const features = [
  { icon: FileSearch, title: "Smart PDF Analysis", desc: "Extract text, tables, figures, and equations automatically." },
  { icon: MessageSquare, title: "Multi-Paper Chat", desc: "Ask questions across hundreds of papers with grounded citations." },
  { icon: Network, title: "Knowledge Graphs", desc: "Visualize connections between authors, topics, and concepts." },
  { icon: Sparkles, title: "Research Ideas", desc: "Discover gaps and generate novel research directions." },
];

export default function LandingPage() {
  return (
    <main className="min-h-screen flex flex-col items-center px-6">
      <nav className="w-full max-w-6xl flex justify-between items-center py-6">
        <span className="text-xl font-semibold gradient-text">Scientia AI</span>
        <div className="flex gap-4">
          <Link href="/login" className="px-4 py-2 text-sm hover:text-accent-light transition">
            Sign In
          </Link>
          <Link
            href="/register"
            className="px-4 py-2 text-sm bg-accent hover:bg-accent-dark rounded-lg transition"
          >
            Get Started
          </Link>
        </div>
      </nav>

      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.6 }}
        className="text-center max-w-3xl mt-24"
      >
        <h1 className="text-5xl md:text-6xl font-bold mb-6">
          Your AI Research Assistant for{" "}
          <span className="gradient-text">Scientific Papers</span>
        </h1>
        <p className="text-lg text-gray-400 mb-8">
          Upload papers, ask questions, generate literature reviews, discover research
          gaps, and build presentations — all powered by AI.
        </p>
        <Link
          href="/register"
          className="inline-block px-8 py-3 bg-accent hover:bg-accent-dark rounded-xl font-medium transition"
        >
          Start Researching Free
        </Link>
      </motion.div>

      <div className="grid md:grid-cols-2 lg:grid-cols-4 gap-6 max-w-6xl mt-24 mb-24 w-full">
        {features.map((f, i) => (
          <GlassCard key={f.title} delay={i * 0.1}>
            <f.icon className="w-8 h-8 text-accent-light mb-4" />
            <h3 className="font-semibold mb-2">{f.title}</h3>
            <p className="text-sm text-gray-400">{f.desc}</p>
          </GlassCard>
        ))}
      </div>
    </main>
  );
}
