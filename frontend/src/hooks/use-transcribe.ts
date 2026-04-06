import { useState, useCallback } from "react";
import { transcribeFile, TranscriptResult } from "@/lib/api";

export interface TranscribeState {
  loading: boolean;
  result: TranscriptResult | null;
  error: string | null;
}

export function useTranscribe() {
  const [state, setState] = useState<TranscribeState>({
    loading: false,
    result: null,
    error: null,
  });

  const transcribe = useCallback(async (file: File) => {
    setState({ loading: true, result: null, error: null });
    try {
      const result = await transcribeFile(file);
      setState({ loading: false, result, error: null });
      return result;
    } catch (err) {
      const msg = err instanceof Error ? err.message : "Transcription failed";
      setState({ loading: false, result: null, error: msg });
      return null;
    }
  }, []);

  return { ...state, transcribe };
}
