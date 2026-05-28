"use client";

import { useEffect, useState } from "react";
import { Activity, Upload, Stethoscope, Lock } from "lucide-react";

export default function HealthcarePage() {
  const [selectedFile, setSelectedFile] = useState<File | null>(null);
  const [loading, setLoading] = useState(false);
  const [uploadMessage, setUploadMessage] = useState("");
  const [token, setToken] = useState<string | null>(null);
  const [clinicalDocuments, setClinicalDocuments] = useState<DocumentItem[]>([]);
  const apiUrl = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";

  useEffect(() => {
    const savedToken = localStorage.getItem("elseaToken");
    setToken(savedToken);
    if (savedToken) {
      fetchClinicalDocuments(savedToken);
    }
  }, []);

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

  const fetchClinicalDocuments = async (accessToken: string) => {
    try {
      const response = await fetch(`${apiUrl}/api/v1/documents/pending-review`, {
        headers: {
          Authorization: `Bearer ${accessToken}`,
        },
      });
      if (!response.ok) {
        return;
      }
      const data: DocumentItem[] = await response.json();
      setClinicalDocuments(data.filter((doc) => doc.document_type === "clinical"));
    } catch (error) {
      // ignore fetch errors for the healthcare dashboard
    }
  };

  const uploadClinicalData = async () => {
    if (!selectedFile) {
      setUploadMessage("Choose a clinical file before uploading.");
      return;
    }

    if (!token) {
      setUploadMessage("Please sign in before uploading clinical data.");
      return;
    }

    const extension = selectedFile.name.slice(selectedFile.name.lastIndexOf(".")).toLowerCase();
    if (![".pdf", ".txt", ".md", ".json", ".docx", ".png", ".jpg", ".jpeg", ".tiff", ".bmp"].includes(extension)) {
      setUploadMessage("Supported clinical files: .pdf, .txt, .md, .json, .docx, .png, .jpg, .jpeg, .tiff, .bmp");
      return;
    }

    setLoading(true);
    setUploadMessage("");

    const formData = new FormData();
    formData.append("file", selectedFile);
    formData.append("upload_type", "clinical");

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
        setUploadMessage(`Clinical file uploaded and queued: ${result.document_id}`);
        setSelectedFile(null);
        if (token) {
          await fetchClinicalDocuments(token);
        }
      }
    } catch (error) {
      setUploadMessage("Unable to reach the backend service.");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="max-w-7xl mx-auto space-y-6">
      <div className="flex flex-col gap-6 lg:flex-row lg:items-center lg:justify-between mb-8">
        <div>
          <h1 className="text-3xl font-bold text-white flex items-center">
            <Activity className="w-8 h-8 text-blue-500 mr-3" />
            Healthcare AI
          </h1>
          <p className="text-slate-400 mt-1">FHIR parsing, clinical summarization, and PHI masking.</p>
        </div>
        <div className="bg-slate-900 border border-slate-800 rounded-xl p-4 w-full sm:w-auto">
          <label className="block text-sm text-slate-300 mb-2">Upload Clinical Data</label>
          <div className="flex flex-col gap-3 sm:flex-row sm:items-center">
            <input
              type="file"
              accept=".pdf,.txt,.md,.json,.docx,.png,.jpg,.jpeg,.tiff,.bmp"
              onChange={(e) => setSelectedFile(e.target.files?.[0] ?? null)}
              className="text-sm text-slate-200"
            />
            <button
              onClick={uploadClinicalData}
              disabled={loading || !selectedFile}
              className="inline-flex items-center gap-2 rounded-lg bg-blue-600 px-4 py-2 text-sm font-medium text-white hover:bg-blue-700 disabled:opacity-50 transition-colors"
            >
              <Upload className="w-4 h-4" />
              {loading ? "Uploading..." : "Upload Clinical Data"}
            </button>
          </div>
          <p className="mt-2 text-xs text-slate-500">Supported clinical file types: .pdf, .txt, .md, .json, .docx, .png, .jpg, .jpeg, .tiff, .bmp</p>
          {uploadMessage && <p className="mt-2 text-sm text-slate-300">{uploadMessage}</p>}
        </div>
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
            <h2 className="text-xl font-semibold text-white">Recent Clinical Uploads</h2>
          </div>
          <p className="text-slate-400 mb-4 text-sm">Recent clinical documents uploaded for review and PHI masking.</p>
          <div className="space-y-3">
            {clinicalDocuments.length === 0 ? (
              <div className="rounded-lg border border-slate-700 bg-slate-800 p-4 text-slate-400">No clinical uploads found.</div>
            ) : (
              clinicalDocuments.map((doc) => (
                <div key={doc.document_id} className="flex justify-between items-center p-3 bg-slate-800 rounded-lg border border-slate-700">
                  <div>
                    <div className="text-sm text-slate-300">{doc.filename}</div>
                    <div className="flex gap-2 mt-1 text-xs text-slate-500">
                      <span>{doc.document_type || "clinical"}</span>
                      <span className={`${doc.handwriting_detected ? "text-red-300" : "text-emerald-300"}`}>
                        {doc.handwriting_detected ? "Possible handwriting" : "No handwriting"}
                      </span>
                    </div>
                  </div>
                  <span className={`text-xs font-medium px-2 py-1 rounded-full ${doc.status === "approved" ? "bg-green-400/10 text-green-400" : doc.status === "rejected" ? "bg-red-400/10 text-red-400" : "bg-yellow-400/10 text-yellow-400"}`}>
                    {doc.status}
                  </span>
                </div>
              ))
            )}
          </div>
        </div>
      </div>
    </div>
  );
}
