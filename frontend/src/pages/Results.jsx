import { useLocation, useNavigate, useParams } from "react-router-dom";
import { useEffect, useState, useRef } from "react";
import axios from "axios";

/* ── Pipeline stages shown during loading ─────────────────────────── */
const PIPELINE_STAGES = [
  { icon: "🧠", label: "Planner Agent", desc: "Analyzing your request & selecting the best domain plugin..." },
  { icon: "🔍", label: "Research Agent", desc: "Scraping web sources and extracting real-world entities..." },
  { icon: "⚖️", label: "Qualification Agent", desc: "Evaluating each prospect against your requirements..." },
  { icon: "👤", label: "Contact Discovery", desc: "Finding decision-makers and key contacts at each organization..." },
  { icon: "✅", label: "Validation & Reflection", desc: "Verifying results quality and refining output..." },
  { icon: "📋", label: "Report Generator", desc: "Compiling your final structured output report..." },
];

const THINKING_MESSAGES = [
  "Searching the web for matching organizations...",
  "Qualifying prospects against your criteria...",
  "Identifying key decision-makers...",
  "Cross-referencing industry signals...",
  "Generating insights and summaries...",
  "Almost there — finalizing your report...",
];

function PipelineLoader({ userRequest }) {
  const [activeStage, setActiveStage] = useState(0);
  const [completedStages, setCompletedStages] = useState([]);
  const [elapsed, setElapsed] = useState(0);
  const [msgIdx, setMsgIdx] = useState(0);
  const startRef = useRef(Date.now());

  useEffect(() => {
    const interval = setInterval(() => {
      setActiveStage(prev => {
        if (prev < PIPELINE_STAGES.length - 1) {
          setCompletedStages(c => [...c, prev]);
          return prev + 1;
        }
        return prev;
      });
    }, 8000);
    return () => clearInterval(interval);
  }, []);

  useEffect(() => {
    const interval = setInterval(() => {
      setMsgIdx(i => (i + 1) % THINKING_MESSAGES.length);
    }, 4000);
    return () => clearInterval(interval);
  }, []);

  useEffect(() => {
    const interval = setInterval(() => {
      setElapsed(Math.floor((Date.now() - startRef.current) / 1000));
    }, 1000);
    return () => clearInterval(interval);
  }, []);

  const progressPct = Math.min(((activeStage + 1) / PIPELINE_STAGES.length) * 100, 95);

  return (
    <div className="fade-in" style={{ maxWidth: 640, margin: '40px auto', padding: '0 16px' }}>
      <div style={{ textAlign: 'center', marginBottom: 36 }}>
        <div style={{
          fontSize: 48, marginBottom: 16,
          animation: 'spin 3s linear infinite',
          display: 'inline-block',
          filter: 'drop-shadow(0 0 16px rgba(99,102,241,0.6))'
        }}>⚡</div>
        <h2 style={{
          fontSize: 22, fontWeight: 800,
          background: 'linear-gradient(135deg, var(--accent-primary), var(--accent-secondary))',
          WebkitBackgroundClip: 'text', WebkitTextFillColor: 'transparent',
          marginBottom: 8
        }}>
          AI Agents Working
        </h2>
        {userRequest && (
          <div style={{
            fontSize: 13, color: 'var(--text-muted)', maxWidth: 480,
            margin: '0 auto', lineHeight: 1.5, fontStyle: 'italic',
            padding: '8px 16px', background: 'var(--bg-input)',
            borderRadius: 8, border: '1px solid var(--border-subtle)'
          }}>
            "{userRequest.length > 80 ? userRequest.slice(0, 80) + '…' : userRequest}"
          </div>
        )}
      </div>

      {/* Progress Bar */}
      <div style={{ marginBottom: 28 }}>
        <div style={{ display: 'flex', justifyContent: 'space-between', fontSize: 11, color: 'var(--text-muted)', marginBottom: 8 }}>
          <span>Pipeline Progress</span>
          <span>{elapsed}s elapsed</span>
        </div>
        <div style={{ height: 6, background: 'var(--bg-input)', borderRadius: 99, border: '1px solid var(--border-subtle)', overflow: 'hidden' }}>
          <div style={{
            height: '100%', borderRadius: 99,
            width: `${progressPct}%`,
            background: 'linear-gradient(90deg, var(--accent-primary), var(--accent-secondary), var(--accent-cyan))',
            transition: 'width 1.2s cubic-bezier(0.4,0,0.2,1)',
            boxShadow: '0 0 12px rgba(99,102,241,0.6)',
          }} />
        </div>
      </div>

      {/* Stage Nodes */}
      <div className="glass-card" style={{ padding: 24, marginBottom: 20 }}>
        <div style={{ display: 'flex', flexDirection: 'column', gap: 0 }}>
          {PIPELINE_STAGES.map((stage, i) => {
            const isDone = completedStages.includes(i);
            const isActive = activeStage === i;
            const isPending = !isDone && !isActive;
            return (
              <div key={i} style={{
                display: 'flex', alignItems: 'flex-start', gap: 14,
                padding: '14px 0',
                borderBottom: i < PIPELINE_STAGES.length - 1 ? '1px solid var(--border-subtle)' : 'none',
                transition: 'all 0.4s ease',
                opacity: isPending ? 0.4 : 1,
              }}>
                <div style={{
                  width: 36, height: 36, borderRadius: '50%', flexShrink: 0,
                  display: 'flex', alignItems: 'center', justifyContent: 'center',
                  fontSize: isDone ? 14 : 18,
                  background: isDone ? 'rgba(16,185,129,0.2)' : isActive ? 'rgba(99,102,241,0.2)' : 'var(--bg-input)',
                  border: isDone ? '2px solid rgba(16,185,129,0.5)' : isActive ? '2px solid rgba(99,102,241,0.6)' : '2px solid var(--border-subtle)',
                  boxShadow: isActive ? '0 0 16px rgba(99,102,241,0.4)' : 'none',
                  transition: 'all 0.4s ease',
                  animation: isActive ? 'pulse-ring 1.5s infinite' : 'none',
                }}>
                  {isDone ? '✓' : stage.icon}
                </div>
                <div style={{ flex: 1, paddingTop: 2 }}>
                  <div style={{
                    fontSize: 13.5, fontWeight: 700,
                    color: isDone ? 'var(--accent-emerald)' : isActive ? 'var(--text-primary)' : 'var(--text-muted)',
                    marginBottom: 3, transition: 'color 0.4s',
                  }}>
                    {stage.label}
                  </div>
                  {(isActive || isDone) && (
                    <div style={{ fontSize: 11.5, color: isDone ? 'var(--text-muted)' : 'var(--text-secondary)', lineHeight: 1.4 }}>
                      {isDone ? '✓ Complete' : stage.desc}
                    </div>
                  )}
                </div>
                <div style={{ flexShrink: 0, paddingTop: 4 }}>
                  {isDone && (
                    <span style={{ fontSize: 10, padding: '2px 8px', borderRadius: 10, fontWeight: 700, background: 'rgba(16,185,129,0.15)', color: 'var(--accent-emerald)', border: '1px solid rgba(16,185,129,0.3)' }}>Done</span>
                  )}
                  {isActive && (
                    <span style={{ fontSize: 10, padding: '2px 8px', borderRadius: 10, fontWeight: 700, background: 'rgba(99,102,241,0.15)', color: 'var(--accent-primary)', border: '1px solid rgba(99,102,241,0.3)', display: 'flex', alignItems: 'center', gap: 5 }}>
                      <span style={{ width: 6, height: 6, borderRadius: '50%', background: 'var(--accent-primary)', animation: 'blink 1s infinite', display: 'inline-block' }} />
                      Running
                    </span>
                  )}
                </div>
              </div>
            );
          })}
        </div>
      </div>

      {/* Thinking message */}
      <div style={{ textAlign: 'center', padding: '14px 20px', background: 'rgba(99,102,241,0.06)', border: '1px solid rgba(99,102,241,0.2)', borderRadius: 10 }}>
        <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'center', gap: 10 }}>
          <div className="spinner" style={{ width: 14, height: 14, borderWidth: 2 }} />
          <span style={{ fontSize: 12.5, color: 'var(--accent-primary)', fontWeight: 500 }}>
            {THINKING_MESSAGES[msgIdx]}
          </span>
        </div>
        <div style={{ fontSize: 11, color: 'var(--text-muted)', marginTop: 6 }}>
          Results will appear automatically — this typically takes 15–45 seconds
        </div>
      </div>

      <style>{`
        @keyframes spin { from { transform: rotate(0deg); } to { transform: rotate(360deg); } }
        @keyframes pulse-ring {
          0%   { box-shadow: 0 0 0 0 rgba(99,102,241,0.5); }
          70%  { box-shadow: 0 0 0 8px rgba(99,102,241,0); }
          100% { box-shadow: 0 0 0 0 rgba(99,102,241,0); }
        }
        @keyframes blink { 0%, 100% { opacity: 1; } 50% { opacity: 0.3; } }
      `}</style>
    </div>
  );
}

