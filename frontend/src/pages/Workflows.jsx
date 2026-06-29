import { useState, useEffect } from 'react';
import axios from 'axios';
import { getErrorMessage } from '../utils/errors';

function WorkflowRow({ wf, onSelect }) {
  const steps = wf.steps?.length ?? 0;
  const ok = wf.steps?.filter(s => s.success).length ?? 0;

  return (
    <tr style={{ cursor: 'pointer' }} onClick={() => onSelect(wf)}>
      <td>
        <div style={{ fontSize: 12, fontFamily: 'monospace', color: 'var(--accent-cyan)' }}>
          {wf.workflow_id?.slice(0, 12)}...
        </div>
      </td>
      <td className="primary" style={{ maxWidth: 240, overflow: 'hidden', textOverflow: 'ellipsis', whiteSpace: 'nowrap' }}>
        {wf.user_request}
      </td>
      <td>
        <span className={`badge ${wf.status === 'completed' ? 'badge-success' : wf.status === 'failed' ? 'badge-error' : 'badge-pending'}`}>
          {wf.status}
        </span>
      </td>
      <td>
        <div style={{ display: 'flex', alignItems: 'center', gap: 6 }}>
          <div style={{
            flex: 1, height: 4, background: 'var(--bg-input)',
            borderRadius: 2, minWidth: 60, maxWidth: 80
          }}>
            <div style={{
              height: '100%', borderRadius: 2,
              width: steps > 0 ? `${(ok / steps) * 100}%` : '0%',
              background: 'linear-gradient(90deg, var(--accent-primary), var(--accent-emerald))',
              transition: 'width 0.5s ease'
            }} />
          </div>
          <span style={{ fontSize: 11, color: 'var(--text-muted)', whiteSpace: 'nowrap' }}>
            {ok}/{steps}
          </span>
        </div>
      </td>
      <td>{wf.execution_time || '-'}</td>
      <td style={{ fontSize: 11 }}>
        {wf.completed_at ? new Date(wf.completed_at).toLocaleString() : '-'}
      </td>
    </tr>
  );
}

