"use client";

import { useState, useCallback } from "react";
import { useDropzone } from "react-dropzone";
import { motion } from "framer-motion";
import { UploadCloud, FileText, CheckCircle, XCircle } from "lucide-react";
import { papersApi } from "@/lib/api";
import { GlassCard } from "@/components/ui/GlassCard";
import { useRouter } from "next/navigation";

export default function UploadPage() {
  const [uploading, setUploading] = useState(false);
  const [progress, setProgress] = useState(0);
  const [result, setResult] = useState<any>(null);
  const [error, setError] = useState("");
  const router = useRouter();

  const onDrop = useCallback(async (acceptedFiles: File[]) => {
    const file = acceptedFiles[0];
    if (!file) return;
    setUploading(true);
    setError("");
    setResult(null);
    try {
      const { data } = await papersApi.upload(file, setProgress);
      setResult(data);
    } catch (err: any) {
      setError(err.response?.data?.detail || "Upload failed");
    } finally {
      setUploading(false);
    }
  }, []);

  const { getRootProps, getInputProps, isDragActive } = useDropzone({
    onDrop,
    accept: {
      "application/pdf": [".pdf"],
      "application/vnd.openxmlformats-officedocument.wordprocessingml.document": [".docx"],
      "text/plain": [".txt"],
    },
    maxFiles: 1,
    disabled: uploading,
  });

  return (
    <div className="max-w-2xl mx-auto space-y-6">
      <div>
        <h1 className="text-2xl font-semibold">Upload Paper</h1>
        <p className="text-gray-400 text-sm mt-1">PDF, DOCX, or TXT — up to 50MB</p>
      </div>

      <div
        {...getRootProps()}
        className={`glass-card p-12 text-center cursor-pointer transition border-2 border-dashed ${
          isDragActive ? "border-accent bg-accent/5" : "border-white/10"
        }`}
      >
        <input {...getInputProps()} />
        <UploadCloud className="w-12 h-12 mx-auto text-accent-light mb-4" />
        {isDragActive ? (
          <p>Drop the file here...</p>
        ) : (
          <>
            <p className="font-medium">Drag & drop a paper, or click to browse</p>
            <p className="text-sm text-gray-500 mt-1">Supports PDF, DOCX, TXT</p>
          </>
        )}
      </div>

      {uploading && (
        <GlassCard>
          <div className="flex items-center gap-3 mb-3">
            <FileText className="w-5 h-5 text-accent-light" />
            <span className="text-sm">Uploading...</span>
          </div>
          <div className="w-full bg-white/10 rounded-full h-2">
            <motion.div
              className="bg-accent h-2 rounded-full"
              initial={{ width: 0 }}
              animate={{ width: `${progress}%` }}
            />
          </div>
          <p className="text-xs text-gray-500 mt-2">{progress}%</p>
        </GlassCard>
      )}

      {error && (
        <GlassCard className="border-red-500/30">
          <div className="flex items-center gap-3 text-red-400">
            <XCircle className="w-5 h-5" />
            <span className="text-sm">{error}</span>
          </div>
        </GlassCard>
      )}

      {result && (
        <GlassCard>
          <div className="flex items-center gap-3 mb-4 text-green-400">
            <CheckCircle className="w-5 h-5" />
            <span className="text-sm font-medium">Upload successful — processing started</span>
          </div>
          <p className="text-sm text-gray-300 mb-1">
            <span className="text-gray-500">Title:</span> {result.title}
          </p>
          <p className="text-sm text-gray-300 mb-1">
            <span className="text-gray-500">Status:</span> {result.status}
          </p>
          <button
            onClick={() => router.push("/papers")}
            className="mt-4 px-4 py-2 bg-accent hover:bg-accent-dark rounded-lg text-sm transition"
          >
            View in Library
          </button>
        </GlassCard>
      )}
    </div>
  );
}
