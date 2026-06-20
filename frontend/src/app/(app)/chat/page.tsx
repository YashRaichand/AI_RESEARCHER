"use client";

import { useState, useEffect, useRef } from "react";
import { Send, FileText, Check } from "lucide-react";
import { papersApi, chatApi, Paper, api } from "@/lib/api";
import { GlassCard } from "@/components/ui/GlassCard";

interface Message {
  role: "user" | "assistant";
  content: string;
  citations?: any[];
}

export default function ChatPage() {
  const [papers, setPapers] = useState<Paper[]>([]);
  const [selectedIds, setSelectedIds] = useState<string[]>([]);
  const [sessionId, setSessionId] = useState<string | null>(null);
  const [messages, setMessages] = useState<Message[]>([]);
  const [input, setInput] = useState("");
  const [streaming, setStreaming] = useState(false);
  const bottomRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    papersApi.list(1, 100).then((res) => setPapers(res.data.papers || []));
  }, []);

  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages]);

  const togglePaper = (id: string) => {
    setSelectedIds((prev) =>
      prev.includes(id) ? prev.filter((p) => p !== id) : [...prev, id]
    );
  };

  const startSession = async () => {
    if (selectedIds.length === 0) return;
    const { data } = await chatApi.createSession(selectedIds, "Research Chat");
    setSessionId(data.id);
    setMessages([]);
  };

  const sendMessage = async () => {
    if (!input.trim() || !sessionId || streaming) return;
    const question = input;
    setInput("");
    setMessages((prev) => [...prev, { role: "user", content: question }]);
    setStreaming(true);
    setMessages((prev) => [...prev, { role: "assistant", content: "" }]);

    try {
      const token = localStorage.getItem("access_token");
      const API_URL = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000/api/v1";
      const response = await fetch(`${API_URL}/chat/sessions/${sessionId}/message`, {
        method: "POST",
        headers: { "Content-Type": "application/json", Authorization: `Bearer ${token}` },
        body: JSON.stringify({ question }),
      });
      const reader = response.body?.getReader();
      const decoder = new TextDecoder();
      let fullText = "";
      let citations: any[] = [];

      while (reader) {
        const { done, value } = await reader.read();
        if (done) break;
        const chunk = decoder.decode(value);
        const lines = chunk.split("\n").filter((l) => l.startsWith("data: "));
        for (const line of lines) {
          try {
            const json = JSON.parse(line.replace("data: ", ""));
            if (json.type === "chunk") {
              fullText += json.content;
              setMessages((prev) => {
                const updated = [...prev];
                updated[updated.length - 1] = { role: "assistant", content: fullText, citations };
                return updated;
              });
            } else if (json.type === "citations") {
              citations = json.sources;
            }
          } catch {}
        }
      }
    } finally {
      setStreaming(false);
    }
  };

  return (
    <div className="flex h-[calc(100vh-4rem)] gap-6">
      <div className="w-72 flex flex-col gap-4">
        <h2 className="font-medium">Select Papers</h2>
        <div className="flex-1 overflow-y-auto space-y-2 pr-2">
          {papers.map((p) => (
            <div
              key={p.id}
              onClick={() => togglePaper(p.id)}
              className={`p-3 rounded-lg cursor-pointer border transition flex items-start gap-2 ${
                selectedIds.includes(p.id)
                  ? "bg-accent/15 border-accent/40"
                  : "bg-white/5 border-white/10 hover:bg-white/10"
              }`}
            >
              <div
                className={`w-4 h-4 rounded border flex items-center justify-center mt-0.5 ${
                  selectedIds.includes(p.id) ? "bg-accent border-accent" : "border-gray-500"
                }`}
              >
                {selectedIds.includes(p.id) && <Check className="w-3 h-3" />}
              </div>
              <span className="text-sm truncate">{p.title}</span>
            </div>
          ))}
        </div>
        <button
          onClick={startSession}
          disabled={selectedIds.length === 0}
          className="py-2.5 bg-accent hover:bg-accent-dark rounded-lg text-sm font-medium transition disabled:opacity-40"
        >
          Start Chat ({selectedIds.length})
        </button>
      </div>

      <div className="flex-1 flex flex-col glass-card p-6">
        {!sessionId ? (
          <div className="flex-1 flex items-center justify-center text-gray-500">
            <div className="text-center">
              <FileText className="w-10 h-10 mx-auto mb-3" />
              <p>Select papers and start a chat session</p>
            </div>
          </div>
        ) : (
          <>
            <div className="flex-1 overflow-y-auto space-y-4 mb-4">
              {messages.map((m, i) => (
                <div key={i} className={`flex ${m.role === "user" ? "justify-end" : "justify-start"}`}>
                  <div
                    className={`max-w-[75%] p-3 rounded-xl text-sm whitespace-pre-wrap ${
                      m.role === "user" ? "bg-accent text-white" : "bg-white/5 border border-white/10"
                    }`}
                  >
                    {m.content || (streaming && i === messages.length - 1 ? "Thinking..." : "")}
                    {m.citations && m.citations.length > 0 && (
                      <div className="mt-2 pt-2 border-t border-white/10 text-xs text-gray-400 space-y-1">
                        {m.citations.slice(0, 3).map((c, ci) => (
                          <div key={ci}>📄 {c.section || "Source"} — {c.chunk_text?.slice(0, 60)}...</div>
                        ))}
                      </div>
                    )}
                  </div>
                </div>
              ))}
              <div ref={bottomRef} />
            </div>
            <div className="flex gap-2">
              <input
                value={input}
                onChange={(e) => setInput(e.target.value)}
                onKeyDown={(e) => e.key === "Enter" && sendMessage()}
                placeholder="Ask about the selected papers..."
                className="flex-1 px-4 py-2.5 bg-white/5 border border-white/10 rounded-lg focus:outline-none focus:border-accent transition"
              />
              <button
                onClick={sendMessage}
                disabled={streaming}
                className="px-4 py-2.5 bg-accent hover:bg-accent-dark rounded-lg transition disabled:opacity-40"
              >
                <Send className="w-4 h-4" />
              </button>
            </div>
          </>
        )}
      </div>
    </div>
  );
}
