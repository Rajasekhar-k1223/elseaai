"use client";

import { useEffect, useState } from "react";
import { Upload, FileText, Search, Database, CheckCircle2, XCircle } from "lucide-react";

type DocumentItem = {
  document_id: string;
  filename: string;
  document_type?: string;
  handwriting_detected?: boolean;
  status: string;
  fine_tune_dataset_path?: string;
  created_at?: string | null;
  updated_at?: string | null;
};

export default function DocumentsPage() {
  const [documents, setDocuments] = useState<DocumentItem[]>([]);
  const [selectedFile, setSelectedFile] = useState<File | null>(null);
  const [loading, setLoading] = useState(false);
  const [uploadMessage, setUploadMessage] = useState("");
  const [fetchError, setFetchError] = useState("");
  const [actionMessage, setActionMessage] = useState("");
  const [token, setToken] = useState<string | null>(null);

  const apiUrl = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";

  useEffect(() => {
    const savedToken = localStorage.getItem("elseaToken");
    setToken(savedToken);
    if (savedToken) {
      fetchDocuments(savedToken);
    }
  }, []);

  const fetchDocuments = async (accessToken: string) => {
    setFetchError("");

    try {
      const response = await fetch(`${apiUrl}/api/v1/documents/pending-review`, {
        headers: {
          Authorization: `Bearer ${accessToken}`,
        },
      });

      if (!response.ok) {
        const errorData = await response.json();
        setFetchError(errorData.detail || "Unable to load documents.");
        setDocuments([]);
        return;
      }

      const data = await response.json();
      setDocuments(data);
    } catch (error) {
      setFetchError("Unable to reach the backend service.");
      setDocuments([]);
    }
  };

  const uploadDocument = async () => {
    if (!selectedFile) {
      setUploadMessage("Choose a file before uploading.");
      return;
    }

    if (!token) {
      setUploadMessage("Please sign in before uploading a document.");
      return;
    }

    const extension = selectedFile.name.slice(selectedFile.name.lastIndexOf(".")).toLowerCase();
    if (![".pdf", ".txt", ".md", ".json", ".docx", ".png", ".jpg", ".jpeg", ".tiff", ".bmp"].includes(extension)) {
      setUploadMessage("Unsupported file type. Supported file types: .pdf, .txt, .md, .json, .docx, .png, .jpg, .jpeg, .tiff, .bmp");
      return;
    }

    setLoading(true);
    setUploadMessage("");

    const formData = new FormData();
    formData.append("file", selectedFile);
    formData.append("upload_type", "general");

    try {
      const response = await fetch(`${apiUrl}/api/v1/documents/upload`, {
        method: "POST",
        headers: {
          Authorization: `Bearer ${token}`,
        },
        body: formData,
      });

      if (!response.ok) {
        const errorData = await response.json();
        setUploadMessage(errorData.detail || "Upload failed.");
      } else {
        const result = await response.json();
        setUploadMessage(`Upload queued: ${result.document_id}`);
        setSelectedFile(null);
        await fetchDocuments(token);
      }
    } catch (error) {
      setUploadMessage("Unable to reach the backend service.");
    } finally {
      setLoading(false);
    }
  };

  const generateFineTuneDataset = async (documentId: string) => {
    if (!token) {
      setActionMessage("Please sign in before generating datasets.");
      return;
    }
    setLoading(true);
    setActionMessage("");

    try {
      const response = await fetch(`${apiUrl}/api/v1/documents/${documentId}/generate-finetune`, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
          Authorization: `Bearer ${token}`,
        },
        body: JSON.stringify({ include_sections: true }),
      });
      if (!response.ok) {
        const errorData = await response.json();
        setActionMessage(errorData.detail || "Dataset generation failed.");
      } else {
        const result = await response.json();
        setActionMessage(`Dataset created: ${result.dataset_path}`);
        fetchDocuments(token);
      }
    } catch (error) {
      setActionMessage("Unable to reach the backend service.");
    } finally {
      setLoading(false);
    }
  };

  const reviewDocument = async (documentId: string, action: "approve" | "reject") => {
    if (!token) {
      setActionMessage("Please sign in before reviewing documents.");
      return;
    }
    setLoading(true);
    setActionMessage("");

    try {
      const response = await fetch(`${apiUrl}/api/v1/documents/${documentId}/review`, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
          Authorization: `Bearer ${token}`,
        },
        body: JSON.stringify({ action }),
      });
      if (!response.ok) {
        const errorData = await response.json();
        setActionMessage(errorData.detail || "Review action failed.");
      } else {
        const result = await response.json();
        setActionMessage(`Document ${result.status}.`);
        fetchDocuments(token);
      }
    } catch (error) {
      setActionMessage("Unable to reach the backend service.");
    } finally {
      setLoading(false);
    }
  };

  const formatDate = (dateString?: string | null) => {
    if (!dateString) return "-";
    return new Date(dateString).toLocaleString();
  };

  return (
    <div className="max-w-6xl mx-auto space-y-6 py-6">
      <div className="flex flex-col gap-4 sm:flex-row sm:items-center sm:justify-between mb-6">
        <div>
          <h1 className="text-3xl font-bold text-white">Document Management</h1>
          <p className="text-slate-400 mt-1">Upload and manage medical files for RAG, review, and fine-tuning.</p>
        </div>
        <div className="bg-slate-900 border border-slate-800 rounded-xl p-4 w-full sm:w-auto">
          <label className="block text-sm text-slate-300 mb-2">Upload a new document</label>
          <div className="flex flex-col gap-3 sm:flex-row sm:items-center">
            <input
              type="file"
              accept=".pdf,.txt,.md,.json,.docx,.png,.jpg,.jpeg,.tiff,.bmp"
              onChange={(e) => setSelectedFile(e.target.files?.[0] ?? null)}
              className="text-sm text-slate-200"
            />
            <button
              onClick={uploadDocument}
              disabled={loading || !selectedFile}
              className="inline-flex items-center gap-2 rounded-lg bg-blue-600 px-4 py-2 text-sm font-medium text-white hover:bg-blue-700 disabled:opacity-50 transition-colors"
            >
              <Upload className="w-4 h-4" />
              {loading ? "Uploading..." : "Upload"}
            </button>
          </div>
          <p className="mt-2 text-xs text-slate-500">Supported file types: .pdf, .txt, .md, .json, .docx, .png, .jpg, .jpeg, .tiff, .bmp</p>
          {uploadMessage && <p className="mt-2 text-sm text-slate-300">{uploadMessage}</p>}
            {actionMessage && <p className="mt-2 text-sm text-slate-300">{actionMessage}</p>}
        </div>
      </div>

      <div className="bg-slate-900 border border-slate-800 rounded-xl overflow-hidden">
        <div className="p-4 border-b border-slate-800 flex flex-col sm:flex-row justify-between items-start sm:items-center gap-4 bg-slate-900/50">
          <div className="flex items-center bg-slate-800 rounded-lg px-3 py-1.5 w-full sm:w-80">
            <Search className="w-4 h-4 text-slate-400 mr-2" />
            <input
              type="text"
              placeholder="Search files..."
              disabled
              className="bg-transparent border-none outline-none w-full text-sm text-white placeholder-slate-500"
            />
          </div>
          <div className="text-sm text-slate-400">Pending review documents are loaded from the backend.</div>
        </div>

        {fetchError && <div className="p-4 text-sm text-red-400">{fetchError}</div>}

        <table className="w-full text-left text-sm text-slate-300">
          <thead className="bg-slate-800/50 text-slate-400">
            <tr>
              <th className="px-6 py-4 font-medium">Document Name</th>
              <th className="px-6 py-4 font-medium">Type</th>
              <th className="px-6 py-4 font-medium">Status</th>
              <th className="px-6 py-4 font-medium">Handwriting</th>
              <th className="px-6 py-4 font-medium">Fine-tune</th>
              <th className="px-6 py-4 font-medium">Actions</th>
              <th className="px-6 py-4 font-medium">Uploaded</th>
              <th className="px-6 py-4 font-medium">Updated</th>
            </tr>
          </thead>
          <tbody className="divide-y divide-slate-800">
            {documents.length === 0 ? (
              <tr>
                <td colSpan={8} className="px-6 py-8 text-center text-slate-500">
                  {token ? "No documents found." : "Sign in to load documents."}
                </td>
              </tr>
            ) : (
              documents.map((doc) => (
                <tr key={doc.document_id} className="hover:bg-slate-800/30 transition-colors">
                  <td className="px-6 py-4">
                    <div className="flex items-center gap-3">
                      <FileText className="w-5 h-5 text-blue-400" />
                      <span className="font-medium text-white">{doc.filename}</span>
                    </div>
                  </td>
                  <td className="px-6 py-4 text-slate-300">{doc.document_type || "general"}</td>
                  <td className="px-6 py-4">
                    <span className="inline-flex items-center gap-2 rounded-full bg-slate-800 px-3 py-1 text-xs font-semibold text-slate-200">
                      {doc.status === "approved" ? (
                        <CheckCircle2 className="w-3.5 h-3.5 text-green-400" />
                      ) : doc.status === "rejected" ? (
                        <XCircle className="w-3.5 h-3.5 text-red-400" />
                      ) : (
                        <Database className="w-3.5 h-3.5 text-yellow-400" />
                      )}
                      {doc.status}
                    </span>
                  </td>
                  <td className="px-6 py-4">
                    <span className={`inline-flex items-center gap-2 rounded-full px-3 py-1 text-xs font-semibold ${doc.handwriting_detected ? "bg-red-500/15 text-red-300" : "bg-emerald-500/15 text-emerald-300"}`}>
                      {doc.handwriting_detected ? "Possible handwriting" : "No handwriting"}
                    </span>
                  </td>
                  <td className="px-6 py-4 text-slate-400">
                    {doc.fine_tune_dataset_path ? (
                      <a href={doc.fine_tune_dataset_path.replace("/app/storage", `${apiUrl}/storage`)} target="_blank" rel="noopener noreferrer" className="text-blue-400 hover:text-blue-300">
                        View JSONL
                      </a>
                    ) : (
                      "Not generated"
                    )}
                  </td>
                  <td className="px-6 py-4 text-right space-x-2">
                    <button
                      className="rounded-lg bg-slate-800 px-3 py-1 text-xs text-slate-200 hover:bg-slate-700 transition-colors"
                      onClick={() => generateFineTuneDataset(doc.document_id)}
                      disabled={loading}
                    >
                      Generate JSONL
                    </button>
                    <button
                      className="rounded-lg bg-green-600 px-3 py-1 text-xs text-white hover:bg-green-700 transition-colors"
                      onClick={() => reviewDocument(doc.document_id, "approve")}
                      disabled={loading}
                    >
                      Approve
                    </button>
                    <button
                      className="rounded-lg bg-red-600 px-3 py-1 text-xs text-white hover:bg-red-700 transition-colors"
                      onClick={() => reviewDocument(doc.document_id, "reject")}
                      disabled={loading}
                    >
                      Reject
                    </button>
                  </td>
                  <td className="px-6 py-4 text-slate-400">{formatDate(doc.created_at)}</td>
                  <td className="px-6 py-4 text-slate-400">{formatDate(doc.updated_at)}</td>
                </tr>
              ))
            )}
          </tbody>
        </table>
      </div>
    </div>
  );
}
