"use client";

import { Upload, FileText, Search, Filter, MoreVertical, Database } from "lucide-react";

export default function DocumentsPage() {
  const documents = [
    { id: 1, name: "Healthcare_Compliance_Q3.pdf", status: "Indexed", date: "2026-05-20", size: "2.4 MB" },
    { id: 2, name: "System_Architecture_V2.docx", status: "Indexing...", date: "2026-05-22", size: "1.1 MB" },
    { id: 3, name: "Security_Audit_Report.pdf", status: "Indexed", date: "2026-05-18", size: "5.7 MB" },
  ];

  return (
    <div className="max-w-6xl mx-auto space-y-6">
      <div className="flex justify-between items-center mb-8">
        <div>
          <h1 className="text-3xl font-bold text-white">Document Management</h1>
          <p className="text-slate-400 mt-1">Upload and manage files for RAG vector embeddings.</p>
        </div>
        <button className="flex items-center bg-blue-600 hover:bg-blue-700 text-white px-4 py-2 rounded-lg font-medium transition-colors">
          <Upload className="w-4 h-4 mr-2" />
          Upload Document
        </button>
      </div>

      <div className="bg-slate-900 border border-slate-800 rounded-xl overflow-hidden">
        <div className="p-4 border-b border-slate-800 flex justify-between items-center bg-slate-900/50">
          <div className="flex items-center bg-slate-800 rounded-lg px-3 py-1.5 w-80">
            <Search className="w-4 h-4 text-slate-400 mr-2" />
            <input 
              type="text" 
              placeholder="Search files..." 
              className="bg-transparent border-none outline-none w-full text-sm text-white"
            />
          </div>
          <button className="flex items-center text-slate-300 hover:text-white px-3 py-1.5 rounded-lg border border-slate-700 hover:bg-slate-800 transition-colors text-sm">
            <Filter className="w-4 h-4 mr-2" />
            Filter
          </button>
        </div>

        <table className="w-full text-left text-sm text-slate-300">
          <thead className="bg-slate-800/50 text-slate-400">
            <tr>
              <th className="px-6 py-4 font-medium">Document Name</th>
              <th className="px-6 py-4 font-medium">Status (Qdrant)</th>
              <th className="px-6 py-4 font-medium">Size</th>
              <th className="px-6 py-4 font-medium">Date Uploaded</th>
              <th className="px-6 py-4 font-medium text-right">Actions</th>
            </tr>
          </thead>
          <tbody className="divide-y divide-slate-800">
            {documents.map((doc) => (
              <tr key={doc.id} className="hover:bg-slate-800/30 transition-colors">
                <td className="px-6 py-4">
                  <div className="flex items-center">
                    <FileText className="w-5 h-5 text-blue-400 mr-3" />
                    <span className="font-medium text-white">{doc.name}</span>
                  </div>
                </td>
                <td className="px-6 py-4">
                  <span className={`inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium ${
                    doc.status === "Indexed" ? "bg-green-500/10 text-green-400" : "bg-yellow-500/10 text-yellow-400"
                  }`}>
                    {doc.status === "Indexed" && <Database className="w-3 h-3 mr-1" />}
                    {doc.status}
                  </span>
                </td>
                <td className="px-6 py-4 text-slate-400">{doc.size}</td>
                <td className="px-6 py-4 text-slate-400">{doc.date}</td>
                <td className="px-6 py-4 text-right">
                  <button className="p-1 text-slate-400 hover:text-white hover:bg-slate-700 rounded transition-colors">
                    <MoreVertical className="w-5 h-5" />
                  </button>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
}
