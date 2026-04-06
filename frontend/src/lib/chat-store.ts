import type { ApiConversation } from "./api";

export interface FileAttachment {
  id: string;
  name: string;
  type: string;
  url: string;
  size: number;
}

export interface Message {
  id: string;
  role: "user" | "assistant";
  content: string;
  files?: FileAttachment[];
  timestamp: number;
}

export interface Conversation {
  id: string;
  title: string;
  messages: Message[];
  createdAt: number;
  updatedAt: number;
}

export function conversationFromApi(c: ApiConversation): Conversation {
  return {
    id: c.id,
    title: c.title,
    createdAt: c.createdAt,
    updatedAt: c.updatedAt,
    messages: c.messages.map((m) => ({
      id: m.id,
      role: m.role,
      content: m.content,
      timestamp: m.timestamp,
    })),
  };
}

let nextId = 1;
export const genId = () => `id-${nextId++}-${Date.now()}`;

const MOCK_RESPONSES = [
  "That's a great question! Let me break it down for you.\n\n## Key Points\n\n1. **First**, consider the fundamentals\n2. **Second**, think about the broader context\n3. **Third**, apply critical thinking\n\nHere's a code example:\n\n```typescript\nconst greeting = (name: string) => {\n  return `Hello, ${name}!`;\n};\n\nconsole.log(greeting('World'));\n```\n\nLet me know if you'd like me to elaborate on any of these points!",
  "I'd be happy to help with that! Here's what I think:\n\n> The best way to learn is by doing.\n\nSome suggestions:\n- Start with the basics\n- Practice regularly\n- Don't be afraid to make mistakes\n- Ask questions when you're stuck\n\n| Approach | Difficulty | Effectiveness |\n|----------|-----------|---------------|\n| Reading  | Low       | Medium        |\n| Practice | Medium    | High          |\n| Teaching | High      | Very High     |",
  "Here's my take on this:\n\nThe concept is actually simpler than it might seem at first. Let me walk you through it step by step.\n\n### Step 1: Understanding the Basics\n\nEvery complex system is built from simple components. The key is understanding how they connect.\n\n### Step 2: Building Up\n\nOnce you grasp the fundamentals, you can start combining them:\n\n```python\ndef solve(problem):\n    parts = break_down(problem)\n    solutions = [analyze(part) for part in parts]\n    return combine(solutions)\n```\n\n### Step 3: Iterating\n\nPerfection comes through iteration. Don't expect to get it right the first time!",
];

export function getMockResponse(): string {
  return MOCK_RESPONSES[Math.floor(Math.random() * MOCK_RESPONSES.length)];
}

export function groupConversationsByDate(conversations: Conversation[]) {
  const now = new Date();
  const today = new Date(now.getFullYear(), now.getMonth(), now.getDate()).getTime();
  const yesterday = today - 86400000;
  const week = today - 7 * 86400000;

  const groups: { label: string; conversations: Conversation[] }[] = [
    { label: "Today", conversations: [] },
    { label: "Yesterday", conversations: [] },
    { label: "Previous 7 Days", conversations: [] },
    { label: "Older", conversations: [] },
  ];

  const sorted = [...conversations].sort((a, b) => b.updatedAt - a.updatedAt);

  for (const c of sorted) {
    if (c.updatedAt >= today) groups[0].conversations.push(c);
    else if (c.updatedAt >= yesterday) groups[1].conversations.push(c);
    else if (c.updatedAt >= week) groups[2].conversations.push(c);
    else groups[3].conversations.push(c);
  }

  return groups.filter((g) => g.conversations.length > 0);
}
