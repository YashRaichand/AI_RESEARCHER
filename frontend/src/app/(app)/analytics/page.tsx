"use client";

import { useEffect, useState } from "react";
import { GlassCard } from "@/components/ui/GlassCard";
import { papersApi, Paper } from "@/lib/api";
import {
  BarChart, Bar, XAxis, YAxis, Tooltip, ResponsiveContainer,
  PieChart, Pie, Cell, LineChart, Line,
} from "recharts";

const COLORS = ["#7F77DD", "#A39CFF", "#534AB7", "#9D97E8", "#3E3880", "#C7C2FF", "#221F4D"];
const TOOLTIP_STYLE = { background: "#0d0d1f", border: "1px solid rgba(255,255,255,0.1)", color: "#fff" };

export default function AnalyticsPage() {
  const [papers, setPapers] = useState<Paper[]>([]);

  useEffect(() => {
    papersApi.list(1, 100).then((res) => setPapers(res.data.papers || []));
  }, []);

  const topicData = Object.entries(
    papers.reduce((acc: Record<string, number>, p) => {
      acc[p.topic] = (acc[p.topic] || 0) + 1;
      return acc;
    }, {})
  ).map(([name, value]) => ({ name, value }));

  const statusData = ["pending", "processing", "completed", "failed"].map((s) => ({
    name: s,
    count: papers.filter((p) => p.status === s).length,
  }));

  const byDate = papers.reduce((acc: Record<string, number>, p) => {
    const d = p.created_at?.slice(0, 10) || "unknown";
    acc[d] = (acc[d] || 0) + 1;
    return acc;
  }, {});
  const uploadTimeline = Object.entries(byDate)
    .sort(([a], [b]) => a.localeCompare(b))
    .map(([date, count]) => ({ date: date.slice(5), count }));

  const qualityBuckets = [0, 20, 40, 60, 80].map((min) => ({
    range: `${min}-${min + 20}`,
    count: papers.filter((p) => (p.quality_score || 0) >= min && (p.quality_score || 0) < min + 20).length,
  }));

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-2xl font-semibold">Analytics</h1>
        <p className="text-gray-400 text-sm mt-1">Insights about your research library</p>
      </div>

      <div className="grid md:grid-cols-3 gap-4">
        {[
          { label: "Total Papers", value: papers.length },
          { label: "Completed", value: papers.filter((p) => p.status === "completed").length },
          { label: "Avg Quality", value: papers.length ? Math.round(papers.reduce((s, p) => s + (p.quality_score || 0), 0) / papers.length) : 0 },
        ].map((s) => (
          <GlassCard key={s.label} className="p-5 text-center">
            <p className="text-3xl font-semibold">{s.value}</p>
            <p className="text-gray-400 text-sm mt-1">{s.label}</p>
          </GlassCard>
        ))}
      </div>

      <div className="grid md:grid-cols-2 gap-6">
        <GlassCard>
          <h3 className="font-medium mb-4">Topic Distribution</h3>
          <ResponsiveContainer width="100%" height={220}>
            <PieChart>
              <Pie data={topicData} dataKey="value" nameKey="name" cx="50%" cy="50%" outerRadius={80}>
                {topicData.map((_, i) => <Cell key={i} fill={COLORS[i % COLORS.length]} />)}
              </Pie>
              <Tooltip contentStyle={TOOLTIP_STYLE} />
            </PieChart>
          </ResponsiveContainer>
        </GlassCard>

        <GlassCard>
          <h3 className="font-medium mb-4">Status Breakdown</h3>
          <ResponsiveContainer width="100%" height={220}>
            <BarChart data={statusData}>
              <XAxis dataKey="name" tick={{ fill: "#9ca3af", fontSize: 12 }} />
              <YAxis tick={{ fill: "#9ca3af", fontSize: 12 }} />
              <Tooltip contentStyle={TOOLTIP_STYLE} />
              <Bar dataKey="count" fill="#7F77DD" radius={[4, 4, 0, 0]} />
            </BarChart>
          </ResponsiveContainer>
        </GlassCard>

        <GlassCard>
          <h3 className="font-medium mb-4">Upload Timeline</h3>
          <ResponsiveContainer width="100%" height={220}>
            <LineChart data={uploadTimeline}>
              <XAxis dataKey="date" tick={{ fill: "#9ca3af", fontSize: 11 }} />
              <YAxis tick={{ fill: "#9ca3af", fontSize: 12 }} />
              <Tooltip contentStyle={TOOLTIP_STYLE} />
              <Line type="monotone" dataKey="count" stroke="#A39CFF" strokeWidth={2} dot={false} />
            </LineChart>
          </ResponsiveContainer>
        </GlassCard>

        <GlassCard>
          <h3 className="font-medium mb-4">Quality Score Distribution</h3>
          <ResponsiveContainer width="100%" height={220}>
            <BarChart data={qualityBuckets}>
              <XAxis dataKey="range" tick={{ fill: "#9ca3af", fontSize: 12 }} />
              <YAxis tick={{ fill: "#9ca3af", fontSize: 12 }} />
              <Tooltip contentStyle={TOOLTIP_STYLE} />
              <Bar dataKey="count" fill="#534AB7" radius={[4, 4, 0, 0]} />
            </BarChart>
          </ResponsiveContainer>
        </GlassCard>
      </div>
    </div>
  );
}