/* ── Step Row ─────────────────────────────────────────────────────── */
function StepRow({ step }) {
  const isOk = step.success;
  const label = step.step === "plugin_execution"
    ? `🧩 ${step.agent || "Plugin"} Pipeline`
    : (step.step || step.agent);
  return (
    <div style={{ display: "flex", alignItems: "center", gap: 10, padding: "8px 0", borderBottom: "1px solid var(--border-subtle)" }}>
      <div style={{
        width: 22, height: 22, borderRadius: "50%", flexShrink: 0,
        background: isOk ? "rgba(16,185,129,0.18)" : "rgba(244,63,94,0.18)",
        color: isOk ? "var(--accent-emerald)" : "var(--accent-rose)",
        display: "flex", alignItems: "center", justifyContent: "center",
        fontSize: 11, fontWeight: 700
      }}>{isOk ? "✓" : "✗"}</div>
      <div style={{ flex: 1, fontSize: 12.5, color: "var(--text-secondary)", fontWeight: 500 }}>{label}</div>
      <div style={{ fontSize: 10.5, color: "var(--text-muted)" }}>
        {step.confidence != null ? `${Math.round(step.confidence * 100)}%` : ""}
      </div>
      <div style={{ fontSize: 10, color: "var(--text-muted)" }}>
        {step.timestamp ? new Date(step.timestamp).toLocaleTimeString() : ""}
      </div>
    </div>
  );
}