function WorkflowModal({ wf, onClose, onDelete }) {
  if (!wf) return null;
  
  const handleDelete = async () => {
    if (window.confirm("Are you sure you want to delete this workflow execution from history?")) {
      try {
        await axios.delete(`/api/workflow/${wf.workflow_id}`);
        onDelete(wf.workflow_id);
        onClose();
      } catch (err) {
        alert(getErrorMessage(err, "Delete failed"));
      }
    }
  };

  return (
    <div className="modal-overlay" onClick={e => e.target === e.currentTarget && onClose()}>
      <div className="modal-box" style={{ position: 'relative' }}>
        <div className="modal-header">
          <div className="modal-title">Workflow Detail</div>
          <button className="modal-close" onClick={onClose}>✕</button>
        </div>
        <div className="modal-body" style={{ paddingBottom: 60 }}>
          {/* Meta */}
          <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: 10, marginBottom: 20 }}>
            {[
              ['ID', wf.workflow_id],
              ['Status', wf.status],
              ['Duration', wf.execution_time || '-'],
              ['Steps', wf.steps?.length ?? 0],
            ].map(([label, val]) => (
              <div key={label} style={{
                background: 'var(--bg-input)', borderRadius: 8,
                padding: '10px 14px', border: '1px solid var(--border-subtle)'
              }}>
                <div style={{ fontSize: 10, color: 'var(--text-muted)', marginBottom: 3, textTransform: 'uppercase', letterSpacing: '0.06em' }}>{label}</div>
                <div style={{ fontSize: 13, fontWeight: 600, color: 'var(--text-primary)', wordBreak: 'break-all' }}>{String(val)}</div>
              </div>
            ))}
          </div>

          {/* Request */}
          <div style={{ marginBottom: 20 }}>
            <div style={{ fontSize: 12, color: 'var(--text-muted)', marginBottom: 6, textTransform: 'uppercase', letterSpacing: '0.06em', fontWeight: 600 }}>User Request</div>
            <div className="code-block">{wf.user_request}</div>
          </div>

          {/* Prominent Final Output Report */}
          {(() => {
            const reportStep = wf.steps?.find(s => s.step === 'ReportGenerator' || s.agent === 'ReportGenerator');
            const reportSummary = reportStep?.data?.report?.summary;
            if (!reportSummary) return null;

            return (
              <div style={{
                background: 'rgba(99, 102, 241, 0.06)',
                border: '1px solid rgba(99, 102, 241, 0.2)',
                borderRadius: 10, padding: 16, marginBottom: 20
              }}>
                <h4 style={{
                  fontSize: 10.5, color: 'var(--accent-cyan)', textTransform: 'uppercase',
                  letterSpacing: '0.06em', marginBottom: 8, fontWeight: 700
                }}>
                  {"\ud83d\udccb"} Final Output Report
                </h4>
                <div style={{
                  fontSize: 12.5, color: 'var(--text-secondary)', lineHeight: 1.5,
                  whiteSpace: 'pre-wrap', fontFamily: 'system-ui'
                }}>
                  {reportSummary}
                </div>
              </div>
            );
          })()}

          {/* Steps */}
          <div style={{ fontSize: 12, color: 'var(--text-muted)', marginBottom: 10, textTransform: 'uppercase', letterSpacing: '0.06em', fontWeight: 600 }}>Execution Steps</div>
          {wf.steps?.map((step, i) => (
            <div key={i} style={{
              display: 'flex', gap: 12, padding: '12px 0',
              borderBottom: i < wf.steps.length - 1 ? '1px solid var(--border-subtle)' : 'none',
              alignItems: 'flex-start'
            }}>
              <div style={{
                width: 24, height: 24, borderRadius: '50%', flexShrink: 0,
                background: step.success ? 'rgba(16,185,129,0.2)' : 'rgba(244,63,94,0.2)',
                color: step.success ? 'var(--accent-emerald)' : 'var(--accent-rose)',
                display: 'flex', alignItems: 'center', justifyContent: 'center',
                fontSize: 11, fontWeight: 700, marginTop: 2
              }}>
                {step.success ? '✓' : '✗'}
              </div>
              <div style={{ flex: 1 }}>
                <div style={{ fontSize: 13, fontWeight: 600, color: 'var(--text-primary)', marginBottom: 3 }}>
                  {step.step || step.agent}
                </div>
                <div style={{ fontSize: 11, color: 'var(--text-muted)' }}>
                  Confidence: {step.confidence != null ? (step.confidence * 100).toFixed(0) + '%' : '-'}
                </div>
                {step.error && (
                  <div style={{ fontSize: 12, color: 'var(--accent-rose)', marginTop: 4 }}>{step.error}</div>
                )}
                {step.data && Object.keys(step.data).length > 0 && (
                  <div style={{ marginTop: 6 }}>
                    {/* Render Report Summary Output Inline */}
                    {(step.step === 'ReportGenerator' || step.agent === 'ReportGenerator') && step.data.report && (
                      <div style={{
                        marginTop: 8, background: 'rgba(255, 255, 255, 0.03)',
                        borderRadius: 6, padding: '10px 12px', border: '1px solid rgba(255,255,255,0.06)'
                      }}>
                        <div style={{ fontSize: 10, fontWeight: 700, color: 'var(--accent-cyan)', textTransform: 'uppercase', marginBottom: 6 }}>
                          {"\ud83d\udccb"} Summary Report
                        </div>
                        <div style={{
                          fontSize: 12, color: 'var(--text-secondary)', lineHeight: 1.45,
                          whiteSpace: 'pre-wrap', fontFamily: 'system-ui'
                        }}>
                          {step.data.report.summary}
                        </div>
                      </div>
                    )}
                    
                    <details style={{ marginTop: 8 }}>
                      <summary style={{ fontSize: 11, color: 'var(--accent-primary)', cursor: 'pointer' }}>View raw JSON data →</summary>
                      <div className="code-block" style={{ marginTop: 8, maxHeight: 200, overflow: 'auto' }}>
                        {JSON.stringify(step.data, null, 2)}
                      </div>
                    </details>
                  </div>
                )}
              </div>
            </div>
          ))}
        </div>
        
        {/* Footer actions inside modal */}
        <div style={{
          position: 'absolute', bottom: 0, left: 0, right: 0, height: 60,
          background: 'var(--bg-card)', borderTop: '1px solid var(--border-subtle)',
          display: 'flex', alignItems: 'center', justifyContent: 'flex-end',
          padding: '0 20px', borderRadius: '0 0 var(--radius-lg) var(--radius-lg)'
        }}>
          <button onClick={handleDelete} className="btn-danger" style={{ padding: '8px 16px', gap: 6 }}>
            🗑️ Delete Workflow
          </button>
        </div>
      </div>
    </div>
  );
}

