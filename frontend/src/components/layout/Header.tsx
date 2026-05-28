"use client";

import { useEffect, useState } from "react";
import { useRouter } from "next/navigation";
import { Bell, Search, UserCircle } from "lucide-react";

export function Header() {
  const [isAuthenticated, setIsAuthenticated] = useState(false);
  const router = useRouter();

  useEffect(() => {
    setIsAuthenticated(Boolean(localStorage.getItem("elseaToken")));
  }, []);

  const handleAuthAction = () => {
    if (isAuthenticated) {
      localStorage.removeItem("elseaToken");
      setIsAuthenticated(false);
      router.push("/login");
      return;
    }
    router.push("/login");
  };

  return (
    <header className="flex items-center justify-between h-16 px-6 bg-slate-900 border-b border-slate-800 text-slate-300">
      <div className="flex items-center bg-slate-800 rounded-md px-3 py-1.5 w-96 focus-within:ring-2 focus-within:ring-blue-500">
        <Search className="w-4 h-4 text-slate-400 mr-2" />
        <input
          type="text"
          placeholder="Search documents, chats, insights..."
          className="bg-transparent border-none outline-none w-full text-sm text-white placeholder-slate-400"
        />
      </div>

      <div className="flex items-center space-x-4">
        <button className="p-2 rounded-full hover:bg-slate-800 transition-colors relative">
          <Bell className="w-5 h-5" />
          <span className="absolute top-1.5 right-1.5 w-2 h-2 bg-red-500 rounded-full"></span>
        </button>
        <button
          onClick={handleAuthAction}
          className="px-4 py-2 rounded-lg border border-slate-700 bg-slate-800 text-sm text-white hover:bg-slate-700 transition-colors"
        >
          {isAuthenticated ? "Logout" : "Login"}
        </button>
      </div>
    </header>
  );
}
