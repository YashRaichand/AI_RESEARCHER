"use client";

import { useEffect, useState } from "react";
import Link from "next/link";
import { Search, Trash2, FileText } from "lucide-react";
import { papersApi, Paper } from "@/lib/api";
import { GlassCard } from "@/components/ui/GlassCard";
import { formatDate, truncate } from "@/lib/utils";

export default function PapersLibraryPage() {
  const [papers, setPapers] = useState<Paper[]>([]);
  const [search, setSearch] = useState("");
  const [loading, setLoading] = useState(true);

  const load = () => {
    papersApi
      .list(1, 100)
      .then((res) => setPapers(res.data.papers || []))
      .finally(() => setLoading(false));
  };

  useEffect(() => {
    load();
  }, []);

  const handleDelete = async (id: string) => {
    await papersApi.delete(id);
    setPapers((prev) => prev.filter((p) => p.id !== id));
  };

  const filtered = papers.filter((p) =>
    p.title.toLowerCase().includes(search.toLowerCase())
  );

  return (
    <div className="space-y-6">
      <div className="flex justify-between items-center">
        <div>
          <h1 className="text-2xl font-semibold">Paper Library</h1>
          <p className="text-gray-400 text-sm mt-1">{papers.length} papers total</p>
        </div>
        <Link
          href="/papers/upload"
          className="px-4 py-2 bg-accent hover:bg-accent-dark rounded-lg text-sm font-medium transition"
        >
          + Upload New
        </Link>
      </div>

      <div className="relative">
        <Search className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-gray-500" />
        <input
          value={search}
          onChange={(e) => setSearch(e.target.value)}
          placeholder="Search papers..."
          className="w-full pl-10 pr-4 py-2.5 bg-white/5 border border-white/10 rounded-lg focus:outline-none focus:border-accent transition"
        />
      </div>

      {loading ? (
        <p className="text-gray-500 text-sm">Loading papers...</p>
      ) : filtered.length === 0 ? (
        <GlassCard className="text-center py-12">
          <FileText className="w-10 h-10 mx-auto text-gray-600 mb-3" />
          <p className="text-gray-400">No papers found</p>
        </GlassCard>
      ) : (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
          {filtered.map((paper, i) => (
            <GlassCard key={paper.id} delay={i * 0.03}>
              <div className="flex justify-between items-start mb-3">
                <span
                  className={`text-xs px-2 py-1 rounded-full ${
                    paper.status === "completed"
                      ? "bg-green-500/10 text-green-400"
                      : paper.status === "processing"
                      ? "bg-yellow-500/10 text-yellow-400"
                      : paper.status === "failed"
                      ? "bg-red-500/10 text-red-400"
                      : "bg-gray-500/10 text-gray-400"
                  }`}
                >
                  {paper.status}
                </span>
                <button
                  onClick={() => handleDelete(paper.id)}
                  className="text-gray-500 hover:text-red-400 transition"
                >
                  <Trash2 className="w-4 h-4" />
                </button>
              </div>
              <h3 className="font-medium text-sm mb-2">{truncate(paper.title, 80)}</h3>
              <p className="text-xs text-gray-500 mb-3">{truncate(paper.abstract || "No abstract", 100)}</p>
              <div className="flex justify-between items-center text-xs text-gray-500">
                <span>{paper.topic}</span>
                <span>{formatDate(paper.created_at)}</span>
              </div>
              {paper.quality_score && (
                <div className="mt-3 flex items-center gap-2">
                  <div className="flex-1 bg-white/10 rounded-full h-1.5">
                    <div
                      className="bg-accent h-1.5 rounded-full"
                      style={{ width: `${paper.quality_score}%` }}
                    />
                  </div>
                  <span className="text-xs text-gray-500">{Math.round(paper.quality_score)}</span>
                </div>
              )}
            </GlassCard>
          ))}
        </div>
      )}
    </div>
  );
}
