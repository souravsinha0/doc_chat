import React, { useState } from 'react';
import { FileText, Lock, User, Mail, Eye, EyeOff, AlertCircle } from 'lucide-react';

const styles = {
  page: {
    minHeight: '100vh',
    background: 'linear-gradient(135deg, #f0f4ff 0%, #faf5ff 50%, #f0fdf4 100%)',
    display: 'flex',
    alignItems: 'center',
    justifyContent: 'center',
    padding: '1.5rem',
  },
  container: {
    width: '100%',
    maxWidth: '420px',
  },
  brand: {
    textAlign: 'center',
    marginBottom: '2rem',
  },
  brandIcon: {
    width: '52px',
    height: '52px',
    background: 'linear-gradient(135deg, #6366f1, #8b5cf6)',
    borderRadius: '14px',
    display: 'flex',
    alignItems: 'center',
    justifyContent: 'center',
    margin: '0 auto 1rem',
    boxShadow: '0 8px 24px rgba(99,102,241,0.3)',
  },
  brandTitle: {
    fontFamily: "'Plus Jakarta Sans', sans-serif",
    fontSize: '1.5rem',
    fontWeight: 800,
    color: '#0f172a',
    letterSpacing: '-0.03em',
  },
  brandSub: {
    fontSize: '0.8rem',
    color: '#94a3b8',
    marginTop: '0.25rem',
    letterSpacing: '0.06em',
    textTransform: 'uppercase',
  },
  card: {
    background: '#ffffff',
    borderRadius: '20px',
    boxShadow: '0 20px 60px rgba(0,0,0,0.1), 0 4px 12px rgba(0,0,0,0.05)',
    overflow: 'hidden',
  },
  tabs: {
    display: 'flex',
    borderBottom: '1px solid #e2e8f0',
  },
  tab: (active) => ({
    flex: 1,
    padding: '1rem',
    border: 'none',
    background: active ? '#ffffff' : '#f8fafc',
    color: active ? '#6366f1' : '#94a3b8',
    fontWeight: active ? 600 : 500,
    fontSize: '0.875rem',
    cursor: 'pointer',
    borderBottom: active ? '2px solid #6366f1' : '2px solid transparent',
    transition: 'all 0.2s',
    fontFamily: 'inherit',
  }),
  form: {
    padding: '1.75rem',
    display: 'flex',
    flexDirection: 'column',
    gap: '1rem',
  },
  fieldGroup: {
    display: 'flex',
    flexDirection: 'column',
    gap: '0.375rem',
  },
  label: {
    fontSize: '0.8rem',
    fontWeight: 600,
    color: '#374151',
    letterSpacing: '0.01em',
  },
  inputWrap: {
    position: 'relative',
    display: 'flex',
    alignItems: 'center',
  },
  inputIcon: {
    position: 'absolute',
    left: '0.875rem',
    color: '#94a3b8',
    pointerEvents: 'none',
  },
  input: (hasError) => ({
    width: '100%',
    padding: '0.65rem 0.875rem 0.65rem 2.5rem',
    border: `1.5px solid ${hasError ? '#ef4444' : '#e2e8f0'}`,
    borderRadius: '10px',
    fontSize: '0.875rem',
    color: '#0f172a',
    background: '#ffffff',
    outline: 'none',
    transition: 'border-color 0.2s, box-shadow 0.2s',
    fontFamily: 'inherit',
  }),
  eyeBtn: {
    position: 'absolute',
    right: '0.875rem',
    background: 'none',
    border: 'none',
    cursor: 'pointer',
    color: '#94a3b8',
    padding: '0',
    display: 'flex',
  },
  error: {
    display: 'flex',
    alignItems: 'center',
    gap: '0.4rem',
    padding: '0.65rem 0.875rem',
    background: '#fef2f2',
    border: '1px solid #fecaca',
    borderRadius: '8px',
    color: '#dc2626',
    fontSize: '0.8rem',
  },
  submitBtn: (loading) => ({
    padding: '0.75rem',
    background: loading ? '#a5b4fc' : 'linear-gradient(135deg, #6366f1, #8b5cf6)',
    color: '#ffffff',
    border: 'none',
    borderRadius: '10px',
    fontSize: '0.9rem',
    fontWeight: 600,
    cursor: loading ? 'not-allowed' : 'pointer',
    transition: 'opacity 0.2s, transform 0.15s',
    fontFamily: 'inherit',
    marginTop: '0.25rem',
  }),
  footer: {
    textAlign: 'center',
    marginTop: '1.5rem',
    fontSize: '0.72rem',
    color: '#94a3b8',
  },
};

