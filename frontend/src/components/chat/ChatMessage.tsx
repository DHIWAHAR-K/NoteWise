import { useState } from "react";
import { Message } from "@/lib/chat-store";
import { MarkdownRenderer } from "./MarkdownRenderer";
import { FileText, Image as ImageIcon, Copy, Check, ThumbsUp, ThumbsDown, RefreshCw } from "lucide-react";

export function ChatMessage({ message }: { message: Message }) {
  const isUser = message.role === "user";
  const [copied, setCopied] = useState(false);

  const handleCopy = () => {
    navigator.clipboard.writeText(message.content);
    setCopied(true);
    setTimeout(() => setCopied(false), 2000);
  };

  return (
    <div className={`flex w-full ${isUser ? "justify-end" : "justify-start"}`}>
      <div
        className={`${
          isUser
            ? "max-w-[75%] bg-user-bubble text-user-bubble-foreground rounded-3xl rounded-br-lg px-4 py-2.5"
            : "max-w-[85%] py-1"
        }`}
      >
        {message.files && message.files.length > 0 && (
          <div className={`flex flex-wrap gap-2 ${isUser ? "mb-2" : "mb-3"}`}>
            {message.files.map((file) => (
              <div
                key={file.id}
                className="flex items-center gap-2 bg-muted/60 rounded-lg px-3 py-1.5 text-xs"
              >
                {file.type.startsWith("image/") ? (
                  <ImageIcon className="h-3.5 w-3.5 text-muted-foreground" />
                ) : (
                  <FileText className="h-3.5 w-3.5 text-muted-foreground" />
                )}
                <span className="truncate max-w-[120px]">{file.name}</span>
              </div>
            ))}
          </div>
        )}

        {isUser ? (
          <p className="text-[15px] whitespace-pre-wrap leading-relaxed">{message.content}</p>
        ) : (
          <MarkdownRenderer content={message.content} />
        )}

        {/* Action icons for AI messages */}
        {!isUser && (
          <div className="flex items-center gap-0.5 mt-3 -ml-1.5">
            <button
              onClick={handleCopy}
              className="p-1.5 rounded-md text-muted-foreground/60 hover:text-foreground hover:bg-accent transition-colors"
              title="Copy"
            >
              {copied ? <Check className="h-4 w-4" /> : <Copy className="h-4 w-4" />}
            </button>
            <button
              className="p-1.5 rounded-md text-muted-foreground/60 hover:text-foreground hover:bg-accent transition-colors"
              title="Good response"
            >
              <ThumbsUp className="h-4 w-4" />
            </button>
            <button
              className="p-1.5 rounded-md text-muted-foreground/60 hover:text-foreground hover:bg-accent transition-colors"
              title="Bad response"
            >
              <ThumbsDown className="h-4 w-4" />
            </button>
            <button
              className="p-1.5 rounded-md text-muted-foreground/60 hover:text-foreground hover:bg-accent transition-colors"
              title="Retry"
            >
              <RefreshCw className="h-4 w-4" />
            </button>
          </div>
        )}
      </div>
    </div>
  );
}
