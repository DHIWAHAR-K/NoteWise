import { useState, useRef, useEffect } from "react";
import {
  Plus,
  Search,
  Settings2,
  MessageCircle,
  FolderKanban,
  Blocks,
  Code2,
  Download,
  PanelLeftClose,
  PanelLeft,
  MoreHorizontal,
  Star,
  Pencil,
  FolderPlus,
  Trash2,
  LogOut,
} from "lucide-react";
import { Conversation, groupConversationsByDate } from "@/lib/chat-store";

interface ChatSidebarProps {
  conversations: Conversation[];
  activeId: string | null;
  onSelect: (id: string) => void;
  onNew: () => void;
  onDelete: (id: string) => void;
  theme: "light" | "dark";
  onToggleTheme: () => void;
  open: boolean;
  onToggle: () => void;
  userEmail?: string;
  onLogout?: () => void;
}

const NAV_TOP = [
  { icon: Plus, label: "New chat", action: "new" },
  { icon: Search, label: "Search" },
  { icon: Settings2, label: "Customize" },
];

const NAV_MID = [
  { icon: MessageCircle, label: "Chats" },
  { icon: FolderKanban, label: "Projects" },
  { icon: Blocks, label: "Artifacts" },
  { icon: Code2, label: "Code" },
];

export function ChatSidebar({
  conversations,
  activeId,
  onSelect,
  onNew,
  onDelete,
  open,
  onToggle,
  userEmail,
  onLogout,
}: ChatSidebarProps) {
  const groups = groupConversationsByDate(conversations);
  const [menuOpenId, setMenuOpenId] = useState<string | null>(null);
  const menuRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    if (!menuOpenId) return;
    const handler = (e: MouseEvent) => {
      if (menuRef.current && !menuRef.current.contains(e.target as Node)) {
        setMenuOpenId(null);
      }
    };
    document.addEventListener("mousedown", handler);
    return () => document.removeEventListener("mousedown", handler);
  }, [menuOpenId]);

  return (
    <>
      {/* Mobile overlay */}
      {open && (
        <div
          className="fixed inset-0 z-40 bg-black/20 lg:hidden"
          onClick={onToggle}
        />
      )}

      <aside
        className="relative z-50 h-full flex flex-col bg-sidebar flex-shrink-0 transition-[width] duration-300 ease-in-out overflow-hidden"
        style={{ width: open ? 260 : 52 }}
      >
        <div className="flex flex-col h-full" style={{ minWidth: open ? 260 : 52 }}>
          {/* Toggle row */}
          <div className={`flex items-center pt-3.5 pb-1 ${open ? "px-3 gap-2.5" : "justify-center"}`}>
            <button
              onClick={onToggle}
              className="p-2 rounded-lg text-muted-foreground hover:text-foreground hover:bg-sidebar-accent transition-colors flex-shrink-0"
              title="Toggle sidebar"
            >
              {open ? <PanelLeftClose className="h-[18px] w-[18px]" /> : <PanelLeft className="h-5 w-5" />}
            </button>
            {open && (
              <span className="text-base font-semibold text-foreground tracking-tight">Claude</span>
            )}
          </div>

          {/* Nav top */}
          <nav className={`mt-0.5 space-y-px ${open ? "px-2" : "px-0 flex flex-col items-center"}`}>
            {NAV_TOP.map((item) => (
              <button
                key={item.label}
                onClick={item.action === "new" ? onNew : undefined}
                className={`flex items-center rounded-lg text-sidebar-foreground hover:text-foreground hover:bg-sidebar-accent transition-colors ${
                  open
                    ? "gap-3 w-full px-3 py-[7px] text-[14px]"
                    : "p-2 justify-center"
                }`}
                title={!open ? item.label : undefined}
              >
                <item.icon className={`flex-shrink-0 ${open ? "h-[17px] w-[17px]" : "h-5 w-5"}`} />
                {open && <span>{item.label}</span>}
              </button>
            ))}
          </nav>

          {/* Separator */}
          <div className={`my-2 ${open ? "mx-3" : "mx-2"} border-t border-sidebar-border`} />

          {/* Nav mid */}
          <nav className={`space-y-px ${open ? "px-2" : "px-0 flex flex-col items-center"}`}>
            {NAV_MID.map((item) => (
              <button
                key={item.label}
                className={`flex items-center rounded-lg text-sidebar-foreground hover:text-foreground hover:bg-sidebar-accent transition-colors ${
                  open
                    ? "gap-3 w-full px-3 py-[7px] text-[14px]"
                    : "p-2 justify-center"
                }`}
                title={!open ? item.label : undefined}
              >
                <item.icon className={`flex-shrink-0 ${open ? "h-[17px] w-[17px]" : "h-5 w-5"}`} />
                {open && <span>{item.label}</span>}
              </button>
            ))}
          </nav>

          {/* Recents (only when expanded) / spacer when collapsed */}
          {open ? (
            <div className="mt-3 flex-1 overflow-y-auto scrollbar-thin px-2">
              <p className="text-[12px] font-medium text-muted-foreground/70 uppercase tracking-wider px-3 py-2">Recents</p>
              <div className="space-y-px">
                {groups.map((group) =>
                  group.conversations.map((c) => (
                    <div
                      key={c.id}
                      className={`group relative flex items-center gap-2 px-3 py-2 rounded-lg cursor-pointer text-[14px] transition-colors ${
                        c.id === activeId
                          ? "bg-sidebar-accent text-foreground"
                          : "text-sidebar-foreground hover:bg-sidebar-accent/60"
                      }`}
                      onClick={() => {
                        onSelect(c.id);
                        setMenuOpenId(null);
                      }}
                    >
                      <span className="truncate flex-1">{c.title}</span>
                      <button
                        onClick={(e) => {
                          e.stopPropagation();
                          setMenuOpenId(menuOpenId === c.id ? null : c.id);
                        }}
                        className={`p-0.5 rounded text-muted-foreground hover:text-foreground transition-all flex-shrink-0 ${
                          menuOpenId === c.id ? "opacity-100" : "opacity-0 group-hover:opacity-100"
                        }`}
                      >
                        <MoreHorizontal className="h-4 w-4" />
                      </button>

                      {menuOpenId === c.id && (
                        <div
                          ref={menuRef}
                          className="absolute right-0 top-full mt-1 z-[60] w-44 rounded-xl bg-popover border border-border shadow-lg py-1 text-[13px]"
                        >
                          <button className="flex items-center gap-2.5 w-full px-3.5 py-1.5 text-popover-foreground hover:bg-accent transition-colors">
                            <Star className="h-3.5 w-3.5" /> Star
                          </button>
                          <button className="flex items-center gap-2.5 w-full px-3.5 py-1.5 text-popover-foreground hover:bg-accent transition-colors">
                            <Pencil className="h-3.5 w-3.5" /> Rename
                          </button>
                          <button className="flex items-center gap-2.5 w-full px-3.5 py-1.5 text-popover-foreground hover:bg-accent transition-colors">
                            <FolderPlus className="h-3.5 w-3.5" /> Add to project
                          </button>
                          <div className="my-1 border-t border-border" />
                          <button
                            onClick={(e) => {
                              e.stopPropagation();
                              onDelete(c.id);
                              setMenuOpenId(null);
                            }}
                            className="flex items-center gap-2.5 w-full px-3.5 py-1.5 text-destructive hover:bg-accent transition-colors"
                          >
                            <Trash2 className="h-3.5 w-3.5" /> Delete
                          </button>
                        </div>
                      )}
                    </div>
                  ))
                )}

                {conversations.length === 0 && (
                  <p className="text-xs text-muted-foreground text-center py-8">
                    No conversations yet
                  </p>
                )}
              </div>
            </div>
          ) : (
            <div className="flex-1" />
          )}

          {/* Bottom */}
          {open ? (
            <div className="flex-shrink-0 border-t border-sidebar-border px-3 py-3 space-y-2">
              <div className="flex items-center gap-2.5 px-1.5">
                <div className="w-8 h-8 rounded-full bg-accent text-foreground flex items-center justify-center text-[11px] font-semibold flex-shrink-0">
                  {(userEmail?.[0] ?? "U").toUpperCase()}
                </div>
                <div className="flex-1 min-w-0">
                  <p className="text-[13px] font-medium text-foreground truncate">
                    {userEmail || "Signed in"}
                  </p>
                  <p className="text-[11px] text-muted-foreground">Account</p>
                </div>
              </div>
              {onLogout && (
                <button
                  type="button"
                  onClick={onLogout}
                  className="flex items-center gap-2 w-full px-3 py-2 rounded-lg text-[13px] text-sidebar-foreground hover:bg-sidebar-accent hover:text-foreground transition-colors"
                >
                  <LogOut className="h-4 w-4 flex-shrink-0" />
                  Log out
                </button>
              )}
            </div>
          ) : (
            <div className="flex flex-col items-center gap-1.5 pb-3">
              <button className="p-2 rounded-lg text-icon-rail-foreground hover:text-foreground hover:bg-sidebar-accent transition-colors" title="Download">
                <Download className="h-5 w-5" />
              </button>
              <div
                className="w-9 h-9 rounded-full bg-accent text-foreground flex items-center justify-center text-[11px] font-semibold cursor-pointer"
                title="User"
              >
                DA
              </div>
            </div>
          )}
        </div>
      </aside>
    </>
  );
}
