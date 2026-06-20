import { useState } from 'react';
import { mfaAPI } from '../api';

/**
 * MFA Challenge Modal — Adaptive challenges based on WHY trust dropped.
 * Supports: Voice Liveness, Push Auth Number Matching.
 */
export default function MFAChallenge({ method = 'PUSH_AUTH', trustScore, onVerified, onCancel }) {
  const [step, setStep] = useState('initial'); // initial | listening | verifying | success | failed
  const [phrase, setPhrase] = useState('');
  const [pushNumber, setPushNumber] = useState(null);
  const [challengeId, setChallengeId] = useState(null);

  // ── Voice Liveness ─────────────────────────────────────────
  const startVoiceLiveness = async () => {
    try {
      const res = await mfaAPI.getVoicePhrase();
      setPhrase(res.data.phrase);
      setStep('listening');

      // Start speech recognition
      const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
      if (!SpeechRecognition) {
        // Fallback: manual entry
        setStep('manual_voice');
        return;
      }

      const recognition = new SpeechRecognition();
      recognition.lang = 'en-US';
      recognition.interimResults = false;

      recognition.onresult = async (event) => {
        const transcript = event.results[0][0].transcript;
        setStep('verifying');

        const verifyRes = await mfaAPI.verifyVoice({
          session_id: localStorage.getItem('sentinel_session'),
          transcript,
        });

        if (verifyRes.data.verified) {
          setStep('success');
          setTimeout(() => onVerified(), 1500);
        } else {
          setStep('failed');
        }
      };

      recognition.onerror = () => setStep('manual_voice');
      recognition.start();
    } catch (err) {
      console.error('Voice liveness error:', err);
      setStep('manual_voice');
    }
  };

  // ── Push Auth ──────────────────────────────────────────────
  const startPushAuth = async () => {
    try {
      // 100% FRONTEND FAKE FOR HACKATHON DEMO (No backend API dependency)
      const fakeNumber = Math.floor(Math.random() * 90 + 10);
      setPushNumber(fakeNumber);
      setChallengeId(`FAKE_CHALLENGE_${Date.now()}`);
      setStep('push_waiting');
    } catch (err) {
      console.error('Push auth error:', err);
      setStep('failed');
    }
  };

  const getReason = () => {
    if (method === 'VOICE_LIVENESS') return 'Unusual typing pattern detected. Your behavioral signature does not match.';
    if (method === 'PUSH_AUTH') return 'New device or unusual location detected. Verify on your trusted device.';
    return 'Additional verification required.';
  };

  return (
    <div className="mfa-overlay">
      <div className="mfa-modal">
        {/* Header */}
        <div className="text-center mb-4">
          <div style={{
            width: 56, height: 56, margin: '0 auto 12px',
            background: 'rgba(255, 59, 92, 0.1)',
            border: '2px solid var(--trust-red)',
            borderRadius: '50%',
            display: 'flex', alignItems: 'center', justifyContent: 'center',
            fontSize: '1.5rem',
          }}>
            &#x1f512;
          </div>
          <h2 style={{ fontSize: '1.3rem', fontWeight: 700 }}>Identity Verification Required</h2>
          <p className="text-secondary" style={{ fontSize: '0.85rem', marginTop: 8 }}>
            {getReason()}
          </p>
          <div style={{
            display: 'inline-block', marginTop: 12,
            padding: '4px 12px', borderRadius: 'var(--radius-full)',
            background: 'rgba(255, 59, 92, 0.1)',
            border: '1px solid rgba(255, 59, 92, 0.3)',
            fontSize: '0.8rem', color: 'var(--trust-red)',
          }}>
            Trust Score: {Math.round(trustScore)}
          </div>
        </div>

        {/* Challenge Content */}
        <div style={{ marginTop: 24 }}>
          {step === 'initial' && method === 'VOICE_LIVENESS' && (
            <div className="text-center">
              <p className="text-secondary mb-4" style={{ fontSize: '0.9rem' }}>
                Read a phrase aloud to verify your identity
              </p>
              <button className="btn btn-primary btn-lg btn-full" onClick={startVoiceLiveness}>
                &#x1f3a4; Start Voice Verification
              </button>
            </div>
          )}

          {step === 'initial' && method === 'PUSH_AUTH' && (
            <div className="text-center">
              <p className="text-secondary mb-4" style={{ fontSize: '0.9rem' }}>
                A verification will be sent to your trusted device
              </p>
              <button className="btn btn-primary btn-lg btn-full" onClick={startPushAuth}>
                Send Push Notification
              </button>
            </div>
          )}

          {step === 'listening' && (
            <div className="text-center">
              <div style={{
                padding: '20px 24px', marginBottom: 16,
                background: 'rgba(255, 107, 53, 0.08)',
                border: '1px solid var(--border-orange)',
                borderRadius: 'var(--radius-md)',
              }}>
                <p className="text-muted" style={{ fontSize: '0.75rem', marginBottom: 8, textTransform: 'uppercase' }}>
                  Read this phrase aloud
                </p>
                <p style={{ fontSize: '1.3rem', fontWeight: 700, color: 'var(--primary)', letterSpacing: '0.02em' }}>
                  "{phrase}"
                </p>
              </div>
              <div className="flex items-center justify-center gap-2">
                <div className="spinner" />
                <span className="text-secondary" style={{ fontSize: '0.85rem' }}>Listening...</span>
              </div>
            </div>
          )}

          {step === 'manual_voice' && (
            <div className="text-center">
              <p className="text-secondary mb-4" style={{ fontSize: '0.85rem' }}>
                Microphone not available or blocked. Type the phrase manually below to bypass:
              </p>
              <div style={{
                padding: '16px', marginBottom: 16,
                background: 'rgba(255, 107, 53, 0.08)',
                border: '1px solid var(--border-orange)',
                borderRadius: 'var(--radius-md)',
              }}>
                <p style={{ fontSize: '1.2rem', fontWeight: 700, color: 'var(--primary)' }}>
                  "{phrase}"
                </p>
              </div>
              <input
                type="text"
                className="input-field mb-4"
                placeholder="Type the exact phrase..."
                autoFocus
                onKeyDown={async (e) => {
                  if (e.key === 'Enter') {
                    setStep('verifying');
                    try {
                      const res = await mfaAPI.verifyVoice({
                        session_id: localStorage.getItem('sentinel_session'),
                        transcript: e.target.value,
                      });
                      if (res.data.verified) {
                        setStep('success');
                        setTimeout(() => onVerified(), 1500);
                      } else {
                        setStep('failed');
                      }
                    } catch (err) {
                      setStep('failed');
                    }
                  }
                }}
              />
              <p className="text-muted" style={{ fontSize: '0.7rem' }}>Press Enter to verify.</p>
            </div>
          )}

          {step === 'push_waiting' && (
            <div className="text-center">
              <div className="spinner" style={{ margin: '0 auto 12px', width: 40, height: 40 }} />
              <p className="text-secondary mb-4">
                Waiting for you to approve the request on your trusted device...
              </p>
              
              {/* FAKE MOBILE NOTIFICATION TOAST (FOR HACKATHON DEMO) */}
              <div style={{
                position: 'fixed',
                top: '20px',
                right: '20px',
                width: '320px',
                background: '#ffffff',
                boxShadow: '0 10px 30px rgba(0,0,0,0.15)',
                borderRadius: '16px',
                padding: '16px',
                zIndex: 9999,
                animation: 'slideInRight 0.5s cubic-bezier(0.16, 1, 0.3, 1)',
                border: '1px solid #e2e8f0',
                textAlign: 'left'
              }}>
                <div style={{ display: 'flex', alignItems: 'center', marginBottom: '8px' }}>
                  <div style={{ width: '20px', height: '20px', background: '#4285F4', borderRadius: '4px', display: 'flex', alignItems: 'center', justifyContent: 'center', color: '#fff', fontSize: '12px', fontWeight: 'bold', marginRight: '8px' }}>G</div>
                  <span style={{ fontSize: '0.8rem', fontWeight: 600, color: '#64748b' }}>Google Prompt</span>
                  <span style={{ fontSize: '0.75rem', color: '#94a3b8', marginLeft: 'auto' }}>now</span>
                </div>
                <p style={{ fontSize: '0.95rem', fontWeight: 700, color: '#1e293b', marginBottom: '4px' }}>
                  Are you trying to sign in?
                </p>
                <p style={{ fontSize: '0.85rem', color: '#475569', marginBottom: '16px' }}>
                  Project Sentinel is trying to verify your identity. Tap the matching number:
                </p>
                
                <div style={{ display: 'flex', justifyContent: 'space-between', gap: '8px' }}>
                  {/* Generate 3 options, one being the correct one */}
                  {[pushNumber - 13, pushNumber, pushNumber + 7].sort().map((num, i) => (
                    <button 
                      key={i}
                      onClick={async () => {
                        if (num === pushNumber) {
                          // 100% FRONTEND FAKE: Instant success without API call!
                          setStep('success');
                          setTimeout(() => onVerified(challengeId), 1500);
                        } else {
                          setStep('failed');
                        }
                      }}
                      style={{
                        flex: 1, padding: '12px 0', fontSize: '1.2rem', fontWeight: 700,
                        color: '#1e293b', background: '#f1f5f9', border: 'none',
                        borderRadius: '8px', cursor: 'pointer', transition: 'background 0.2s'
                      }}
                      onMouseOver={(e) => e.currentTarget.style.background = '#e2e8f0'}
                      onMouseOut={(e) => e.currentTarget.style.background = '#f1f5f9'}
                    >
                      {num}
                    </button>
                  ))}
                </div>
              </div>
            </div>
          )}

          {step === 'verifying' && (
            <div className="text-center">
              <div className="spinner" style={{ margin: '0 auto 12px', width: 40, height: 40 }} />
              <p className="text-secondary">Verifying identity...</p>
            </div>
          )}

          {step === 'success' && (
            <div className="text-center">
              <div style={{ fontSize: '3rem', marginBottom: 12 }}>&#x2705;</div>
              <p style={{ fontSize: '1.1rem', fontWeight: 600, color: 'var(--trust-green)' }}>
                Identity Verified
              </p>
              <p className="text-secondary mt-2" style={{ fontSize: '0.85rem' }}>
                Trust score recovered. Unlocking session...
              </p>
            </div>
          )}

          {step === 'failed' && (
            <div className="text-center">
              <div style={{ fontSize: '3rem', marginBottom: 12 }}>&#x274c;</div>
              <p style={{ fontSize: '1.1rem', fontWeight: 600, color: 'var(--trust-red)' }}>
                Verification Failed
              </p>
              <p className="text-secondary mt-2 mb-4" style={{ fontSize: '0.85rem' }}>
                Please try again or contact support.
              </p>
              <button className="btn btn-outline" onClick={() => setStep('initial')}>
                Try Again
              </button>
            </div>
          )}
        </div>

        {/* Cancel */}
        {step !== 'success' && (
          <button
            className="btn btn-ghost btn-full mt-4"
            onClick={onCancel}
            style={{ fontSize: '0.8rem' }}
          >
            Cancel &amp; Logout
          </button>
        )}
      </div>
    </div>
  );
}
