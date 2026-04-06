const BASE = (import.meta.env.VITE_API_BASE as string | undefined)?.replace(/\/$/, "") || "/api";

/** Stored JWT. Readable by any script on this origin (XSS risk); prefer httpOnly cookies for production apps handling sensitive data. */
const TOKEN_KEY = "notewise_access_token";

export function getAccessToken(): string | null {
  try {
    return localStorage.getItem(TOKEN_KEY);
  } catch {
    return null;
  }
}

export function setAccessToken(token: string | null): void {
  try {
    if (token) localStorage.setItem(TOKEN_KEY, token);
    else localStorage.removeItem(TOKEN_KEY);
  } catch {
    /* ignore */
  }
}

function mergeInit(init?: RequestInit): RequestInit {
  const headers = new Headers(init?.headers);
  const t = getAccessToken();
  if (t) headers.set("Authorization", `Bearer ${t}`);
  return { ...init, headers };
}

function parseDetail(data: unknown): string {
  if (!data || typeof data !== "object") return "Request failed";
  const d = (data as { detail?: unknown }).detail;
  if (typeof d === "string") return d;
  if (Array.isArray(d)) {
    return d
      .map((x) =>
        typeof x === "object" && x !== null && "msg" in x
          ? String((x as { msg: string }).msg)
          : String(x)
      )
      .join(", ");
  }
  return "Request failed";
}

export interface AuthUser {
  id: string;
  email: string;
  is_active: boolean;
}

export async function authRegister(email: string, password: string): Promise<void> {
  const res = await fetch(`${BASE}/auth/register`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ email, password }),
  });
  const data = await res.json().catch(() => ({}));
  if (!res.ok) throw new Error(parseDetail(data));
  const token = (data as { access_token?: string }).access_token;
  if (!token) throw new Error("No access token returned");
  setAccessToken(token);
}

export async function authLogin(email: string, password: string): Promise<void> {
  const res = await fetch(`${BASE}/auth/login`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ email, password }),
  });
  const data = await res.json().catch(() => ({}));
  if (!res.ok) throw new Error(parseDetail(data));
  const token = (data as { access_token?: string }).access_token;
  if (!token) throw new Error("No access token returned");
  setAccessToken(token);
}

export async function fetchMe(): Promise<AuthUser> {
  const res = await fetch(`${BASE}/auth/me`, mergeInit());
  const data = await res.json().catch(() => ({}));
  if (!res.ok) throw new Error(parseDetail(data));
  return data as AuthUser;
}

export interface TranscriptResult {
  transcript: string;
  confidence?: number;
  status: string;
  disclaimer: string;
}

export async function transcribeFile(file: File): Promise<TranscriptResult> {
  const form = new FormData();
  form.append("file", file);
  const res = await fetch(`${BASE}/transcribe/upload`, mergeInit({ method: "POST", body: form }));
  if (!res.ok) {
    const data = await res.json().catch(() => ({}));
    throw new Error(parseDetail(data));
  }
  return res.json();
}

export async function ragQuery(
  query: string,
  topK = 5
): Promise<{ chunks: { text: string; source: string }[] }> {
  const res = await fetch(
    `${BASE}/rag/query`,
    mergeInit({
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ query, top_k: topK }),
    })
  );
  if (!res.ok) throw new Error(parseDetail(await res.json().catch(() => ({}))));
  return res.json();
}

export interface SOAPNote {
  subjective: string;
  objective: string;
  assessment: string;
  plan: string;
  citations?: string[];
}

export async function generateSOAP(
  transcript: string,
  ragContext?: string
): Promise<SOAPNote> {
  const res = await fetch(
    `${BASE}/soap/generate`,
    mergeInit({
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ transcript, rag_context: ragContext }),
    })
  );
  if (!res.ok) throw new Error(parseDetail(await res.json().catch(() => ({}))));
  return res.json();
}

export async function textToSpeech(text: string): Promise<Blob> {
  const res = await fetch(
    `${BASE}/soap/tts`,
    mergeInit({
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ text }),
    })
  );
  if (!res.ok) throw new Error(parseDetail(await res.json().catch(() => ({}))));
  return res.blob();
}

export async function classifyImage(file: File) {
  const form = new FormData();
  form.append("file", file);
  const res = await fetch(`${BASE}/imaging/classify`, mergeInit({ method: "POST", body: form }));
  if (!res.ok) throw new Error(parseDetail(await res.json().catch(() => ({}))));
  return res.json();
}

/** Chat history (MongoDB via backend; requires Bearer). */

export interface ApiChatMessage {
  id: string;
  role: "user" | "assistant";
  content: string;
  timestamp: number;
}

export interface ApiConversation {
  id: string;
  title: string;
  createdAt: number;
  updatedAt: number;
  messages: ApiChatMessage[];
}

export interface ApiConversationSummary {
  id: string;
  title: string;
  updatedAt: number;
}

export async function listChatConversations(): Promise<ApiConversationSummary[]> {
  const res = await fetch(`${BASE}/chat/conversations`, mergeInit());
  if (!res.ok) throw new Error(parseDetail(await res.json().catch(() => ({}))));
  return res.json();
}

export async function createChatConversation(body: { title?: string } = {}): Promise<ApiConversation> {
  const res = await fetch(
    `${BASE}/chat/conversations`,
    mergeInit({
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(body),
    })
  );
  if (!res.ok) throw new Error(parseDetail(await res.json().catch(() => ({}))));
  return res.json();
}

export async function getChatConversation(id: string): Promise<ApiConversation> {
  const res = await fetch(`${BASE}/chat/conversations/${encodeURIComponent(id)}`, mergeInit());
  if (!res.ok) throw new Error(parseDetail(await res.json().catch(() => ({}))));
  return res.json();
}

export async function appendChatMessage(
  conversationId: string,
  body: { role: "user" | "assistant"; content: string; id?: string; timestamp?: number }
): Promise<ApiConversation> {
  const res = await fetch(
    `${BASE}/chat/conversations/${encodeURIComponent(conversationId)}/messages`,
    mergeInit({
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(body),
    })
  );
  if (!res.ok) throw new Error(parseDetail(await res.json().catch(() => ({}))));
  return res.json();
}

export async function deleteChatConversation(id: string): Promise<void> {
  const res = await fetch(`${BASE}/chat/conversations/${encodeURIComponent(id)}`, mergeInit({ method: "DELETE" }));
  if (!res.ok) throw new Error(parseDetail(await res.json().catch(() => ({}))));
}

/** Scribe session persistence (transcript + SOAP). Requires Bearer. */

export interface ApiScribeSession {
  id: string;
  transcript: string;
  soap: Record<string, unknown> | null;
  linkedConversationId: string | null;
  createdAt: number;
  updatedAt: number;
}

export async function createScribeSession(body: {
  transcript: string;
  soap?: SOAPNote;
  linkedConversationId?: string;
}): Promise<ApiScribeSession> {
  const res = await fetch(
    `${BASE}/scribe/sessions`,
    mergeInit({
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        transcript: body.transcript,
        soap: body.soap,
        linkedConversationId: body.linkedConversationId,
      }),
    })
  );
  if (!res.ok) throw new Error(parseDetail(await res.json().catch(() => ({}))));
  return res.json();
}
