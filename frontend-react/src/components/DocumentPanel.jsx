import React, { useState, useCallback } from 'react';
import { useDropzone } from 'react-dropzone';
import { Upload, X, FileText, File, Trash2, CheckSquare, Square, Loader2, AlertCircle, CheckCircle2 } from 'lucide-react';

const ACCEPTED_TYPES = {
  'application/pdf': ['.pdf'],
  'application/msword': ['.doc'],
  'application/vnd.openxmlformats-officedocument.wordprocessingml.document': ['.docx'],
  'application/vnd.ms-excel': ['.xls'],
  'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet': ['.xlsx'],
  'text/csv': ['.csv'],
  'application/vnd.ms-powerpoint': ['.ppt'],
  'application/vnd.openxmlformats-officedocument.presentationml.presentation': ['.pptx'],
  'text/plain': ['.txt'],
  'text/x-python': ['.py'],
  'text/markdown': ['.md'],
};

const EXT_COLORS = {
  pdf: '#ef4444', doc: '#3b82f6', docx: '#3b82f6',
  xlsx: '#10b981', xls: '#10b981', csv: '#10b981',
  ppt: '#f59e0b', pptx: '#f59e0b',
  txt: '#6366f1', py: '#8b5cf6', md: '#06b6d4',
};

function ExtBadge({ filename }) {
  const ext = filename.split('.').pop().toLowerCase();
  const color = EXT_COLORS[ext] || '#94a3b8';
  return (
    <span style={{
      fontSize: '0.6rem', fontWeight: 700, padding: '1px 5px',
      borderRadius: '4px', background: `${color}18`, color,
      border: `1px solid ${color}30`, letterSpacing: '0.04em',
      textTransform: 'uppercase', flexShrink: 0,
    }}>{ext}</span>
  );
}

