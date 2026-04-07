import React, { useState, useRef, useEffect } from 'react';
import ReactMarkdown from 'react-markdown';
import remarkGfm from 'remark-gfm';
import { Send, Plus, Bot, User, Loader2, FileText, Calendar } from 'lucide-react';

const mdComponents = {
  table: ({ children }) => (
    <div style={{ overflowX: 'auto', margin: '0.5rem 0' }}>
      <table style={{ borderCollapse: 'collapse', width: '100%', fontSize: '0.82rem' }}>{children}</table>
    </div>
  ),
  th: ({ children }) => (
    <th style={{ padding: '0.4rem 0.75rem', background: '#f1f5f9', border: '1px solid #e2e8f0', fontWeight: 600, textAlign: 'left' }}>{children}</th>
  ),
  td: ({ children }) => (
    <td style={{ padding: '0.4rem 0.75rem', border: '1px solid #e2e8f0' }}>{children}</td>
  ),
  code: ({ inline, children }) =>
    inline ? (
      <code style={{ background: '#f1f5f9', padding: '0.1rem 0.35rem', borderRadius: '4px', fontSize: '0.82em', color: '#6366f1' }}>{children}</code>
    ) : (
      <pre style={{ background: '#f8fafc', border: '1px solid #e2e8f0', borderRadius: '8px', padding: '0.75rem', overflowX: 'auto', fontSize: '0.82rem', margin: '0.5rem 0' }}>
        <code>{children}</code>
      </pre>
    ),
};

function ChatBubble({ msg }) {
  const isUser = msg.role === 'user';
  return (
    <div style={{ display: 'flex', gap: '0.6rem', alignItems: 'flex-start', flexDirection: isUser ? 'row-reverse' : 'row', marginBottom: '1rem' }}>
      <div style={{
        width: '30px', height: '30px', borderRadius: '50%', flexShrink: 0,
        background: isUser ? 'linear-gradient(135deg, #6366f1, #8b5cf6)' : '#f1f5f9',
        display: 'flex', alignItems: 'center', justifyContent: 'center',
        border: isUser ? 'none' : '1px solid #e2e8f0',
      }}>
        {isUser ? <User size={14} color="#fff" /> : <Bot size={14} color="#6366f1" />}
      </div>
      <div style={{
        maxWidth: '78%',
        padding: '0.65rem 0.9rem',
        borderRadius: isUser ? '14px 4px 14px 14px' : '4px 14px 14px 14px',
        background: isUser ? 'linear-gradient(135deg, #6366f1, #8b5cf6)' : '#ffffff',
        color: isUser ? '#ffffff' : '#0f172a',
        fontSize: '0.875rem',
        lineHeight: '1.6',
        boxShadow: '0 1px 3px rgba(0,0,0,0.06)',
        border: isUser ? 'none' : '1px solid #e2e8f0',
      }}>
        {isUser ? (
          <span>{msg.content}</span>
        ) : (
          <ReactMarkdown remarkPlugins={[remarkGfm]} components={mdComponents}>
            {msg.content}
          </ReactMarkdown>
        )}
      </div>
    </div>
  );
}

