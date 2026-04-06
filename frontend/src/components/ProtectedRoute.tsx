import { type ReactNode, useEffect, useState } from "react";
import { Navigate } from "react-router-dom";
import { fetchMe, getAccessToken, setAccessToken } from "@/lib/api";

export function ProtectedRoute({ children }: { children: ReactNode }) {
  const [state, setState] = useState<"loading" | "ok" | "redirect">("loading");

  useEffect(() => {
    let cancelled = false;
    const t = getAccessToken();
    if (!t) {
      setState("redirect");
      return;
    }
    void (async () => {
      try {
        await fetchMe();
        if (!cancelled) setState("ok");
      } catch {
        setAccessToken(null);
        if (!cancelled) setState("redirect");
      }
    })();
    return () => {
      cancelled = true;
    };
  }, []);

  if (state === "loading") {
    return (
      <div className="flex h-screen w-full items-center justify-center bg-background text-muted-foreground text-sm">
        Loading…
      </div>
    );
  }
  if (state === "redirect") {
    return <Navigate to="/login" replace />;
  }
  return <>{children}</>;
}