export default function DocumentPanel({
  documents, selectedDocIds, onSelectionChange,
  onUpload, onDelete, uploadInProgress, uploadProgress, uploadStatus,
}) {
  const [pendingFiles, setPendingFiles] = useState([]);

  const onDrop = useCallback((accepted) => {
    setPendingFiles((prev) => {
      const existing = new Set(prev.map((f) => f.name));
      const newFiles = accepted.filter((f) => !existing.has(f.name));
      return [...prev, ...newFiles].slice(0, 30);
    });
  }, []);

  const { getRootProps, getInputProps, isDragActive } = useDropzone({
    onDrop,
    accept: ACCEPTED_TYPES,
    multiple: true,
    disabled: uploadInProgress,
  });

  const removePending = (name) => setPendingFiles((p) => p.filter((f) => f.name !== name));

  const handleUpload = async () => {
    if (!pendingFiles.length) return;
    await onUpload(pendingFiles);
    setPendingFiles([]);
  };

  const toggleDoc = (id) => {
    const sid = String(id);
    if (selectedDocIds.includes(sid)) {
      onSelectionChange(selectedDocIds.filter((x) => x !== sid));
    } else {
      onSelectionChange([...selectedDocIds, sid]);
    }
  };

  return (
    <div style={{ display: 'flex', flexDirection: 'column', gap: '1rem', height: '100%' }}>
      {/* Upload zone */}
      <div style={{
        background: '#ffffff', borderRadius: '14px',
        boxShadow: '0 1px 3px rgba(0,0,0,0.06)', border: '1px solid #e2e8f0', overflow: 'hidden',
      }}>
        <div style={{ padding: '1rem 1rem 0.75rem', borderBottom: '1px solid #f1f5f9' }}>
          <div style={{ fontSize: '0.7rem', fontWeight: 700, letterSpacing: '0.1em', textTransform: 'uppercase', color: '#94a3b8' }}>
            Upload Documents
          </div>
        </div>
        <div style={{ padding: '0.875rem' }}>
          <div
            {...getRootProps()}
            style={{
              border: `2px dashed ${isDragActive ? '#6366f1' : '#e2e8f0'}`,
              borderRadius: '10px',
              padding: '1.25rem',
              textAlign: 'center',
              cursor: uploadInProgress ? 'not-allowed' : 'pointer',
              background: isDragActive ? '#eef2ff' : '#fafafa',
              transition: 'all 0.2s',
              opacity: uploadInProgress ? 0.6 : 1,
            }}
          >
            <input {...getInputProps()} />
            <Upload size={20} color={isDragActive ? '#6366f1' : '#94a3b8'} style={{ margin: '0 auto 0.5rem' }} />
            <div style={{ fontSize: '0.8rem', color: '#475569', fontWeight: 500 }}>
              {isDragActive ? 'Drop files here' : 'Drag & drop or click to browse'}
            </div>
            <div style={{ fontSize: '0.7rem', color: '#94a3b8', marginTop: '0.25rem' }}>
              PDF, DOCX, XLSX, CSV, PPTX, TXT, PY, MD
            </div>
          </div>

          {/* Pending files list */}
          {pendingFiles.length > 0 && (
            <div style={{ marginTop: '0.75rem' }}>
              <div style={{ maxHeight: '120px', overflowY: 'auto', display: 'flex', flexDirection: 'column', gap: '0.3rem' }}>
                {pendingFiles.map((f) => (
                  <div key={f.name} style={{
                    display: 'flex', alignItems: 'center', gap: '0.5rem',
                    padding: '0.35rem 0.5rem', background: '#f8fafc', borderRadius: '7px',
                    border: '1px solid #e2e8f0',
                  }}>
                    <File size={12} color="#6366f1" style={{ flexShrink: 0 }} />
                    <span style={{ fontSize: '0.75rem', color: '#374151', flex: 1, overflow: 'hidden', textOverflow: 'ellipsis', whiteSpace: 'nowrap' }}>
                      {f.name}
                    </span>
                    <ExtBadge filename={f.name} />
                    <button onClick={() => removePending(f.name)} style={{ background: 'none', border: 'none', cursor: 'pointer', color: '#94a3b8', padding: 0, display: 'flex' }}>
                      <X size={13} />
                    </button>
                  </div>
                ))}
              </div>

              {/* Progress bar */}
              {uploadInProgress && (
                <div style={{ marginTop: '0.75rem' }}>
                  <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: '0.3rem' }}>
                    <span style={{ fontSize: '0.72rem', color: '#6366f1', fontWeight: 500 }}>Processing…</span>
                    <span style={{ fontSize: '0.72rem', color: '#94a3b8' }}>{uploadProgress}%</span>
                  </div>
                  <div style={{ height: '5px', background: '#e2e8f0', borderRadius: '99px', overflow: 'hidden' }}>
                    <div style={{
                      height: '100%', width: `${uploadProgress}%`,
                      background: 'linear-gradient(90deg, #6366f1, #8b5cf6)',
                      borderRadius: '99px', transition: 'width 0.4s ease',
                    }} />
                  </div>
                </div>
              )}

              {uploadStatus && (
                <div style={{
                  marginTop: '0.6rem', padding: '0.5rem 0.75rem', borderRadius: '8px',
                  display: 'flex', alignItems: 'center', gap: '0.4rem', fontSize: '0.75rem',
                  background: uploadStatus.type === 'success' ? '#ecfdf5' : '#fef2f2',
                  color: uploadStatus.type === 'success' ? '#059669' : '#dc2626',
                  border: `1px solid ${uploadStatus.type === 'success' ? '#a7f3d0' : '#fecaca'}`,
                }}>
                  {uploadStatus.type === 'success' ? <CheckCircle2 size={13} /> : <AlertCircle size={13} />}
                  {uploadStatus.message}
                </div>
              )}

              {!uploadInProgress && (
                <button
                  onClick={handleUpload}
                  style={{
                    marginTop: '0.75rem', width: '100%', padding: '0.6rem',
                    background: 'linear-gradient(135deg, #6366f1, #8b5cf6)',
                    color: '#fff', border: 'none', borderRadius: '8px',
                    fontSize: '0.82rem', fontWeight: 600, cursor: 'pointer',
                    display: 'flex', alignItems: 'center', justifyContent: 'center', gap: '0.4rem',
                    fontFamily: 'inherit',
                  }}
                >
                  <Upload size={14} />
                  Upload {pendingFiles.length} file{pendingFiles.length !== 1 ? 's' : ''}
                </button>
              )}
              {uploadInProgress && (
                <div style={{
                  marginTop: '0.75rem', width: '100%', padding: '0.6rem',
                  background: '#f1f5f9', borderRadius: '8px', fontSize: '0.82rem',
                  color: '#6366f1', display: 'flex', alignItems: 'center', justifyContent: 'center', gap: '0.4rem',
                }}>
                  <Loader2 size={14} style={{ animation: 'spin 1s linear infinite' }} />
                  Ingesting documents…
                </div>
              )}
            </div>
          )}
        </div>
      </div>

      {/* Document list */}
      <div style={{
        background: '#ffffff', borderRadius: '14px', flex: 1,
        boxShadow: '0 1px 3px rgba(0,0,0,0.06)', border: '1px solid #e2e8f0',
        display: 'flex', flexDirection: 'column', overflow: 'hidden',
      }}>
        <div style={{ padding: '1rem 1rem 0.75rem', borderBottom: '1px solid #f1f5f9', display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
          <div style={{ fontSize: '0.7rem', fontWeight: 700, letterSpacing: '0.1em', textTransform: 'uppercase', color: '#94a3b8' }}>
            Documents
          </div>
          <span style={{ fontSize: '0.72rem', color: '#94a3b8' }}>
            {selectedDocIds.length > 0 ? `${selectedDocIds.length} selected` : 'All docs'}
          </span>
        </div>
        <div style={{ flex: 1, overflowY: 'auto', padding: '0.5rem' }}>
          {documents.length === 0 ? (
            <div style={{ textAlign: 'center', padding: '2rem 1rem', color: '#94a3b8' }}>
              <FileText size={28} style={{ margin: '0 auto 0.5rem', opacity: 0.4 }} />
              <div style={{ fontSize: '0.8rem' }}>No documents yet</div>
              <div style={{ fontSize: '0.72rem', marginTop: '0.25rem' }}>Upload files to get started</div>
            </div>
          ) : (
            documents.map((doc) => {
              const selected = selectedDocIds.includes(String(doc.id));
              return (
                <div key={doc.id} style={{
                  display: 'flex', alignItems: 'center', gap: '0.5rem',
                  padding: '0.45rem 0.5rem', borderRadius: '8px',
                  background: selected ? '#eef2ff' : 'transparent',
                  border: `1px solid ${selected ? '#c7d2fe' : 'transparent'}`,
                  marginBottom: '0.2rem', transition: 'all 0.15s',
                }}>
                  <button onClick={() => toggleDoc(doc.id)} style={{ background: 'none', border: 'none', cursor: 'pointer', color: selected ? '#6366f1' : '#cbd5e1', padding: 0, display: 'flex', flexShrink: 0 }}>
                    {selected ? <CheckSquare size={15} /> : <Square size={15} />}
                  </button>
                  <div style={{ flex: 1, minWidth: 0 }}>
                    <div style={{ display: 'flex', alignItems: 'center', gap: '0.35rem' }}>
                      <span style={{ fontSize: '0.78rem', color: '#374151', overflow: 'hidden', textOverflow: 'ellipsis', whiteSpace: 'nowrap' }} title={doc.filename}>
                        {doc.filename.length > 20 ? doc.filename.slice(0, 18) + '…' : doc.filename}
                      </span>
                      <ExtBadge filename={doc.filename} />
                    </div>
                    <div style={{ fontSize: '0.65rem', color: '#94a3b8', marginTop: '1px' }}>{doc.uploaded_at}</div>
                  </div>
                  <button
                    onClick={() => onDelete(doc.id)}
                    style={{ background: 'none', border: 'none', cursor: 'pointer', color: '#cbd5e1', padding: '0.2rem', display: 'flex', borderRadius: '5px', transition: 'color 0.15s, background 0.15s', flexShrink: 0 }}
                    onMouseEnter={(e) => { e.currentTarget.style.color = '#ef4444'; e.currentTarget.style.background = '#fef2f2'; }}
                    onMouseLeave={(e) => { e.currentTarget.style.color = '#cbd5e1'; e.currentTarget.style.background = 'transparent'; }}
                    title={`Delete ${doc.filename}`}
                  >
                    <Trash2 size={13} />
                  </button>
                </div>
              );
            })
          )}
        </div>
      </div>

      <style>{`@keyframes spin { from { transform: rotate(0deg); } to { transform: rotate(360deg); } }`}</style>
    </div>
  );
}
