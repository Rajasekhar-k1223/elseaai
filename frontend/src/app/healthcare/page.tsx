"use client";

import { Activity, Upload, Stethoscope, Lock } from "lucide-react";

export default function HealthcarePage() {
  return (
    <div className="max-w-7xl mx-auto space-y-6">
      <div className="flex justify-between items-center mb-8">
        <div>
          <h1 className="text-3xl font-bold text-white flex items-center">
            <Activity className="w-8 h-8 text-blue-500 mr-3" />
            Healthcare AI
          </h1>
          <p className="text-slate-400 mt-1">FHIR parsing, clinical summarization, and PHI masking.</p>
        </div>
        <button className="flex items-center bg-blue-600 hover:bg-blue-700 text-white px-4 py-2 rounded-lg font-medium transition-colors">
          <Upload className="w-4 h-4 mr-2" />
          Upload Clinical Data
        </button>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        <div className="bg-slate-900 border border-slate-800 rounded-xl p-6">
          <div className="flex items-center mb-4">
            <Stethoscope className="w-6 h-6 text-green-500 mr-2" />
            <h2 className="text-xl font-semibold text-white">Clinical Assistant</h2>
          </div>
          <p className="text-slate-400 mb-4 text-sm">Ask clinical questions against indexed FHIR resources and patient histories.</p>
          <div className="bg-slate-800 rounded-lg p-4 h-64 flex items-center justify-center border border-slate-700">
            <p className="text-slate-500 text-sm">AI Assistant Interface (Loaded via Component)</p>
          </div>
        </div>

        <div className="bg-slate-900 border border-slate-800 rounded-xl p-6">
          <div className="flex items-center mb-4">
            <Lock className="w-6 h-6 text-purple-500 mr-2" />
            <h2 className="text-xl font-semibold text-white">PHI Masking Status</h2>
          </div>
          <p className="text-slate-400 mb-4 text-sm">Real-time status of PII/PHI extraction and anonymization.</p>
          <div className="space-y-3">
             <div className="flex justify-between items-center p-3 bg-slate-800 rounded-lg border border-slate-700">
               <span className="text-sm text-slate-300">patient_record_784.json</span>
               <span className="text-xs font-medium text-green-400 bg-green-400/10 px-2 py-1 rounded-full">Masked</span>
             </div>
             <div className="flex justify-between items-center p-3 bg-slate-800 rounded-lg border border-slate-700">
               <span className="text-sm text-slate-300">lab_results_v2.pdf</span>
               <span className="text-xs font-medium text-green-400 bg-green-400/10 px-2 py-1 rounded-full">Masked</span>
             </div>
             <div className="flex justify-between items-center p-3 bg-slate-800 rounded-lg border border-slate-700">
               <span className="text-sm text-slate-300">doctor_notes_0522.docx</span>
               <span className="text-xs font-medium text-yellow-400 bg-yellow-400/10 px-2 py-1 rounded-full">Processing...</span>
             </div>
          </div>
        </div>
      </div>
    </div>
  );
}
