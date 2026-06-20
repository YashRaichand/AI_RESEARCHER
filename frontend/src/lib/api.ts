import axios, { AxiosInstance } from "axios";

const API_URL = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000/api/v1";

export const api: AxiosInstance = axios.create({
  baseURL: API_URL,
  headers: { "Content-Type": "application/json" },
});

api.interceptors.request.use((config) => {
  if (typeof window !== "undefined") {
    const token = localStorage.getItem("access_token");
    if (token) config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
});

api.interceptors.response.use(
  (response) => response,
  async (error) => {
    const originalRequest = error.config;
    if (error.response?.status === 401 && !originalRequest._retry) {
      originalRequest._retry = true;
      try {
        const refreshToken = localStorage.getItem("refresh_token");
        if (refreshToken) {
          const { data } = await axios.post(`${API_URL}/auth/refresh`, {
            refresh_token: refreshToken,
          });
          localStorage.setItem("access_token", data.access_token);
          originalRequest.headers.Authorization = `Bearer ${data.access_token}`;
          return api(originalRequest);
        }
      } catch {
        localStorage.removeItem("access_token");
        localStorage.removeItem("refresh_token");
        window.location.href = "/login";
      }
    }
    return Promise.reject(error);
  }
);

// ── Typed API functions ──────────────────────────────────────────────
export interface User {
  id: string;
  email: string;
  name: string;
  avatar_url?: string;
  role: string;
}

export interface Paper {
  id: string;
  title: string;
  authors: string[];
  abstract?: string;
  keywords: string[];
  file_type: string;
  status: string;
  topic: string;
  quality_score?: number;
  page_count: number;
  word_count: number;
  created_at: string;
}

export const authApi = {
  login: (email: string, password: string) =>
    api.post("/auth/login", { email, password }),
  register: (email: string, password: string, name: string) =>
    api.post("/auth/register", { email, password, name }),
  me: () => api.get<User>("/auth/me"),
  logout: () => {
    localStorage.removeItem("access_token");
    localStorage.removeItem("refresh_token");
  },
};

export const papersApi = {
  upload: (file: File, onProgress?: (pct: number) => void) => {
    const formData = new FormData();
    formData.append("file", file);
    return api.post<Paper>("/papers/upload", formData, {
      headers: { "Content-Type": "multipart/form-data" },
      onUploadProgress: (e) => {
        if (onProgress && e.total) onProgress(Math.round((e.loaded / e.total) * 100));
      },
    });
  },
  list: (page = 1, perPage = 20) =>
    api.get(`/papers?page=${page}&per_page=${perPage}`),
  get: (id: string) => api.get<Paper>(`/papers/${id}`),
  delete: (id: string) => api.delete(`/papers/${id}`),
  status: (id: string) => api.get(`/papers/${id}/status`),
};

export const chatApi = {
  createSession: (paperIds: string[], title?: string) =>
    api.post("/chat/sessions", { paper_ids: paperIds, title }),
  listSessions: () => api.get("/chat/sessions"),
  getHistory: (sessionId: string) => api.get(`/chat/sessions/${sessionId}/history`),
};

export const literatureReviewApi = {
  generate: (topic: string, paperIds: string[]) =>
    api.post("/literature-review/generate", { topic, paper_ids: paperIds }),
  list: () => api.get("/literature-review"),
};

export const gapsApi = {
  detect: (paperIds: string[]) => api.post("/gaps/detect", { paper_ids: paperIds }),
};

export const compareApi = {
  compare: (paperIds: string[]) => api.post("/compare", { paper_ids: paperIds }),
};

export const graphApi = {
  build: (paperIds: string[], title?: string) =>
    api.post("/knowledge-graph/build", { paper_ids: paperIds, title }),
  list: () => api.get("/knowledge-graph"),
};

export const ideasApi = {
  generate: (paperIds: string[]) => api.post("/ideas/generate", { paper_ids: paperIds }),
  list: () => api.get("/ideas"),
};

export const flashcardsApi = {
  generate: (paperId: string) => api.post("/flashcards/generate", { paper_id: paperId }),
  list: () => api.get("/flashcards"),
  markLearned: (cardId: string) => api.patch(`/flashcards/${cardId}/learned`),
};

export const slidesApi = {
  generate: (paperIds: string[], title?: string) =>
    api.post("/slides/generate", { paper_ids: paperIds, title }, { responseType: "blob" }),
};
