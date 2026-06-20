"use client";

import { useState, useEffect, useRef } from "react";
import { Check } from "lucide-react";
import { papersApi, graphApi, Paper } from "@/lib/api";
import { GlassCard } from "@/components/ui/GlassCard";

const TYPE_COLORS: Record<string, string> = {
  paper: "#A39CFF",
  author: "#7F77DD",
  topic: "#2DD4BF",
  concept: "#FBBF24",
};

export default function KnowledgeGraphPage() {
  const [papers, setPapers] = useState<Paper[]>([]);
  const [selectedIds, setSelectedIds] = useState<string[]>([]);
  const [graph, setGraph] = useState<any>(null);
  const [loading, setLoading] = useState(false);
  const canvasRef = useRef<HTMLCanvasElement>(null);

  useEffect(() => {
    papersApi.list(1, 100).then((res) => setPapers(res.data.papers || []));
  }, []);

  useEffect(() => {
    if (!graph || !canvasRef.current) return;
    const canvas = canvasRef.current;
    const ctx = canvas.getContext("2d");
    if (!ctx) return;
    const width = canvas.width;
    const height = canvas.height;
    ctx.clearRect(0, 0, width, height);

    const nodes = graph.nodes.map((n: any, i: number) => ({
      ...n,
      x: width / 2 + Math.cos((i / graph.nodes.length) * 2 * Math.PI) * 200,
      y: height / 2 + Math.sin((i / graph.nodes.length) * 2 * Math.PI) * 200,
    }));
    const nodeMap = Object.fromEntries(nodes.map((n: any) => [n.id, n]));

    ctx.strokeStyle = "rgba(255,255,255,0.15)";
    graph.edges.forEach((e: any) => {
      const s = nodeMap[e.source];
      const t = nodeMap[e.target];
      if (s && t) {
        ctx.beginPath();
        ctx.moveTo(s.x, s.y);
        ctx.lineTo(t.x, t.y);
        ctx.stroke();
      }
    });

    nodes.forEach((n: any) => {
      ctx.beginPath();
      ctx.arc(n.x, n.y, 8 + n.weight * 6, 0, 2 * Math.PI);
      ctx.fillStyle = TYPE_COLORS[n.type] || "#888";
      ctx.fill();
      ctx.fillStyle = "#fff";
      ctx.font = "10px sans-serif";
      ctx.fillText(n.label.slice(0, 20), n.x + 12, n.y + 4);
    });
  }, [graph]);

  const toggle = (id: string) =>
    setSelectedIds((prev) => (prev.includes(id) ? prev.filter((p) => p !== id) : [...prev, id]));

  const build = async () => {
    if (selectedIds.length === 0) return;
    setLoading(true);
    try {
      const { data } = await graphApi.build(selectedIds, "My Knowledge Graph");
      setGraph(data);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-2xl font-semibold">Knowledge Graph</h1>
        <p className="text-gray-400 text-sm mt-1">Visualize relationships between papers, authors, and topics</p>
      </div>

      <GlassCard>
        <p className="text-sm text-gray-400 mb-2">Select Papers ({selectedIds.length} selected)</p>
        <div className="max-h-40 overflow-y-auto space-y-2 mb-4">
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
          onClick={build}
          disabled={loading || selectedIds.length === 0}
          className="px-5 py-2.5 bg-accent hover:bg-accent-dark rounded-lg text-sm font-medium transition disabled:opacity-40"
        >
          {loading ? "Building..." : "Build Graph"}
        </button>
      </GlassCard>

      {graph && (
        <GlassCard>
          <canvas ref={canvasRef} width={800} height={500} className="w-full" />
          <div className="flex gap-4 mt-4 text-xs text-gray-400">
            {Object.entries(TYPE_COLORS).map(([type, color]) => (
              <div key={type} className="flex items-center gap-1.5">
                <div className="w-2.5 h-2.5 rounded-full" style={{ background: color }} />
                {type}
              </div>
            ))}
          </div>
        </GlassCard>
      )}
    </div>
  );
}
