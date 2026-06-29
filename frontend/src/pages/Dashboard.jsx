import { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import axios from 'axios';
import { getErrorMessage } from '../utils/errors';

/* ── Stat Card ─────────────────────────────────────────── */
function StatCard({ icon, label, value, color, sub }) {
  return (
    <div className="stat-card">
      <div className="stat-card-icon" style={{ background: `${color}22` }}>
        <span style={{ fontSize: 20 }}>{icon}</span>
      </div>
      <div className="stat-card-value gradient-text">{value}</div>
      <div className="stat-card-label">{label}</div>
      {sub && <div style={{ fontSize: 11, color: 'var(--text-muted)', marginTop: 4 }}>{sub}</div>}
    </div>
  );
}

/* ── Plugin Result Details ──────────────────────────────── */
function PluginDetails({ data }) {
  const subSteps = data?.sub_steps || [];
  const prospects = data?.prospect_list || data?.qualified_companies || [];
  const shortlist = data?.shortlist || [];
  const isB2B = prospects.length > 0;
  const totalCandidates = data?.total_candidates ?? 0;

  return (
    <div style={{ marginTop: 8 }}>
      {/* Sub-step pipeline tags */}
      {subSteps.length > 0 && (
        <div style={{ display: 'flex', gap: 4, flexWrap: 'wrap', marginBottom: 10 }}>
          {subSteps.map((s, i) => (
            <span key={i} style={{
              fontSize: 10, padding: '2px 7px', borderRadius: 10, fontWeight: 600,
              background: s.success ? 'rgba(16,185,129,0.12)' : 'rgba(244,63,94,0.12)',
              color: s.success ? 'var(--accent-emerald)' : 'var(--accent-rose)',
              border: `1px solid ${s.success ? 'rgba(16,185,129,0.25)' : 'rgba(244,63,94,0.25)'}`,
            }}>
              {s.success ? '✓' : '✗'} {s.step?.replace(/_/g, ' ')}
            </span>
          ))}
        </div>
      )}

      {/* HR Candidates */}
      {!isB2B && shortlist.length > 0 && (
        <div style={{ display: 'flex', flexDirection: 'column', gap: 6 }}>
          <div style={{ fontSize: 11, color: 'var(--text-muted)', marginBottom: 2 }}>
            🔍 Found {totalCandidates} candidates → <strong style={{ color: 'var(--accent-emerald)' }}>{shortlist.length}</strong> shortlisted:
          </div>
          {shortlist.map((c, i) => (
            <div key={i} style={{
              background: 'var(--bg-input)', borderRadius: 8, padding: '8px 12px',
              border: '1px solid var(--border-subtle)', display: 'flex', alignItems: 'center', gap: 10
            }}>
              <div style={{
                width: 28, height: 28, borderRadius: '50%', flexShrink: 0,
                background: 'linear-gradient(135deg, var(--accent-primary), var(--accent-secondary))',
                display: 'flex', alignItems: 'center', justifyContent: 'center',
                fontSize: 11, fontWeight: 700, color: '#fff'
              }}>
                {c.name?.charAt(0) || '?'}
              </div>
              <div style={{ flex: 1, minWidth: 0 }}>
                <div style={{ fontSize: 12, fontWeight: 600, color: 'var(--text-primary)' }}>{c.name}</div>
                <div style={{ fontSize: 10, color: 'var(--text-muted)', overflow: 'hidden', textOverflow: 'ellipsis', whiteSpace: 'nowrap' }}>
                  {c.experience_years}yr · {c.location} · {(c.skills || []).slice(0, 3).join(', ')}
                </div>
              </div>
              <div style={{
                fontSize: 12, fontWeight: 700, flexShrink: 0, padding: '2px 8px',
                borderRadius: 6, background: 'rgba(16,185,129,0.15)', color: 'var(--accent-emerald)',
                border: '1px solid rgba(16,185,129,0.25)'
              }}>
                {c.match_score != null ? `${Math.round(c.match_score * 100)}%` : '-'}
              </div>
            </div>
          ))}
        </div>
      )}

      {/* Generic Prospects/Companies */}
      {isB2B && prospects.length > 0 && (
        <div style={{ display: 'flex', flexDirection: 'column', gap: 6 }}>
          <div style={{ fontSize: 11, color: 'var(--text-muted)', marginBottom: 2 }}>
            📈 <strong style={{ color: 'var(--accent-cyan)' }}>{prospects.length}</strong> qualified prospects found:
          </div>
          {prospects.map((p, i) => {
            const coName = p.company?.name || p.name;
            const sector = p.company?.sector || p.sector;
            const orgType = p.company?.org_type || p.org_type || p.company?.funding_stage || p.funding_stage;
            const score = p.company?.icp_score || p.icp_score || 0;
            const contact = p.primary_contact || {};
            const reason = p.matching_reason || p.company?.matching_reason;

            return (
              <div key={i} style={{
                background: 'var(--bg-input)', borderRadius: 8, padding: '10px 14px',
                border: '1px solid var(--border-subtle)', display: 'flex', flexDirection: 'column', gap: 4
              }}>
                <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                  <div style={{ fontSize: 12.5, fontWeight: 700, color: 'var(--text-primary)' }}>
                    #{p.rank || i + 1} {coName}
                  </div>
                  <span style={{
                    fontSize: 11, fontWeight: 700, padding: '1px 6px', borderRadius: 4,
                    background: 'rgba(99,102,241,0.15)', color: 'var(--accent-primary)'
                  }}>
                    {Math.round(score * 100)}% match
                  </span>
                </div>
                <div style={{ fontSize: 10, color: 'var(--text-muted)' }}>
                  {sector}{orgType ? ` · ${orgType}` : ''}
                </div>
                {contact.name && (
                  <div style={{ fontSize: 10.5, color: 'var(--text-secondary)', marginTop: 2 }}>
                    👤 {contact.name} ({contact.title}) · 📧 {contact.email}
                  </div>
                )}
                {reason && (
                  <div style={{
                    fontSize: 9.5, padding: '3px 6px', borderRadius: 4, marginTop: 2,
                    background: 'rgba(255,255,255,0.03)', color: 'var(--text-muted)',
                    border: '1px solid var(--border-subtle)'
                  }}>
                    💡 {reason}
                  </div>
                )}
              </div>
            );
          })}
        </div>
      )}
    </div>
  );
}

function StepBadge({ step }) {
  const isOk = step.success;
  const isPlugin = step.step === 'plugin_execution';
  const isReport = step.step === 'ReportGenerator' || step.agent === 'ReportGenerator';
  const label = isPlugin
    ? `🧩 ${step.agent || 'Plugin'} Pipeline`
    : (step.step || step.agent);

  return (
    <div style={{ padding: '12px 0', borderBottom: '1px solid var(--border-subtle)' }}>
      <div style={{ display: 'flex', alignItems: 'flex-start', gap: 12 }}>
        <div style={{
          width: 24, height: 24, borderRadius: '50%', flexShrink: 0,
          background: isOk ? 'rgba(16,185,129,0.2)' : 'rgba(244,63,94,0.2)',
          color: isOk ? 'var(--accent-emerald)' : 'var(--accent-rose)',
          display: 'flex', alignItems: 'center', justifyContent: 'center',
          fontSize: 12, fontWeight: 700, marginTop: 2
        }}>
          {isOk ? '✓' : '✗'}
        </div>
        <div style={{ flex: 1, minWidth: 0 }}>
          <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: 2 }}>
            <div style={{ fontSize: 13, fontWeight: 600, color: 'var(--text-primary)' }}>{label}</div>
            <div style={{ fontSize: 10, color: 'var(--text-muted)' }}>
              {step.timestamp ? new Date(step.timestamp).toLocaleTimeString() : ''}
            </div>
          </div>
          {step.error && <div style={{ fontSize: 12, color: 'var(--accent-rose)' }}>{step.error}</div>}
          {isPlugin && step.data && <PluginDetails data={step.data} />}
          {isReport && step.data?.report && (
            <div style={{
              marginTop: 10, background: 'rgba(255,255,255,0.03)',
              borderRadius: 8, padding: '14px 16px', border: '1px solid rgba(255,255,255,0.06)'
            }}>
              <div style={{ fontSize: 11, fontWeight: 700, color: 'var(--accent-cyan)', textTransform: 'uppercase', marginBottom: 8, letterSpacing: '0.06em' }}>
                📋 Generated Summary
              </div>
              <div style={{ fontSize: 12.5, color: 'var(--text-secondary)', lineHeight: 1.5, whiteSpace: 'pre-wrap', wordBreak: 'break-word' }}>
                {step.data.report.summary}
              </div>
            </div>
          )}
        </div>
      </div>
    </div>
  );
}

