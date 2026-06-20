"use client";

import { useState, useEffect } from "react";
import { BookOpen, Check } from "lucide-react";
import { papersApi, literatureReviewApi, Paper } from "@/lib/api";
import { GlassCard } from "@/components/ui/GlassCard";

export default function LiteratureReviewPage() {
  const [papers, setPapers] = useState<Paper[]>([]);
  const [selectedIds, setSelectedIds] = useState<string[]>([]);
  const [topic, setTopic] = useState("");
  const [loading, setLoading] = useState(false);
  const [review, setReview] = useState<any>(null);

  useEffect(() => {
    papersApi.list(1, 100).then((res) => setPapers(res.data.papers || []));
  }, []);

  const toggle = (id: string) =>
    setSelectedIds((prev) => (prev.includes(id) ? prev.filter((p) => p !== id) : [...prev, id]));

  const generate = async () => {
    if (!topic || selectedIds.length === 0) return;
    setLoading(true);
    try {
      const { data } = await literatureReviewApi.generate(topic, selectedIds);
      setReview(data);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-2xl font-semibold">Literature Review Generator</h1>
        <p className="text-gray-400 text-sm mt-1">Generate a structured academic review from your papers</p>
      </div>

      <GlassCard>
        <label className="text-sm text-gray-400">Research Topic</label>
        <input
          value={topic}
          onChange={(e) => setTopic(e.target.value)}
          placeholder="e.g. Transformer optimization techniques"
          className="w-full mt-1 mb-4 px-4 py-2.5 bg-white/5 border border-white/10 rounded-lg focus:outline-none focus:border-accent transition"
        />
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
          disabled={loading || !topic || selectedIds.length === 0}
          className="px-5 py-2.5 bg-accent hover:bg-accent-dark rounded-lg text-sm font-medium transition disabled:opacity-40"
        >
          {loading ? "Generating..." : "Generate Review"}
        </button>
      </GlassCard>

      {review && (
        <GlassCard>
          <div className="flex items-center gap-2 mb-4">
            <BookOpen className="w-5 h-5 text-accent-light" />
            <h2 className="font-medium">{review.topic}</h2>
          </div>
          <div className="prose prose-invert prose-sm max-w-none whitespace-pre-wrap text-gray-300">
            {review.content}
          </div>
        </GlassCard>
      )}
    </div>
  );
}
