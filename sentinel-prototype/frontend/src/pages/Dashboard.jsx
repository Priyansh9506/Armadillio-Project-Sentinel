import { useState, useEffect, useRef } from 'react';
import { useNavigate } from 'react-router-dom';
import TrustGauge from '../components/TrustGauge';
import MFAChallenge from '../components/MFAChallenge';
import telemetrySDK from '../sdk/telemetry';
import { authAPI, paymentsAPI } from '../api';



export default function Dashboard() {
  const navigate = useNavigate();
  const [user, setUser] = useState(null);
  const [trustScore, setTrustScore] = useState(100);
  const [subScores, setSubScores] = useState({});
  const [decision, setDecision] = useState('ALLOW');
  const [mfaMethod, setMfaMethod] = useState(null);
  const [showMFA, setShowMFA] = useState(false);
  const [transactions, setTransactions] = useState([]);
  const [activeModal, setActiveModal] = useState(null); // 'transfer' | 'upi' | 'bills' | 'setpin' | 'changepin' | null
  const [transferAmount, setTransferAmount] = useState('');
  const [transferAccount, setTransferAccount] = useState('');
  const [transferIfsc, setTransferIfsc] = useState('');
  const [transferNote, setTransferNote] = useState('');
  const [transferPin, setTransferPin] = useState('');
  const [transferStatus, setTransferStatus] = useState(null);
  const [transferError, setTransferError] = useState('');
  const [hasPIN, setHasPIN] = useState(false);
  // PIN change state
  const [oldPin, setOldPin] = useState('');
  const [newPin, setNewPin] = useState('');
  const [pinChangeStatus, setPinChangeStatus] = useState(null);
  const [pendingPinChange, setPendingPinChange] = useState(false);
  const [verifyPhone, setVerifyPhone] = useState('');
  
  // Password change state
  const [oldPassword, setOldPassword] = useState('');
  const [newPassword, setNewPassword] = useState('');
  const [pendingPasswordChange, setPendingPasswordChange] = useState(false);
  
  // Pending payment state for MFA
  const [pendingPayment, setPendingPayment] = useState(null);
  
  // Hackathon Demo Mode: Give presenter control over the auto-lock popup
  const [demoAutoLock, setDemoAutoLock] = useState(false);

  const showMFARef = useRef(false);
  const lastVerifiedRef = useRef(0);

  useEffect(() => {
    showMFARef.current = showMFA;
  }, [showMFA]);

  useEffect(() => {
    const userData = localStorage.getItem('sentinel_user');
    const sessionId = localStorage.getItem('sentinel_session');

    if (!userData || !sessionId) {
      navigate('/');
      return;
    }

    const parsedUser = JSON.parse(userData);
    setUser(parsedUser);
    if (parsedUser.has_pin !== undefined) setHasPIN(parsedUser.has_pin);

    // Fetch live user data (including balance and has_pin)
    authAPI.getMe().then(r => {
      setUser(r.data);
      if (r.data.has_pin !== undefined) setHasPIN(r.data.has_pin);
      localStorage.setItem('sentinel_user', JSON.stringify(r.data));
    }).catch(() => {});

    // Start the telemetry SDK
    telemetrySDK.start(sessionId, (data) => {
      // 60-second grace period after a successful MFA verification
      if (Date.now() - lastVerifiedRef.current < 60000) {
        setTrustScore(90);
        setDecision('ALLOW');
        // keep old subscores but force behavioral to look okay
        return;
      }

      setTrustScore(Math.round(data.trust_score));
      setDecision(data.decision);
      setSubScores({
        behavioral: Math.round(data.sub_scores.behavioral),
        device: Math.round(data.sub_scores.device),
        session: Math.round(data.sub_scores.session),
        graph: Math.round(data.sub_scores.graph),
      });
    });

    return () => telemetrySDK.stop();
  }, [navigate]);

  // Check if UPI PIN is set on load and fetch transactions
  useEffect(() => {
    const token = localStorage.getItem('sentinel_token');
    if (!token) return;
    
    paymentsAPI.getPinStatus()
      .then(r => setHasPIN(r.data.has_pin))
      .catch(() => {});
      
    paymentsAPI.getTransactions()
      .then(r => setTransactions(r.data.transactions || []))
      .catch(() => {});
  }, []);

  // Payments WebSocket for Real-Time Updates
  useEffect(() => {
    if (!user) return;

    let ws = new WebSocket(`ws://localhost:8000/api/payments/ws/${user.user_id}`);
    
    ws.onmessage = (event) => {
      try {
        const data = JSON.parse(event.data);
        if (data.type === 'BALANCE_UPDATE') {
          setUser(prev => {
            const updated = { ...prev, balance: data.balance };
            localStorage.setItem('sentinel_user', JSON.stringify(updated));
            return updated;
          });
        } else if (data.type === 'NEW_TRANSACTION') {
          setUser(prev => {
            const updated = { ...prev, balance: data.new_balance };
            localStorage.setItem('sentinel_user', JSON.stringify(updated));
            return updated;
          });
          setTransactions(prev => [data.transaction, ...prev].slice(0, 20));
        }
      } catch (err) {
        console.error("WS Parsing error:", err);
      }
    };

    return () => {
      ws.close();
    };
  }, [user?.user_id]);

  const handleLogout = async () => {
    telemetrySDK.stop();
    const sessionId = localStorage.getItem('sentinel_session');
    if (sessionId) {
      try {
        await authAPI.logout({ session_id: sessionId });
      } catch (err) {
        console.error('Logout error', err);
      }
    }
    localStorage.clear();
    navigate('/');
  };

  const handleMFAVerified = async (challengeId) => {
    setShowMFA(false);
    lastVerifiedRef.current = Date.now();
    setTrustScore(90);
    setDecision('ALLOW');
    setSubScores(prev => ({ ...prev, behavioral: 90 }));

    // If MFA was triggered specifically to change the PIN
    if (pendingPinChange) {
      setPendingPinChange(false);
      try {
        await paymentsAPI.changeUpiPin({ old_pin: oldPin, new_pin: newPin, mfa_token: challengeId });
        alert('✅ UPI PIN changed successfully!');
        setOldPin(''); 
        setNewPin('');
      } catch (err) { 
        alert('Failed to change PIN. Network error.'); 
      }
    }

    if (pendingPasswordChange) {
      setPendingPasswordChange(false);
      try {
        await authAPI.changePassword({ old_password: oldPassword, new_password: newPassword, mfa_token: challengeId });
        alert('✅ Password changed successfully!');
        setOldPassword(''); 
        setNewPassword('');
      } catch (err) { 
        alert('Failed to change password. Network error.'); 
      }
    }

    if (pendingPayment) {
      await executePayment();
    }
  };

  const executePayment = async () => {
    const session_id = localStorage.getItem('sentinel_session');
    
    // OPTIMISTIC UPDATE: Deduct balance instantly and show success
    const amountFloat = parseFloat(transferAmount);
    setUser(prev => {
      const updated = { ...prev, balance: prev.balance - amountFloat };
      localStorage.setItem('sentinel_user', JSON.stringify(updated));
      return updated;
    });
    
    // Add a fake transaction instantly
    const fakeTxn = {
      id: `UPI${Math.random().toString(36).substring(2, 10).toUpperCase()}`,
      amount: -amountFloat,
      merchant: transferAccount,
      category: activeModal === 'upi' ? 'UPI_PAYMENT' : 'TRANSFER',
      is_duress: false,
      timestamp: new Date().toISOString()
    };
    setTransactions(prev => [fakeTxn, ...prev].slice(0, 20));

    setTransferStatus({ success: true, message: `₹${amountFloat} sent successfully!`, transaction_id: fakeTxn.id });
    setPendingPayment(false);

    // FIRE AND FORGET THE ACTUAL API CALL IN BACKGROUND
    try {
      let req;
      if (activeModal === 'upi') {
        req = paymentsAPI.upiSend({ session_id, to_upi_id: transferAccount, amount: amountFloat, note: transferNote, upi_pin: transferPin });
      } else if (activeModal === 'transfer') {
        req = paymentsAPI.transferNeft({ session_id, to_account: transferAccount, ifsc_code: transferIfsc, amount: amountFloat, note: transferNote, txn_pin: transferPin });
      } else if (activeModal === 'bills') {
        req = paymentsAPI.billsPay({ session_id, biller_id: transferAccount, amount: amountFloat, txn_pin: transferPin });
      }
      
      req.then(() => {
        // Clear modal after 2 seconds ON SUCCESS
        setTimeout(() => {
          setActiveModal(null); setTransferStatus(null); setTransferError('');
          setTransferAmount(''); setTransferAccount(''); setTransferIfsc('');
          setTransferNote(''); setTransferPin('');
        }, 2000);
      }).catch(err => {
        // REVERT optimistic update on failure!
        setUser(prev => {
          const reverted = { ...prev, balance: prev.balance + amountFloat };
          localStorage.setItem('sentinel_user', JSON.stringify(reverted));
          return reverted;
        });
        setTransactions(prev => prev.filter(t => t.id !== fakeTxn.id));
        setTransferStatus(null);
        setTransferError(err.response?.data?.detail || 'Transaction Failed (Invalid PIN or Network Error)');
      });
    } catch (err) {
      // Ignore initial setup errors
    }
  };

  const handlePayment = async (e) => {
    if (e) e.preventDefault();
    setTransferError('');
    
    if (decision === 'STEP_UP' || decision === 'BLOCK' || demoAutoLock) {
      // Trigger MFA instead of processing immediately
      setPendingPayment(true);
      setMfaMethod('PUSH_AUTH');
      setShowMFA(true);
      return;
    }

    await executePayment();
  };

  const handleSetPin = async (e) => {
    e.preventDefault();
    setTransferError('');
    try {
      await paymentsAPI.setUpiPin({ new_pin: newPin, phone_no: verifyPhone });
      setHasPIN(true);
      setTransferStatus({ message: 'UPI PIN set successfully! You can now make payments.' });
      setNewPin('');
      setTimeout(() => { setActiveModal(null); setTransferStatus(null); }, 2000);
    } catch (err) { setTransferError('Failed to set PIN'); }
  };

  const triggerPinChangeMfa = (e) => {
    e.preventDefault();
    setTransferError('');
    if (oldPin === newPin) {
      setTransferError('New PIN must be different from current PIN');
      return;
    }
    
    // Hide modal, open MFA Push Auth challenge
    setActiveModal(null);
    setMfaMethod('PUSH_AUTH');
    setPendingPinChange(true);
    setShowMFA(true);
  };

  const triggerPasswordChangeMfa = (e) => {
    e.preventDefault();
    setTransferError('');
    if (oldPassword === newPassword) {
      setTransferError('New password must be different from current password');
      return;
    }
    
    setActiveModal(null);
    setMfaMethod('PUSH_AUTH');
    setPendingPasswordChange(true);
    setShowMFA(true);
  };

  // Lock the dashboard only if Demo Auto-Lock is enabled
  const isLocked = demoAutoLock && (decision === 'STEP_UP' || decision === 'BLOCK');

  return (
    <div className="page">
      {/* Header */}
      <header className="header">
        <div className="header-logo">
          <img src="/bob-logo.png" alt="Bank of Baroda" style={{ height: 28, marginRight: 8, objectFit: 'contain' }} />
          <div style={{ width: 1, height: 20, background: 'var(--border-subtle)', marginRight: 8 }} />
          <img src="/armadillo-logo.png" alt="Armadillo" style={{ height: 28, marginRight: 16, objectFit: 'contain' }} />
          <div style={{ display: 'flex', flexDirection: 'column', justifyContent: 'center' }}>
            <h1 style={{ fontSize: '1.1rem', fontWeight: 800, color: 'var(--brand-navy)', lineHeight: 1.2, margin: 0 }}>
              Bank of Baroda
            </h1>
            <span style={{ fontSize: '0.65rem', color: 'var(--text-secondary)', textTransform: 'uppercase', letterSpacing: '0.05em', fontWeight: 600 }}>
              Identity Trust by Armadillo
            </span>
          </div>
        </div>
        <div className="flex items-center gap-4">
          {user && (
            <span className="text-secondary" style={{ fontSize: '0.85rem' }}>
              Welcome, <strong className="text-orange">{user.username}</strong>
            </span>
          )}
          <button className="btn btn-ghost btn-sm" onClick={() => navigate('/soc')}>
            SOC Dashboard
          </button>
          <button className="btn btn-ghost btn-sm" onClick={handleLogout}>
            Logout
          </button>
        </div>
      </header>

      {/* Dashboard Grid */}
      <div className={`content-grid dashboard-grid ${isLocked ? 'dashboard-content locked' : 'dashboard-content'}`}>
        {/* Left Column — Trust Gauge */}
        <div>
          <TrustGauge score={trustScore} subScores={subScores} />

          {/* Decision Indicator */}
          <div className="glass-card p-4 mt-4 text-center">
            <div style={{
              fontSize: '0.7rem', textTransform: 'uppercase', letterSpacing: '0.1em',
              color: 'var(--text-muted)', marginBottom: 8,
            }}>
              Current Decision
            </div>
            <div style={{
              padding: '8px 16px',
              borderRadius: 'var(--radius-full)',
              fontSize: '0.85rem',
              fontWeight: 700,
              background: decision === 'ALLOW'
                ? 'rgba(0, 212, 170, 0.1)'
                : decision === 'STEP_UP'
                  ? 'rgba(255, 184, 0, 0.1)'
                  : 'rgba(255, 59, 92, 0.1)',
              color: decision === 'ALLOW'
                ? 'var(--trust-green)'
                : decision === 'STEP_UP'
                  ? 'var(--trust-yellow)'
                  : 'var(--trust-red)',
              border: `1px solid ${decision === 'ALLOW'
                ? 'rgba(0, 212, 170, 0.3)'
                : decision === 'STEP_UP'
                  ? 'rgba(255, 184, 0, 0.3)'
                  : 'rgba(255, 59, 92, 0.3)'}`,
            }}>
              {decision === 'ALLOW' ? 'TRUSTED' : decision === 'STEP_UP' ? 'STEP-UP MFA' : 'BLOCKED'}
            </div>
          </div>
        </div>

        {/* Right Column — Banking Content */}
        <div className="flex-col gap-4" style={{ display: 'flex' }}>
          {/* Balance Card */}
          <div className="glass-card p-6">
            <div className="flex justify-between items-center mb-4">
              <div>
                <p className="text-muted" style={{ fontSize: '0.75rem', textTransform: 'uppercase', letterSpacing: '0.1em' }}>
                  Savings Account
                </p>
                <h2 style={{ fontSize: '2rem', fontWeight: 800, marginTop: 4 }}>
                  <span className="text-muted" style={{ fontSize: '1.2rem' }}>&#x20b9;</span>
                  {user?.balance ? user.balance.toLocaleString('en-IN', { minimumFractionDigits: 2, maximumFractionDigits: 2 }).split('.')[0] : '0'}
                  <span className="text-muted" style={{ fontSize: '1rem' }}>.{user?.balance ? user.balance.toLocaleString('en-IN', { minimumFractionDigits: 2, maximumFractionDigits: 2 }).split('.')[1] : '00'}</span>
                </h2>
              </div>
              <div style={{
                padding: '8px 16px',
                background: 'rgba(0, 212, 170, 0.1)',
                borderRadius: 'var(--radius-full)',
                fontSize: '0.8rem',
                color: 'var(--trust-green)',
              }}>
                A/C: XXXX4521
              </div>
            </div>

            {/* Quick Actions */}
            <div className="flex gap-2 mt-4" style={{ flexWrap: 'wrap' }}>
              {!hasPIN && (
                <button className="btn btn-primary btn-sm" style={{ background: 'var(--trust-yellow)', color: '#000' }}
                  onClick={() => setActiveModal('setpin')}>
                  ⚠ Set UPI PIN
                </button>
              )}
              <button className="btn btn-primary btn-sm" onClick={() => hasPIN ? setActiveModal('upi') : setActiveModal('setpin')}>
                UPI Pay
              </button>
              <button className="btn btn-outline btn-sm" onClick={() => hasPIN ? setActiveModal('transfer') : setActiveModal('setpin')}>
                Transfer
              </button>
              <button className="btn btn-outline btn-sm" onClick={() => hasPIN ? setActiveModal('bills') : setActiveModal('setpin')}>
                Pay Bills
              </button>
              {hasPIN && (
                <button className="btn btn-outline btn-sm" onClick={() => setActiveModal('changepin')}>
                  Change PIN
                </button>
              )}
              <button className="btn btn-outline btn-sm" onClick={() => setActiveModal('changepassword')}>
                Change Password
              </button>
              {/* DEMO CONTROL BUTTON */}
              <button 
                className="btn btn-sm" 
                style={{ background: demoAutoLock ? 'var(--trust-green)' : 'var(--border-subtle)', color: demoAutoLock ? '#fff' : 'var(--text-secondary)' }}
                onClick={() => setDemoAutoLock(!demoAutoLock)}
              >
                {demoAutoLock ? 'Demo: Auto-Lock ON' : 'Demo: Auto-Lock OFF'}
              </button>
            </div>
          </div>

          {/* Transactions */}
          <div className="glass-card p-6">
            <h3 style={{ fontSize: '0.9rem', fontWeight: 600, marginBottom: 16, color: 'var(--text-secondary)' }}>
              Recent Transactions
            </h3>
            {transactions.length === 0 ? (
              <p className="text-muted" style={{ fontSize: '0.85rem' }}>No recent transactions.</p>
            ) : (
              transactions.map(txn => (
                <div className="txn-row" key={txn.id}>
                  <div>
                    <p style={{ fontWeight: 500, fontSize: '0.9rem' }}>{txn.merchant}</p>
                    <p className="text-muted" style={{ fontSize: '0.75rem' }}>{new Date(txn.timestamp).toLocaleString()} &bull; {txn.category}</p>
                  </div>
                  <div className={`txn-amount ${txn.amount < 0 ? 'negative' : 'positive'}`}
                    style={{ fontWeight: 600, fontSize: '0.95rem', fontFamily: "'JetBrains Mono', monospace" }}>
                    {txn.amount < 0 ? '-' : '+'}&#x20b9;{Math.abs(txn.amount).toLocaleString('en-IN')}
                  </div>
                </div>
              ))
            )}
          </div>

          {/* Telemetry Status */}
          <div className="glass-card p-4">
            <div className="flex items-center gap-3">
              <div style={{ width: 10, height: 10, borderRadius: '50%', background: isLocked ? 'var(--trust-red)' : 'var(--trust-green)', boxShadow: isLocked ? '0 0 8px var(--trust-red)' : '0 0 8px var(--trust-green)' }}></div>
              <span className="text-secondary" style={{ fontSize: '0.8rem', fontWeight: 600, textTransform: 'uppercase', letterSpacing: '0.05em' }}>
                {isLocked ? 'Telemetry Suspended' : 'Telemetry Active'}
              </span>
            </div>
            <p className="text-muted mt-2" style={{ fontSize: '0.75rem', lineHeight: 1.4 }}>
              Background behavioral analysis running at 3s intervals.
            </p>
          </div>
        </div>
      </div>

      {/* ─── SET UPI PIN Modal ─── */}
      {activeModal === 'setpin' && (
        <div className="mfa-overlay" onClick={() => setActiveModal(null)}>
          <div className="mfa-modal" onClick={e => e.stopPropagation()}>
            <h2 style={{ fontSize: '1.2rem', fontWeight: 700, marginBottom: 20 }}>🔐 Set Your UPI PIN</h2>
            {transferStatus ? (
              <div className="text-center">
                <div style={{ fontSize: '3rem', marginBottom: 12 }}>✅</div>
                <p style={{ fontWeight: 600, color: 'var(--trust-green)' }}>{transferStatus.message}</p>
              </div>
            ) : (
              <form onSubmit={handleSetPin}>
                <p className="text-muted mb-4" style={{ fontSize: '0.85rem' }}>
                  Set a 4 or 6 digit UPI PIN to authorize payments.
                </p>
                <div className="input-group mb-4">
                  <label>Verify Registered Mobile Number</label>
                  <input className="input-field" type="text" placeholder="Enter mobile number"
                    maxLength={15} value={verifyPhone || ''} onChange={e => setVerifyPhone(e.target.value)} required />
                </div>
                <div className="input-group mb-4">
                  <label>New UPI PIN</label>
                  <input className="input-field" type="password" placeholder="4 or 6 digits"
                    maxLength={6} value={newPin} onChange={e => setNewPin(e.target.value)} required />
                </div>
                {transferError && <p style={{ color: 'var(--trust-red)', fontSize: '0.85rem', marginBottom: 12 }}>{transferError}</p>}
                <div style={{ display: 'flex', gap: '10px' }}>
                  <button className="btn btn-outline btn-full" type="button" onClick={() => setActiveModal(null)}>Cancel</button>
                  <button className="btn btn-primary btn-full" type="submit">Set PIN</button>
                </div>
              </form>
            )}
          </div>
        </div>
      )}

      {/* ─── CHANGE UPI PIN Modal ─── */}
      {activeModal === 'changepin' && (
        <div className="mfa-overlay" onClick={() => setActiveModal(null)}>
          <div className="mfa-modal" onClick={e => e.stopPropagation()}>
            <h2 style={{ fontSize: '1.2rem', fontWeight: 700, marginBottom: 6 }}>🔄 Change UPI PIN</h2>
            <p className="text-muted mb-4" style={{ fontSize: '0.8rem' }}>Requires old PIN + MFA verification</p>
            {pinChangeStatus ? (
              <div className="text-center">
                <div style={{ fontSize: '3rem', marginBottom: 12 }}>✅</div>
                <p style={{ fontWeight: 600, color: 'var(--trust-green)' }}>{pinChangeStatus.message}</p>
              </div>
            ) : (
              <form onSubmit={triggerPinChangeMfa}>
                <div className="input-group mb-4">
                  <label>Current PIN</label>
                  <input className="input-field" type="password" placeholder="Enter current PIN"
                    maxLength={6} value={oldPin} onChange={e => setOldPin(e.target.value)} required />
                </div>
                <div className="input-group mb-4">
                  <label>New PIN</label>
                  <input className="input-field" type="password" placeholder="4 or 6 digits"
                    maxLength={6} value={newPin} onChange={e => setNewPin(e.target.value)} required />
                </div>
                {transferError && <p style={{ color: 'var(--trust-red)', fontSize: '0.85rem', marginBottom: 12 }}>{transferError}</p>}
                <div style={{ display: 'flex', gap: '10px' }}>
                  <button className="btn btn-outline btn-full" type="button" onClick={() => setActiveModal(null)}>Cancel</button>
                  <button className="btn btn-primary btn-full" type="submit">Verify</button>
                </div>
              </form>
            )}
          </div>
        </div>
      )}
      {/* ─── CHANGE PASSWORD Modal ─── */}
      {activeModal === 'changepassword' && (
        <div className="mfa-overlay" onClick={() => setActiveModal(null)}>
          <div className="mfa-modal" onClick={e => e.stopPropagation()}>
            <h2 style={{ fontSize: '1.2rem', fontWeight: 700, marginBottom: 6 }}>🔑 Change Password</h2>
            <p className="text-muted mb-4" style={{ fontSize: '0.8rem' }}>Requires old password + MFA verification</p>
            <form onSubmit={triggerPasswordChangeMfa}>
              <div className="input-group mb-4">
                <label>Current Password</label>
                <input className="input-field" type="password" placeholder="Enter current password"
                  value={oldPassword} onChange={e => setOldPassword(e.target.value)} required />
              </div>
              <div className="input-group mb-4">
                <label>New Password</label>
                <input className="input-field" type="password" placeholder="Enter new password"
                  value={newPassword} onChange={e => setNewPassword(e.target.value)} required />
              </div>
              {transferError && <p style={{ color: 'var(--trust-red)', fontSize: '0.85rem', marginBottom: 12 }}>{transferError}</p>}
              <div style={{ display: 'flex', gap: '10px' }}>
                <button className="btn btn-outline btn-full" type="button" onClick={() => setActiveModal(null)}>Cancel</button>
                <button className="btn btn-primary btn-full" type="submit">Verify</button>
              </div>
            </form>
          </div>
        </div>
      )}

      {/* ─── Payment Modals (UPI / NEFT / Bills) ─── */}
      {(activeModal === 'upi' || activeModal === 'transfer' || activeModal === 'bills') && (
        <div className="mfa-overlay" onClick={() => setActiveModal(null)}>
          <div className="mfa-modal" onClick={e => e.stopPropagation()}>
            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: 20 }}>
              <h2 style={{ fontSize: '1.2rem', fontWeight: 700 }}>
                {activeModal === 'transfer' && '🏦 NEFT / IMPS Transfer'}
                {activeModal === 'upi' && '📱 Send via UPI'}
                {activeModal === 'bills' && '📄 Pay Utility Bill'}
              </h2>
              <div style={{ 
                fontSize: '0.7rem', padding: '4px 8px', borderRadius: '4px',
                background: decision === 'ALLOW' ? 'rgba(0, 212, 170, 0.1)' : 'rgba(255, 184, 0, 0.1)',
                color: decision === 'ALLOW' ? 'var(--trust-green)' : 'var(--trust-yellow)',
                border: `1px solid ${decision === 'ALLOW' ? 'var(--trust-green)' : 'var(--trust-yellow)'}`
              }}>
                {decision === 'ALLOW' ? '✓ Sentinel Verified' : '⚠ High Risk'}
              </div>
            </div>

            {decision === 'BLOCK' ? (
              <div className="text-center" style={{ padding: '20px 0' }}>
                <div style={{ fontSize: '3rem', marginBottom: 12 }}>🚫</div>
                <p style={{ fontWeight: 600, color: 'var(--trust-red)' }}>Transaction Blocked</p>
                <p className="text-muted" style={{ fontSize: '0.85rem', marginTop: 8 }}>
                  Sentinel AI detected unauthorized access. Your account is temporarily locked.
                </p>
              </div>
            ) : transferStatus ? (
              <div className="text-center">
                <div style={{ fontSize: '3rem', marginBottom: 12 }}>✅</div>
                <p style={{ fontWeight: 600, color: 'var(--trust-green)' }}>{transferStatus.message}</p>
                {transferStatus.transaction_id && (
                  <p className="text-muted" style={{ fontSize: '0.8rem', marginTop: 8, fontFamily: "'JetBrains Mono', monospace" }}>
                    Txn ID: {transferStatus.transaction_id}
                  </p>
                )}
              </div>
            ) : (
              <form onSubmit={handlePayment}>
                
                {/* Dynamic Fields */}
                {activeModal === 'upi' ? (
                  <div className="input-group mb-4">
                    <label>Receiver UPI ID</label>
                    <input className="input-field" placeholder="e.g. merchant@ybl"
                      value={transferAccount} onChange={e => setTransferAccount(e.target.value)} required />
                  </div>
                ) : activeModal === 'bills' ? (
                  <div className="input-group mb-4">
                    <label>Biller ID / Consumer No.</label>
                    <input className="input-field" placeholder="e.g. 1000987654"
                      value={transferAccount} onChange={e => setTransferAccount(e.target.value)} required />
                  </div>
                ) : (
                  <>
                    <div className="input-group mb-4">
                      <label>Receiver Account Number</label>
                      <input className="input-field" placeholder="e.g. 1122334455"
                        value={transferAccount} onChange={e => setTransferAccount(e.target.value)} required />
                    </div>
                    <div className="input-group mb-4">
                      <label>IFSC Code</label>
                      <input className="input-field" placeholder="BARB0XXXXXX"
                        value={transferIfsc} onChange={e => setTransferIfsc(e.target.value)} required />
                    </div>
                  </>
                )}

                <div className="input-group mb-4">
                  <label>Amount (₹)</label>
                  <input className="input-field" type="number" placeholder="Enter amount"
                    value={transferAmount} onChange={e => setTransferAmount(e.target.value)} required />
                </div>

                {activeModal !== 'bills' && (
                  <div className="input-group mb-4">
                    <label>Add a Note (optional)</label>
                    <input className="input-field" placeholder="e.g. Dinner split, Rent"
                      value={transferNote} onChange={e => setTransferNote(e.target.value)} />
                  </div>
                )}

                <div className="input-group mb-4">
                  <label>{activeModal === 'upi' ? 'UPI PIN' : 'Transaction PIN'}</label>
                  <input className="input-field" type="password" placeholder="Enter PIN" maxLength={10}
                    value={transferPin} onChange={e => setTransferPin(e.target.value)} required />
                </div>

                {transferError && <p style={{ color: 'var(--trust-red)', fontSize: '0.85rem', marginBottom: 12 }}>{transferError}</p>}

                <p className="text-muted mb-4" style={{ fontSize: '0.7rem' }}>
                  🛡️ Under duress? Append 9999 to your PIN — the transaction will appear successful but funds will be held securely.
                </p>
                <div style={{ display: 'flex', gap: '10px' }}>
                  <button className="btn btn-outline btn-full" type="button" onClick={() => setActiveModal(null)}>Cancel</button>
                  <button className="btn btn-primary btn-full" type="submit">
                    {activeModal === 'bills' ? 'Pay Bill' : activeModal === 'upi' ? 'Send via UPI' : 'Confirm Transfer'}
                  </button>
                </div>
              </form>
            )}
          </div>
        </div>
      )}

      {/* ─── Fully Functional Auto-MFA Lock Overlay ─── */}
      {isLocked && !showMFA && (
        <div className="mfa-overlay">
          <div className="mfa-modal text-center">
            <div style={{ fontSize: '3.5rem', marginBottom: 16 }}>🔒</div>
            <h2 style={{ fontSize: '1.4rem', fontWeight: 800, marginBottom: 8, color: 'var(--trust-red)' }}>
              Security Lock Activated
            </h2>
            <p className="text-muted mb-6" style={{ fontSize: '0.9rem', lineHeight: 1.5 }}>
              Sentinel AI detected behavioral patterns that deviate from your baseline. To protect your account, please verify your identity to continue.
            </p>
            <button className="btn btn-primary btn-full mb-3" onClick={() => setShowMFA(true)}>
              Verify via Push Auth
            </button>
            <button className="btn btn-outline btn-full" onClick={handleLogout}>
              Secure Logout
            </button>
          </div>
        </div>
      )}

      {/* MFA Challenge Overlay */}
      {showMFA && (
        <MFAChallenge
          method={mfaMethod || 'PUSH_AUTH'}
          trustScore={trustScore}
          onVerified={handleMFAVerified}
          onCancel={handleLogout}
        />
      )}
    </div>
  );
}
