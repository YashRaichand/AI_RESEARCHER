"use client";

import { useState, useEffect } from "react";
import { Presentation, Check, Download } from "lucide-react";
import { papersApi, slidesApi, Paper } from "@/lib/api";
import { GlassCard } from "@/components/ui/GlassCard";

export default function SlidesPage() {
  const [papers, setPapers] = useState<Paper[]>([]);
  const [selectedIds, setSelectedIds] = useState<string[]>([]);
  const [title, setTitle] = useState("Research Presentation");
  const [loading, setLoading] = useState(false);
  const [downloadUrl, setDownloadUrl] = useState<string | null>(null);

  useEffect(() => {
    papersApi.list(1, 100).then((res) => setPapers(res.data.papers || []));
  }, []);

  const toggle = (id: string) =>
    setSelectedIds((prev) => (prev.includes(id) ? prev.filter((p) => p !== id) : [...prev, id]));

  const generate = async () => {
    if (selectedIds.length === 0) return;
    setLoading(true);
    setDownloadUrl(null);
    try {
      const { data } = await slidesApi.generate(selectedIds, title);
      const blob = new Blob([data], {
        type: "application/vnd.openxmlformats-officedocument.presentationml.presentation",
      });
      const url = URL.createObjectURL(blob);
      setDownloadUrl(url);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="space-y-6 max-w-2xl mx-auto">
      <div>
        <h1 className="text-2xl font-semibold">Presentation Builder</h1>
        <p className="text-gray-400 text-sm mt-1">Generate a PPTX presentation from selected papers</p>
      </div>

      <GlassCard>
        <label className="text-sm text-gray-400">Presentation Title</label>
        <input
          value={title}
          onChange={(e) => setTitle(e.target.value)}
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
          disabled={loading || selectedIds.length === 0}
          className="flex items-center gap-2 px-5 py-2.5 bg-accent hover:bg-accent-dark rounded-lg text-sm font-medium transition disabled:opacity-40"
        >
          <Presentation className="w-4 h-4" />
          {loading ? "Generating..." : "Generate Presentation"}
        </button>
      </GlassCard>

      {downloadUrl && (
        <GlassCard>
          <p className="text-sm text-green-400 mb-4">✓ Presentation ready!</p>
          <a
            href={downloadUrl}
            download={`${title}.pptx`}
            className="flex items-center gap-2 px-5 py-2.5 bg-green-500/20 hover:bg-green-500/30 text-green-400 rounded-lg text-sm transition w-fit"
          >
            <Download className="w-4 h-4" /> Download PPTX
          </a>
        </GlassCard>
      )}
    </div>
  );
}
