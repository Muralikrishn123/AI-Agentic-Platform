import { useState, useEffect, useRef } from 'react';
import axios from 'axios';

// Simulated live logs from workflow steps
function generateMockLogs(workflows) {
  const logs = [];
  workflows.forEach(wf => {
    logs.push({
      time: wf.completed_at || new Date().toISOString(),
      level: 'INFO',
      source: 'WorkflowEngine',
      message: `Workflow started: ${wf.workflow_id?.slice(0, 8)}`,
    });
    (wf.steps || []).forEach(step => {
      // Check if a report step signals fallback mode (llm_active === false)
      const isReportStep = (step.step === 'ReportGenerator' || step.agent === 'ReportGenerator');
      const llmActive = step.data?.report?.metadata?.llm_active;
      if (isReportStep && llmActive === false) {
        logs.push({
          time: step.timestamp || wf.completed_at || new Date().toISOString(),
          level: 'WARN',
          source: 'GeminiAI',
          message: '⚠️ Gemini API quota exhausted — workflow ran on Local Fallback Mode. Results are pre-mapped, not AI-generated. Quota resets within 24h.',
        });
      }
      logs.push({
        time: step.timestamp || wf.completed_at || new Date().toISOString(),
        level: step.success ? 'INFO' : 'ERROR',
        source: step.agent || step.step,
        message: step.success
          ? `✅ ${step.step || step.agent} completed (confidence: ${step.confidence != null ? (step.confidence * 100).toFixed(0) + '%' : '-'})`
          : `❌ ${step.step || step.agent} failed: ${step.error || 'Unknown error'}`,
      });
    });
    if (wf.status === 'completed') {
      logs.push({
        time: wf.completed_at || new Date().toISOString(),
        level: 'INFO',
        source: 'WorkflowEngine',
        message: `✅ Workflow completed in ${wf.execution_time || '-'}`,
      });
    }
  });
  return logs.sort((a, b) => new Date(b.time) - new Date(a.time));
}


const LEVEL_CLASS = {
  INFO:  'log-level-info',
  WARN:  'log-level-warn',
  ERROR: 'log-level-error',
  DEBUG: 'log-level-debug',
};

