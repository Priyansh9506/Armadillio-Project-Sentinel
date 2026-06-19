import { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { authAPI } from '../api';

export default function Login() {
  const [username, setUsername] = useState('');
  const [credential, setCredential] = useState('');
  const [loginType, setLoginType] = useState('password'); // 'password', 'pin', 'otp'
  const [error, setError] = useState('');
  const [loading, setLoading] = useState(false);
  const navigate = useNavigate();

  const handleLogin = async (e) => {
    e.preventDefault();
    setError('');
    setLoading(true);

    try {
      const res = await authAPI.login({ username, credential, login_type: loginType });
      const { token, refresh_token, session_id, user } = res.data;

      localStorage.setItem('sentinel_token', token);
      if (refresh_token) {
        localStorage.setItem('sentinel_refresh_token', refresh_token);
      }
      localStorage.setItem('sentinel_session', session_id);
      localStorage.setItem('sentinel_user', JSON.stringify(user));

      navigate('/dashboard');
    } catch (err) {
      setError(err.response?.data?.detail || 'Login failed. Check credentials.');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="page" style={{ display: 'flex', alignItems: 'center', justifyContent: 'center', minHeight: '100vh' }}>
      <div className="glass-card" style={{ padding: '48px 40px', maxWidth: '420px', width: '90%', animation: 'slideUp 0.6s ease-out' }}>
        {/* Logo & Title */}
        <div className="text-center mb-4">
          <div style={{ display: 'flex', justifyContent: 'center', gap: 16, marginBottom: 16, alignItems: 'center' }}>
            <img src="/bob-logo.png" alt="Bank of Baroda" style={{ height: 48, objectFit: 'contain' }} />
            <div style={{ width: 1, height: 32, background: 'var(--border-subtle)' }} />
            <img src="/armadillo-logo.png" alt="Armadillo" style={{ height: 48, objectFit: 'contain' }} />
          </div>
          <h1 style={{
            fontSize: '1.4rem', fontWeight: 800,
            color: 'var(--brand-navy)'
          }}>
            Bank of Baroda
          </h1>
          <p className="text-secondary" style={{ fontSize: '0.9rem', marginTop: 6, fontWeight: 500 }}>
            Continuous Identity Trust System
          </p>
          <p className="text-muted" style={{ fontSize: '0.7rem', marginTop: 4, letterSpacing: '0.05em', textTransform: 'uppercase' }}>
            Secured by Team Armadillo
          </p>
        </div>

        {/* Login Type Tabs */}
        <div style={{ display: 'flex', gap: 10, marginBottom: 24 }}>
          <button type="button" className={`btn ${loginType === 'password' ? 'btn-primary' : 'btn-outline'}`} style={{ flex: 1, padding: '8px' }} onClick={() => { setLoginType('password'); setCredential(''); }}>Password</button>
          <button type="button" className={`btn ${loginType === 'pin' ? 'btn-primary' : 'btn-outline'}`} style={{ flex: 1, padding: '8px' }} onClick={() => { setLoginType('pin'); setCredential(''); }}>PIN</button>
          <button type="button" className={`btn ${loginType === 'otp' ? 'btn-primary' : 'btn-outline'}`} style={{ flex: 1, padding: '8px' }} onClick={() => { setLoginType('otp'); setCredential(''); }}>OTP</button>
        </div>

        {/* Login Form */}
        <form onSubmit={handleLogin}>
          <div className="input-group mb-4">
            <label>Mobile Number / Customer ID</label>
            <input
              id="login-username"
              type="text"
              className="input-field"
              placeholder="Enter Mobile No. or Customer ID"
              value={username}
              onChange={(e) => setUsername(e.target.value)}
              autoComplete="username"
              required
            />
          </div>

          <div className="input-group mb-4">
            <label>{loginType === 'password' ? 'Password' : loginType === 'pin' ? 'Login PIN' : 'Enter OTP'}</label>
            <input
              id="login-credential"
              type={loginType === 'password' || loginType === 'pin' ? 'password' : 'text'}
              className="input-field"
              placeholder={loginType === 'password' ? 'Enter your password' : loginType === 'pin' ? 'Enter 6-digit PIN' : 'Enter 6-digit OTP'}
              value={credential}
              onChange={(e) => setCredential(e.target.value)}
              autoComplete={loginType === 'password' ? 'current-password' : 'off'}
              required
            />
          </div>

          {error && (
            <div style={{
              padding: '10px 14px',
              background: 'rgba(255, 59, 92, 0.1)',
              border: '1px solid rgba(255, 59, 92, 0.3)',
              borderRadius: 'var(--radius-sm)',
              color: 'var(--trust-red)',
              fontSize: '0.85rem',
              marginBottom: 16,
            }}>
              {error}
            </div>
          )}

          <button
            id="login-submit"
            type="submit"
            className="btn btn-primary btn-full btn-lg"
            disabled={loading}
            style={{ marginTop: 8 }}
          >
            {loading ? <span className="spinner" /> : 'Sign In Securely'}
          </button>
        </form>

        {/* Footer */}
        <div className="text-center" style={{ marginTop: 32 }}>
          <p className="text-muted" style={{ fontSize: '0.7rem' }}>
            Behavioral biometrics start capturing after login.
          </p>
          <p className="text-muted" style={{ fontSize: '0.65rem', marginTop: 4 }}>
            Powered by Continuous Identity Trust &amp; Adaptive MFA
          </p>
        </div>
      </div>
    </div>
  );
}
