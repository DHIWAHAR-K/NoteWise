import ReactMarkdown from "react-markdown";
import remarkGfm from "remark-gfm";
import { Prism as SyntaxHighlighter } from "react-syntax-highlighter";
import { oneLight, oneDark } from "react-syntax-highlighter/dist/esm/styles/prism";
import { Copy, Check } from "lucide-react";
import { useState } from "react";

function CodeBlock({ language, children }: { language: string; children: string }) {
  const [copied, setCopied] = useState(false);
  const isDark = document.documentElement.classList.contains("dark");

  const handleCopy = () => {
    navigator.clipboard.writeText(children);
    setCopied(true);
    setTimeout(() => setCopied(false), 2000);
  };

  return (
    <div className="relative group my-3 rounded-lg overflow-hidden border border-border">
      <div className="flex items-center justify-between px-4 py-1.5 bg-muted text-xs text-muted-foreground">
        <span>{language || "text"}</span>
        <button
          onClick={handleCopy}
          className="flex items-center gap-1 hover:text-foreground transition-colors"
        >
          {copied ? <Check className="h-3.5 w-3.5" /> : <Copy className="h-3.5 w-3.5" />}
          {copied ? "Copied" : "Copy"}
        </button>
      </div>
      <SyntaxHighlighter
        language={language || "text"}
        style={isDark ? oneDark : oneLight}
        customStyle={{
          margin: 0,
          borderRadius: 0,
          fontSize: "0.8125rem",
          background: isDark ? "hsl(220, 10%, 13%)" : "hsl(40, 20%, 95%)",
        }}
      >
        {children}
      </SyntaxHighlighter>
    </div>
  );
}

export function MarkdownRenderer({ content }: { content: string }) {
  return (
    <ReactMarkdown
      remarkPlugins={[remarkGfm]}
      className="prose prose-sm dark:prose-invert max-w-none leading-relaxed"
      components={{
        code({ className, children, ...props }) {
          const match = /language-(\w+)/.exec(className || "");
          const text = String(children).replace(/\n$/, "");
          if (match) {
            return <CodeBlock language={match[1]} children={text} />;
          }
          return (
            <code
              className="bg-muted px-1.5 py-0.5 rounded text-[0.8125rem] font-mono"
              {...props}
            >
              {children}
            </code>
          );
        },
        table({ children }) {
          return (
            <div className="my-3 overflow-x-auto rounded-lg border border-border">
              <table className="min-w-full text-sm">{children}</table>
            </div>
          );
        },
        th({ children }) {
          return <th className="bg-muted px-3 py-2 text-left font-medium">{children}</th>;
        },
        td({ children }) {
          return <td className="px-3 py-2 border-t border-border">{children}</td>;
        },
        blockquote({ children }) {
          return (
            <blockquote className="border-l-3 border-primary/40 pl-4 my-3 text-muted-foreground italic">
              {children}
            </blockquote>
          );
        },
        a({ href, children }) {
          return (
            <a href={href} target="_blank" rel="noopener noreferrer" className="text-primary underline underline-offset-2 hover:text-primary/80">
              {children}
            </a>
          );
        },
        p({ children }) {
          return <p className="my-2 leading-relaxed">{children}</p>;
        },
        ul({ children }) {
          return <ul className="my-2 ml-1 list-disc list-inside space-y-1">{children}</ul>;
        },
        ol({ children }) {
          return <ol className="my-2 ml-1 list-decimal list-inside space-y-1">{children}</ol>;
        },
        h2({ children }) {
          return <h2 className="text-lg font-semibold mt-5 mb-2">{children}</h2>;
        },
        h3({ children }) {
          return <h3 className="text-base font-semibold mt-4 mb-1.5">{children}</h3>;
        },
      }}
    />
  );
}