/* ── Main Results Page ────────────────────────────────────────────── */
export default function Results() {
  const location = useLocation();
  const navigate = useNavigate();
  const { workflowId } = useParams();
  const [result, setResult] = useState(location.state?.workflow || null);
  const [fetchError, setFetchError] = useState(false);
  const userRequest = location.state?.userRequest || result?.user_request || '';

  useEffect(() => {
    if (!workflowId || workflowId === 'None' || workflowId === 'undefined') {
      setFetchError(true);
      return;
    }
    const terminalStatuses = ['completed', 'failed', 'error'];
    if (result && terminalStatuses.includes(result.status)) {
      return;
    }
    let stopped = false;
    const poll = async () => {
      try {
        const r = await axios.get(`/api/workflow/${workflowId}`);
        if (!stopped) {
          setResult(r.data);
          if (!terminalStatuses.includes(r.data?.status)) {
            setTimeout(poll, 3000);
          }
        }
      } catch {
        if (!stopped) setFetchError(true);
      }
    };
    poll();
    return () => { stopped = true; };
  }, [workflowId]);

  const isRunning = !fetchError && (!result || !['completed', 'failed', 'error'].includes(result?.status));

  if (isRunning) {
    return <PipelineLoader userRequest={userRequest} />;
  }

  if (!result || fetchError) {
    return (
      <div className="fade-in" style={{ textAlign: "center", padding: 60 }}>
        <div style={{ fontSize: 40, marginBottom: 12 }}>📭</div>
        <div style={{ color: "var(--text-muted)", marginBottom: 20 }}>No result to display.</div>
        <button className="btn-primary" onClick={() => navigate("/dashboard")}>← Back to Dashboard</button>
      </div>
    );
  }

  const reportStep = result.steps?.find(s => s.step === "ReportGenerator" || s.agent === "ReportGenerator");
  const reportSummary = reportStep?.data?.report?.summary;
  const pluginStep = result.steps?.find(s => s.step === "plugin_execution");
  const pd = pluginStep?.data || null;
  const isHR = pd?.plugin === "hr_recruitment" || (pd?.shortlist?.length > 0);
  const isB2B = pd?.plugin === "b2b_sales" || (pd?.qualified_companies?.length > 0 || pd?.prospect_list?.length > 0 || pd?.prospects?.length > 0);
  const isFailed = result.status === "failed" || result.status === "error";
  const failErrors = result.errors?.filter(e => e) || [];
  const isQuotaError = failErrors.some(e => typeof e === 'string' && (e.includes('429') || e.toLowerCase().includes('quota')));
  const firstStepError = result.steps?.find(s => !s.success)?.error || '';
  const isStepQuotaError = typeof firstStepError === 'string' && (firstStepError.includes('429') || firstStepError.toLowerCase().includes('quota'));

  const downloadReportTxt = () => {
    if (!reportSummary) return;
    const blob = new Blob([reportSummary], { type: 'text/plain;charset=utf-8' });
    const url = URL.createObjectURL(blob);
    const link = document.createElement('a');
    link.href = url;
    link.download = `Report_${workflowId || 'summary'}.txt`;
    link.click();
    URL.revokeObjectURL(url);
  };

  const exportCRM = () => {
    const prospects = pd?.prospect_list || pd?.qualified_companies || pd?.prospects || [];
    if (!prospects.length && !isHR) { alert("No prospects available to export."); return; }
    let csvContent = "";
    if (isHR) {
      const candidates = pd?.shortlist || [];
      csvContent += "Name,Role,Experience (Years),Match Score,Skills,Location,Availability\n";
      candidates.forEach(c => {
        csvContent += `"${c.name || ''}","${c.role || ''}","${c.experience_years || ''}","${Math.round((c.match_score || 0)*100)}%","${(c.skills || []).join('; ')}","${c.location || ''}","${c.availability || ''}"\n`;
      });
    } else {
      csvContent += "Rank,Name,Sector,Employees,Org Type,Match Score,Contact Name,Contact Title,Contact Email,Reason\n";
      prospects.forEach((p, i) => {
        const name = p.company?.name || p.company_name || p.name || '';
        const sector = p.company?.sector || p.sector || '';
        const score = p.company?.icp_score || p.icp_score || 0;
        const orgType = p.company?.org_type || p.org_type || p.company?.funding_stage || p.funding_stage || '';
        const emp = p.company?.employee_count || p.employee_count || '';
        const contact = p.primary_contact || {};
        const reason = p.matching_reason || p.company?.matching_reason || '';
        csvContent += `"${p.rank || i + 1}","${name}","${sector}","${emp}","${orgType}","${Math.round(score * 100)}%","${contact.name || ''}","${contact.title || ''}","${contact.email || ''}","${reason.replace(/"/g, '""')}"\n`;
      });
    }
    const blob = new Blob([csvContent], { type: 'text/csv;charset=utf-8' });
    const url = URL.createObjectURL(blob);
    const link = document.createElement('a');
    link.href = url;
    link.download = `${isHR ? 'Candidates' : 'Prospects'}_${workflowId || 'leads'}.csv`;
    link.click();
    URL.revokeObjectURL(url);
  };

  return (
    <div className="fade-in">
      {/* Header */}
      <div className="page-header" style={{ marginBottom: 28 }}>
        <div>
          <h1 className="page-title">Workflow Results</h1>
          <p style={{ color: "var(--text-muted)", fontSize: 13, marginTop: 4 }}>
            {result.user_request?.slice(0, 90)}{result.user_request?.length > 90 ? "..." : ""}
          </p>
        </div>
        <div style={{ display: "flex", gap: 10, alignItems: "center" }}>
          <span className={`badge ${result.status === "completed" ? "badge-success" : "badge-error"}`} style={{ padding: "5px 14px" }}>
            {result.status}
          </span>
          <button className="btn-secondary" onClick={() => navigate("/dashboard")} style={{ padding: "8px 16px", fontSize: 13 }}>
            ← New Workflow
          </button>
        </div>
      </div>

      {/* Meta strip */}
      <div style={{ display: "grid", gridTemplateColumns: "repeat(4,1fr)", gap: 14, marginBottom: 28 }}>
        {[
          ["🆔 Workflow ID", result.workflow_id?.slice(0, 12) + "..."],
          ["⏱ Duration", result.execution_time || "-"],
          ["📋 Steps", result.steps?.length ?? 0],
          ["⚠️ Errors", result.errors?.length ?? 0],
        ].map(([label, val]) => (
          <div key={label} style={{ background: "var(--bg-card)", borderRadius: 10, padding: "14px 16px", border: "1px solid var(--border-subtle)", boxShadow: "var(--shadow-card)" }}>
            <div style={{ fontSize: 10.5, color: "var(--text-muted)", marginBottom: 5, fontWeight: 600 }}>{label}</div>
            <div style={{ fontSize: 15, fontWeight: 700, color: "var(--text-primary)" }}>{val}</div>
          </div>
        ))}
      </div>

      {/* Failed banner */}
      {isFailed && (
        <div className="fade-in" style={{ marginBottom: 28, padding: "20px 24px", borderRadius: 14, background: "linear-gradient(135deg, rgba(244,63,94,0.12), rgba(220,38,38,0.08))", border: "1px solid rgba(244,63,94,0.35)" }}>
          <div style={{ display: "flex", alignItems: "center", gap: 12, marginBottom: 10 }}>
            <span style={{ fontSize: 24 }}>⚠️</span>
            <div style={{ fontSize: 15, fontWeight: 700, color: "#f43f5e" }}>
              {(isQuotaError || isStepQuotaError) ? "AI Quota Limit Reached" : "Workflow Failed"}
            </div>
          </div>
          <div style={{ fontSize: 13, color: "var(--text-secondary)", lineHeight: 1.65 }}>
            {(isQuotaError || isStepQuotaError)
              ? "The Gemini AI free-tier daily quota has been exhausted. Please try again later (quota resets daily), or add a paid API key in your .env file."
              : (failErrors[0] || firstStepError || "An unexpected error occurred during workflow execution.")}
          </div>
          <button className="btn-primary" onClick={() => navigate("/dashboard")} style={{ marginTop: 16, padding: "9px 20px", fontSize: 13 }}>← Try Again</button>
        </div>
      )}

      {/* HITL Banner */}
      {result.hitl_status === "pending" && (
        <div className="fade-in" style={{ marginBottom: 28, padding: "18px 24px", borderRadius: 14, background: "linear-gradient(135deg, rgba(251,191,36,0.12), rgba(245,158,11,0.08))", border: "1px solid rgba(251,191,36,0.4)", display: "flex", alignItems: "center", justifyContent: "space-between", gap: 16 }}>
          <div style={{ display: "flex", alignItems: "center", gap: 14 }}>
            <span style={{ fontSize: 26 }}>✋</span>
            <div>
              <div style={{ fontSize: 15, fontWeight: 700, color: "#fbbf24" }}>Human Approval Required</div>
              <div style={{ fontSize: 12.5, color: "var(--text-muted)", marginTop: 3 }}>
                {result.hitl_message || "The plugin has completed its analysis. Please review and approve the results."}
              </div>
            </div>
          </div>
          <button className="btn-primary" onClick={() => navigate("/approvals")} style={{ background: "linear-gradient(135deg, #fbbf24, #f59e0b)", color: "#000", border: "none", whiteSpace: "nowrap" }}>
            Go to Approvals →
          </button>
        </div>
      )}

      {/* Final Report */}
      {reportSummary && (
        <div className="glass-card fade-in" style={{ padding: 32, marginBottom: 28, border: "1px solid rgba(99,102,241,0.25)", background: "rgba(99,102,241,0.04)", boxShadow: "var(--shadow-glow), var(--shadow-card)" }}>
          <div style={{ display: "flex", alignItems: "center", justifyContent: "space-between", marginBottom: 20, flexWrap: "wrap", gap: 10 }}>
            <h2 style={{ fontSize: 17, fontWeight: 800, color: "var(--text-primary)" }}>🎯 Final Output Report</h2>
            <div style={{ display: "flex", gap: 8, alignItems: "center" }}>
              <button onClick={downloadReportTxt} className="btn-secondary" style={{ padding: "6px 12px", fontSize: 11.5, fontWeight: 600, display: "flex", alignItems: "center", gap: 5 }}>
                📥 Download (TXT)
              </button>
              {(isB2B || isHR) && (
                <button onClick={exportCRM} className="btn-secondary" style={{ padding: "6px 12px", fontSize: 11.5, fontWeight: 600, borderColor: "var(--accent-primary)", color: "var(--accent-primary)", display: "flex", alignItems: "center", gap: 5 }}>
                  📊 Export CSV (CRM)
                </button>
              )}
              <span style={{ fontSize: 11, color: "var(--text-muted)", padding: "3px 10px", borderRadius: 6, background: "var(--bg-input)", border: "1px solid var(--border-subtle)" }}>
                {reportStep?.data?.report?.metadata?.plugin_active ? "🧩 Active Plugin Mode" : "🤖 AI Advisory Mode"}
              </span>
            </div>
          </div>
          {reportStep?.data?.report?.metadata?.llm_active === false && (
            <div style={{ display: "flex", alignItems: "flex-start", gap: 10, background: "rgba(251,191,36,0.1)", border: "1px solid rgba(251,191,36,0.35)", borderRadius: 10, padding: "12px 16px", marginBottom: 18 }}>
              <span style={{ fontSize: 18, flexShrink: 0 }}>⚠️</span>
              <div>
                <div style={{ fontSize: 13, fontWeight: 700, color: "#fbbf24", marginBottom: 3 }}>Running on Local Fallback Mode</div>
                <div style={{ fontSize: 12, color: "var(--text-muted)", lineHeight: 1.5 }}>
                  The Gemini AI quota has been exhausted for today. Results are generated using local heuristics. Full AI analysis resumes once the daily quota resets.
                </div>
              </div>
            </div>
          )}
          <div style={{ fontSize: 14, color: "var(--text-primary)", lineHeight: 1.75, whiteSpace: "pre-wrap", fontFamily: "system-ui", padding: "22px 26px", background: "rgba(0,0,0,0.18)", borderRadius: 12, border: "1px solid var(--border-subtle)" }}>
            {reportSummary}
          </div>
          {reportStep?.data?.report?.metadata && (
            <div style={{ display: "flex", gap: 18, marginTop: 14, fontSize: 11.5, color: "var(--text-muted)" }}>
              <span>⏱ Duration: <strong>{reportStep.data.report.metadata.execution_time || "-"}</strong></span>
              <span>• Workflow ID: <strong>{result.workflow_id}</strong></span>
            </div>
          )}
        </div>
      )}

      {/* HR Candidate Cards */}
      {isHR && (() => {
        const shortlist = pd.shortlist || [];
        const total = pd.total_candidates || 0;
        if (!shortlist.length) return null;
        return (
          <div className="glass-card fade-in" style={{ padding: 32, marginBottom: 28, border: "1px solid rgba(16,185,129,0.25)", background: "rgba(16,185,129,0.03)" }}>
            <div style={{ display: "flex", alignItems: "center", justifyContent: "space-between", marginBottom: 22 }}>
              <h2 style={{ fontSize: 17, fontWeight: 800, color: "var(--text-primary)" }}>👥 Shortlisted Candidates</h2>
              <div style={{ display: "flex", gap: 10, alignItems: "center" }}>
                <span style={{ fontSize: 12, color: "var(--text-muted)" }}>{total} scanned</span>
                <span className="badge badge-success">{shortlist.length} Shortlisted</span>
              </div>
            </div>
            <div style={{ display: "grid", gridTemplateColumns: "repeat(auto-fill, minmax(300px, 1fr))", gap: 18 }}>
              {shortlist.map((c, i) => (
                <div key={i} style={{ background: "var(--bg-card)", borderRadius: 14, padding: "22px 24px", border: "1px solid var(--border-subtle)", boxShadow: "var(--shadow-card)", transition: "all 0.2s" }}
                  onMouseEnter={e => { e.currentTarget.style.transform = "translateY(-3px)"; e.currentTarget.style.boxShadow = "var(--shadow-glow), var(--shadow-card)"; }}
                  onMouseLeave={e => { e.currentTarget.style.transform = "translateY(0)"; e.currentTarget.style.boxShadow = "var(--shadow-card)"; }}>
                  <div style={{ display: "flex", alignItems: "center", gap: 14, marginBottom: 14 }}>
                    <div style={{ width: 48, height: 48, borderRadius: "50%", flexShrink: 0, background: `linear-gradient(135deg, hsl(${i * 80 + 190}, 65%, 55%), hsl(${i * 80 + 230}, 65%, 38%))`, display: "flex", alignItems: "center", justifyContent: "center", fontSize: 18, fontWeight: 800, color: "#fff" }}>{c.name?.charAt(0)}</div>
                    <div style={{ flex: 1 }}>
                      <div style={{ fontSize: 15, fontWeight: 700, color: "var(--text-primary)" }}>{c.name}</div>
                      <div style={{ fontSize: 12, color: "var(--text-muted)", marginTop: 2 }}>{c.role} · {c.experience_years}y exp</div>
                    </div>
                    <div style={{ fontSize: 17, fontWeight: 900, color: c.match_score >= 0.8 ? "var(--accent-emerald)" : "#fbbf24", background: c.match_score >= 0.8 ? "rgba(16,185,129,0.12)" : "rgba(251,191,36,0.12)", borderRadius: 10, padding: "5px 11px", border: `1px solid ${c.match_score >= 0.8 ? "rgba(16,185,129,0.3)" : "rgba(251,191,36,0.3)"}` }}>{Math.round((c.match_score || 0) * 100)}%</div>
                  </div>
                  <div style={{ display: "flex", flexWrap: "wrap", gap: 6, marginBottom: 14 }}>
                    {(c.skills || []).slice(0, 6).map((sk, j) => (
                      <span key={j} style={{ fontSize: 10.5, padding: "3px 8px", borderRadius: 6, background: "rgba(99,102,241,0.1)", color: "var(--accent-primary)", border: "1px solid rgba(99,102,241,0.2)", fontWeight: 600 }}>{sk}</span>
                    ))}
                  </div>
                  <div style={{ display: "flex", justifyContent: "space-between", fontSize: 11.5, color: "var(--text-muted)", paddingTop: 12, borderTop: "1px solid var(--border-subtle)" }}>
                    <span>📍 {c.location}</span><span>🕐 {c.availability}</span>
                  </div>
                </div>
              ))}
            </div>
          </div>
        );
      })()}

      {/* Prospect Cards (Generic / B2B) */}
      {isB2B && (() => {
        const prospects = pd.prospect_list || pd.qualified_companies || pd.prospects || [];
        if (!prospects.length) return null;
        return (
          <div className="glass-card fade-in" style={{ padding: 32, marginBottom: 28, border: "1px solid rgba(99,102,241,0.25)", background: "rgba(99,102,241,0.03)" }}>
            <div style={{ display: "flex", alignItems: "center", justifyContent: "space-between", marginBottom: 22 }}>
              <h2 style={{ fontSize: 17, fontWeight: 800, color: "var(--text-primary)" }}>📈 Qualified Prospects</h2>
              <span className="badge" style={{ background: "rgba(99,102,241,0.2)", color: "var(--accent-primary)", border: "1px solid rgba(99,102,241,0.3)" }}>{prospects.length} Found</span>
            </div>
            <div style={{ display: "grid", gridTemplateColumns: "repeat(auto-fill, minmax(310px, 1fr))", gap: 18 }}>
              {prospects.slice(0, 9).map((p, i) => {
                const name = p.company?.name || p.company_name || p.name;
                const sector = p.company?.sector || p.sector;
                const score = p.company?.icp_score || p.icp_score || 0;
                const orgType = p.company?.org_type || p.org_type || p.company?.funding_stage || p.funding_stage;
                const emp = p.company?.employee_count || p.employee_count;
                const contact = p.primary_contact || {};
                const reason = p.matching_reason || p.company?.matching_reason;
                return (
                  <div key={i} style={{ background: "var(--bg-card)", borderRadius: 14, padding: "22px 24px", border: "1px solid var(--border-subtle)", boxShadow: "var(--shadow-card)", transition: "all 0.2s" }}
                    onMouseEnter={e => { e.currentTarget.style.transform = "translateY(-3px)"; e.currentTarget.style.boxShadow = "var(--shadow-glow), var(--shadow-card)"; }}
                    onMouseLeave={e => { e.currentTarget.style.transform = "translateY(0)"; e.currentTarget.style.boxShadow = "var(--shadow-card)"; }}>
                    <div style={{ display: "flex", justifyContent: "space-between", alignItems: "flex-start", marginBottom: 10 }}>
                      <div style={{ fontSize: 15, fontWeight: 700, color: "var(--text-primary)" }}>#{p.rank || i + 1} {name}</div>
                      <span style={{ fontSize: 13, fontWeight: 800, padding: "4px 10px", borderRadius: 8, background: "rgba(99,102,241,0.15)", color: "var(--accent-primary)", border: "1px solid rgba(99,102,241,0.25)", flexShrink: 0, marginLeft: 8 }}>{Math.round(score * 100)}% match</span>
                    </div>
                    <div style={{ fontSize: 12, color: "var(--text-muted)", marginBottom: 12 }}>
                      {sector}{emp ? ` · ${emp}` : ''}{orgType ? ` · ${orgType}` : ''}
                    </div>
                    {contact.name && (
                      <div style={{ fontSize: 12, color: "var(--text-secondary)", padding: "9px 12px", background: "rgba(0,0,0,0.15)", borderRadius: 8, marginBottom: 10 }}>
                        👤 <strong>{contact.name}</strong> - {contact.title}<br />
                        <span style={{ fontSize: 11, color: "var(--text-muted)" }}>📧 {contact.email}</span>
                      </div>
                    )}
                    {reason && <div style={{ fontSize: 11, color: "var(--text-muted)", fontStyle: "italic" }}>💡 {reason}</div>}
                  </div>
                );
              })}
            </div>
          </div>
        );
      })()}

      {/* Execution Pipeline */}
      <div className="glass-card" style={{ padding: 24 }}>
        <h3 style={{ fontSize: 14, fontWeight: 700, color: "var(--text-primary)", marginBottom: 14 }}>🔄 Execution Pipeline</h3>
        {result.steps?.map((step, i) => <StepRow key={i} step={step} />)}
      </div>
    </div>
  );
}