export default function Workflows() {
  const [workflows, setWorkflows] = useState([]);
  const [loading, setLoading]     = useState(true);
  const [selected, setSelected]   = useState(null);

  const [filter, setFilter]       = useState('all');

  const load = () => {
    setLoading(true);
    axios.get('/api/workflow/')
      .then(r => setWorkflows(Array.isArray(r.data) ? r.data : []))
      .catch(() => setWorkflows([]))
      .finally(() => setLoading(false));
  };

  useEffect(() => { load(); }, []);

  const filtered = workflows.filter(wf => filter === 'all' || wf.status === filter);

  return (
    <div className="fade-in">
      <div className="page-header">
        <div>
          <h1 className="page-title">Workflows</h1>
          <p className="page-subtitle">All workflow executions - click any row for details</p>
        </div>
        <button className="btn-secondary" onClick={load} style={{ gap: 6 }}>
          {"\ud83d\udd04"} Refresh
        </button>
      </div>

      {/* Filter tabs */}
      <div style={{ display: 'flex', gap: 8, marginBottom: 20 }}>
        {['all', 'completed', 'failed', 'in_progress'].map(f => (
          <button
            key={f}
            onClick={() => setFilter(f)}
            style={{
              padding: '6px 14px', borderRadius: 20, fontSize: 12, fontWeight: 500,
              cursor: 'pointer', fontFamily: 'Inter, sans-serif',
              background: filter === f ? 'var(--accent-primary)' : 'var(--bg-card)',
              color: filter === f ? '#fff' : 'var(--text-muted)',
              border: `1px solid ${filter === f ? 'var(--accent-primary)' : 'var(--border-subtle)'}`,
              transition: 'all 0.2s',
            }}
          >
            {f === 'all' ? `All (${workflows.length})` : f}
          </button>
        ))}
      </div>

      {/* Table */}
      <div className="glass-card" style={{ overflow: 'hidden', padding: 0 }}>
        {loading ? (
          <div style={{ padding: 48, textAlign: 'center' }}>
            <div className="spinner" style={{ margin: '0 auto', width: 28, height: 28 }} />
            <div style={{ color: 'var(--text-muted)', marginTop: 16, fontSize: 14 }}>Loading workflows...</div>
          </div>
        ) : filtered.length === 0 ? (
          <div className="empty-state">
            <div className="empty-state-icon">{"\ud83d\udd04"}</div>
            <div className="empty-state-title">No workflows found</div>
            <div className="empty-state-text">Go to Dashboard and run a workflow to see it here.</div>
          </div>
        ) : (
          <div style={{ overflowX: 'auto' }}>
            <table className="data-table">
              <thead>
                <tr>
                  <th>ID</th>
                  <th>Request</th>
                  <th>Status</th>
                  <th>Progress</th>
                  <th>Duration</th>
                  <th>Completed</th>
                </tr>
              </thead>
              <tbody>
                {filtered.map((wf, i) => (
                  <WorkflowRow key={i} wf={wf} onSelect={setSelected} />
                ))}
              </tbody>
            </table>
          </div>
        )}
      </div>

      {selected && (
        <WorkflowModal
          wf={selected}
          onClose={() => setSelected(null)}
          onDelete={(id) => setWorkflows(list => list.filter(w => w.workflow_id !== id))}
        />
      )}
    </div>
  );
}
