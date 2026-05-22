"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";
import { LayoutDashboard, MessageSquare, FileText, Activity, Shield, Cloud, Server, Settings } from "lucide-react";

const navigation = [
  { name: "Dashboard", href: "/", icon: LayoutDashboard },
  { name: "AI Assistant", href: "/chat", icon: MessageSquare },
  { name: "Documents", href: "/documents", icon: FileText },
  { name: "Healthcare AI", href: "/healthcare", icon: Activity },
  { name: "Cybersecurity AI", href: "/cybersecurity", icon: Shield },
  { name: "DevSecOps AI", href: "/devsecops", icon: Server },
  { name: "CloudOps AI", href: "/cloudops", icon: Cloud },
];

export function Sidebar() {
  const pathname = usePathname();

  return (
    <div className="flex flex-col w-64 h-screen px-4 py-8 bg-slate-900 border-r border-slate-800 text-slate-300">
      <div className="flex items-center justify-center mb-10">
        <h1 className="text-2xl font-bold text-white tracking-wider">ElseaAI</h1>
      </div>
      
      <div className="flex flex-col flex-1 space-y-2">
        {navigation.map((item) => {
          const isActive = pathname === item.href;
          const Icon = item.icon;
          
          return (
            <Link
              key={item.name}
              href={item.href}
              className={`flex items-center px-4 py-3 rounded-lg transition-colors ${
                isActive 
                  ? "bg-blue-600 text-white" 
                  : "hover:bg-slate-800 hover:text-white"
              }`}
            >
              <Icon className="w-5 h-5 mr-3" />
              <span className="font-medium">{item.name}</span>
            </Link>
          );
        })}
      </div>

      <div className="mt-auto">
        <Link
          href="/settings"
          className="flex items-center px-4 py-3 rounded-lg transition-colors hover:bg-slate-800 hover:text-white"
        >
          <Settings className="w-5 h-5 mr-3" />
          <span className="font-medium">Settings</span>
        </Link>
      </div>
    </div>
  );
}
