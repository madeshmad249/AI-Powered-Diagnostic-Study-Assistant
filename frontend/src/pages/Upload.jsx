import React, { useState, useEffect } from 'react';
import { 
  UploadCloud, 
  FileText, 
  BookOpen, 
  FileQuestion, 
  Layers, 
  CheckCircle2, 
  AlertCircle,
  Database,
  RefreshCw,
  Sparkles
} from 'lucide-react';
import { api } from '../api';

export default function Upload({ onNavigateToTopics }) {
  const [documents, setDocuments] = useState([]);
  const [loading, setLoading] = useState(true);
  const [uploading, setUploading] = useState(false);
  const [selectedFile, setSelectedFile] = useState(null);
  const [docType, setDocType] = useState('notes');
  const [message, setMessage] = useState(null);

  const fetchDocs = async () => {
    try {
      setLoading(true);
      const docs = await api.listDocuments();
      setDocuments(docs);
    } catch (err) {
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchDocs();
  }, []);

  const handleFileChange = (e) => {
    if (e.target.files && e.target.files[0]) {
      setSelectedFile(e.target.files[0]);
    }
  };

  const handleUpload = async (e) => {
    e.preventDefault();
    if (!selectedFile) return;

    setUploading(true);
    setMessage(null);
    try {
      const res = await api.uploadDocument(selectedFile, docType);
      setMessage({ type: 'success', text: `${res.message} (${res.chunk_count} vector chunks indexed into ChromaDB)` });
      setSelectedFile(null);
      fetchDocs();
    } catch (err) {
      setMessage({ type: 'error', text: err.message || 'Upload failed' });
    } finally {
      setUploading(false);
    }
  };

  const docTypeLabels = {
    syllabus: { name: 'Course Syllabus', icon: BookOpen, color: 'text-indigo-400 bg-indigo-500/10 border-indigo-500/20' },
    notes: { name: 'Study Notes & Chapters', icon: FileText, color: 'text-emerald-400 bg-emerald-500/10 border-emerald-500/20' },
    past_paper: { name: 'Past Exam Papers', icon: FileQuestion, color: 'text-amber-400 bg-amber-500/10 border-amber-500/20' }
  };

  const totalChunks = documents.reduce((acc, d) => acc + (d.chunk_count || 0), 0);
  const totalPages = documents.reduce((acc, d) => acc + (d.page_count || 0), 0);

  return (
    <div className="max-w-6xl mx-auto px-4 sm:px-6 py-8 space-y-8">
      
      {/* Header Banner */}
      <div className="bg-slate-900 border border-slate-800 rounded-2xl p-6 relative overflow-hidden shadow-xl">
        <div className="flex flex-col md:flex-row md:items-center justify-between gap-4">
          <div>
            <div className="flex items-center space-x-2 text-indigo-400 font-semibold text-xs mb-1">
              <Database className="w-4 h-4" />
              <span>Step 2: Document Ingestion & Chunking Pipeline</span>
            </div>
            <h1 className="text-2xl font-extrabold text-white">Course Materials & Vector Ingestion</h1>
            <p className="text-sm text-slate-400 mt-1 max-w-2xl">
              Upload PDFs and text files. The engine extracts pages, creates overlapping chunks (~600 chars), tags exact source metadata, and indexes them into ChromaDB for grounded retrieval.
            </p>
          </div>
          <div className="flex items-center gap-3">
            <div className="bg-slate-950/70 border border-slate-800 rounded-xl px-4 py-3 text-center">
              <div className="text-xs text-slate-400">Indexed Chunks</div>
              <div className="text-xl font-extrabold text-indigo-400">{totalChunks}</div>
            </div>
            <div className="bg-slate-950/70 border border-slate-800 rounded-xl px-4 py-3 text-center">
              <div className="text-xs text-slate-400">Total Pages</div>
              <div className="text-xl font-extrabold text-emerald-400">{totalPages}</div>
            </div>
          </div>
        </div>
      </div>

      {/* Upload Zone */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        
        {/* Upload Form Card */}
        <div className="lg:col-span-1 bg-slate-900 border border-slate-800 rounded-2xl p-5 shadow-lg space-y-4">
          <h2 className="text-sm font-bold text-white flex items-center space-x-2">
            <UploadCloud className="w-4 h-4 text-indigo-400" />
            <span>Upload New Material</span>
          </h2>

          <form onSubmit={handleUpload} className="space-y-4">
            <div>
              <label className="block text-xs font-medium text-slate-300 mb-1.5">Document Category</label>
              <div className="grid grid-cols-1 gap-2">
                {[
                  { id: 'notes', label: 'Study Notes / Textbooks', desc: 'RAG context for quizzes & tutor' },
                  { id: 'syllabus', label: 'Syllabus / Outline', desc: 'Topic tree & module structure' },
                  { id: 'past_paper', label: 'Past Exam Papers', desc: 'Calculates topic exam frequency' }
                ].map((cat) => (
                  <label
                    key={cat.id}
                    className={`flex items-start p-2.5 rounded-xl border text-xs cursor-pointer transition ${
                      docType === cat.id
                        ? 'border-indigo-500 bg-indigo-500/10 text-white'
                        : 'border-slate-800 bg-slate-950/50 text-slate-400 hover:border-slate-700'
                    }`}
                  >
                    <input
                      type="radio"
                      name="doc_type"
                      value={cat.id}
                      checked={docType === cat.id}
                      onChange={(e) => setDocType(e.target.value)}
                      className="mt-0.5 text-indigo-600 focus:ring-0 mr-2"
                    />
                    <div>
                      <div className="font-semibold text-slate-200">{cat.label}</div>
                      <div className="text-[10px] text-slate-500">{cat.desc}</div>
                    </div>
                  </label>
                ))}
              </div>
            </div>

            {/* File Input */}
            <div>
              <label className="block text-xs font-medium text-slate-300 mb-1.5">Select PDF or Text File</label>
              <div className="border-2 border-dashed border-slate-700 hover:border-indigo-500 rounded-xl p-4 text-center cursor-pointer bg-slate-950/40 transition">
                <input
                  type="file"
                  accept=".pdf,.txt,.md"
                  onChange={handleFileChange}
                  className="hidden"
                  id="file-upload-input"
                />
                <label htmlFor="file-upload-input" className="cursor-pointer block">
                  <UploadCloud className="w-8 h-8 text-slate-500 mx-auto mb-2" />
                  <span className="text-xs text-indigo-400 font-medium block">
                    {selectedFile ? selectedFile.name : 'Choose file or drag & drop'}
                  </span>
                  <span className="text-[10px] text-slate-500 block mt-0.5">
                    Supports .pdf, .txt, .md (max 50MB)
                  </span>
                </label>
              </div>
            </div>

            {message && (
              <div className={`p-3 rounded-lg text-xs flex items-start space-x-2 ${
                message.type === 'success'
                  ? 'bg-emerald-500/10 text-emerald-400 border border-emerald-500/30'
                  : 'bg-rose-500/10 text-rose-400 border border-rose-500/30'
              }`}>
                {message.type === 'success' ? <CheckCircle2 className="w-4 h-4 shrink-0 mt-0.5" /> : <AlertCircle className="w-4 h-4 shrink-0 mt-0.5" />}
                <span>{message.text}</span>
              </div>
            )}

            <button
              type="submit"
              disabled={!selectedFile || uploading}
              className="w-full py-2.5 px-4 rounded-xl bg-indigo-600 hover:bg-indigo-500 disabled:opacity-50 text-white font-medium text-xs shadow-md shadow-indigo-600/30 transition flex items-center justify-center space-x-2"
            >
              {uploading ? (
                <>
                  <RefreshCw className="w-4 h-4 animate-spin" />
                  <span>Extracting & Indexing...</span>
                </>
              ) : (
                <>
                  <Layers className="w-4 h-4" />
                  <span>Chunk & Index into ChromaDB</span>
                </>
              )}
            </button>
          </form>
        </div>

        {/* Existing Documents List */}
        <div className="lg:col-span-2 bg-slate-900 border border-slate-800 rounded-2xl p-5 shadow-lg space-y-4">
          <div className="flex items-center justify-between">
            <h2 className="text-sm font-bold text-white flex items-center space-x-2">
              <FileText className="w-4 h-4 text-emerald-400" />
              <span>Indexed Materials in Vector Store ({documents.length})</span>
            </h2>
            <button
              onClick={onNavigateToTopics}
              className="text-xs text-indigo-400 hover:text-indigo-300 font-medium flex items-center space-x-1"
            >
              <span>View Topic Map</span>
              <Sparkles className="w-3 h-3 text-amber-400" />
            </button>
          </div>

          {loading ? (
            <div className="py-12 text-center text-slate-500 text-xs">Loading indexed documents...</div>
          ) : documents.length === 0 ? (
            <div className="py-12 text-center text-slate-500 text-xs">No documents uploaded yet. Upload your syllabus and notes above!</div>
          ) : (
            <div className="divide-y divide-slate-800">
              {documents.map((doc) => {
                const badge = docTypeLabels[doc.doc_type] || docTypeLabels.notes;
                const Icon = badge.icon;
                return (
                  <div key={doc.id} className="py-3.5 flex items-center justify-between gap-4">
                    <div className="flex items-center space-x-3 min-w-0">
                      <div className="p-2 rounded-lg bg-slate-800 text-slate-300 border border-slate-700">
                        <Icon className="w-4 h-4" />
                      </div>
                      <div className="truncate">
                        <h4 className="text-xs font-semibold text-white truncate">{doc.filename}</h4>
                        <div className="flex items-center space-x-2 mt-0.5 text-[11px] text-slate-400">
                          <span>{doc.page_count} {doc.page_count === 1 ? 'Page' : 'Pages'}</span>
                          <span>•</span>
                          <span className="text-indigo-400 font-medium">{doc.chunk_count} Chroma Chunks</span>
                          <span>•</span>
                          <span>{new Date(doc.uploaded_at).toLocaleDateString()}</span>
                        </div>
                      </div>
                    </div>

                    <div className="flex items-center space-x-2 shrink-0">
                      <span className={`px-2.5 py-1 rounded-full text-[10px] font-semibold border ${badge.color}`}>
                        {badge.name}
                      </span>
                    </div>
                  </div>
                );
              })}
            </div>
          )}
        </div>

      </div>

    </div>
  );
}
