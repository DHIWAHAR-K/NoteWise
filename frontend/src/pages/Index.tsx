import { useState, useRef, useEffect, useCallback } from "react";
import { useNavigate } from "react-router-dom";
import { ChevronDown, Share } from "lucide-react";
import { ChatSidebar } from "@/components/chat/ChatSidebar";
import { ChatMessage } from "@/components/chat/ChatMessage";
import { ChatInput } from "@/components/chat/ChatInput";
import { WelcomeScreen } from "@/components/chat/WelcomeScreen";
import { TypingIndicator } from "@/components/chat/TypingIndicator";
import { useTheme } from "@/hooks/use-theme";
import {
  Conversation,
  Message,
  FileAttachment,
  genId,
  getMockResponse,
  conversationFromApi,
} from "@/lib/chat-store";
import { useTranscribe } from "@/hooks/use-transcribe";
import {
  generateSOAP,
  listChatConversations,
  getChatConversation,
  createChatConversation,
  appendChatMessage,
  deleteChatConversation,
  createScribeSession,
  fetchMe,
  setAccessToken,
} from "@/lib/api";
import { SOAPDisplay } from "@/components/chat/SOAPDisplay";
import { SOAPNote } from "@/lib/api";

function mergeFilesOntoMessage(
  conv: Conversation,
  messageId: string,
  files: FileAttachment[] | undefined
): Conversation {
  if (!files?.length) return conv;
  return {
    ...conv,
    messages: conv.messages.map((m) =>
      m.id === messageId ? { ...m, files } : m
    ),
  };
}

