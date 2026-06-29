import { useState, useEffect } from 'react';
import axios from 'axios';
import { getErrorMessage } from '../utils/errors';

/* ── Status Badge ── */
function StatusBadge({ status }) {
  const map = {
    pending:  { bg: 'rgba(251,191,36,0.2)', color: '#fbbf24', border: 'rgba(251,191,36,0.4)', label: '⏳ Pending' },
    approved: { bg: 'rgba(16,185,129,0.2)', color: 'var(--accent-emerald)', border: 'rgba(16,185,129,0.4)', label: '✅ Approved' },
    rejected: { bg: 'rgba(244,63,94,0.2)',  color: 'var(--accent-rose)', border: 'rgba(244,63,94,0.4)', label: '❌ Rejected' },
  };
  const s = map[status] || map.pending;
  return (
    <span style={{
      padding: '3px 10px', borderRadius: 12, fontSize: 11, fontWeight: 700,
      background: s.bg, color: s.color, border: `1px solid ${s.border}`,
    }}>
      {s.label}
    </span>
  );
}

/* ── Main Approvals Page ── */
export default function Approvals() {
  const [approvals, setApprovals] = useState([]);
  const [loading, setLoading] = useState(true);
  const [actionLoading, setActionLoading] = useState(null);
  const [notes, setNotes] = useState({});
  const [filter, setFilter] = useState('all');

  // Track status of individual items: { [workflowId]: { [itemId]: 'approved' | 'rejected' } }
  const [itemStatuses, setItemStatuses] = useState({});
  // Track rejection reasons: { [workflowId]: { [itemId]: 'reason text' } }
  const [rejectionReasons, setRejectionReasons] = useState({});

  const fetchApprovals = async () => {
    try {
      const token = localStorage.getItem('token');
      const { data } = await axios.get('/api/hitl/', {
        headers: token ? { Authorization: `Bearer ${token}` } : {},
      });
      setApprovals(data);

      // Initialize selection states for pending items
      const initialStatuses = {};
      const initialReasons = {};
      data.forEach(app => {
        if (app.status === 'pending') {
          initialStatuses[app.workflow_id] = {};
          initialReasons[app.workflow_id] = {};
          const items = app.review_items || [];
          items.forEach(item => {
            const itemId = item.company?.name || item.id || item.name;
            initialStatuses[app.workflow_id][itemId] = 'approved'; // Default to approved
          });
        }
      });
      setItemStatuses(initialStatuses);
      setRejectionReasons(initialReasons);
    } catch (e) {
      console.error(e);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => { fetchApprovals(); }, []);

  // Toggle single item status
  const toggleItemStatus = (workflowId, itemId, currentStatus) => {
    const nextStatus = currentStatus === 'approved' ? 'rejected' : 'approved';
    
    // If transitioning to rejected, prompt the user for a reason
    if (nextStatus === 'rejected') {
      const reason = window.prompt(`Why are you rejecting "${itemId}"? (Reason will be saved to database):`);
      if (reason === null) return; // Cancelled
      setRejectionReasons(prev => ({
        ...prev,
        [workflowId]: {
          ...prev[workflowId],
          [itemId]: reason || 'No feedback provided'
        }
      }));
    } else {
      // Clear reason if re-approved
      setRejectionReasons(prev => {
        const next = { ...prev };
        if (next[workflowId]) {
          delete next[workflowId][itemId];
        }
        return next;
      });
    }

    setItemStatuses(prev => ({
      ...prev,
      [workflowId]: {
        ...prev[workflowId],
        [itemId]: nextStatus
      }
    }));
  };

  // Bulk set all items
  const setAllItemsStatus = (workflowId, items, status) => {
    const nextStatuses = {};
    const nextReasons = { ...rejectionReasons[workflowId] };

    items.forEach(item => {
      const itemId = item.company?.name || item.id || item.name;
      nextStatuses[itemId] = status;
      if (status === 'rejected') {
        nextReasons[itemId] = 'Bulk rejected by reviewer';
      } else {
        delete nextReasons[itemId];
      }
    });

    setItemStatuses(prev => ({
      ...prev,
      [workflowId]: nextStatuses
    }));
    setRejectionReasons(prev => ({
      ...prev,
      [workflowId]: nextReasons
    }));
  };

  // Submit complete review notes + selection details
  const submitReview = async (workflowId, actionType, items) => {
    setActionLoading(workflowId + actionType);

    const statuses = itemStatuses[workflowId] || {};
    const reasons = rejectionReasons[workflowId] || {};

    // Filter approved and rejected lists
    const approved_item_ids = [];
    const rejected_items = [];

    items.forEach(item => {
      const itemId = item.company?.name || item.id || item.name;
      const status = statuses[itemId] || 'approved';
      if (status === 'approved') {
        approved_item_ids.push(itemId);
      } else {
        rejected_items.push({
          id: itemId,
          reason: reasons[itemId] || 'Rejected by reviewer'
        });
      }
    });

    // If all items were rejected, mark the overall action as "rejected"
    const overallAction = (actionType === 'reject' || approved_item_ids.length === 0) ? 'reject' : 'approve';

    try {
      const token = localStorage.getItem('token');
      await axios.post('/api/hitl/action', {
        workflow_id: workflowId,
        action: overallAction,
        notes: notes[workflowId] || null,
        approved_item_ids,
        rejected_items
      }, {
        headers: token ? { Authorization: `Bearer ${token}` } : {},
      });
      await fetchApprovals();
    } catch (e) {
      alert(getErrorMessage(e, 'Action failed'));
    } finally {
      setActionLoading(null);
    }
  };

  const filtered = filter === 'all' ? approvals : approvals.filter(a => a.status === filter);
  const pendingCount = approvals.filter(a => a.status === 'pending').length;

  return (
    <div className="fade-in">
      <div className="page-header">
        <div>
          <h1 className="page-title">
            ✋ Human-in-the-Loop Approvals
            {pendingCount > 0 && (
              <span style={{
                marginLeft: 10, fontSize: 13, padding: '2px 10px', borderRadius: 12,
                background: 'rgba(251,191,36,0.2)', color: '#fbbf24',
                border: '1px solid rgba(251,191,36,0.4)',
              }}>
                {pendingCount} pending
              </span>
            )}
          </h1>
          <p className="page-subtitle">
            Validate, filter, and approve prospect intelligence records before final outreach
          </p>
        </div>
        <button
          className="btn-secondary"
          onClick={fetchApprovals}
          style={{ alignSelf: 'center' }}
        >
          {"\ud83d\udd04"} Refresh
        </button>
      </div>

      {/* Filter tabs */}
      <div style={{ display: 'flex', gap: 8, marginBottom: 24 }}>
        {['all', 'pending', 'approved', 'rejected'].map(f => (
          <button
            key={f}
            onClick={() => setFilter(f)}
            style={{
              padding: '6px 16px', borderRadius: 8, fontSize: 12, fontWeight: 600,
              border: '1px solid',
              borderColor: filter === f ? 'var(--accent-primary)' : 'var(--border-subtle)',
              background: filter === f ? 'rgba(99,102,241,0.15)' : 'var(--bg-input)',
              color: filter === f ? 'var(--accent-primary)' : 'var(--text-muted)',
              cursor: 'pointer', transition: 'all 0.2s', fontFamily: 'Inter, sans-serif',
            }}
          >
            {f.charAt(0).toUpperCase() + f.slice(1)}
            {f === 'pending' && pendingCount > 0 && ` (${pendingCount})`}
          </button>
        ))}
      </div>

      {loading ? (
        <div style={{ textAlign: 'center', padding: 60, color: 'var(--text-muted)' }}>
          <div className="spinner" style={{ margin: '0 auto 16px' }} />
          Loading approvals...
        </div>
      ) : filtered.length === 0 ? (
        <div className="glass-card" style={{ padding: 60, textAlign: 'center' }}>
          <div style={{ fontSize: 40, marginBottom: 16 }}>🎉</div>
          <div style={{ fontSize: 15, color: 'var(--text-secondary)', fontWeight: 600 }}>
            {filter === 'pending' ? 'No pending approvals - all caught up!' : 'No approvals yet. Run a workflow to generate one.'}
          </div>
        </div>
      ) : (
        <div style={{ display: 'flex', flexDirection: 'column', gap: 20 }}>
          {filtered.map((approval, i) => {
            const items = approval.review_items || [];
            const isBizB = approval.review_type === 'b2b_prospects';
            const isPending = approval.status === 'pending';
            const statuses = itemStatuses[approval.workflow_id] || {};
            const reasons = rejectionReasons[approval.workflow_id] || {};

            return (
              <div key={i} className="glass-card" style={{ padding: 24 }}>
                {/* Header */}
                <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', marginBottom: 16 }}>
                  <div>
                    <div style={{ display: 'flex', alignItems: 'center', gap: 10, marginBottom: 4 }}>
                      <StatusBadge status={approval.status} />
                      <span style={{ fontSize: 11, color: 'var(--text-muted)' }}>
                        Workflow {approval.workflow_id?.slice(0, 8)}...
                      </span>
                    </div>
                    <div style={{ fontSize: 14, fontWeight: 600, color: 'var(--text-primary)', marginBottom: 4 }}>
                      {isBizB ? '🏢 B2B Prospect Selection' : '👥 Candidate Selection'}
                    </div>
                    <div style={{ fontSize: 12, color: 'var(--text-muted)', maxWidth: 500 }}>
                      "{approval.user_request}"
                    </div>
                  </div>
                  <div style={{ fontSize: 11, color: 'var(--text-muted)', textAlign: 'right' }}>
                    {new Date(approval.created_at).toLocaleString()}
                    {approval.approved_at && (
                      <div style={{ color: 'var(--accent-emerald)', marginTop: 4 }}>
                        Approved: {new Date(approval.approved_at).toLocaleString()}
                      </div>
                    )}
                    {approval.rejected_at && (
                      <div style={{ color: 'var(--accent-rose)', marginTop: 4 }}>
                        Rejected: {new Date(approval.rejected_at).toLocaleString()}
                      </div>
                    )}
                  </div>
                </div>

                {/* Bulk Actions (Pending only) */}
                {isPending && (
                  <div style={{ display: 'flex', gap: 10, marginBottom: 16 }}>
                    <button
                      className="btn-secondary"
                      onClick={() => setAllItemsStatus(approval.workflow_id, items, 'approved')}
                      style={{ fontSize: 11, padding: '4px 10px' }}
                    >
                      Select All
                    </button>
                    <button
                      className="btn-secondary"
                      onClick={() => setAllItemsStatus(approval.workflow_id, items, 'rejected')}
                      style={{ fontSize: 11, padding: '4px 10px', color: 'var(--accent-rose)', borderColor: 'rgba(244,63,94,0.2)' }}
                    >
                      Deselect All
                    </button>
                  </div>
                )}

                {/* List items to validate individually */}
                <div style={{ marginBottom: 16, maxHeight: 400, overflowY: 'auto' }}>
                  {items.map((item, j) => {
                    const itemId = isBizB ? item.company?.name || item.name : item.name;
                    const status = statuses[itemId] || 'approved';
                    const isRejected = status === 'rejected';

                    return (
                      <div
                        key={j}
                        style={{
                          background: isRejected ? 'rgba(244,63,94,0.02)' : 'var(--bg-input)',
                          borderRadius: 8, padding: '14px 16px',
                          border: isRejected ? '1px dashed rgba(244,63,94,0.25)' : '1px solid var(--border-subtle)',
                          marginBottom: 10,
                          display: 'flex', justifyContent: 'space-between', alignItems: 'center',
                          opacity: isRejected ? 0.65 : 1,
                          transition: 'all 0.2s'
                        }}
                      >
                        <div style={{ flex: 1, paddingRight: 16 }}>
                          <div style={{ display: 'flex', alignItems: 'center', gap: 10, marginBottom: 4 }}>
                            {isPending && (
                              <input
                                type="checkbox"
                                checked={!isRejected}
                                onChange={() => toggleItemStatus(approval.workflow_id, itemId, status)}
                                style={{ width: 16, height: 16, cursor: 'pointer', accentColor: 'var(--accent-primary)' }}
                              />
                            )}
                            <div style={{
                              fontSize: 13, fontWeight: 700,
                              textDecoration: isRejected ? 'line-through' : 'none',
                              color: isRejected ? 'var(--text-muted)' : 'var(--text-primary)'
                            }}>
                              {isBizB ? `#${item.rank || j + 1} ${itemId}` : item.name}
                            </div>
                          </div>

                          <div style={{ fontSize: 11.5, color: 'var(--text-secondary)', marginTop: 2, paddingLeft: isPending ? 26 : 0 }}>
                            {isBizB ? (
                              <>
                                {[
                                  item.company?.sector || item.sector,
                                  (item.company?.employee_count || item.employee_count) ? `${item.company?.employee_count || item.employee_count} emp` : null,
                                  item.company?.funding_stage || item.funding_stage,
                                  item.company?.hq || item.hq || item.company?.location || item.location
                                ].filter(Boolean).join(' · ')}
                                {item.primary_contact && (
                                  <div style={{ marginTop: 4, color: 'var(--text-muted)', fontSize: 11 }}>
                                    👤 {item.primary_contact.name} ({item.primary_contact.title}) · 📧 {item.primary_contact.email}
                                  </div>
                                )}
                              </>
                            ) : (
                              <>{item.role} · {item.experience_years}yr exp · {item.location} · {(item.skills || []).slice(0, 4).join(', ')}</>
                            )}
                          </div>

                          {/* Matching / AI Explanations */}
                          {!isRejected && (isBizB ? (item.matching_reason || item.company?.matching_reason) : (item.match_explanation || item.explanation)) && (
                            <div style={{
                              fontSize: 10.5, padding: '4px 8px', borderRadius: 4, marginTop: 8, marginLeft: isPending ? 26 : 0,
                              background: 'rgba(99,102,241,0.06)', color: 'var(--text-secondary)',
                              border: '1px solid rgba(99,102,241,0.15)',
                            }}>
                              💡 Reason: {isBizB ? (item.matching_reason || item.company?.matching_reason) : (item.match_explanation || item.explanation)}
                            </div>
                          )}

                          {/* Rejection Feedbacks */}
                          {isRejected && (
                            <div style={{
                              fontSize: 11, padding: '4px 8px', borderRadius: 4, marginTop: 8, marginLeft: isPending ? 26 : 0,
                              background: 'rgba(244,63,94,0.08)', color: 'var(--accent-rose)',
                              border: '1px solid rgba(244,63,94,0.15)',
                            }}>
                              🚫 Feedback: {reasons[itemId] || 'Excluded from execution'}
                            </div>
                          )}
                        </div>

                        {/* Fit Score Badge */}
                        <div style={{ textAlign: 'right', flexShrink: 0 }}>
                          <div style={{
                            fontSize: 12, fontWeight: 700, padding: '3px 8px', borderRadius: 6,
                            background: isRejected ? 'rgba(255,255,255,0.05)' : 'rgba(16,185,129,0.12)',
                            color: isRejected ? 'var(--text-muted)' : 'var(--accent-emerald)',
                          }}>
                            {isBizB 
                              ? `ICP ${Math.round((item.company?.icp_score || item.icp_score || 0) * 100)}%` 
                              : `Fit ${Math.round((item.match_score || 0) * 100)}%`}
                          </div>
                        </div>
                      </div>
                    );
                  })}
                </div>

                {/* Reviewer Action Buttons */}
                {isPending && (
                  <div>
                    <textarea
                      placeholder="Enter optional overview notes for this approval..."
                      value={notes[approval.workflow_id] || ''}
                      onChange={e => setNotes(n => ({ ...n, [approval.workflow_id]: e.target.value }))}
                      className="form-textarea"
                      rows={2}
                      style={{ marginBottom: 12, fontSize: 12 }}
                    />
                    <div style={{ display: 'flex', gap: 10 }}>
                      <button
                        className="btn-primary"
                        disabled={actionLoading === approval.workflow_id + 'approve'}
                        onClick={() => submitReview(approval.workflow_id, 'approve', items)}
                        style={{ flex: 2, justifyContent: 'center', padding: '10px 0' }}
                      >
                        {actionLoading === approval.workflow_id + 'approve'
                          ? <><div className="spinner" /> Syncing...</>
                          : '✅ Confirm Selection & Send Outreach'}
                      </button>
                      <button
                        onClick={() => submitReview(approval.workflow_id, 'reject', items)}
                        disabled={actionLoading === approval.workflow_id + 'reject'}
                        style={{
                          flex: 1, padding: '10px 0', borderRadius: 8, cursor: 'pointer',
                          fontWeight: 600, fontSize: 13, fontFamily: 'Inter, sans-serif',
                          background: 'rgba(244,63,94,0.15)', color: 'var(--accent-rose)',
                          border: '1px solid rgba(244,63,94,0.3)',
                        }}
                      >
                        ❌ Reject All
                      </button>
                    </div>
                  </div>
                )}

                {/* Resolved Review details (Audits) */}
                {!isPending && (
                  <div style={{ display: 'flex', flexDirection: 'column', gap: 8 }}>
                    {approval.reviewer_notes && (
                      <div style={{
                        padding: '8px 12px', borderRadius: 6, fontSize: 12,
                        background: 'var(--bg-input)', color: 'var(--text-secondary)',
                        border: '1px solid var(--border-subtle)',
                      }}>
                        💬 Notes: {approval.reviewer_notes}
                      </div>
                    )}
                    {approval.rejected_items && approval.rejected_items.length > 0 && (
                      <details style={{ cursor: 'pointer' }}>
                        <summary style={{ fontSize: 11, color: 'var(--accent-rose)', fontWeight: 600 }}>
                          🚫 View Rejection Feedback Logs ({approval.rejected_items.length})
                        </summary>
                        <div style={{ marginTop: 8, paddingLeft: 12 }}>
                          {approval.rejected_items.map((rej, k) => (
                            <div key={k} style={{ fontSize: 11.5, color: 'var(--text-muted)', marginBottom: 4 }}>
                              • <strong>{rej.id}</strong>: {rej.reason}
                            </div>
                          ))}
                        </div>
                      </details>
                    )}
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
