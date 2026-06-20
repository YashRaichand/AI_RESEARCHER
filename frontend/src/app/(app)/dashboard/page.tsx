"use client";

import { useEffect, useState } from "react";
import { motion } from "framer-motion";
import { FileText, MessageSquare, Lightbulb, BookOpen, Upload } from "lucide-react";
import Link from "next/link";
import { GlassCard } from "@/components/ui/GlassCard";
import { papersApi, Paper } from "@/lib/api";
import {
  PieChart, Pie, Cell, ResponsiveContainer, Tooltip,
} from "recharts";

const COLORS = ["#7F77DD", "#A39CFF", "#534AB7", "#9D97E8", "#3E3880", "#C7C2FF", "#221F4D"];

export default function DashboardPage() {
  const [papers, setPapers] = useState<Paper[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    papersApi
      .list(1, 50)
      .then((res) => setPapers(res.data.papers || []))
      .catch(() => {})
      .finally(() => setLoading(false));
  }, []);

  const topicCounts = papers.reduce((acc: Record<string, number>, p) => {
    acc[p.topic] = (acc[p.topic] || 0) + 1;
    return acc;
  }, {});
  const topicData = Object.entries(topicCounts).map(([name, value]) => ({ name, value }));

  const stats = [
    { label: "Papers Uploaded", value: papers.length, icon: FileText },
    { label: "Completed", value: papers.filter((p) => p.status === "completed").length, icon: BookOpen },
    { label: "Processing", value: papers.filter((p) => p.status === "processing").length, icon: MessageSquare },
    { label: "Avg Quality", value: papers.length ? Math.round(papers.reduce((s, p) => s + (p.quality_score || 0), 0) / papers.length) : 0, icon: Lightbulb },
  ];

  return (
    <div className="space-y-8">
      <div className="flex justify-between items-center">
        <div>
          <h1 className="text-2xl font-semibold">Dashboard</h1>
          <p className="text-gray-400 text-sm mt-1">Your research overview</p>
        </div>
        <Link
          href="/papers/upload"
          className="flex items-center gap-2 px-4 py-2 bg-accent hover:bg-accent-dark rounded-lg text-sm font-medium transition"
        >
          <Upload className="w-4 h-4" /> Upload Paper
        </Link>
      </div>

      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
        {stats.map((s, i) => (
          <GlassCard key={s.label} delay={i * 0.05} className="p-5">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-gray-400 text-xs">{s.label}</p>
                <p className="text-3xl font-semibold mt-1">{s.value}</p>
              </div>
              <s.icon className="w-8 h-8 text-accent-light/70" />
            </div>
          </GlassCard>
        ))}
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <GlassCard>
          <h3 className="font-medium mb-4">Topic Distribution</h3>
          {topicData.length > 0 ? (
            <ResponsiveContainer width="100%" height={260}>
              <PieChart>
                <Pie data={topicData} dataKey="value" nameKey="name" cx="50%" cy="50%" outerRadius={90} label>
                  {topicData.map((_, i) => (
                    <Cell key={i} fill={COLORS[i % COLORS.length]} />
                  ))}
                </Pie>
                <Tooltip contentStyle={{ background: "#0d0d1f", border: "1px solid rgba(255,255,255,0.1)" }} />
              </PieChart>
            </ResponsiveContainer>
          ) : (
            <p className="text-gray-500 text-sm py-12 text-center">No papers yet — upload one to see insights</p>
          )}
        </GlassCard>

        <GlassCard>
          <h3 className="font-medium mb-4">Recent Papers</h3>
          <div className="space-y-3 max-h-64 overflow-y-auto">
            {loading ? (
              <p className="text-gray-500 text-sm">Loading...</p>
            ) : papers.length === 0 ? (
              <p className="text-gray-500 text-sm">No papers uploaded yet.</p>
            ) : (
              papers.slice(0, 6).map((p) => (
                <div key={p.id} className="flex items-center justify-between p-3 bg-white/5 rounded-lg">
                  <div className="truncate pr-4">
                    <p className="text-sm truncate">{p.title}</p>
                    <p className="text-xs text-gray-500">{p.topic}</p>
                  </div>
                  <span
                    className={`text-xs px-2 py-1 rounded-full whitespace-nowrap ${
                      p.status === "completed"
                        ? "bg-green-500/10 text-green-400"
                        : p.status === "processing"
                        ? "bg-yellow-500/10 text-yellow-400"
                        : p.status === "failed"
                        ? "bg-red-500/10 text-red-400"
                        : "bg-gray-500/10 text-gray-400"
                    }`}
                  >
                    {p.status}
                  </span>
                </div>
              ))
            )}
          </div>
        </GlassCard>
      </div>
    </div>
  );
}
