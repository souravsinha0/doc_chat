import React, { useState, useEffect, useCallback } from 'react';
import { v4 as uuidv4 } from 'uuid';
import { FileText, LogOut } from 'lucide-react';
import { useAuth } from './hooks/useAuth';
import { documentsApi, chatApi } from './api/client';
import AuthPage from './components/AuthPage';
import DocumentPanel from './components/DocumentPanel';
import ChatPanel from './components/ChatPanel';
import HistoryPanel from './components/HistoryPanel';

export default function App() {
  const { isAuthenticated, username, login, register, logout } = useAuth();

  const [documents, setDocuments] = useState([]);
  const [selectedDocIds, setSelectedDocIds] = useState([]);
  const [messages, setMessages] = useState([]);
  const [chatLoading, setChatLoading] = useState(false);
  const [sessionId, setSessionId] = useState(() => uuidv4());
  const [sessions, setSessions] = useState([]);
  const [startDate, setStartDate] = useState('');
  const [endDate, setEndDate] = useState('');
  const [uploadInProgress, setUploadInProgress] = useState(false);
  const [uploadProgress, setUploadProgress] = useState(0);
  const [uploadStatus, setUploadStatus] = useState(null);

  const loadDocuments = useCallback(async () => {
    try {
      const res = await documentsApi.list();
      setDocuments(res.data);
    } catch {}
  }, []);

  const loadSessions = useCallback(async () => {
    try {
      const res = await chatApi.getSessions();
      setSessions(res.data);
    } catch {}
  }, []);

  useEffect(() => {
    if (isAuthenticated) {
      loadDocuments();
      loadSessions();
    }
  }, [isAuthenticated, loadDocuments, loadSessions]);

  const handleUpload = async (files) => {
    setUploadInProgress(true);
    setUploadProgress(10);
    setUploadStatus(null);
    const formData = new FormData();
    files.forEach((f) => formData.append('files', f));
    try {
      const res = await documentsApi.upload(formData, (evt) => {
        if (evt.total) {
          // Upload phase is ~50%, ingestion is the rest
          const pct = Math.round((evt.loaded / evt.total) * 50);
          setUploadProgress(pct);
        }
      });
      setUploadProgress(100);
      setUploadStatus({ type: 'success', message: `${res.data.length} document(s) processed successfully` });
      await loadDocuments();
    } catch (err) {
      setUploadStatus({ type: 'error', message: err.response?.data?.detail || 'Upload failed' });
    } finally {
      setUploadInProgress(false);
      setTimeout(() => setUploadStatus(null), 4000);
    }
  };

  const handleDeleteDoc = async (id) => {
    try {
      await documentsApi.delete(id);
      setDocuments((prev) => prev.filter((d) => d.id !== id));
      setSelectedDocIds((prev) => prev.filter((x) => x !== String(id)));
    } catch {}
  };

  const handleSend = async (text) => {
    setMessages((prev) => [...prev, { role: 'user', content: text }]);
    setChatLoading(true);
    try {
      const payload = {
        query: text,
        session_id: sessionId,
        document_ids: selectedDocIds.length > 0 ? selectedDocIds : null,
        start_date: startDate || null,
        end_date: endDate || null,
      };
      const res = await chatApi.send(payload);
      setMessages((prev) => [...prev, { role: 'assistant', content: res.data.answer }]);
      // Refresh sessions list after first message
      loadSessions();
    } catch (err) {
      setMessages((prev) => [...prev, { role: 'assistant', content: `Error: ${err.response?.data?.detail || 'Something went wrong'}` }]);
    } finally {
      setChatLoading(false);
    }
  };

  const handleNewChat = () => {
    setSessionId(uuidv4());
    setMessages([]);
  };

  const handleSelectSession = async (session) => {
    setSessionId(session.session_id);
    try {
      const res = await chatApi.getHistory(session.session_id);
      setMessages(res.data.map((m) => ({ role: m.role, content: m.content })));
    } catch {}
  };

  const handleDeleteSession = async (sessionId) => {
    try {
      await chatApi.deleteSession(sessionId);
      setSessions((prev) => prev.filter((s) => s.session_id !== sessionId));
    } catch {}
  };

  if (!isAuthenticated) {
    return <AuthPage onLogin={login} onRegister={register} />;
  }

  return (
    <div style={{ minHeight: '100vh', background: '#f5f7fa', display: 'flex', flexDirection: 'column' }}>
      {/* Top navbar */}
      <header style={{
        background: '#ffffff', borderBottom: '1px solid #e2e8f0',
        padding: '0 1.5rem', height: '56px',
        display: 'flex', alignItems: 'center', justifyContent: 'space-between',
        boxShadow: '0 1px 3px rgba(0,0,0,0.04)',
        position: 'sticky', top: 0, zIndex: 100,
      }}>
        <div style={{ display: 'flex', alignItems: 'center', gap: '0.6rem' }}>
          <div style={{ width: '30px', height: '30px', background: 'linear-gradient(135deg, #6366f1, #8b5cf6)', borderRadius: '8px', display: 'flex', alignItems: 'center', justifyContent: 'center' }}>
            <FileText size={16} color="#fff" />
          </div>
          <span style={{ fontFamily: "'Plus Jakarta Sans', sans-serif", fontSize: '1rem', fontWeight: 800, color: '#0f172a', letterSpacing: '-0.02em' }}>
            Velocis Document Analyzer
          </span>
          <span style={{ fontSize: '0.65rem', color: '#94a3b8', letterSpacing: '0.08em', textTransform: 'uppercase', marginLeft: '0.25rem' }}>
            Document Intelligence
          </span>
        </div>
        <div style={{ display: 'flex', alignItems: 'center', gap: '1rem' }}>
          <span style={{ fontSize: '0.82rem', color: '#475569' }}>
            👤 <strong style={{ color: '#0f172a' }}>{username}</strong>
          </span>
          <button
            onClick={logout}
            style={{
              display: 'flex', alignItems: 'center', gap: '0.35rem',
              padding: '0.4rem 0.875rem', borderRadius: '8px',
              border: '1px solid #e2e8f0', background: '#ffffff',
              color: '#475569', fontSize: '0.8rem', cursor: 'pointer',
              fontFamily: 'inherit', fontWeight: 500, transition: 'all 0.15s',
            }}
            onMouseEnter={(e) => { e.currentTarget.style.borderColor = '#ef4444'; e.currentTarget.style.color = '#ef4444'; }}
            onMouseLeave={(e) => { e.currentTarget.style.borderColor = '#e2e8f0'; e.currentTarget.style.color = '#475569'; }}
          >
            <LogOut size={13} /> Logout
          </button>
        </div>
      </header>

      {/* Main 3-column layout */}
      <main style={{ flex: 1, display: 'grid', gridTemplateColumns: '280px 1fr 240px', gap: '1rem', padding: '1rem 1.25rem', maxWidth: '1600px', width: '100%', margin: '0 auto', height: 'calc(100vh - 56px)', boxSizing: 'border-box' }}>
        {/* Left: Documents */}
        <div style={{ display: 'flex', flexDirection: 'column', gap: '0', overflow: 'hidden' }}>
          <DocumentPanel
            documents={documents}
            selectedDocIds={selectedDocIds}
            onSelectionChange={setSelectedDocIds}
            onUpload={handleUpload}
            onDelete={handleDeleteDoc}
            uploadInProgress={uploadInProgress}
            uploadProgress={uploadProgress}
            uploadStatus={uploadStatus}
          />
        </div>

        {/* Center: Chat */}
        <div style={{ overflow: 'hidden' }}>
          <ChatPanel
            messages={messages}
            onSend={handleSend}
            loading={chatLoading}
            uploadInProgress={uploadInProgress}
            selectedDocIds={selectedDocIds}
            startDate={startDate}
            endDate={endDate}
            sessionId={sessionId}
            onNewChat={handleNewChat}
            onStartDateChange={setStartDate}
            onEndDateChange={setEndDate}
          />
        </div>

        {/* Right: History */}
        <div style={{ overflow: 'hidden' }}>
          <HistoryPanel
            sessions={sessions}
            currentSessionId={sessionId}
            onSelect={handleSelectSession}
            onDelete={handleDeleteSession}
            onRefresh={loadSessions}
          />
        </div>
      </main>
    </div>
  );
}