const Index = () => {
  const navigate = useNavigate();
  const { theme, toggleTheme } = useTheme();
  const { transcribe } = useTranscribe();
  const [userEmail, setUserEmail] = useState<string>("");
  const [soapNotes, setSoapNotes] = useState<Record<string, SOAPNote>>({});
  const [conversations, setConversations] = useState<Conversation[]>([]);
  const [activeId, setActiveId] = useState<string | null>(null);
  const [isTyping, setIsTyping] = useState(false);
  const [sidebarOpen, setSidebarOpen] = useState(true);
  const scrollRef = useRef<HTMLDivElement>(null);

  const active = conversations.find((c) => c.id === activeId) ?? null;
  const hasMessages = active && active.messages.length > 0;

  const scrollToBottom = useCallback(() => {
    setTimeout(() => {
      scrollRef.current?.scrollTo({ top: scrollRef.current.scrollHeight, behavior: "smooth" });
    }, 50);
  }, []);

  useEffect(() => {
    void fetchMe()
      .then((u) => setUserEmail(u.email))
      .catch(() => {});
  }, []);

  useEffect(() => {
    let cancelled = false;
    (async () => {
      try {
        const summaries = await listChatConversations();
        if (cancelled || summaries.length === 0) return;
        const full = await Promise.all(summaries.map((s) => getChatConversation(s.id)));
        if (!cancelled) {
          setConversations(full.map(conversationFromApi));
        }
      } catch {
        /* Chat unavailable — start with empty sidebar */
      }
    })();
    return () => {
      cancelled = true;
    };
  }, []);

  const handleLogout = useCallback(() => {
    setAccessToken(null);
    navigate("/login", { replace: true });
  }, [navigate]);

  const handleNewChat = useCallback(() => {
    setActiveId(null);
  }, []);

  const handleDeleteConversation = useCallback(
    async (id: string) => {
      try {
        await deleteChatConversation(id);
      } catch {
        /* remove locally even if server returns error */
      }
      setConversations((prev) => prev.filter((c) => c.id !== id));
      if (activeId === id) setActiveId(null);
    },
    [activeId]
  );

  const handleSend = useCallback(
    (content: string, files: FileAttachment[]) => {
      const audioFile = files.find(
        (f) => f.type.startsWith("audio/") || f.type.startsWith("video/")
      );

      void (async () => {
        let convId = activeId;
        const userMsg: Message = {
          id: genId(),
          role: "user",
          content,
          files: files.length > 0 ? files : undefined,
          timestamp: Date.now(),
        };

        try {
          if (!convId) {
            const title = content.slice(0, 40) + (content.length > 40 ? "…" : "");
            const created = await createChatConversation({ title });
            convId = created.id;
            setConversations((prev) => [conversationFromApi(created), ...prev]);
            setActiveId(convId);
            const afterUser = await appendChatMessage(convId, {
              id: userMsg.id,
              role: "user",
              content: userMsg.content,
              timestamp: userMsg.timestamp,
            });
            setConversations((prev) =>
              prev.map((c) =>
                c.id === convId
                  ? mergeFilesOntoMessage(conversationFromApi(afterUser), userMsg.id, userMsg.files)
                  : c
              )
            );
          } else {
            setConversations((prev) =>
              prev.map((c) =>
                c.id === convId
                  ? {
                      ...c,
                      messages: [...c.messages, userMsg],
                      updatedAt: Date.now(),
                    }
                  : c
              )
            );
            const afterUser = await appendChatMessage(convId, {
              id: userMsg.id,
              role: "user",
              content: userMsg.content,
              timestamp: userMsg.timestamp,
            });
            setConversations((prev) =>
              prev.map((c) =>
                c.id === convId
                  ? mergeFilesOntoMessage(conversationFromApi(afterUser), userMsg.id, userMsg.files)
                  : c
              )
            );
          }

          scrollToBottom();
          setIsTyping(true);

          const getReply = async (): Promise<string> => {
            if (audioFile) {
              const blob = await fetch(audioFile.url).then((r) => r.blob());
              const file = new File([blob], audioFile.name, { type: audioFile.type });
              const result = await transcribe(file);
              if (result) {
                return `**Transcript** *(${result.disclaimer})*\n\n${result.transcript}`;
              }
              return "Transcription failed. Please check your API key and try again.";
            }
            return getMockResponse();
          };

          const replyContent = await getReply();
          const aiMsg: Message = {
            id: genId(),
            role: "assistant",
            content: replyContent,
            timestamp: Date.now(),
          };

          const afterAi = await appendChatMessage(convId, {
            id: aiMsg.id,
            role: "assistant",
            content: aiMsg.content,
            timestamp: aiMsg.timestamp,
          });
          setConversations((prev) =>
            prev.map((c) => (c.id === convId ? conversationFromApi(afterAi) : c))
          );
          setIsTyping(false);
          scrollToBottom();

          if (replyContent.startsWith("**Transcript**") && audioFile) {
            const transcriptText = replyContent.replace(/^\*\*Transcript\*\*[^\n]*\n\n/, "");
            try {
              const note = await generateSOAP(transcriptText);
              setSoapNotes((prev) => ({ ...prev, [aiMsg.id]: note }));
              try {
                await createScribeSession({
                  transcript: transcriptText,
                  soap: note,
                  linkedConversationId: convId ?? undefined,
                });
              } catch {
                /* scribe persistence optional */
              }
            } catch {
              /* SOAP optional */
            }
          }
        } catch {
          setIsTyping(false);
        }
      })();
    },
    [activeId, scrollToBottom, transcribe]
  );

  useEffect(() => {
    scrollToBottom();
  }, [active?.messages.length, scrollToBottom]);

  return (
    <div className="flex h-screen w-full overflow-hidden bg-background">
      <ChatSidebar
        conversations={conversations}
        activeId={activeId}
        onSelect={(id) => { setActiveId(id); setSidebarOpen(false); }}
        onNew={() => { handleNewChat(); setSidebarOpen(false); }}
        onDelete={(id) => {
          void handleDeleteConversation(id);
        }}
        theme={theme}
        onToggleTheme={toggleTheme}
        open={sidebarOpen}
        onToggle={() => setSidebarOpen((o) => !o)}
        userEmail={userEmail}
        onLogout={handleLogout}
      />

      <div className="flex-1 flex flex-col min-w-0">
        {/* Header */}
        <header className="flex items-center justify-between h-11 px-4 flex-shrink-0">
          <div />
          {hasMessages ? (
            <>
              <button className="flex items-center gap-1 text-[13px] font-medium text-foreground/80 hover:text-foreground transition-colors">
                {active.title}
                <ChevronDown className="h-3 w-3" />
              </button>
              <button className="flex items-center gap-1.5 text-[13px] text-muted-foreground hover:text-foreground transition-colors px-2.5 py-1 rounded-lg hover:bg-accent">
                <Share className="h-3.5 w-3.5" />
                Share
              </button>
            </>
          ) : (
            <div />
          )}
        </header>

        {/* Welcome (centered input) or Chat (bottom input) */}
        {!hasMessages ? (
          <WelcomeScreen onSend={handleSend} disabled={isTyping} />
        ) : (
          <>
            <div ref={scrollRef} className="flex-1 overflow-y-auto scrollbar-thin">
              <div className="max-w-3xl mx-auto px-4 py-6 space-y-5">
                {active.messages.map((msg) => (
                  <div key={msg.id}>
                    <ChatMessage message={msg} />
                    {soapNotes[msg.id] && (
                      <div className="mt-2">
                        <SOAPDisplay note={soapNotes[msg.id]} />
                      </div>
                    )}
                  </div>
                ))}
                {isTyping && <TypingIndicator />}
              </div>
            </div>
            <div className="flex-shrink-0">
              <ChatInput onSend={handleSend} disabled={isTyping} />
            </div>
          </>
        )}
      </div>
    </div>
  );
};

export default Index;
