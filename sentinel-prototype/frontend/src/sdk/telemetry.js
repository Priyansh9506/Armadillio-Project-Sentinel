/**
 * Project Sentinel — Keystroke & Mouse Telemetry SDK
 * Captures behavioral biometrics silently and sends to backend.
 */

class TelemetrySDK {
  constructor() {
    this.keystrokes = [];
    this.mousePositions = [];
    this.lastKeyUp = null;
    this.lastMousePos = null;
    this.intervalId = null;
    this.sessionId = null;
    this.onTrustUpdate = null; // callback
  }

  start(sessionId, onTrustUpdate) {
    this.sessionId = sessionId;
    this.onTrustUpdate = onTrustUpdate;

    // Keystroke listeners
    document.addEventListener('keydown', this._onKeyDown);
    document.addEventListener('keyup', this._onKeyUp);

    // Mouse listener
    document.addEventListener('mousemove', this._onMouseMove);

    // Send telemetry every 3 seconds
    this.intervalId = setInterval(() => this._sendTelemetry(), 3000);

    console.log('[Sentinel SDK] Telemetry started for session:', sessionId);
  }

  stop() {
    document.removeEventListener('keydown', this._onKeyDown);
    document.removeEventListener('keyup', this._onKeyUp);
    document.removeEventListener('mousemove', this._onMouseMove);
    if (this.intervalId) clearInterval(this.intervalId);
    this.keystrokes = [];
    this.mousePositions = [];
    console.log('[Sentinel SDK] Telemetry stopped');
  }

  // ── Keystroke Capture ──────────────────────────────────────
  _onKeyDown = (e) => {
    const now = performance.now();
    const existing = this.keystrokes.find(k => k.key === e.key && !k.keyUp);
    if (!existing) {
      this.keystrokes.push({
        key: e.key,
        keyDown: now,
        keyUp: null,
        dwellTime: null,
        flightTime: this.lastKeyUp ? now - this.lastKeyUp : null,
      });
    }
  };

  _onKeyUp = (e) => {
    const now = performance.now();
    const stroke = this.keystrokes.find(k => k.key === e.key && !k.keyUp);
    if (stroke) {
      stroke.keyUp = now;
      stroke.dwellTime = now - stroke.keyDown;
    }
    this.lastKeyUp = now;
  };

  // ── Mouse Capture ──────────────────────────────────────────
  _onMouseMove = (e) => {
    const now = performance.now();
    const pos = { x: e.clientX, y: e.clientY, t: now };

    if (this.lastMousePos) {
      const dx = pos.x - this.lastMousePos.x;
      const dy = pos.y - this.lastMousePos.y;
      const dt = (pos.t - this.lastMousePos.t) / 1000; // seconds
      const distance = Math.sqrt(dx * dx + dy * dy);
      pos.velocity = dt > 0 ? distance / dt : 0;
    }

    this.mousePositions.push(pos);
    this.lastMousePos = pos;

    // Keep buffer manageable
    if (this.mousePositions.length > 200) {
      this.mousePositions = this.mousePositions.slice(-100);
    }
  };

  // ── Compute Aggregate Metrics ──────────────────────────────
  _computeKeystrokeMetrics() {
    const completed = this.keystrokes.filter(k => k.dwellTime !== null);
    if (completed.length < 3) return null;

    const dwellTimes = completed.map(k => k.dwellTime);
    const flightTimes = completed.filter(k => k.flightTime !== null).map(k => k.flightTime);

    const avg = arr => arr.reduce((a, b) => a + b, 0) / arr.length;
    const std = arr => {
      const m = avg(arr);
      return Math.sqrt(arr.reduce((sum, x) => sum + (x - m) ** 2, 0) / arr.length);
    };

    return {
      avg_dwell_time: avg(dwellTimes),
      avg_flight_time: flightTimes.length > 0 ? avg(flightTimes) : 0,
      std_dwell_time: std(dwellTimes),
      std_flight_time: flightTimes.length > 0 ? std(flightTimes) : 0,
      typing_speed: completed.length / 3, // chars per 3-second window
      sample_size: completed.length,
    };
  }

  _computeMouseMetrics() {
    if (this.mousePositions.length < 5) return null;

    const velocities = this.mousePositions
      .filter(p => p.velocity !== undefined)
      .map(p => p.velocity);

    if (velocities.length < 2) return null;

    const avg = arr => arr.reduce((a, b) => a + b, 0) / arr.length;

    // Path straightness: ratio of direct distance to actual path length
    const first = this.mousePositions[0];
    const last = this.mousePositions[this.mousePositions.length - 1];
    const directDistance = Math.sqrt(
      (last.x - first.x) ** 2 + (last.y - first.y) ** 2
    );

    let pathLength = 0;
    for (let i = 1; i < this.mousePositions.length; i++) {
      const dx = this.mousePositions[i].x - this.mousePositions[i - 1].x;
      const dy = this.mousePositions[i].y - this.mousePositions[i - 1].y;
      pathLength += Math.sqrt(dx * dx + dy * dy);
    }

    return {
      avg_velocity: avg(velocities),
      max_velocity: Math.max(...velocities),
      path_straightness: pathLength > 0 ? directDistance / pathLength : 0,
      sample_size: this.mousePositions.length,
    };
  }

  // ── Send to Backend ────────────────────────────────────────
  async _sendTelemetry() {
    const keystrokeMetrics = this._computeKeystrokeMetrics();
    const mouseMetrics = this._computeMouseMetrics();

    if (!keystrokeMetrics && !mouseMetrics) return;

    const token = localStorage.getItem('sentinel_token');
    if (!token) return;

    try {
      const response = await fetch('http://localhost:8000/api/telemetry/ingest', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${token}`,
        },
        body: JSON.stringify({
          session_id: this.sessionId,
          keystroke_metrics: keystrokeMetrics,
          mouse_metrics: mouseMetrics,
        }),
      });

      if (response.ok) {
        const data = await response.json();
        if (this.onTrustUpdate) {
          this.onTrustUpdate(data);
        }
      }
    } catch (err) {
      console.warn('[Sentinel SDK] Telemetry send failed:', err.message);
    }

    // Clear processed keystrokes, keep mouse buffer
    this.keystrokes = [];
  }

  // ── Device Fingerprint ─────────────────────────────────────
  static getFingerprint() {
    const canvas = document.createElement('canvas');
    const ctx = canvas.getContext('2d');
    ctx.textBaseline = 'top';
    ctx.font = '14px Arial';
    ctx.fillText('Sentinel Fingerprint', 2, 2);
    const canvasHash = canvas.toDataURL().slice(-32);

    return {
      hash: btoa([
        navigator.userAgent,
        screen.width + 'x' + screen.height,
        Intl.DateTimeFormat().resolvedOptions().timeZone,
        navigator.language,
        screen.colorDepth,
        navigator.platform,
        canvasHash,
      ].join('|')).slice(0, 32),
      user_agent: navigator.userAgent,
      screen_resolution: screen.width + 'x' + screen.height,
      timezone: Intl.DateTimeFormat().resolvedOptions().timeZone,
      language: navigator.language,
      color_depth: screen.colorDepth,
      platform: navigator.platform,
      hardware_concurrency: navigator.hardwareConcurrency,
      touch_support: 'ontouchstart' in window,
      canvas_hash: canvasHash,
    };
  }
}

// Singleton instance
const telemetrySDK = new TelemetrySDK();
export default telemetrySDK;