export default function AuthPage({ onLogin, onRegister }) {
  const [tab, setTab] = useState('login');
  const [showPwd, setShowPwd] = useState(false);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  const [loginForm, setLoginForm] = useState({ username: '', password: '' });
  const [regForm, setRegForm] = useState({ username: '', email: '', password: '', confirm: '' });

  const handleLogin = async (e) => {
    e.preventDefault();
    setError('');
    setLoading(true);
    try {
      await onLogin({ username: loginForm.username, password: loginForm.password });
    } catch (err) {
      setError(err.response?.data?.detail || 'Invalid credentials');
    } finally {
      setLoading(false);
    }
  };

  const handleRegister = async (e) => {
    e.preventDefault();
    setError('');
    if (regForm.password !== regForm.confirm) {
      setError('Passwords do not match');
      return;
    }
    setLoading(true);
    try {
      await onRegister({ username: regForm.username, email: regForm.email, password: regForm.password });
    } catch (err) {
      setError(err.response?.data?.detail || 'Registration failed');
    } finally {
      setLoading(false);
    }
  };

  const focusStyle = (e) => {
    e.target.style.borderColor = '#6366f1';
    e.target.style.boxShadow = '0 0 0 3px rgba(99,102,241,0.12)';
  };
  const blurStyle = (e) => {
    e.target.style.borderColor = '#e2e8f0';
    e.target.style.boxShadow = 'none';
  };

  return (
    <div style={styles.page}>
      <div style={styles.container}>
        <div style={styles.brand}>
          <div style={styles.brandIcon}>
            <FileText size={26} color="#ffffff" />
          </div>
          <div style={styles.brandTitle}>Velocis Document Analyzer</div>
          <div style={styles.brandSub}>Secure Document Intelligence</div>
        </div>

        <div style={styles.card}>
          <div style={styles.tabs}>
            <button style={styles.tab(tab === 'login')} onClick={() => { setTab('login'); setError(''); }}>
              Sign In
            </button>
            <button style={styles.tab(tab === 'register')} onClick={() => { setTab('register'); setError(''); }}>
              Create Account
            </button>
          </div>

          {tab === 'login' ? (
            <form style={styles.form} onSubmit={handleLogin}>
              {error && <div style={styles.error}><AlertCircle size={14} />{error}</div>}
              <div style={styles.fieldGroup}>
                <label style={styles.label}>Username</label>
                <div style={styles.inputWrap}>
                  <span style={styles.inputIcon}><User size={15} /></span>
                  <input
                    style={styles.input(false)}
                    placeholder="your_username"
                    value={loginForm.username}
                    onChange={(e) => setLoginForm({ ...loginForm, username: e.target.value })}
                    onFocus={focusStyle} onBlur={blurStyle}
                    required
                  />
                </div>
              </div>
              <div style={styles.fieldGroup}>
                <label style={styles.label}>Password</label>
                <div style={styles.inputWrap}>
                  <span style={styles.inputIcon}><Lock size={15} /></span>
                  <input
                    style={{ ...styles.input(false), paddingRight: '2.5rem' }}
                    type={showPwd ? 'text' : 'password'}
                    placeholder="••••••••"
                    value={loginForm.password}
                    onChange={(e) => setLoginForm({ ...loginForm, password: e.target.value })}
                    onFocus={focusStyle} onBlur={blurStyle}
                    required
                  />
                  <button type="button" style={styles.eyeBtn} onClick={() => setShowPwd(!showPwd)}>
                    {showPwd ? <EyeOff size={15} /> : <Eye size={15} />}
                  </button>
                </div>
              </div>
              <button type="submit" style={styles.submitBtn(loading)} disabled={loading}>
                {loading ? 'Signing in…' : 'Sign In'}
              </button>
            </form>
          ) : (
            <form style={styles.form} onSubmit={handleRegister}>
              {error && <div style={styles.error}><AlertCircle size={14} />{error}</div>}
              <div style={styles.fieldGroup}>
                <label style={styles.label}>Username</label>
                <div style={styles.inputWrap}>
                  <span style={styles.inputIcon}><User size={15} /></span>
                  <input style={styles.input(false)} placeholder="choose_username"
                    value={regForm.username} onChange={(e) => setRegForm({ ...regForm, username: e.target.value })}
                    onFocus={focusStyle} onBlur={blurStyle} required />
                </div>
              </div>
              <div style={styles.fieldGroup}>
                <label style={styles.label}>Email</label>
                <div style={styles.inputWrap}>
                  <span style={styles.inputIcon}><Mail size={15} /></span>
                  <input style={styles.input(false)} type="email" placeholder="you@company.com"
                    value={regForm.email} onChange={(e) => setRegForm({ ...regForm, email: e.target.value })}
                    onFocus={focusStyle} onBlur={blurStyle} required />
                </div>
              </div>
              <div style={styles.fieldGroup}>
                <label style={styles.label}>Password</label>
                <div style={styles.inputWrap}>
                  <span style={styles.inputIcon}><Lock size={15} /></span>
                  <input style={{ ...styles.input(false), paddingRight: '2.5rem' }}
                    type={showPwd ? 'text' : 'password'} placeholder="min. 8 characters"
                    value={regForm.password} onChange={(e) => setRegForm({ ...regForm, password: e.target.value })}
                    onFocus={focusStyle} onBlur={blurStyle} required />
                  <button type="button" style={styles.eyeBtn} onClick={() => setShowPwd(!showPwd)}>
                    {showPwd ? <EyeOff size={15} /> : <Eye size={15} />}
                  </button>
                </div>
              </div>
              <div style={styles.fieldGroup}>
                <label style={styles.label}>Confirm Password</label>
                <div style={styles.inputWrap}>
                  <span style={styles.inputIcon}><Lock size={15} /></span>
                  <input style={styles.input(regForm.confirm && regForm.confirm !== regForm.password)}
                    type="password" placeholder="••••••••"
                    value={regForm.confirm} onChange={(e) => setRegForm({ ...regForm, confirm: e.target.value })}
                    onFocus={focusStyle} onBlur={blurStyle} required />
                </div>
              </div>
              <button type="submit" style={styles.submitBtn(loading)} disabled={loading}>
                {loading ? 'Creating account…' : 'Create Account'}
              </button>
            </form>
          )}
        </div>
        <div style={styles.footer}>© 2026 Velocis Intelligence Unit</div>
      </div>
    </div>
  );
}
