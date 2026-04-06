import { useState, useRef, useCallback, type DragEvent, type KeyboardEvent } from "react";
import { ArrowUp, Plus, X, ChevronDown, AudioLines } from "lucide-react";
import { FileAttachment, genId } from "@/lib/chat-store";

interface ChatInputProps {
  onSend: (content: string, files: FileAttachment[]) => void;
  disabled?: boolean;
  isWelcome?: boolean;
}

export function ChatInput({ onSend, disabled, isWelcome }: ChatInputProps) {
  const [text, setText] = useState("");
  const [files, setFiles] = useState<FileAttachment[]>([]);
  const [dragging, setDragging] = useState(false);
  const textareaRef = useRef<HTMLTextAreaElement>(null);
  const fileInputRef = useRef<HTMLInputElement>(null);

  const canSend = (text.trim().length > 0 || files.length > 0) && !disabled;

  const handleSend = useCallback(() => {
    if (!canSend) return;
    onSend(text.trim(), files);
    setText("");
    setFiles([]);
    if (textareaRef.current) {
      textareaRef.current.style.height = "auto";
    }
  }, [canSend, text, files, onSend]);

  const handleKeyDown = (e: KeyboardEvent<HTMLTextAreaElement>) => {
    if (e.key === "Enter" && !e.shiftKey) {
      e.preventDefault();
      handleSend();
    }
  };

  const handleInput = () => {
    const el = textareaRef.current;
    if (el) {
      el.style.height = "auto";
      el.style.height = Math.min(el.scrollHeight, 200) + "px";
    }
  };

  const addFiles = (fileList: FileList | null) => {
    if (!fileList) return;
    const newFiles: FileAttachment[] = Array.from(fileList).map((f) => ({
      id: genId(),
      name: f.name,
      type: f.type,
      url: URL.createObjectURL(f),
      size: f.size,
    }));
    setFiles((prev) => [...prev, ...newFiles]);
  };

  const removeFile = (id: string) => {
    setFiles((prev) => {
      const f = prev.find((x) => x.id === id);
      if (f) URL.revokeObjectURL(f.url);
      return prev.filter((x) => x.id !== id);
    });
  };

  const handleDrop = (e: DragEvent) => {
    e.preventDefault();
    setDragging(false);
    addFiles(e.dataTransfer.files);
  };

  return (
    <div className="w-full max-w-2xl mx-auto px-4 pb-4">
      <div
        className={`relative rounded-2xl border bg-card shadow-sm transition-colors ${
          dragging ? "border-primary ring-2 ring-primary/20" : "border-border/70"
        }`}
        onDragOver={(e) => {
          e.preventDefault();
          setDragging(true);
        }}
        onDragLeave={() => setDragging(false)}
        onDrop={handleDrop}
      >
        {/* File chips */}
        {files.length > 0 && (
          <div className="flex flex-wrap gap-2 px-3 pt-3">
            {files.map((file) => (
              <div
                key={file.id}
                className="flex items-center gap-1.5 bg-muted rounded-lg px-2.5 py-1.5 text-xs"
              >
                <span className="truncate max-w-[120px]">{file.name}</span>
                <button
                  onClick={() => removeFile(file.id)}
                  className="text-muted-foreground hover:text-foreground"
                >
                  <X className="h-3 w-3" />
                </button>
              </div>
            ))}
          </div>
        )}

        {/* Textarea */}
        <div className="px-4 pt-3 pb-1">
          <textarea
            ref={textareaRef}
            value={text}
            onChange={(e) => setText(e.target.value)}
            onKeyDown={handleKeyDown}
            onInput={handleInput}
            placeholder={isWelcome ? "How can Claude help you today?" : "Reply to Claude..."}
            rows={1}
            className="w-full resize-none bg-transparent text-[15px] outline-none placeholder:text-muted-foreground/70 max-h-[200px] py-1 leading-relaxed"
          />
        </div>

        {/* Bottom row */}
        <div className="flex items-center justify-between px-3 pb-2.5">
          <button
            onClick={() => fileInputRef.current?.click()}
            className="p-1.5 rounded-lg text-muted-foreground hover:text-foreground hover:bg-accent transition-colors"
            type="button"
          >
            <Plus className="h-5 w-5" />
          </button>

          <div className="flex items-center gap-1.5">
            {/* Model selector */}
            <button
              className="flex items-center gap-1 text-xs text-muted-foreground hover:text-foreground transition-colors px-2.5 py-1.5 rounded-lg hover:bg-accent"
              type="button"
            >
              Claude 3.5 Sonnet
              <ChevronDown className="h-3 w-3" />
            </button>

            <button
              className="p-1.5 rounded-lg text-muted-foreground hover:text-foreground hover:bg-accent transition-colors"
              type="button"
            >
              <AudioLines className="h-4 w-4" />
            </button>

            {/* Send button */}
            {canSend && (
              <button
                onClick={handleSend}
                className="p-1.5 rounded-lg bg-foreground text-background hover:opacity-80 transition-all"
                type="button"
              >
                <ArrowUp className="h-4 w-4" />
              </button>
            )}
          </div>
        </div>

        <input
          ref={fileInputRef}
          type="file"
          multiple
          className="hidden"
          onChange={(e) => addFiles(e.target.files)}
        />
      </div>

      <p className="text-center text-[11px] text-muted-foreground/60 mt-2.5">
        Claude can make mistakes. Please double-check responses.
      </p>
    </div>
  );
}
