import { useState } from "react";
import { SOAPNote, textToSpeech } from "@/lib/api";

interface SOAPDisplayProps {
  note: SOAPNote;
}

export function SOAPDisplay({ note }: SOAPDisplayProps) {
  const [audioUrl, setAudioUrl] = useState<string | null>(null);
  const [loading, setLoading] = useState(false);

  const handleTTS = async () => {
    const summary = `Subjective: ${note.subjective}. Assessment: ${note.assessment}. Plan: ${note.plan}.`;
    setLoading(true);
    try {
      const blob = await textToSpeech(summary);
      setAudioUrl(URL.createObjectURL(blob));
    } catch {
      // silent fail — TTS is optional
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="rounded-lg border border-border bg-muted/30 p-4 space-y-3 text-sm">
      <p className="text-[10px] text-destructive font-medium uppercase tracking-wide">
        NOT for clinical use
      </p>
      {(["subjective", "objective", "assessment", "plan"] as const).map((key) => (
        <div key={key}>
          <p className="font-semibold capitalize text-foreground">{key}</p>
          <p className="text-muted-foreground whitespace-pre-wrap">{note[key]}</p>
        </div>
      ))}
      {note.citations && note.citations.length > 0 && (
        <div>
          <p className="font-semibold text-foreground">References</p>
          <ul className="list-disc list-inside text-muted-foreground">
            {note.citations.map((c, i) => <li key={i}>{c}</li>)}
          </ul>
        </div>
      )}
      <div className="pt-1">
        <button
          onClick={handleTTS}
          disabled={loading}
          className="text-xs px-3 py-1 rounded-md bg-primary text-primary-foreground hover:bg-primary/90 disabled:opacity-50"
        >
          {loading ? "Generating audio…" : "Read SOAP aloud"}
        </button>
        {audioUrl && (
          <audio controls src={audioUrl} className="mt-2 w-full" />
        )}
      </div>
    </div>
  );
}