export default function Logs() {
  const [logs, setLogs]         = useState([]);
  const [loading, setLoading]   = useState(true);
  const [filter, setFilter]     = useState('ALL');
  const [autoRefresh, setAutoRefresh] = useState(true);
  const [search, setSearch]     = useState('');
  const scrollRef = useRef(null);

  const loadLogs = async () => {
    try {
      // Try real logs endpoint first
      const [apiLogs, workflows] = await Promise.all([
        axios.get('/api/logs/').catch(() => ({ data: [] })),
        axios.get('/api/workflow/').catch(() => ({ data: [] })),
      ]);

      let combined = [];

      if (Array.isArray(apiLogs.data) && apiLogs.data.length > 0) {
        combined = apiLogs.data;
      } else {
        // Generate from workflow steps as fallback
        combined = generateMockLogs(Array.isArray(workflows.data) ? workflows.data : []);
      }

      // Add system boot logs if empty
      if (combined.length === 0) {
        combined = [
          { time: new Date().toISOString(), level: 'INFO', source: 'System', message: '🚀 Agentic AI Platform v3.0 started' },
          { time: new Date().toISOString(), level: 'INFO', source: 'AgentRegistry', message: '✅ PlannerAgent registered' },
          { time: new Date().toISOString(), level: 'INFO', source: 'AgentRegistry', message: '✅ ValidationAgent registered' },
          { time: new Date().toISOString(), level: 'INFO', source: 'AgentRegistry', message: '✅ ReflectionAgent registered' },
          { time: new Date().toISOString(), level: 'INFO', source: 'AgentRegistry', message: '✅ ReportGenerator registered' },
          { time: new Date().toISOString(), level: 'INFO', source: 'PluginLifecycle', message: '🧩 HR Recruitment Plugin initializing...' },
          { time: new Date().toISOString(), level: 'INFO', source: 'HRPlugin', message: '✅ RequirementExtractionAgent registered (Gemini AI)' },
          { time: new Date().toISOString(), level: 'INFO', source: 'HRPlugin', message: '✅ CandidateMatchExplanationAgent registered' },
          { time: new Date().toISOString(), level: 'INFO', source: 'EventBus', message: '{"\u26a1"} SYSTEM_READY event emitted' },
        ];
      }

      setLogs(combined);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadLogs();
  }, []);

  useEffect(() => {
    if (!autoRefresh) return;
    const interval = setInterval(loadLogs, 5000);
    return () => clearInterval(interval);
  }, [autoRefresh]);

  const filtered = logs.filter(log => {
    const levelMatch = filter === 'ALL' || log.level === filter;
    const searchMatch = !search || (
      (log.message || '').toLowerCase().includes(search.toLowerCase()) ||
      (log.source || '').toLowerCase().includes(search.toLowerCase())
    );
    return levelMatch && searchMatch;
  });

  return (
    <div className="fade-in">
      <div className="page-header">
        <div>
          <h1 className="page-title">System Logs</h1>
          <p className="page-subtitle">Real-time agent execution logs</p>
        </div>
        <div style={{ display: 'flex', gap: 8, alignItems: 'center' }}>
          <button
            className={autoRefresh ? 'btn-primary' : 'btn-secondary'}
            onClick={() => setAutoRefresh(!autoRefresh)}
            style={{ fontSize: 12, padding: '7px 14px' }}
          >
            {autoRefresh ? '⏸ Pause' : '▶ Live'}
          </button>
          <button className="btn-secondary" onClick={loadLogs} style={{ fontSize: 12, padding: '7px 14px' }}>
            {"\ud83d\udd04"} Refresh
          </button>
        </div>
      </div>

      {/* Controls */}
      <div style={{ display: 'flex', gap: 12, marginBottom: 20, flexWrap: 'wrap' }}>
        {/* Search */}
        <input
          type="text"
          className="form-input"
          placeholder="🔍 Search logs..."
          value={search}
          onChange={e => setSearch(e.target.value)}
          style={{ flex: 1, minWidth: 200, maxWidth: 320, padding: '9px 14px' }}
        />

        {/* Level filter */}
        <div style={{ display: 'flex', gap: 6 }}>
          {['ALL', 'INFO', 'WARN', 'ERROR', 'DEBUG'].map(lvl => (
            <button
              key={lvl}
              onClick={() => setFilter(lvl)}
              style={{
                padding: '6px 12px', borderRadius: 20, fontSize: 11, fontWeight: 600,
                cursor: 'pointer', fontFamily: 'Inter, sans-serif',
                background: filter === lvl ? 'var(--accent-primary)' : 'var(--bg-card)',
                color: filter === lvl ? '#fff' : 'var(--text-muted)',
                border: `1px solid ${filter === lvl ? 'var(--accent-primary)' : 'var(--border-subtle)'}`,
                transition: 'all 0.2s',
              }}
            >
              {lvl}
            </button>
          ))}
        </div>

        <div style={{ display: 'flex', alignItems: 'center', gap: 6, fontSize: 12, color: 'var(--text-muted)' }}>
          {filtered.length} entries
          {autoRefresh && (
            <>
              <div className="pulse-dot pulse-dot-green" />
              <span style={{ color: 'var(--accent-emerald)' }}>Live</span>
            </>
          )}
        </div>
      </div>

      {/* Log stream */}
      <div className="glass-card" style={{ padding: 0, overflow: 'hidden' }}>
        <div
          ref={scrollRef}
          style={{ padding: '16px 24px', maxHeight: 620, overflowY: 'auto', fontFamily: 'Fira Code, Courier New, monospace' }}
        >
          {loading ? (
            <div style={{ textAlign: 'center', padding: 48 }}>
              <div className="spinner" style={{ margin: '0 auto', width: 28, height: 28 }} />
              <div style={{ color: 'var(--text-muted)', marginTop: 16, fontSize: 14 }}>Loading logs...</div>
            </div>
          ) : filtered.length === 0 ? (
            <div className="empty-state">
              <div className="empty-state-icon">{"\ud83d\udccb"}</div>
              <div className="empty-state-title">No logs found</div>
              <div className="empty-state-text">Run a workflow to generate logs.</div>
            </div>
          ) : (
            filtered.map((log, i) => (
              <div key={i} className="log-entry">
                <span className="log-time">
                  {log.time ? new Date(log.time).toLocaleTimeString() : '-'}
                </span>
                <span className={`log-level ${LEVEL_CLASS[log.level] || ''}`}>
                  [{log.level || 'INFO'}]
                </span>
                <span style={{ color: 'var(--accent-primary)', flexShrink: 0, minWidth: 80, fontSize: 11 }}>
                  {log.source || 'System'}
                </span>
                <span className="log-msg">{log.message}</span>
              </div>
            ))
          )}
        </div>
      </div>
    </div>
  );
}