export default function ChatPanel({
  messages, onSend, loading, uploadInProgress,
  selectedDocIds, startDate, endDate, sessionId, onNewChat,
  onStartDateChange, onEndDateChange,
}) {
  const [input, setInput] = useState('');
  const [showDateFilter, setShowDateFilter] = useState(false);
  const bottomRef = useRef(null);
  const textareaRef = useRef(null);

  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages, loading]);

  const handleSend = () => {
    const trimmed = input.trim();
    if (!trimmed || loading || uploadInProgress) return;
    onSend(trimmed);
    setInput('');
    if (textareaRef.current) textareaRef.current.style.height = 'auto';
  };

  const handleKeyDown = (e) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSend();
    }
  };

  const handleTextareaChange = (e) => {
    setInput(e.target.value);
    e.target.style.height = 'auto';
    e.target.style.height = Math.min(e.target.scrollHeight, 120) + 'px';
  };

  const contextLabel = selectedDocIds.length > 0
    ? `${selectedDocIds.length} doc${selectedDocIds.length !== 1 ? 's' : ''} selected`
    : 'All documents';

  return (
    <div style={{ display: 'flex', flexDirection: 'column', height: '100%', background: '#ffffff', borderRadius: '14px', boxShadow: '0 1px 3px rgba(0,0,0,0.06)', border: '1px solid #e2e8f0', overflow: 'hidden' }}>
      {/* Header */}
      <div style={{ padding: '0.875rem 1.25rem', borderBottom: '1px solid #f1f5f9', display: 'flex', alignItems: 'center', justifyContent: 'space-between', background: '#fafafa' }}>
        <div style={{ display: 'flex', alignItems: 'center', gap: '0.75rem' }}>
          <div style={{ fontFamily: "'Plus Jakarta Sans', sans-serif", fontSize: '1rem', fontWeight: 700, color: '#0f172a' }}>
            Chat
          </div>
          <span style={{
            fontSize: '0.7rem', padding: '0.2rem 0.6rem', borderRadius: '99px',
            background: selectedDocIds.length > 0 ? '#eef2ff' : '#f1f5f9',
            color: selectedDocIds.length > 0 ? '#6366f1' : '#94a3b8',
            border: `1px solid ${selectedDocIds.length > 0 ? '#c7d2fe' : '#e2e8f0'}`,
            fontWeight: 500,
          }}>
            <FileText size={10} style={{ display: 'inline', marginRight: '0.25rem', verticalAlign: 'middle' }} />
            {contextLabel}
          </span>
        </div>
        <div style={{ display: 'flex', gap: '0.5rem', alignItems: 'center' }}>
          <button
            onClick={() => setShowDateFilter(!showDateFilter)}
            style={{
              padding: '0.35rem 0.7rem', borderRadius: '7px', border: '1px solid #e2e8f0',
              background: showDateFilter ? '#eef2ff' : '#ffffff', color: showDateFilter ? '#6366f1' : '#94a3b8',
              fontSize: '0.75rem', cursor: 'pointer', display: 'flex', alignItems: 'center', gap: '0.3rem',
              fontFamily: 'inherit', fontWeight: 500,
            }}
          >
            <Calendar size={13} /> Date Filter
          </button>
          <button
            onClick={onNewChat}
            style={{
              padding: '0.35rem 0.75rem', borderRadius: '7px',
              background: 'linear-gradient(135deg, #6366f1, #8b5cf6)',
              color: '#fff', border: 'none', fontSize: '0.75rem', cursor: 'pointer',
              display: 'flex', alignItems: 'center', gap: '0.3rem', fontFamily: 'inherit', fontWeight: 600,
            }}
          >
            <Plus size={13} /> New Chat
          </button>
        </div>
      </div>

      {/* Date filter bar */}
      {showDateFilter && (
        <div style={{ padding: '0.6rem 1.25rem', borderBottom: '1px solid #f1f5f9', background: '#fafafa', display: 'flex', alignItems: 'center', gap: '1rem' }}>
          <span style={{ fontSize: '0.75rem', color: '#475569', fontWeight: 500 }}>From:</span>
          <input type="date" value={startDate || ''} onChange={(e) => onStartDateChange(e.target.value)}
            style={{ padding: '0.3rem 0.5rem', border: '1px solid #e2e8f0', borderRadius: '6px', fontSize: '0.78rem', color: '#374151', fontFamily: 'inherit', outline: 'none' }} />
          <span style={{ fontSize: '0.75rem', color: '#475569', fontWeight: 500 }}>To:</span>
          <input type="date" value={endDate || ''} onChange={(e) => onEndDateChange(e.target.value)}
            style={{ padding: '0.3rem 0.5rem', border: '1px solid #e2e8f0', borderRadius: '6px', fontSize: '0.78rem', color: '#374151', fontFamily: 'inherit', outline: 'none' }} />
          {(startDate || endDate) && (
            <button onClick={() => { onStartDateChange(''); onEndDateChange(''); }}
              style={{ fontSize: '0.72rem', color: '#ef4444', background: 'none', border: 'none', cursor: 'pointer', fontFamily: 'inherit' }}>
              Clear
            </button>
          )}
        </div>
      )}

      {/* Upload blocking banner */}
      {uploadInProgress && (
        <div style={{ padding: '0.6rem 1.25rem', background: '#fffbeb', borderBottom: '1px solid #fde68a', display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
          <Loader2 size={14} color="#d97706" style={{ animation: 'spin 1s linear infinite', flexShrink: 0 }} />
          <span style={{ fontSize: '0.78rem', color: '#92400e', fontWeight: 500 }}>
            Documents are being processed. Chat will be available once ingestion completes.
          </span>
        </div>
      )}

      {/* Messages */}
      <div style={{ flex: 1, overflowY: 'auto', padding: '1.25rem' }}>
        {messages.length === 0 ? (
          <div style={{ display: 'flex', flexDirection: 'column', alignItems: 'center', justifyContent: 'center', height: '100%', textAlign: 'center', color: '#94a3b8' }}>
            <div style={{ width: '56px', height: '56px', background: '#f1f5f9', borderRadius: '50%', display: 'flex', alignItems: 'center', justifyContent: 'center', margin: '0 auto 1rem' }}>
              <Bot size={26} color="#6366f1" />
            </div>
            <div style={{ fontFamily: "'Plus Jakarta Sans', sans-serif", fontSize: '1.05rem', fontWeight: 700, color: '#374151', marginBottom: '0.4rem' }}>
              Start a conversation
            </div>
            <div style={{ fontSize: '0.82rem', maxWidth: '280px', lineHeight: 1.6 }}>
              Upload documents and ask anything — summaries, comparisons, specific data points.
            </div>
          </div>
        ) : (
          messages.map((msg, i) => <ChatBubble key={i} msg={msg} />)
        )}
        {loading && (
          <div style={{ display: 'flex', gap: '0.6rem', alignItems: 'flex-start', marginBottom: '1rem' }}>
            <div style={{ width: '30px', height: '30px', borderRadius: '50%', background: '#f1f5f9', display: 'flex', alignItems: 'center', justifyContent: 'center', border: '1px solid #e2e8f0', flexShrink: 0 }}>
              <Bot size={14} color="#6366f1" />
            </div>
            <div style={{ padding: '0.65rem 0.9rem', background: '#ffffff', border: '1px solid #e2e8f0', borderRadius: '4px 14px 14px 14px', boxShadow: '0 1px 3px rgba(0,0,0,0.06)' }}>
              <div style={{ display: 'flex', gap: '4px', alignItems: 'center' }}>
                {[0, 1, 2].map((i) => (
                  <div key={i} style={{ width: '6px', height: '6px', borderRadius: '50%', background: '#6366f1', animation: `bounce 1.2s ease-in-out ${i * 0.2}s infinite` }} />
                ))}
              </div>
            </div>
          </div>
        )}
        <div ref={bottomRef} />
      </div>

      {/* Input */}
      <div style={{ padding: '0.875rem 1.25rem', borderTop: '1px solid #f1f5f9', background: '#fafafa' }}>
        <div style={{
          display: 'flex', gap: '0.6rem', alignItems: 'flex-end',
          background: '#ffffff', border: '1.5px solid #e2e8f0', borderRadius: '12px',
          padding: '0.5rem 0.5rem 0.5rem 0.875rem',
          transition: 'border-color 0.2s, box-shadow 0.2s',
        }}
          onFocus={(e) => { e.currentTarget.style.borderColor = '#6366f1'; e.currentTarget.style.boxShadow = '0 0 0 3px rgba(99,102,241,0.1)'; }}
          onBlur={(e) => { e.currentTarget.style.borderColor = '#e2e8f0'; e.currentTarget.style.boxShadow = 'none'; }}
        >
          <textarea
            ref={textareaRef}
            value={input}
            onChange={handleTextareaChange}
            onKeyDown={handleKeyDown}
            placeholder={uploadInProgress ? 'Waiting for document processing…' : 'Ask about your documents…'}
            disabled={loading || uploadInProgress}
            rows={1}
            style={{
              flex: 1, border: 'none', outline: 'none', resize: 'none',
              fontSize: '0.875rem', color: '#0f172a', background: 'transparent',
              fontFamily: 'inherit', lineHeight: '1.5', maxHeight: '120px',
              cursor: uploadInProgress ? 'not-allowed' : 'text',
            }}
          />
          <button
            onClick={handleSend}
            disabled={!input.trim() || loading || uploadInProgress}
            style={{
              width: '34px', height: '34px', borderRadius: '8px', border: 'none',
              background: (!input.trim() || loading || uploadInProgress) ? '#f1f5f9' : 'linear-gradient(135deg, #6366f1, #8b5cf6)',
              color: (!input.trim() || loading || uploadInProgress) ? '#94a3b8' : '#ffffff',
              cursor: (!input.trim() || loading || uploadInProgress) ? 'not-allowed' : 'pointer',
              display: 'flex', alignItems: 'center', justifyContent: 'center',
              transition: 'all 0.2s', flexShrink: 0,
            }}
          >
            <Send size={15} />
          </button>
        </div>
        <div style={{ fontSize: '0.68rem', color: '#94a3b8', marginTop: '0.4rem', textAlign: 'center' }}>
          Press Enter to send · Shift+Enter for new line
        </div>
      </div>

      <style>{`
        @keyframes spin { from { transform: rotate(0deg); } to { transform: rotate(360deg); } }
        @keyframes bounce { 0%, 80%, 100% { transform: scale(0.6); opacity: 0.4; } 40% { transform: scale(1); opacity: 1; } }
      `}</style>
    </div>
  );
}