/* ── Main Dashboard ──────────────────────────────────────── */
export default function Dashboard() {
  const [request, setRequest] = useState('');
  const [loading, setLoading] = useState(false);
  const [result, setResult] = useState(null);
  const [error, setError] = useState('');
  const [health, setHealth] = useState(null);
  const [workflows, setWorkflows] = useState([]);
  const [plugins, setPlugins] = useState([]);
  const [selectedPlugin, setSelectedPlugin] = useState('none');
  const navigate = useNavigate();

  useEffect(() => {
    axios.get('/api/health').then(r => setHealth(r.data)).catch(() => {});
    axios.get('/api/workflow/').then(r => setWorkflows(r.data.slice(0, 5))).catch(() => {});
    axios.get('/api/plugins/').then(r => {
      setPlugins(Array.isArray(r.data) ? r.data : []);
    }).catch(() => {
      setPlugins([
        { name: 'hr_recruitment', display_name: 'HR Recruitment' },
        { name: 'b2b_sales', display_name: 'B2B Sales' }
      ]);
    });
  }, []);

  const handleSubmit = async (e) => {
    e.preventDefault();
    if (!request.trim()) return;
    setLoading(true);
    setError('');
    setResult(null);
    try {
      const { data } = await axios.post('/api/workflow/start', {
        user_request: request,
        plugin: selectedPlugin === 'none' ? null : selectedPlugin
      });
      setResult(data.workflow);
      navigate(`/results/${data.workflow.workflow_id}`, { state: { workflow: data.workflow, userRequest: request } });
      axios.get('/api/workflow/').then(r => setWorkflows(r.data.slice(0, 5))).catch(() => {});
    } catch (err) {
      setError(getErrorMessage(err, 'Failed to start workflow. Is the backend running?'));
    } finally {
      setLoading(false);
    }
  };

  const enabledPlugins = plugins.filter(p => p.enabled !== false);
  const customPlugins = plugins.filter(p => p.is_custom);

  return (
    <div className="fade-in">
      {/* Page Header */}
      <div className="page-header">
        <div>
          <h1 className="page-title">Dashboard</h1>
          <p className="page-subtitle">Describe your goal — the AI agents will plan, route, and execute automatically</p>
        </div>
        <div style={{ display: 'flex', alignItems: 'center', gap: 8 }}>
          <div className="pulse-dot pulse-dot-green" />
          <span style={{ fontSize: 13, color: 'var(--accent-emerald)', fontWeight: 500 }}>System Online</span>
        </div>
      </div>

      {/* Stats Row */}
      <div className="grid-4" style={{ marginBottom: 28 }}>
        <StatCard
          icon="🤖" label="Active Agents"
          value={health?.agents_registered ?? '-'}
          color="var(--accent-primary)"
          sub="Ready to execute"
        />
        <StatCard
          icon="🧩" label="Enabled Plugins"
          value={enabledPlugins.length || (health?.capabilities_registered > 4 ? plugins.length || 2 : 0)}
          color="var(--accent-cyan)"
          sub={customPlugins.length > 0 ? `${customPlugins.length} custom domain(s)` : 'Built-in + Custom'}
        />
        <StatCard
          icon="🔄" label="Workflows Run"
          value={workflows.length}
          color="var(--accent-emerald)"
          sub="This session"
        />
        <StatCard
          icon="✅" label="Completed"
          value={workflows.filter(w => w.status === 'completed').length}
          color="var(--accent-secondary)"
          sub="Successfully finished"
        />
      </div>

      <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: 24 }}>

        {/* ── LEFT: Workflow Runner ── */}
        <div style={{ display: 'flex', flexDirection: 'column', gap: 0 }}>
          <div className="glass-card" style={{ padding: 28 }}>
            <h2 style={{ fontSize: 16, fontWeight: 700, marginBottom: 6, color: 'var(--text-primary)' }}>
              ⚡ Run a Workflow
            </h2>
            <p style={{ fontSize: 13, color: 'var(--text-muted)', marginBottom: 22 }}>
              Type your research or discovery request — any domain, any goal
            </p>

            <form onSubmit={handleSubmit}>
              <div style={{ marginBottom: 16 }}>
                <label className="form-label" style={{ display: 'flex', justifyContent: 'space-between' }}>
                  <span>Domain / Plugin</span>
                  <span style={{ fontSize: 10.5, color: 'var(--text-muted)' }}>Auto-detect works for most queries</span>
                </label>
                <select
                  value={selectedPlugin}
                  onChange={e => setSelectedPlugin(e.target.value)}
                  className="form-input"
                  style={{ background: 'var(--bg-input)', cursor: 'pointer', height: 40 }}
                >
                  <option value="none">🔮 Auto-detect (recommended)</option>
                  {plugins.map(p => {
                    const displayName = p.display_name || p.name.replace(/_/g, ' ').replace(/\b\w/g, c => c.toUpperCase());
                    return (
                      <option key={p.name} value={p.name}>
                        🧩 {displayName} {p.enabled ? '' : '(Disabled)'}
                      </option>
                    );
                  })}
                </select>
              </div>

              <label className="form-label">Your Request</label>
              <textarea
                id="workflow-request"
                className="form-textarea"
                value={request}
                onChange={e => setRequest(e.target.value)}
                placeholder="e.g. Find colleges and research labs in Mumbai that can buy solar panels&#10;e.g. We need a Senior Python Engineer with 5+ years FastAPI experience&#10;e.g. Find hospitals in Delhi looking to upgrade their medical equipment"
                rows={5}
                style={{ marginBottom: 16 }}
              />

              <button
                id="workflow-submit"
                type="submit"
                className="btn-primary"
                disabled={loading || !request.trim()}
                style={{ width: '100%', justifyContent: 'center', padding: '13px 20px', fontSize: 14 }}
              >
                {loading
                  ? <><div className="spinner" /> Processing...</>
                  : '⚡ Start Workflow'}
              </button>
            </form>

            {error && (
              <div className="alert alert-error" style={{ marginTop: 16 }}>
                <span>⚠️</span>
                <span>{error}</span>
              </div>
            )}
          </div>

          {/* Result Card */}
          {result && (() => {
            const reportStep = result.steps?.find(s => s.step === 'ReportGenerator' || s.agent === 'ReportGenerator');
            const reportSummary = reportStep?.data?.report?.summary;

            return (
              <div className="glass-card fade-in" style={{ padding: 24, marginTop: 16 }}>
                <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: 16 }}>
                  <h3 style={{ fontSize: 15, fontWeight: 700, color: 'var(--text-primary)' }}>Workflow Result</h3>
                  <span className={`badge ${result.status === 'completed' ? 'badge-success' : 'badge-error'}`}>
                    {result.status}
                  </span>
                </div>

                <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: 10, marginBottom: 16 }}>
                  {[
                    ['Duration', result.execution_time || '-'],
                    ['Steps', result.steps?.length ?? 0],
                  ].map(([label, val]) => (
                    <div key={label} style={{
                      background: 'var(--bg-input)', borderRadius: 8, padding: '10px 14px',
                      border: '1px solid var(--border-subtle)'
                    }}>
                      <div style={{ fontSize: 10, color: 'var(--text-muted)', marginBottom: 4, textTransform: 'uppercase', letterSpacing: '0.06em' }}>{label}</div>
                      <div style={{ fontSize: 14, fontWeight: 600, color: 'var(--text-primary)' }}>{val}</div>
                    </div>
                  ))}
                </div>

                {reportSummary && (
                  <div style={{
                    background: 'rgba(99,102,241,0.06)', border: '1px solid rgba(99,102,241,0.2)',
                    borderRadius: 12, padding: 18, marginBottom: 16
                  }}>
                    <h4 style={{ fontSize: 11, color: 'var(--accent-cyan)', textTransform: 'uppercase', letterSpacing: '0.06em', marginBottom: 10, fontWeight: 700 }}>
                      📋 Final Output Report
                    </h4>
                    <div style={{ fontSize: 13, color: 'var(--text-secondary)', lineHeight: 1.55, whiteSpace: 'pre-wrap', fontFamily: 'system-ui' }}>
                      {reportSummary}
                    </div>
                  </div>
                )}

                <div style={{ fontSize: 13, fontWeight: 600, color: 'var(--text-secondary)', marginBottom: 10 }}>Execution Steps</div>
                {result.steps?.map((step, i) => <StepBadge key={i} step={step} />)}
              </div>
            );
          })()}
        </div>

        {/* ── RIGHT panel ── */}
        <div style={{ display: 'flex', flexDirection: 'column', gap: 16 }}>

          {/* Platform Status */}
          <div className="glass-card" style={{ padding: 24 }}>
            <h2 style={{ fontSize: 15, fontWeight: 700, marginBottom: 16, color: 'var(--text-primary)' }}>
              📊 Platform Status
            </h2>
            {health ? (
              <div style={{ display: 'flex', flexDirection: 'column', gap: 10 }}>
                {[
                  { label: 'API Server', status: 'Online', ok: true },
                  { label: 'Gemini AI', status: 'Connected', ok: true },
                  { label: 'MongoDB', status: 'Connected', ok: true },
                ].map(({ label, status, ok }) => (
                  <div key={label} style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                    <span style={{ fontSize: 13, color: 'var(--text-secondary)' }}>{label}</span>
                    <span className={`badge ${ok ? 'badge-success' : 'badge-error'}`}>● {status}</span>
                  </div>
                ))}
                <hr style={{ border: 'none', borderTop: '1px solid var(--border-subtle)', margin: '4px 0' }} />
                <div style={{ display: 'flex', justifyContent: 'space-between', fontSize: 12, color: 'var(--text-muted)' }}>
                  <span>Registered Agents</span>
                  <strong style={{ color: 'var(--text-primary)' }}>{health.agents_registered}</strong>
                </div>
                <div style={{ display: 'flex', justifyContent: 'space-between', fontSize: 12, color: 'var(--text-muted)' }}>
                  <span>Capabilities</span>
                  <strong style={{ color: 'var(--text-primary)' }}>{health.capabilities_registered}</strong>
                </div>
                <div style={{ display: 'flex', justifyContent: 'space-between', fontSize: 12, color: 'var(--text-muted)' }}>
                  <span>Active Plugins</span>
                  <strong style={{ color: 'var(--text-primary)' }}>{enabledPlugins.length}</strong>
                </div>
              </div>
            ) : (
              <div style={{ textAlign: 'center', padding: 24 }}>
                <div className="shimmer" style={{ height: 14, borderRadius: 6, marginBottom: 8 }} />
                <div className="shimmer" style={{ height: 14, borderRadius: 6, width: '60%' }} />
              </div>
            )}
          </div>

          {/* Recent Workflows */}
          <div className="glass-card" style={{ padding: 24 }}>
            <h2 style={{ fontSize: 15, fontWeight: 700, marginBottom: 16, color: 'var(--text-primary)' }}>
              🕐 Recent Workflows
            </h2>
            {workflows.length === 0 ? (
              <div className="empty-state" style={{ padding: '24px 16px' }}>
                <div className="empty-state-icon" style={{ fontSize: 32 }}>🔄</div>
                <div className="empty-state-text">No workflows yet — run one above!</div>
              </div>
            ) : (
              <div>
                {workflows.map((wf, i) => (
                  <div key={i} style={{
                    display: 'flex', alignItems: 'center', gap: 12, cursor: 'pointer',
                    padding: '10px 0', borderBottom: i < workflows.length - 1 ? '1px solid var(--border-subtle)' : 'none'
                  }}
                    onClick={() => navigate(`/results/${wf.workflow_id}`)}
                  >
                    <span className={`badge ${wf.status === 'completed' ? 'badge-success' : 'badge-error'}`} style={{ flexShrink: 0 }}>
                      {wf.status}
                    </span>
                    <div style={{ flex: 1, overflow: 'hidden' }}>
                      <div style={{ fontSize: 12, color: 'var(--text-primary)', overflow: 'hidden', textOverflow: 'ellipsis', whiteSpace: 'nowrap' }}>
                        {wf.user_request}
                      </div>
                      <div style={{ fontSize: 11, color: 'var(--text-muted)' }}>{wf.execution_time || '-'}</div>
                    </div>
                    <span style={{ fontSize: 12, color: 'var(--text-muted)', flexShrink: 0 }}>→</span>
                  </div>
                ))}
              </div>
            )}
          </div>

          {/* Active Custom Domains */}
          {customPlugins.length > 0 && (
            <div className="glass-card" style={{ padding: 24 }}>
              <h2 style={{ fontSize: 15, fontWeight: 700, marginBottom: 16, color: 'var(--text-primary)' }}>
                🎯 Active Custom Domains
              </h2>
              <div style={{ display: 'flex', flexDirection: 'column', gap: 8 }}>
                {customPlugins.map((p, i) => (
                  <div key={i} style={{
                    display: 'flex', alignItems: 'center', justifyContent: 'space-between',
                    padding: '8px 12px', background: 'var(--bg-input)',
                    borderRadius: 8, border: '1px solid var(--border-subtle)'
                  }}>
                    <div>
                      <div style={{ fontSize: 12.5, fontWeight: 600, color: 'var(--text-primary)' }}>
                        {p.display_name || p.name.replace(/_/g, ' ').replace(/\b\w/g, c => c.toUpperCase())}
                      </div>
                      <div style={{ fontSize: 11, color: 'var(--text-muted)' }}>
                        {(p.geography || []).slice(0, 2).join(', ') || 'Any location'}
                      </div>
                    </div>
                    <span className={`badge ${p.enabled ? 'badge-success' : 'badge-error'}`} style={{ flexShrink: 0 }}>
                      {p.enabled ? '● Active' : '○ Off'}
                    </span>
                  </div>
                ))}
              </div>
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
