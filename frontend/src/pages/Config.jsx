import { useState, useEffect } from 'react';
import axios from 'axios';
import { getErrorMessage } from '../utils/errors';

const ORG_TYPE_SUGGESTIONS = [
  'Company', 'Hospital', 'College / University', 'Research Laboratory',
  'Manufacturing Plant', 'NGO / Non-Profit', 'Government Agency',
  'Retail Chain', 'Hotel / Hospitality', 'Clinic / Healthcare Center',
  'School / EdTech', 'Startup', 'Enterprise', 'Factory'
];

const TRIGGER_SUGGESTIONS = [
  'expansion', 'procurement', 'new_project', 'funding', 'hiring',
  'sustainability_mandate', 'equipment_upgrade', 'campus_expansion',
  'digital_transformation', 'infrastructure_upgrade', 'product_launch',
  'regulatory_compliance'
];

const SENIORITIES = ['C-Level', 'VP', 'Director', 'Manager', 'Staff'];
const DEPARTMENTS = ['Operations', 'Engineering', 'HR', 'Leadership', 'Product', 'Sales', 'Procurement', 'Administration', 'Finance', 'Clinical', 'Facilities'];
const SIZE_UNITS = ['employees', 'students', 'beds', 'sq ft', 'staff', 'researchers'];
const SIGNAL_LEVELS = ['low', 'medium', 'high'];

function Tag({ label, active, onClick }) {
  return (
    <button
      type="button"
      onClick={onClick}
      style={{
        padding: '4px 12px', borderRadius: 20, fontSize: 12, fontWeight: 600,
        cursor: 'pointer', transition: 'all 0.15s', fontFamily: 'Inter, sans-serif',
        background: active ? 'rgba(99,102,241,0.2)' : 'var(--bg-input)',
        color: active ? 'var(--accent-primary)' : 'var(--text-muted)',
        border: `1px solid ${active ? 'rgba(99,102,241,0.4)' : 'var(--border-subtle)'}`,
      }}
    >
      {active ? '✓ ' : ''}{label}
    </button>
  );
}

function Section({ title, subtitle, children }) {
  return (
    <div style={{ marginBottom: 24 }}>
      <div style={{ marginBottom: 10 }}>
        <h3 style={{ fontSize: 13, fontWeight: 700, color: 'var(--text-primary)', marginBottom: 2 }}>
          {title}
        </h3>
        {subtitle && <p style={{ fontSize: 11, color: 'var(--text-muted)', margin: 0 }}>{subtitle}</p>}
      </div>
      <div style={{ borderBottom: '1px solid var(--border-subtle)', marginBottom: 12 }} />
      {children}
    </div>
  );
}

const DEFAULT_CONFIG = {
  icp: {
    organization_types: ['Company', 'Hospital', 'College / University'],
    target_geographies: ['India'],
    target_keywords: [],
    business_triggers: ['expansion', 'procurement', 'new_project'],
    min_signal_strength: 'medium',
    min_match_score: 0.6,
    size_min: '',
    size_max: '',
    size_unit: 'employees',
  },
  personas: [
    { role: 'Facility Manager', seniority: 'Manager', department: 'Operations', priority: 1 }
  ]
};

