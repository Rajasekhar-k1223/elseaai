"use client";

import { Server, Terminal, Code2 } from "lucide-react";

export default function DevSecOpsPage() {
  return (
    <div className="max-w-7xl mx-auto space-y-6">
      <div className="flex justify-between items-center mb-8">
        <div>
          <h1 className="text-3xl font-bold text-white flex items-center">
            <Server className="w-8 h-8 text-indigo-500 mr-3" />
            DevSecOps AI
          </h1>
          <p className="text-slate-400 mt-1">YAML analysis, infrastructure troubleshooting, and CI/CD insights.</p>
        </div>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        <div className="bg-slate-900 border border-slate-800 rounded-xl p-6">
          <div className="flex items-center mb-4">
            <Code2 className="w-6 h-6 text-indigo-400 mr-2" />
            <h2 className="text-xl font-semibold text-white">Config Analysis</h2>
          </div>
          <p className="text-slate-400 mb-4 text-sm">Upload Kubernetes/Docker YAMLs to detect misconfigurations.</p>
          <div className="border-2 border-dashed border-slate-700 rounded-xl p-8 flex flex-col items-center justify-center text-slate-500 bg-slate-800/50 hover:bg-slate-800 transition-colors cursor-pointer">
             <Terminal className="w-10 h-10 mb-2" />
             <p>Drag and drop YAML/Dockerfile here</p>
          </div>
        </div>
      </div>
    </div>
  );
}
