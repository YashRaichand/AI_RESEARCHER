"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";
import {
  LayoutDashboard, FileText, MessageSquare, BookOpen, Search,
  Network, Lightbulb, CreditCard, Presentation as PresentationIcon,
  BarChart3, LogOut,
} from "lucide-react";
import { useAuth } from "@/lib/auth-context";
import { cn } from "@/lib/utils";

const navItems = [
  { href: "/dashboard", label: "Dashboard", icon: LayoutDashboard },
  { href: "/papers", label: "Papers", icon: FileText },
  { href: "/chat", label: "Chat", icon: MessageSquare },
  { href: "/literature-review", label: "Literature Review", icon: BookOpen },
  { href: "/gaps", label: "Research Gaps", icon: Search },
  { href: "/knowledge-graph", label: "Knowledge Graph", icon: Network },
  { href: "/ideas", label: "Ideas", icon: Lightbulb },
  { href: "/flashcards", label: "Flashcards", icon: CreditCard },
  { href: "/slides", label: "Presentations", icon: PresentationIcon },
  { href: "/analytics", label: "Analytics", icon: BarChart3 },
];

export default function DashboardShell({ children }: { children: React.ReactNode }) {
  const pathname = usePathname();
  const { user, logout } = useAuth();

  return (
    <div className="flex min-h-screen">
      <aside className="w-64 glass border-r border-white/10 flex flex-col p-4 fixed h-screen">
        <div className="px-2 py-4 mb-4">
          <span className="text-xl font-semibold gradient-text">Scientia AI</span>
        </div>
        <nav className="flex-1 space-y-1">
          {navItems.map((item) => {
            const active = pathname === item.href;
            return (
              <Link
                key={item.href}
                href={item.href}
                className={cn(
                  "flex items-center gap-3 px-3 py-2.5 rounded-lg text-sm transition",
                  active
                    ? "bg-accent/20 text-accent-light border border-accent/30"
                    : "text-gray-400 hover:bg-white/5 hover:text-white"
                )}
              >
                <item.icon className="w-4 h-4" />
                {item.label}
              </Link>
            );
          })}
        </nav>
        <div className="border-t border-white/10 pt-4 mt-4">
          <div className="flex items-center gap-3 px-3 py-2 mb-2">
            <div className="w-8 h-8 rounded-full bg-accent flex items-center justify-center text-sm font-medium">
              {user?.name?.[0]?.toUpperCase() || "U"}
            </div>
            <div className="text-sm truncate">{user?.name || "User"}</div>
          </div>
          <button
            onClick={logout}
            className="flex items-center gap-3 px-3 py-2 w-full text-sm text-gray-400 hover:text-red-400 transition rounded-lg hover:bg-white/5"
          >
            <LogOut className="w-4 h-4" />
            Logout
          </button>
        </div>
      </aside>
      <main className="flex-1 ml-64 p-8">{children}</main>
    </div>
  );
}
