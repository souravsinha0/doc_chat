import React from 'react';
import { MessageSquare, Trash2, RefreshCw, Clock } from 'lucide-react';
import { formatDistanceToNow, isToday, isYesterday, parseISO } from 'date-fns';

function groupByDate(sessions) {
  const groups = {};
  sessions.forEach((s) => {
    let label;
    try {
      const d = parseISO(s.last_message);
      if (isToday(d)) label = 'Today';
      else if (isYesterday(d)) label = 'Yesterday';
      else label = d.toLocaleDateString('en-GB', { day: '2-digit', month: 'short', year: 'numeric' });
    } catch {
      label = 'Other';
    }
    if (!groups[label]) groups[label] = [];
    groups[label].push(s);
  });
  return groups;
}

export default function HistoryPanel({ sessions, currentSessionId, onSelect, onDelete, onRefresh }) {
  const grouped = groupByDate(sessions);
  const order = ['Today', 'Yesterday', ...Object.keys(grouped).filter((k) => k !== 'Today' && k !== 'Yesterday').sort((a, b) => b.localeCompare(a))];

  return (
    <div style={{ display: 'flex', flexDirection: 'column', height: '100%', background: '#ffffff', borderRadius: '14px', boxShadow: '0 1px 3px rgba(0,0,0,0.06)', border: '1px solid #e2e8f0', overflow: 'hidden' }}>
      <div style={{ padding: '0.875rem 1rem 0.75rem', borderBottom: '1px solid #f1f5f9', display: 'flex', alignItems: 'center', justifyContent: 'space-between', background: '#fafafa' }}>
        <div style={{ fontFamily: "'Plus Jakarta Sans', sans-serif", fontSize: '0.95rem', fontWeight: 700, color: '#0f172a' }}>
          History
        </div>
        <button
          onClick={onRefresh}
          style={{ background: 'none', border: '1px solid #e2e8f0', borderRadius: '6px', cursor: 'pointer', color: '#94a3b8', padding: '0.25rem', display: 'flex', transition: 'all 0.15s' }}
          onMouseEnter={(e) => { e.currentTarget.style.color = '#6366f1'; e.currentTarget.style.borderColor = '#c7d2fe'; }}
          onMouseLeave={(e) => { e.currentTarget.style.color = '#94a3b8'; e.currentTarget.style.borderColor = '#e2e8f0'; }}
          title="Refresh history"
        >
          <RefreshCw size={13} />
        </button>
      </div>

      <div style={{ flex: 1, overflowY: 'auto', padding: '0.5rem' }}>
        {sessions.length === 0 ? (
          <div style={{ textAlign: 'center', padding: '2rem 1rem', color: '#94a3b8' }}>
            <Clock size={26} style={{ margin: '0 auto 0.5rem', opacity: 0.4 }} />
            <div style={{ fontSize: '0.8rem' }}>No previous chats</div>
          </div>
        ) : (
          order.filter((g) => grouped[g]).map((group) => (
            <div key={group}>
              <div style={{ fontSize: '0.62rem', fontWeight: 700, letterSpacing: '0.1em', textTransform: 'uppercase', color: '#94a3b8', padding: '0.5rem 0.5rem 0.3rem' }}>
                {group}
              </div>
              {grouped[group].map((session) => {
                const isActive = session.session_id === currentSessionId;
                let timeAgo = '';
                try { timeAgo = formatDistanceToNow(parseISO(session.last_message), { addSuffix: true }); } catch {}
                return (
                  <div key={session.session_id} style={{
                    display: 'flex', alignItems: 'center', gap: '0.4rem',
                    padding: '0.45rem 0.5rem', borderRadius: '8px', marginBottom: '0.15rem',
                    background: isActive ? '#eef2ff' : 'transparent',
                    border: `1px solid ${isActive ? '#c7d2fe' : 'transparent'}`,
                    transition: 'all 0.15s',
                  }}
                    onMouseEnter={(e) => { if (!isActive) e.currentTarget.style.background = '#f8fafc'; }}
                    onMouseLeave={(e) => { if (!isActive) e.currentTarget.style.background = 'transparent'; }}
                  >
                    <button
                      onClick={() => onSelect(session)}
                      style={{ flex: 1, background: 'none', border: 'none', cursor: 'pointer', textAlign: 'left', padding: 0, display: 'flex', alignItems: 'center', gap: '0.5rem', minWidth: 0 }}
                    >
                      <div style={{ width: '26px', height: '26px', borderRadius: '6px', background: isActive ? '#6366f1' : '#f1f5f9', display: 'flex', alignItems: 'center', justifyContent: 'center', flexShrink: 0 }}>
                        <MessageSquare size={12} color={isActive ? '#fff' : '#94a3b8'} />
                      </div>
                      <div style={{ minWidth: 0 }}>
                        <div style={{ fontSize: '0.75rem', color: isActive ? '#4f46e5' : '#374151', fontWeight: isActive ? 600 : 400, overflow: 'hidden', textOverflow: 'ellipsis', whiteSpace: 'nowrap' }}>
                          {session.session_id.slice(0, 8)}…
                        </div>
                        <div style={{ fontSize: '0.65rem', color: '#94a3b8' }}>{timeAgo}</div>
                      </div>
                    </button>
                    <button
                      onClick={() => onDelete(session.session_id)}
                      style={{ background: 'none', border: 'none', cursor: 'pointer', color: '#cbd5e1', padding: '0.2rem', display: 'flex', borderRadius: '5px', transition: 'color 0.15s, background 0.15s', flexShrink: 0 }}
                      onMouseEnter={(e) => { e.currentTarget.style.color = '#ef4444'; e.currentTarget.style.background = '#fef2f2'; }}
                      onMouseLeave={(e) => { e.currentTarget.style.color = '#cbd5e1'; e.currentTarget.style.background = 'transparent'; }}
                    >
                      <Trash2 size={12} />
                    </button>
                  </div>
                );
              })}
            </div>
          ))
        )}
      </div>
    </div>
  );
}
