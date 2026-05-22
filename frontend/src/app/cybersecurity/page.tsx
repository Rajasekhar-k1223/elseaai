"use client";

import { Shield, ShieldAlert, AlertTriangle, Eye } from "lucide-react";

export default function CybersecurityPage() {
  return (
    <div className="max-w-7xl mx-auto space-y-6">
      <div className="flex justify-between items-center mb-8">
        <div>
          <h1 className="text-3xl font-bold text-white flex items-center">
            <Shield className="w-8 h-8 text-red-500 mr-3" />
            Cybersecurity AI
          </h1>
          <p className="text-slate-400 mt-1">SIEM dashboard, threat explanation, and log analysis.</p>
        </div>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        <div className="lg:col-span-2 space-y-6">
          <div className="bg-slate-900 border border-slate-800 rounded-xl p-6">
            <h2 className="text-xl font-semibold text-white mb-4">Threat Narratives</h2>
            <div className="space-y-4">
              <div className="p-4 bg-red-500/10 border border-red-500/20 rounded-lg">
                <div className="flex items-center mb-2">
                  <ShieldAlert className="w-5 h-5 text-red-500 mr-2" />
                  <h3 className="font-medium text-white">Multiple Failed Logins (SSH)</h3>
                </div>
                <p className="text-sm text-slate-300 leading-relaxed">
                  <strong>AI Analysis:</strong> Detected 45 failed SSH login attempts originating from IP <code className="bg-slate-800 px-1 rounded">192.168.1.105</code> targeting the `root` user over a 3-minute window. This behavior matches a standard brute-force dictionary attack signature.
                </p>
                <div className="mt-3 flex space-x-2">
                  <button className="text-xs bg-red-600 hover:bg-red-700 text-white px-3 py-1.5 rounded transition-colors">Block IP</button>
                  <button className="text-xs bg-slate-700 hover:bg-slate-600 text-white px-3 py-1.5 rounded transition-colors">View Raw Logs</button>
                </div>
              </div>
            </div>
          </div>
        </div>

        <div className="space-y-6">
          <div className="bg-slate-900 border border-slate-800 rounded-xl p-6">
            <h2 className="text-lg font-semibold text-white mb-4">Security Posture</h2>
            <div className="space-y-4">
              <div className="flex items-center justify-between">
                <span className="text-sm text-slate-400 flex items-center"><AlertTriangle className="w-4 h-4 mr-2 text-yellow-500"/> Active Alerts</span>
                <span className="text-xl font-bold text-white">12</span>
              </div>
              <div className="flex items-center justify-between">
                <span className="text-sm text-slate-400 flex items-center"><Eye className="w-4 h-4 mr-2 text-blue-500"/> Monitored Assets</span>
                <span className="text-xl font-bold text-white">142</span>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
