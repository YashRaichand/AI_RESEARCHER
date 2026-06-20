"use client";

import { useState, useEffect } from "react";
import { Search, Check } from "lucide-react";
import { papersApi, gapsApi, Paper } from "@/lib/api";
import { GlassCard } from "@/components/ui/GlassCard";

export default function GapsPage() {
  const [papers, setPapers] = useState<Paper[]>([]);
  const [selectedIds, setSelectedIds] = useState<string[]>([]);
  const [loading, setLoading] = useState(false);
  const [gaps, setGaps] = useState<any[]>([]);

  useEffect(() => {
    papersApi.list(1, 100).then((res) => setPapers(res.data.papers || []));
  }, []);

  const toggle = (id: string) =>
    setSelectedIds((prev) => (prev.includes(id) ? prev.filter((p) => p !== id) : [...prev, id]));

  const detect = async () => {
    if (selectedIds.length === 0) return;
    setLoading(true);
    try {
      const { data } = await gapsApi.detect(selectedIds);
      setGaps(data.gaps || []);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-2xl font-semibold">Research Gap Explorer</h1>
        <p className="text-gray-400 text-sm mt-1">Discover underexplored topics and opportunities</p>
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
          onClick={detect}
          disabled={loading || selectedIds.length === 0}
          className="px-5 py-2.5 bg-accent hover:bg-accent-dark rounded-lg text-sm font-medium transition disabled:opacity-40"
        >
          {loading ? "Analyzing..." : "Detect Gaps"}
        </button>
      </GlassCard>

      <div className="grid md:grid-cols-2 gap-4">
        {gaps.map((g, i) => (
          <GlassCard key={i} delay={i * 0.05}>
            <div className="flex justify-between items-start mb-2">
              <h3 className="font-medium text-sm">{g.topic}</h3>
              <span className="text-xs px-2 py-1 bg-accent/15 text-accent-light rounded-full">
                {g.novelty_score}/100
              </span>
            </div>
            <p className="text-sm text-gray-400 mb-3">{g.description}</p>
            {g.suggested_experiments?.length > 0 && (
              <div>
                <p className="text-xs text-gray-500 mb-1">Suggested experiments:</p>
                <ul className="text-xs text-gray-400 list-disc list-inside space-y-1">
                  {g.suggested_experiments.slice(0, 3).map((s: string, si: number) => (
                    <li key={si}>{s}</li>
                  ))}
                </ul>
              </div>
            )}
          </GlassCard>
        ))}
      </div>
    </div>
  );
}
