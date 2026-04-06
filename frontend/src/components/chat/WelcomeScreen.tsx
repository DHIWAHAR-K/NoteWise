import { Sparkles, Pencil, GraduationCap, Code2 } from "lucide-react";
import { ChatInput } from "./ChatInput";
import { FileAttachment } from "@/lib/chat-store";

const ACTION_CHIPS = [
  { icon: Pencil, label: "Write" },
  { icon: GraduationCap, label: "Learn" },
  { icon: Code2, label: "Code" },
];

interface WelcomeScreenProps {
  onSend: (content: string, files: FileAttachment[]) => void;
  disabled?: boolean;
}

export function WelcomeScreen({ onSend, disabled }: WelcomeScreenProps) {
  const getGreeting = () => {
    const hour = new Date().getHours();
    if (hour < 12) return "Good morning";
    if (hour < 17) return "Good afternoon";
    return "Good evening";
  };

  return (
    <div className="flex flex-col items-center justify-center flex-1 px-4">
      <div className="mb-6">
        <Sparkles className="h-9 w-9 text-muted-foreground/70" strokeWidth={1.5} />
      </div>

      <h1 className="text-[28px] font-medium mb-8 text-foreground tracking-[-0.01em]">
        {getGreeting()}, User
      </h1>

      {/* Centered input */}
      <div className="w-full max-w-2xl mb-4">
        <ChatInput onSend={onSend} disabled={disabled} isWelcome />
      </div>

      {/* Action chips */}
      <div className="flex flex-wrap gap-2 justify-center">
        {ACTION_CHIPS.map((chip) => (
          <button
            key={chip.label}
            onClick={() => onSend(`Help me ${chip.label.toLowerCase()}`, [])}
            className="flex items-center gap-2 text-[13px] px-4 py-2 rounded-full border border-border/80 hover:bg-accent transition-colors text-muted-foreground hover:text-foreground"
          >
            <chip.icon className="h-3.5 w-3.5" />
            {chip.label}
          </button>
        ))}
      </div>
    </div>
  );
}
