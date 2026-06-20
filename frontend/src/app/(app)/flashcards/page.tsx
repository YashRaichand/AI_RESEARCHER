"use client";

import { useState, useEffect } from "react";
import { motion, AnimatePresence } from "framer-motion";
import { Check, ChevronLeft, ChevronRight } from "lucide-react";
import { papersApi, flashcardsApi, Paper } from "@/lib/api";
import { GlassCard } from "@/components/ui/GlassCard";

export default function FlashcardsPage() {
  const [papers, setPapers] = useState<Paper[]>([]);
  const [selectedPaperId, setSelectedPaperId] = useState<string>("");
  const [loading, setLoading] = useState(false);
  const [cards, setCards] = useState<any[]>([]);
  const [current, setCurrent] = useState(0);
  const [flipped, setFlipped] = useState(false);

  useEffect(() => {
    papersApi.list(1, 100).then((res) => setPapers(res.data.papers || []));
  }, []);

  const generate = async () => {
    if (!selectedPaperId) return;
    setLoading(true);
    try {
      const { data } = await flashcardsApi.generate(selectedPaperId);
      setCards(data.flashcards || []);
      setCurrent(0);
      setFlipped(false);
    } finally {
      setLoading(false);
    }
  };

  const markLearned = async () => {
    const card = cards[current];
    if (card?.id) await flashcardsApi.markLearned(card.id);
    next();
  };

  const next = () => {
    setFlipped(false);
    setTimeout(() => setCurrent((c) => Math.min(c + 1, cards.length - 1)), 150);
  };

  const prev = () => {
    setFlipped(false);
    setTimeout(() => setCurrent((c) => Math.max(c - 1, 0)), 150);
  };

  const diffColor: Record<string, string> = {
    easy: "text-green-400",
    medium: "text-yellow-400",
    hard: "text-red-400",
  };

  return (
    <div className="space-y-6 max-w-2xl mx-auto">
      <div>
        <h1 className="text-2xl font-semibold">Flashcards</h1>
        <p className="text-gray-400 text-sm mt-1">Study key concepts from your papers</p>
      </div>

      <GlassCard>
        <label className="text-sm text-gray-400">Select a Paper</label>
        <select
          value={selectedPaperId}
          onChange={(e) => setSelectedPaperId(e.target.value)}
          className="w-full mt-1 mb-4 px-4 py-2.5 bg-white/5 border border-white/10 rounded-lg focus:outline-none focus:border-accent transition"
        >
          <option value="">Choose a paper...</option>
          {papers.map((p) => (
            <option key={p.id} value={p.id}>{p.title}</option>
          ))}
        </select>
        <button
          onClick={generate}
          disabled={loading || !selectedPaperId}
          className="px-5 py-2.5 bg-accent hover:bg-accent-dark rounded-lg text-sm font-medium transition disabled:opacity-40"
        >
          {loading ? "Generating..." : "Generate Flashcards"}
        </button>
      </GlassCard>

      {cards.length > 0 && (
        <div>
          <div className="flex justify-between items-center mb-4">
            <p className="text-sm text-gray-400">Card {current + 1} of {cards.length}</p>
            <div className="flex gap-2">
              <span className={`text-xs ${diffColor[cards[current]?.difficulty] || ""}`}>
                {cards[current]?.difficulty}
              </span>
              <span className="text-xs text-gray-500 bg-white/5 px-2 py-1 rounded-full">
                {cards[current]?.card_type}
              </span>
            </div>
          </div>

          <div className="w-full bg-white/10 rounded-full h-1.5 mb-6">
            <div
              className="bg-accent h-1.5 rounded-full transition-all"
              style={{ width: `${((current + 1) / cards.length) * 100}%` }}
            />
          </div>

          <div
            onClick={() => setFlipped((f) => !f)}
            className="cursor-pointer"
            style={{ perspective: "1000px" }}
          >
            <motion.div
              animate={{ rotateY: flipped ? 180 : 0 }}
              transition={{ duration: 0.4 }}
              style={{ transformStyle: "preserve-3d", position: "relative", minHeight: 200 }}
            >
              <div
                className="glass-card p-8 absolute inset-0 flex flex-col items-center justify-center text-center"
                style={{ backfaceVisibility: "hidden" }}
              >
                <p className="text-xs text-gray-500 mb-3 uppercase tracking-wider">Question</p>
                <p className="text-lg font-medium">{cards[current]?.front}</p>
                <p className="text-xs text-gray-500 mt-6">Click to reveal answer</p>
              </div>
              <div
                className="glass-card p-8 absolute inset-0 flex flex-col items-center justify-center text-center bg-accent/10"
                style={{ backfaceVisibility: "hidden", transform: "rotateY(180deg)" }}
              >
                <p className="text-xs text-gray-500 mb-3 uppercase tracking-wider">Answer</p>
                <p className="text-base text-gray-200">{cards[current]?.back}</p>
              </div>
            </motion.div>
          </div>

          <div className="flex justify-between items-center mt-6">
            <button
              onClick={prev}
              disabled={current === 0}
              className="p-2 glass rounded-lg disabled:opacity-30 transition"
            >
              <ChevronLeft className="w-5 h-5" />
            </button>
            <button
              onClick={markLearned}
              className="flex items-center gap-2 px-4 py-2 bg-green-500/20 hover:bg-green-500/30 text-green-400 rounded-lg text-sm transition"
            >
              <Check className="w-4 h-4" /> Mark Learned
            </button>
            <button
              onClick={next}
              disabled={current === cards.length - 1}
              className="p-2 glass rounded-lg disabled:opacity-30 transition"
            >
              <ChevronRight className="w-5 h-5" />
            </button>
          </div>
        </div>
      )}
    </div>
  );
}
