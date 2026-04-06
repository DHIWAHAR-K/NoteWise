

## Problem

The current sidebar uses two completely separate layouts (expanded vs collapsed) that crossfade with opacity. This is not how the Claude sidebar works. In Claude's UI:

1. The **icon rail is always visible** (52px) — it never disappears
2. When expanded, a **panel slides out beside the rail**, pushing content or overlaying it
3. The total expanded width is ~280px (rail + panel)

Currently, the sidebar swaps between two overlapping absolute-positioned divs, which means the icon rail vanishes when expanded and the full panel vanishes when collapsed. The user wants the rail to persist at all times.

## Plan

### 1. Restructure ChatSidebar layout

Rewrite the sidebar to use a **two-part architecture**:

```text
┌──────┬─────────────────┐
│ Rail │   Slide Panel   │
│ 52px │   ~228px wide   │
│      │  (when open)    │
│ Always│                 │
│visible│                 │
└──────┴─────────────────┘
```

- The `<aside>` always renders the **icon rail** (52px, flex-col, icons stacked)
- Next to it (inside the same aside or as a sibling), render the **expandable panel** that slides in/out using `width` + `overflow-hidden` transition
- When collapsed: aside is 52px (rail only)
- When expanded: aside is 280px (rail 52px + panel 228px), with a smooth `transition-[width]`

### 2. Icon rail (always rendered)

- Fixed 52px column, always visible
- Contains: toggle button (CopyIcon), Plus, Search, Settings2, MessageCircle, FolderKanban, Blocks, Code2
- Bottom: blue dot, Download, user avatar "DA"
- Same styling as the current collapsed state

### 3. Expandable panel (conditionally visible)

- Rendered beside the rail, slides in via width transition
- Contains: "Claude" header, nav labels (New chat, Search, etc.), Recents list, user profile footer
- Uses `opacity` + `transition` for content fade-in to avoid text clipping during animation

### 4. Index.tsx — no changes needed

The parent already handles `sidebarOpen` state and passes `open`/`onToggle` props. No structural changes required there.

### Files to modify
- `src/components/chat/ChatSidebar.tsx` — full rewrite of the layout structure

