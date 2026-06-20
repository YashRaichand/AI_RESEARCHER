"use client";

import { useState, useEffect } from "react";
import { Lightbulb, Check } from "lucide-react";
import { papersApi, ideasApi, Paper } from "@/lib/api";
import { GlassCard } from "@/components/ui/GlassCard";

export default function IdeasPage() {
  const [papers, setPapers] = useState<Paper[]>([]);
  const [selectedIds, setSelectedIds] = useState<string[]>([]);
  const [loading, setLoading] = useState(false);
  const [ideas, setIdeas] = useState<any[]>([]);

  useEffect(() => {
    papersApi.list(1, 100).then((res) => setPapers(res.data.papers || []));
  }, []);

  const toggle = (id: string) =>
    setSelectedIds((prev) => (prev.includes(id) ? prev.filter((p) => p !== id) : [...prev, id]));

  const generate = async () => {
    if (selectedIds.length === 0) return;
    setLoading(true);
    try {
      const { data } = await ideasApi.generate(selectedIds);
      setIdeas(data.ideas || []);
    } finally {
      setLoading(false);
    }
  };

  const difficultyColor: Record<string, string> = {
    easy: "text-green-400 bg-green-500/10",
    medium: "text-yellow-400 bg-yellow-500/10",
    hard: "text-red-400 bg-red-500/10",
  };

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-2xl font-semibold">Research Idea Generator</h1>
        <p className="text-gray-400 text-sm mt-1">Discover novel research directions from your papers</p>
      </div>

      <GlassCard>
        <p className="text-sm text-gray-400 mb-2">Select Papers ({selectedIds.length} selected)</p>
        <div className="max-h-48 overflow-y-auto space-y-2 mb-4">
          {papers.map((p) => (
            <div
              key={p.id}
              onClick={() => toggle(p.id)}
              className={`p-2.5 rounded-lg cursor-pointer border flex items-center gap-2 text-sm ${
                selectedIds.includes(p.id) ? "bg-accent/15 border-accent/40" : "bg-white/5 border-white/10"
              }`}
            >
              <div className={`w-4 h-4 rounded border flex items-center justify-center ${selectedIds.includes(p.id) ? "bg-accent border-accent" : "border-gray-500"}`}>
                {selectedIds.includes(p.id) && <Check className="w-3 h-3" />}
              </div>
              {p.title}
            </div>
          ))}
        </div>
        <button
          onClick={generate}
          disabled={loading || selectedIds.length === 0}
          className="px-5 py-2.5 bg-accent hover:bg-accent-dark rounded-lg text-sm font-medium transition disabled:opacity-40"
        >
          {loading ? "Generating ideas..." : "Generate Ideas"}
        </button>
      </GlassCard>

      <div className="grid md:grid-cols-2 gap-4">
        {ideas.map((idea, i) => (
          <GlassCard key={i} delay={i * 0.05}>
            <div className="flex justify-between items-start mb-2">
              <div className="flex items-center gap-2">
                <Lightbulb className="w-4 h-4 text-accent-light" />
                <h3 className="font-medium text-sm">{idea.title}</h3>
              </div>
              <span className={`text-xs px-2 py-1 rounded-full ${difficultyColor[idea.difficulty] || "text-gray-400 bg-gray-500/10"}`}>
                {idea.difficulty}
              </span>
            </div>
            <p className="text-sm text-gray-400 mb-3">{idea.description}</p>
            {idea.rationale && (
              <p className="text-xs text-gray-500 mb-3 italic">{idea.rationale}</p>
            )}
            <div className="flex items-center justify-between">
              <div className="flex items-center gap-2">
                <div className="w-24 bg-white/10 rounded-full h-1.5">
                  <div className="bg-accent h-1.5 rounded-full" style={{ width: `${idea.novelty_score || 0}%` }} />
                </div>
                <span className="text-xs text-gray-500">Novelty {idea.novelty_score || 0}</span>
              </div>
            </div>
            {idea.research_questions?.length > 0 && (
              <div className="mt-3 pt-3 border-t border-white/10">
                <p className="text-xs text-gray-500 mb-1">Research questions:</p>
                {idea.research_questions.slice(0, 2).map((q: string, qi: number) => (
                  <p key={qi} className="text-xs text-gray-400">• {q}</p>
                ))}
              </div>
            )}
          </GlassCard>
        ))}
      </div>
    </div>
  );
}
