import { Sparkles } from "lucide-react";

export function TypingIndicator() {
  return (
    <div className="flex items-center gap-2 py-4 px-1">
      <Sparkles className="h-5 w-5 text-primary animate-sparkle-pulse" />
    </div>
  );
}
