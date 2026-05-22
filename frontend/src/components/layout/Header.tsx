"use client";

import { Bell, Search, UserCircle } from "lucide-react";

export function Header() {
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
        <div className="flex items-center space-x-2 cursor-pointer hover:text-white transition-colors">
          <UserCircle className="w-8 h-8" />
          <div className="flex flex-col text-sm">
            <span className="font-medium text-white">Super Admin</span>
            <span className="text-xs text-slate-400">admin@elsea.ai</span>
          </div>
        </div>
      </div>
    </header>
  );
}
