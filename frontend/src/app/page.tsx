"use client";

import { Activity, Users, FileText, Database, ShieldAlert, Cpu } from "lucide-react";

const stats = [
  { name: "Active Models", value: "3", icon: Cpu, color: "text-blue-500", bg: "bg-blue-500/10" },
  { name: "Indexed Documents", value: "1,249", icon: FileText, color: "text-green-500", bg: "bg-green-500/10" },
  { name: "Total Queries", value: "8,342", icon: Activity, color: "text-purple-500", bg: "bg-purple-500/10" },
  { name: "Active Users", value: "42", icon: Users, color: "text-orange-500", bg: "bg-orange-500/10" },
];

export default function Dashboard() {
  return (
    <div className="max-w-7xl mx-auto space-y-6">
      <div className="flex justify-between items-center mb-8">
        <div>
          <h1 className="text-3xl font-bold text-white">Platform Overview</h1>
          <p className="text-slate-400 mt-1">System status and usage analytics across all domains.</p>
        </div>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
        {stats.map((stat) => {
          const Icon = stat.icon;
          return (
            <div key={stat.name} className="bg-slate-900 border border-slate-800 rounded-xl p-6">
              <div className="flex items-center">
                <div className={`p-3 rounded-lg ${stat.bg}`}>
                  <Icon className={`w-6 h-6 ${stat.color}`} />
                </div>
                <div className="ml-4">
                  <p className="text-sm font-medium text-slate-400">{stat.name}</p>
                  <p className="text-2xl font-bold text-white">{stat.value}</p>
                </div>
              </div>
            </div>
          );
        })}
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6 mt-8">
        <div className="bg-slate-900 border border-slate-800 rounded-xl p-6">
          <h2 className="text-lg font-semibold text-white mb-4">Recent AI Activity</h2>
          <div className="space-y-4">
            {[1, 2, 3].map((i) => (
              <div key={i} className="flex items-start space-x-3 pb-4 border-b border-slate-800 last:border-0 last:pb-0">
                <div className="p-2 bg-slate-800 rounded-lg mt-1">
                  <MessageSquare className="w-4 h-4 text-blue-400" />
                </div>
                <div>
                  <p className="text-sm font-medium text-white">Healthcare domain summarized patient file #842</p>
                  <p className="text-xs text-slate-400 mt-1">Model: llama3.2 • 2 mins ago</p>
                </div>
              </div>
            ))}
          </div>
        </div>

        <div className="bg-slate-900 border border-slate-800 rounded-xl p-6">
          <h2 className="text-lg font-semibold text-white mb-4">System Alerts</h2>
          <div className="space-y-4">
            <div className="flex items-start space-x-3 pb-4 border-b border-slate-800">
                <div className="p-2 bg-red-500/10 rounded-lg mt-1">
                  <ShieldAlert className="w-4 h-4 text-red-500" />
                </div>
                <div>
                  <p className="text-sm font-medium text-white">Suspicious login attempt detected</p>
                  <p className="text-xs text-slate-400 mt-1">Cybersecurity Module • 15 mins ago</p>
                </div>
            </div>
            <div className="flex items-start space-x-3 pb-4 border-b border-slate-800">
                <div className="p-2 bg-yellow-500/10 rounded-lg mt-1">
                  <Database className="w-4 h-4 text-yellow-500" />
                </div>
                <div>
                  <p className="text-sm font-medium text-white">Qdrant indexing queue building up</p>
                  <p className="text-xs text-slate-400 mt-1">System • 1 hour ago</p>
                </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}

// Just importing MessageSquare here for the mock data above
import { MessageSquare } from "lucide-react";