export default function Config() {
  const [config, setConfig] = useState(null);
  const [saving, setSaving] = useState(false);
  const [saved, setSaved] = useState(false);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [newPersona, setNewPersona] = useState({ role: '', seniority: 'Manager', department: 'Operations' });

  const fetchConfig = () => {
    setLoading(true);
    setError(null);
    const token = localStorage.getItem('token');
    axios.get('/api/config/', {
      headers: token ? { Authorization: `Bearer ${token}` } : {},
    }).then(r => {
      // Migrate old SaaS configs to new generic format
      const raw = r.data;
      const icp = raw.icp || {};
      const merged = {
        ...DEFAULT_CONFIG.icp,
        ...icp,
        // Map legacy fields to new generic ones if missing
        organization_types: icp.organization_types || (icp.sectors ? icp.sectors : DEFAULT_CONFIG.icp.organization_types),
        target_geographies: icp.target_geographies || icp.geographies || DEFAULT_CONFIG.icp.target_geographies,
        target_keywords: icp.target_keywords || icp.preferred_tech || [],
        business_triggers: icp.business_triggers || icp.trigger_types || DEFAULT_CONFIG.icp.business_triggers,
        min_match_score: icp.min_match_score || icp.min_icp_score || 0.6,
        size_min: icp.size_min || (icp.min_employees ? String(icp.min_employees) : ''),
        size_max: icp.size_max || (icp.max_employees ? String(icp.max_employees) : ''),
        size_unit: icp.size_unit || 'employees',
      };
      setConfig({ icp: merged, personas: raw.personas || DEFAULT_CONFIG.personas });
      setLoading(false);
    }).catch((err) => {
      setConfig(DEFAULT_CONFIG);
      setError(getErrorMessage(err, 'Could not load saved config. Using defaults.'));
      setLoading(false);
    });
  };

  useEffect(() => { fetchConfig(); }, []);

  const updateICP = (key, val) => setConfig(c => ({ ...c, icp: { ...c.icp, [key]: val } }));

  const toggleOrgType = (val) => {
    const arr = config?.icp?.organization_types || [];
    updateICP('organization_types', arr.includes(val) ? arr.filter(x => x !== val) : [...arr, val]);
  };

  const toggleTrigger = (val) => {
    const arr = config?.icp?.business_triggers || [];
    updateICP('business_triggers', arr.includes(val) ? arr.filter(x => x !== val) : [...arr, val]);
  };

  const handleAddPersona = () => {
    if (!newPersona.role.trim()) return;
    setConfig(c => ({
      ...c,
      personas: [...c.personas, { ...newPersona, priority: c.personas.length + 1 }]
    }));
    setNewPersona({ role: '', seniority: 'Manager', department: 'Operations' });
  };

  const handleSave = async (e) => {
    e.preventDefault();
    setSaving(true);
    try {
      const token = localStorage.getItem('token');
      await axios.post('/api/config/', config, {
        headers: token ? { Authorization: `Bearer ${token}` } : {}
      });
      setSaved(true);
      setTimeout(() => setSaved(false), 3000);
    } catch (err) {
      alert(getErrorMessage(err, 'Save failed'));
    } finally {
      setSaving(false);
    }
  };

  if (loading) return (
    <div style={{ textAlign: 'center', padding: 80 }}>
      <div className="spinner" style={{ margin: '0 auto 16px' }} />
      <div style={{ color: 'var(--text-muted)' }}>Loading configuration...</div>
    </div>
  );

  const icp = config?.icp || DEFAULT_CONFIG.icp;
  const personas = config?.personas || [];

  return (
    <div className="fade-in">
      <div className="page-header">
        <div>
          <h1 className="page-title">⚙️ Platform Configuration</h1>
          <p className="page-subtitle">Configure your universal discovery settings — works for any business domain</p>
        </div>
        {saved && (
          <div style={{
            padding: '8px 16px', borderRadius: 8, fontSize: 13, fontWeight: 600,
            background: 'rgba(16,185,129,0.15)', color: 'var(--accent-emerald)',
            border: '1px solid rgba(16,185,129,0.3)', alignSelf: 'center',
          }}>
            ✅ Configuration saved!
          </div>
        )}
        {error && (
          <div style={{
            padding: '8px 16px', borderRadius: 8, fontSize: 12,
            background: 'rgba(245,158,11,0.1)', color: '#f59e0b',
            border: '1px solid rgba(245,158,11,0.3)', alignSelf: 'center', maxWidth: 300
          }}>
            ⚠️ {error}
          </div>
        )}
      </div>

      <form onSubmit={handleSave}>
        <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: 24 }}>

          {/* ── LEFT: Target Profile ── */}
          <div className="glass-card" style={{ padding: 28 }}>
            <h2 style={{ fontSize: 16, fontWeight: 700, color: 'var(--text-primary)', marginBottom: 24 }}>
              🎯 Target Profile
            </h2>

            <Section
              title="Target Organization Types"
              subtitle="Select all organization types you want to discover"
            >
              <div style={{ display: 'flex', flexWrap: 'wrap', gap: 6 }}>
                {ORG_TYPE_SUGGESTIONS.map(s => (
                  <Tag key={s} label={s}
                    active={(icp.organization_types || []).includes(s)}
                    onClick={() => toggleOrgType(s)} />
                ))}
              </div>
              <input
                className="form-input"
                style={{ marginTop: 10 }}
                placeholder="Add custom type (press Enter)"
                onKeyDown={e => {
                  if (e.key === 'Enter') {
                    e.preventDefault();
                    const val = e.target.value.trim();
                    if (val) { toggleOrgType(val); e.target.value = ''; }
                  }
                }}
              />
            </Section>

            <Section
              title="Target Geographies"
              subtitle="Countries, states, or cities to focus on"
            >
              <input
                className="form-input"
                value={(icp.target_geographies || []).join(', ')}
                onChange={e => updateICP('target_geographies', e.target.value.split(',').map(g => g.trim()).filter(Boolean))}
                placeholder="India, Mumbai, Maharashtra, USA..."
              />
            </Section>

            <Section
              title="Target Keywords"
              subtitle="Domain-specific keywords to identify prospects (comma-separated)"
            >
              <input
                className="form-input"
                value={(icp.target_keywords || []).join(', ')}
                onChange={e => updateICP('target_keywords', e.target.value.split(',').map(t => t.trim()).filter(Boolean))}
                placeholder="e.g. Solar Panel, EHR System, Industrial Automation, Recruitment Software..."
              />
              <div style={{ fontSize: 11, color: 'var(--text-muted)', marginTop: 4 }}>
                Higher overlap with prospect context = higher match score.
              </div>
            </Section>

            <Section
              title="Size Range"
              subtitle="Set target organization size (use the unit that fits your domain)"
            >
              <div style={{ display: 'flex', gap: 10, alignItems: 'center', flexWrap: 'wrap' }}>
                <div style={{ flex: 1, minWidth: 80 }}>
                  <label className="form-label">Min</label>
                  <input
                    type="text"
                    className="form-input"
                    value={icp.size_min || ''}
                    onChange={e => updateICP('size_min', e.target.value)}
                    placeholder="100"
                  />
                </div>
                <div style={{ marginTop: 20, color: 'var(--text-muted)' }}>–</div>
                <div style={{ flex: 1, minWidth: 80 }}>
                  <label className="form-label">Max</label>
                  <input
                    type="text"
                    className="form-input"
                    value={icp.size_max || ''}
                    onChange={e => updateICP('size_max', e.target.value)}
                    placeholder="10000"
                  />
                </div>
                <div style={{ flex: 1, minWidth: 100 }}>
                  <label className="form-label">Unit</label>
                  <select
                    className="form-input"
                    value={icp.size_unit || 'employees'}
                    onChange={e => updateICP('size_unit', e.target.value)}
                  >
                    {SIZE_UNITS.map(u => <option key={u} value={u}>{u}</option>)}
                  </select>
                </div>
              </div>
            </Section>

            <Section
              title="Minimum Match Score (0% – 100%)"
              subtitle="Only surface prospects that meet this threshold"
            >
              <div style={{ display: 'flex', alignItems: 'center', gap: 12 }}>
                <input
                  type="range" min="0" max="1" step="0.05"
                  value={icp.min_match_score || 0.6}
                  onChange={e => updateICP('min_match_score', parseFloat(e.target.value))}
                  style={{ flex: 1 }}
                />
                <span style={{
                  minWidth: 40, textAlign: 'center', fontWeight: 700,
                  color: 'var(--accent-primary)', fontSize: 14
                }}>
                  {((icp.min_match_score || 0.6) * 100).toFixed(0)}%
                </span>
              </div>
            </Section>
          </div>

          {/* ── RIGHT: Triggers + Personas ── */}
          <div style={{ display: 'flex', flexDirection: 'column', gap: 24 }}>

            <div className="glass-card" style={{ padding: 28 }}>
              <h2 style={{ fontSize: 16, fontWeight: 700, color: 'var(--text-primary)', marginBottom: 24 }}>
                📡 Business Triggers
              </h2>

              <Section
                title="Active Trigger Signals"
                subtitle="What buying signals should we look for?"
              >
                <div style={{ display: 'flex', flexWrap: 'wrap', gap: 6 }}>
                  {TRIGGER_SUGGESTIONS.map(t => (
                    <Tag key={t} label={t.replace(/_/g, ' ')}
                      active={(icp.business_triggers || []).includes(t)}
                      onClick={() => toggleTrigger(t)} />
                  ))}
                </div>
                <input
                  className="form-input"
                  style={{ marginTop: 10 }}
                  placeholder="Add custom trigger (press Enter)"
                  onKeyDown={e => {
                    if (e.key === 'Enter') {
                      e.preventDefault();
                      const val = e.target.value.trim().replace(/ /g, '_');
                      if (val) { toggleTrigger(val); e.target.value = ''; }
                    }
                  }}
                />
              </Section>

              <Section
                title="Minimum Signal Strength"
                subtitle="How strong must a buying signal be to surface a prospect?"
              >
                <div style={{ display: 'flex', gap: 8 }}>
                  {SIGNAL_LEVELS.map(s => (
                    <Tag key={s} label={s.charAt(0).toUpperCase() + s.slice(1)}
                      active={(icp.min_signal_strength || 'medium') === s}
                      onClick={() => updateICP('min_signal_strength', s)} />
                  ))}
                </div>
              </Section>
            </div>

            <div className="glass-card" style={{ padding: 28 }}>
              <h2 style={{ fontSize: 16, fontWeight: 700, color: 'var(--text-primary)', marginBottom: 24 }}>
                👤 Target Personas
              </h2>
              <p style={{ fontSize: 12, color: 'var(--text-muted)', marginTop: -16, marginBottom: 16 }}>
                Decision makers to find at each prospect organization
              </p>

              {personas.map((p, i) => (
                <div key={i} style={{
                  background: 'var(--bg-input)', borderRadius: 8, padding: '10px 14px',
                  border: '1px solid var(--border-subtle)', marginBottom: 8,
                  display: 'flex', alignItems: 'center', justifyContent: 'space-between',
                }}>
                  <div>
                    <div style={{ fontSize: 13, fontWeight: 600, color: 'var(--text-primary)' }}>
                      #{p.priority} {p.role}
                    </div>
                    <div style={{ fontSize: 11, color: 'var(--text-muted)' }}>
                      {p.seniority} · {p.department}
                    </div>
                  </div>
                  <button
                    type="button"
                    onClick={() => setConfig(c => ({ ...c, personas: c.personas.filter((_, j) => j !== i) }))}
                    style={{ background: 'none', border: 'none', color: 'var(--text-muted)', cursor: 'pointer', fontSize: 18, padding: 4 }}
                  >
                    ×
                  </button>
                </div>
              ))}

              {/* Add Persona inline */}
              <div style={{
                background: 'rgba(99,102,241,0.04)', borderRadius: 8, padding: 14,
                border: '1px dashed rgba(99,102,241,0.3)', marginTop: 8
              }}>
                <div style={{ fontSize: 12, fontWeight: 600, color: 'var(--accent-primary)', marginBottom: 10 }}>
                  ➕ Add Persona
                </div>
                <div style={{ display: 'flex', gap: 8, flexWrap: 'wrap' }}>
                  <input
                    className="form-input"
                    style={{ flex: 2, minWidth: 120 }}
                    placeholder="Role (e.g. Facility Manager)"
                    value={newPersona.role}
                    onChange={e => setNewPersona(p => ({ ...p, role: e.target.value }))}
                  />
                  <select
                    className="form-input"
                    style={{ flex: 1, minWidth: 100 }}
                    value={newPersona.seniority}
                    onChange={e => setNewPersona(p => ({ ...p, seniority: e.target.value }))}
                  >
                    {SENIORITIES.map(s => <option key={s} value={s}>{s}</option>)}
                  </select>
                  <select
                    className="form-input"
                    style={{ flex: 1, minWidth: 110 }}
                    value={newPersona.department}
                    onChange={e => setNewPersona(p => ({ ...p, department: e.target.value }))}
                  >
                    {DEPARTMENTS.map(d => <option key={d} value={d}>{d}</option>)}
                  </select>
                  <button
                    type="button"
                    className="btn-primary"
                    onClick={handleAddPersona}
                    style={{ padding: '8px 16px', fontSize: 12 }}
                  >
                    Add
                  </button>
                </div>
              </div>
            </div>
          </div>
        </div>

        <div style={{ marginTop: 24, display: 'flex', justifyContent: 'flex-end' }}>
          <button
            id="save-config"
            type="submit"
            className="btn-primary"
            disabled={saving}
            style={{ padding: '12px 32px' }}
          >
            {saving ? <><div className="spinner" /> Saving...</> : '💾 Save Configuration'}
          </button>
        </div>
      </form>
    </div>
  );
}
