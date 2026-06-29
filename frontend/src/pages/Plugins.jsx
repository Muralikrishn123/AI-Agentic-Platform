import { useState, useEffect } from 'react';
import axios from 'axios';
import { getErrorMessage } from '../utils/errors';

const PLUGIN_META = {
  hr_recruitment: {
    icon: '👥',
    color: 'var(--accent-primary)',
    fullName: 'HR Recruitment',
    category: 'Human Resources',
    description: 'Automates the full recruitment workflow from job description to candidate shortlist using Gemini AI.',
    stage: 'C Iteration 2',
    agents: [
      { name: 'RequirementExtractionAgent', desc: 'Extracts structured job requirements using Gemini AI' },
      { name: 'CandidateMatchExplanationAgent', desc: 'Generates AI explanations for candidate match scores' },
      { name: 'CandidateSearchAgent', desc: 'Searches candidate database' },
      { name: 'CandidateMatchingAgent', desc: 'Matches candidates to requirements' },
      { name: 'CandidateScoringAgent', desc: 'Scores candidate fit' },
      { name: 'CandidateShortlistingAgent', desc: 'Generates shortlist' },
    ]
  },
  b2b_sales: {
    icon: '📈',
    color: 'var(--accent-cyan)',
    fullName: 'B2B Sales Intelligence',
    category: 'Sales & Revenue',
    description: 'Identifies high-value B2B prospects using trigger monitoring, ICP matching, company enrichment, and contact discovery.',
    stage: 'C - 6 Agents',
    agents: [
      { name: 'TriggerMonitorAgent', desc: 'Monitors funding, hiring, and growth trigger signals' },
      { name: 'ICPMatcherAgent', desc: 'Matches companies against your Ideal Customer Profile' },
      { name: 'CompanyEnricherAgent', desc: 'Enriches company data with sector, size, funding info' },
      { name: 'DecisionMakerFinderAgent', desc: 'Discovers key decision-makers and their roles' },
      { name: 'ContactEnricherAgent', desc: 'Finds and validates contact email / LinkedIn info' },
      { name: 'ProspectSummaryAgent', desc: 'Produces a ranked prospect list with outreach rationale' },
    ]
  }
};

function PluginCard({ name, meta, capabilities, enabled, onDelete, onToggle }) {
  const [expanded, setExpanded] = useState(false);
  const [toggling, setToggling] = useState(false);

  // Custom dynamic plugins
  const isCustom = meta.capabilities?.custom === true;
  const customMeta = isCustom ? {
    icon: '🧩',
    color: 'var(--accent-cyan)',
    fullName: meta.capabilities.description ? name.replace(/_/g, ' ').replace(/\b\w/g, c => c.toUpperCase()) : name,
    category: 'Custom Dynamic Domain',
    description: meta.capabilities.description || 'Custom configured business intelligence pipeline.',
    stage: 'Dynamic Core',
    agents: [
      { name: 'ResearchAgent', desc: 'Scans sector signals for custom targets' },
      { name: 'QualificationAgent', desc: 'Qualifies targets against dynamic ICP parameters' },
      { name: 'ContactDiscoveryAgent', desc: 'Identifies matching decision-maker persona profiles' }
    ]
  } : null;

  const pluginMeta = customMeta || PLUGIN_META[name] || { icon: '🧩', color: 'var(--accent-cyan)', fullName: name };

  const myCaps = isCustom
    ? (meta.capabilities?.capabilities || [])
    : capabilities.filter(c =>
        (c.agent || '').toLowerCase().includes(name.replace('_', ''))
        || pluginMeta.agents?.some(a => a.name === c.agent)
      ).map(c => c.name);

  const handleToggle = async () => {
    if (!onToggle) return;
    setToggling(true);
    try {
      await onToggle(name, enabled);
    } finally {
      setToggling(false);
    }
  };

  return (
    <div className="glass-card fade-in" style={{ padding: 24, marginBottom: 16, opacity: enabled ? 1 : 0.65, transition: 'opacity 0.3s' }}>
      {/* Header */}
      <div style={{ display: 'flex', alignItems: 'flex-start', gap: 16, marginBottom: 16 }}>
        <div style={{
          width: 52, height: 52, borderRadius: 14,
          background: `${pluginMeta.color}22`,
          border: `1px solid ${pluginMeta.color}44`,
          display: 'flex', alignItems: 'center', justifyContent: 'center',
          fontSize: 24, flexShrink: 0
        }}>
          {pluginMeta.icon}
        </div>
        <div style={{ flex: 1 }}>
          <div style={{ display: 'flex', alignItems: 'center', gap: 8, marginBottom: 4, flexWrap: 'wrap' }}>
            <h3 style={{ fontSize: 16, fontWeight: 700, color: 'var(--text-primary)' }}>
              {pluginMeta.fullName || name}
            </h3>
            {isCustom && (
              <span className="badge badge-purple" style={{ fontSize: 10 }}>Custom</span>
            )}
          </div>
          <div style={{ fontSize: 12, color: 'var(--text-muted)' }}>
            {pluginMeta.category} · {pluginMeta.stage ? `Stage ${pluginMeta.stage}` : ''}
          </div>
        </div>
        {/* Action buttons */}
        <div style={{ display: 'flex', gap: 8, alignItems: 'center', flexShrink: 0 }}>
          {/* Enable / Disable toggle */}
          <button
            onClick={handleToggle}
            disabled={toggling}
            className="btn-secondary"
            style={{
              padding: '6px 14px', fontSize: 12, fontWeight: 600,
              borderColor: enabled ? 'rgba(239,68,68,0.5)' : 'rgba(16,185,129,0.5)',
              color: enabled ? 'var(--accent-rose)' : 'var(--accent-emerald)',
              opacity: toggling ? 0.6 : 1,
              minWidth: 90
            }}
          >
            {toggling ? '...' : enabled ? '⏸ Disable' : '▶ Enable'}
          </button>
          {/* Delete — available for all plugins */}
          {onDelete && (
            <button
              onClick={() => onDelete(name, isCustom)}
              className="btn-secondary"
              style={{ padding: '6px 12px', fontSize: 12, borderColor: 'var(--accent-rose)', color: 'var(--accent-rose)' }}
            >
              🗑 Delete
            </button>
          )}
        </div>
      </div>

      {/* Description */}
      <p style={{ fontSize: 13, color: 'var(--text-secondary)', lineHeight: 1.7, marginBottom: 16 }}>
        {pluginMeta.description}
      </p>

      {/* Dynamic Configuration for custom plugins */}
      {isCustom && meta.capabilities && (
        <div style={{ marginBottom: 16, background: 'rgba(255,255,255,0.02)', padding: '16px 20px', borderRadius: 8, border: '1px solid var(--border-subtle)' }}>
          <div style={{ fontSize: 11, fontWeight: 700, color: 'var(--accent-cyan)', textTransform: 'uppercase', marginBottom: 12, letterSpacing: '0.05em' }}>Domain Configuration</div>
          <div style={{ fontSize: 12, color: 'var(--text-secondary)', display: 'flex', flexDirection: 'column', gap: 12 }}>
            {meta.capabilities.geography && meta.capabilities.geography.length > 0 && (
              <div>🌍 Geography: <strong style={{ color: 'var(--text-primary)' }}>{meta.capabilities.geography.join(', ')}</strong></div>
            )}
            {meta.capabilities.organizationTypes && meta.capabilities.organizationTypes.length > 0 && (
              <div>🏢 Org Types: <strong style={{ color: 'var(--text-primary)' }}>{meta.capabilities.organizationTypes.join(', ')}</strong></div>
            )}
            {meta.capabilities.keywords && meta.capabilities.keywords.length > 0 && (
              <div>🔑 Keywords: <strong style={{ color: 'var(--text-primary)' }}>{meta.capabilities.keywords.join(', ')}</strong></div>
            )}
            {meta.capabilities.triggers && meta.capabilities.triggers.length > 0 && (
              <div>⚡ Triggers: <strong style={{ color: 'var(--text-primary)' }}>{meta.capabilities.triggers.join(', ')}</strong></div>
            )}
            
            {meta.capabilities.personas && meta.capabilities.personas.length > 0 && (
              <div style={{ borderTop: '1px solid rgba(255,255,255,0.05)', paddingTop: 10 }}>
                <div style={{ fontSize: 10, fontWeight: 700, color: 'var(--text-muted)', textTransform: 'uppercase', marginBottom: 6 }}>Target Personas</div>
                <div style={{ display: 'flex', flexWrap: 'wrap', gap: 8 }}>
                  {meta.capabilities.personas.map((p, idx) => (
                    <span key={idx} style={{ background: 'rgba(99,102,241,0.1)', border: '1px solid rgba(99,102,241,0.2)', padding: '4px 8px', borderRadius: 6, fontSize: 11 }}>
                      👤 <strong>{p.role}</strong> ({p.seniority} · {p.department})
                    </span>
                  ))}
                </div>
              </div>
            )}

            {meta.capabilities.requirements && meta.capabilities.requirements.length > 0 && (
              <div style={{ borderTop: '1px solid rgba(255,255,255,0.05)', paddingTop: 10 }}>
                <div style={{ fontSize: 10, fontWeight: 700, color: 'var(--text-muted)', textTransform: 'uppercase', marginBottom: 6 }}>Qualification Rules</div>
                <div style={{ display: 'flex', flexWrap: 'wrap', gap: 6 }}>
                  {meta.capabilities.requirements.map((r, idx) => (
                    <span key={idx} style={{ background: 'rgba(16,185,129,0.1)', border: '1px solid rgba(16,185,129,0.2)', padding: '4px 8px', borderRadius: 6, fontSize: 11 }}>
                      ⚙️ {r.field} <strong style={{ color: 'var(--accent-emerald)' }}>{r.operator}</strong> {r.value}
                    </span>
                  ))}
                </div>
              </div>
            )}
          </div>
        </div>
      )}

      {/* Capabilities */}
      {myCaps.length > 0 && (
        <div style={{ marginBottom: 16 }}>
          <div style={{ fontSize: 11, fontWeight: 600, color: 'var(--text-muted)', textTransform: 'uppercase', letterSpacing: '0.06em', marginBottom: 8 }}>
            Registered Capabilities
          </div>
          <div style={{ display: 'flex', flexWrap: 'wrap', gap: 6 }}>
            {myCaps.map((capName, i) => (
              <span key={i} className="badge badge-purple">{capName}</span>
            ))}
          </div>
        </div>
      )}

      {/* Agents expand */}
      <button
        onClick={() => setExpanded(!expanded)}
        className="btn-secondary"
        style={{ width: '100%', justifyContent: 'center', fontSize: 12, padding: '8px 16px' }}
      >
        {expanded ? '▲ Hide Agents' : `▼ View ${pluginMeta.agents?.length || 0} Agents`}
      </button>

      {expanded && pluginMeta.agents && (
        <div style={{ marginTop: 16, display: 'flex', flexDirection: 'column', gap: 8 }}>
          {pluginMeta.agents.map((agent, i) => {
            const isActive = isCustom || capabilities.some(c => c.agent === agent.name);
            return (
              <div key={i} style={{
                display: 'flex', gap: 12, alignItems: 'flex-start',
                padding: '10px 12px', borderRadius: 8,
                background: isActive ? 'rgba(16,185,129,0.08)' : 'var(--bg-input)',
                border: `1px solid ${isActive ? 'rgba(16,185,129,0.2)' : 'var(--border-subtle)'}`,
              }}>
                <span style={{ fontSize: 16, marginTop: 1 }}>{isActive ? '✅' : '⏳'}</span>
                <div>
                  <div style={{ fontSize: 13, fontWeight: 600, color: isActive ? 'var(--accent-emerald)' : 'var(--text-secondary)' }}>
                    {agent.name}
                  </div>
                  <div style={{ fontSize: 12, color: 'var(--text-muted)', marginTop: 2 }}>{agent.desc}</div>
                </div>
              </div>
            );
          })}
        </div>
      )}
    </div>
  );
}

function CapabilityTable({ capabilities }) {
  const categoryColors = {
    planning: 'badge-purple',
    validation: 'badge-info',
    analysis: 'badge-pending',
    reporting: 'badge-success',
    extraction: 'badge-purple',
    search: 'badge-info',
    matching: 'badge-pending',
    scoring: 'badge-success',
    shortlisting: 'badge-success',
    explanation: 'badge-info',
  };

  return (
    <div className="glass-card" style={{ overflow: 'hidden', padding: 0 }}>
      <div style={{ padding: '20px 24px 0', marginBottom: 4 }}>
        <h2 style={{ fontSize: 16, fontWeight: 700, color: 'var(--text-primary)' }}>
          🎯 All Registered Capabilities
        </h2>
        <p style={{ fontSize: 13, color: 'var(--text-muted)', marginTop: 4 }}>
          {capabilities.length} capabilities mapped to agents via Capability Registry
        </p>
      </div>
      <div style={{ overflowX: 'auto' }}>
        <table className="data-table">
          <thead>
            <tr>
              <th>Capability</th>
              <th>Agent</th>
              <th>Category</th>
              <th>Description</th>
            </tr>
          </thead>
          <tbody>
            {capabilities.map((cap, i) => (
              <tr key={i}>
                <td className="primary" style={{ fontFamily: 'monospace', fontSize: 12 }}>{cap.name}</td>
                <td style={{ fontSize: 12, color: 'var(--accent-cyan)' }}>{cap.agent}</td>
                <td>
                  <span className={`badge ${categoryColors[cap.category] || 'badge-info'}`}>
                    {cap.category}
                  </span>
                </td>
                <td style={{ fontSize: 12, maxWidth: 240, overflow: 'hidden', textOverflow: 'ellipsis', whiteSpace: 'nowrap' }}>
                  {cap.description}
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
}

export default function Plugins() {
  const [plugins, setPlugins]         = useState([]);
  const [capabilities, setCapabilities] = useState([]);
  const [loading, setLoading]         = useState(true);
  const [showModal, setShowModal]     = useState(false);

  // Form State for creating custom plugins
  const [formName, setFormName] = useState('');
  const [formDesc, setFormDesc] = useState('');
  const [formGeography, setFormGeography] = useState('');
  const [formOrgTypes, setFormOrgTypes] = useState('');
  const [formKeywords, setFormKeywords] = useState('');
  const [formTriggers, setFormTriggers] = useState('');
  const [formPersonas, setFormPersonas] = useState([
    { role: 'Facility Manager', department: 'Operations', seniority: 'Manager' }
  ]);
  const [formRequirements, setFormRequirements] = useState([
    { field: 'Employees', operator: '>=', value: '500' }
  ]);

  const loadData = () => {
    setLoading(true);
    Promise.all([
      axios.get('/api/plugins/').catch(() => ({ data: [] })),
      axios.get('/api/capabilities').catch(() => ({ data: { capabilities: [] } })),
    ]).then(([plugRes, capRes]) => {
      setPlugins(Array.isArray(plugRes.data) ? plugRes.data : []);
      setCapabilities(capRes.data?.capabilities || []);
    }).finally(() => setLoading(false));
  };

  useEffect(() => {
    loadData();
  }, []);

  const handleAddPersona = () => {
    setFormPersonas([...formPersonas, { role: '', department: '', seniority: 'Manager' }]);
  };

  const handleUpdatePersona = (index, key, val) => {
    const updated = [...formPersonas];
    updated[index][key] = val;
    setFormPersonas(updated);
  };

  const handleRemovePersona = (index) => {
    setFormPersonas(formPersonas.filter((_, i) => i !== index));
  };

  const handleAddRequirement = () => {
    setFormRequirements([...formRequirements, { field: '', operator: '=', value: '' }]);
  };

  const handleUpdateRequirement = (index, key, val) => {
    const updated = [...formRequirements];
    updated[index][key] = val;
    setFormRequirements(updated);
  };

  const handleRemoveRequirement = (index) => {
    setFormRequirements(formRequirements.filter((_, i) => i !== index));
  };

  const applyTemplate = (type) => {
    if (type === 'saas') {
      setFormGeography('United States, India');
      setFormOrgTypes('Software Company, Enterprise SaaS, Tech Startup');
      setFormKeywords('SaaS, Cloud Computing, Salesforce CRM, Developer Tools');
      setFormTriggers('Funding Round, Hiring Software Engineers, Digital Transformation');
      setFormPersonas([
        { role: 'CTO', department: 'Engineering', seniority: 'C-Level' },
        { role: 'VP of Sales', department: 'Sales', seniority: 'VP' }
      ]);
      setFormRequirements([
        { field: 'Employees', operator: '>=', value: '100' },
        { field: 'Funding Stage', operator: '=', value: 'Series A' },
        { field: 'Tech Stack', operator: 'contains', value: 'React' },
        { field: 'Revenue', operator: '>=', value: '10M' }
      ]);
    } else if (type === 'healthcare') {
      setFormGeography('United Kingdom, Europe, USA');
      setFormOrgTypes('Hospital Group, Clinical Laboratory, Medical Clinic');
      setFormKeywords('Pediatric Care, Medical Imaging, EHR Integration');
      setFormTriggers('New Outpatient Clinic Expansion, Sourcing Diagnostic Equipment');
      setFormPersonas([
        { role: 'Chief Medical Officer', department: 'Clinical Operations', seniority: 'C-Level' },
        { role: 'Director of Procurement', department: 'Operations', seniority: 'Director' }
      ]);
      setFormRequirements([
        { field: 'Beds', operator: '>=', value: '100' },
        { field: 'Digital Transformation', operator: '=', value: 'Yes' },
        { field: 'AI Adoption', operator: '=', value: 'High' }
      ]);
    } else if (type === 'solar') {
      setFormGeography('India, Maharashtra, Mumbai');
      setFormOrgTypes('College Campus, Research Laboratory, Manufacturing Plant');
      setFormKeywords('Solar Power, Net Zero Campus, Commercial Solar Panels');
      setFormTriggers('Campus Expansion, Sourcing Clean Energy Suppliers, Renewable Energy Mandate');
      setFormPersonas([
        { role: 'Facility Manager', department: 'Operations', seniority: 'Manager' },
        { role: 'Estate Officer', department: 'Administration', seniority: 'Director' }
      ]);
      setFormRequirements([
        { field: 'Employees', operator: '>=', value: '500' },
        { field: 'Location', operator: '=', value: 'Mumbai' },
        { field: 'Roof Area', operator: '>=', value: '10000 sq ft' },
        { field: 'Sustainability Initiative', operator: '=', value: 'Yes' }
      ]);
    } else if (type === 'manufacturing') {
      setFormGeography('Germany, India, China');
      setFormOrgTypes('Industrial Factory, Automotive Assembly, Heavy Machinery Plant');
      setFormKeywords('Industrial Automation, Supply Chain Logistics, Power Grid Connection');
      setFormTriggers('Hiring Facility Engineers, Upgrading Factory Production Capacity');
      setFormPersonas([
        { role: 'Plant Manager', department: 'Operations', seniority: 'Director' },
        { role: 'Procurement Specialist', department: 'Purchasing', seniority: 'Manager' }
      ]);
      setFormRequirements([
        { field: 'Factory Size', operator: '>=', value: '50000 sq ft' },
        { field: 'Power Consumption', operator: '=', value: 'High' },
        { field: 'Expansion Plans', operator: '=', value: 'Yes' }
      ]);
    }
  };

  const handleCreatePlugin = async (e) => {
    e.preventDefault();
    if (!formName.trim()) return;

    try {
      await axios.post('/api/plugins/create', {
        domainName: formName,
        description: formDesc,
        geography: formGeography.split(',').map(s => s.trim()).filter(Boolean),
        organizationTypes: formOrgTypes.split(',').map(s => s.trim()).filter(Boolean),
        keywords: formKeywords.split(',').map(s => s.trim()).filter(Boolean),
        businessTriggers: formTriggers.split(',').map(s => s.trim()).filter(Boolean),
        personas: formPersonas.filter(p => p.role.trim()),
        requirements: formRequirements.filter(r => r.field.trim() && r.value.trim()),
      });
      setShowModal(false);
      
      // Reset form
      setFormName('');
      setFormDesc('');
      setFormGeography('');
      setFormOrgTypes('');
      setFormKeywords('');
      setFormTriggers('');
      setFormPersonas([{ role: 'Facility Manager', department: 'Operations', seniority: 'Manager' }]);
      setFormRequirements([{ field: 'Employees', operator: '>=', value: '500' }]);
      
      // Reload plugins
      loadData();
    } catch (err) {
      alert(getErrorMessage(err, 'Failed to create plugin'));
    }
  };

  const handleDeletePlugin = async (name, isCustom) => {
    const msg = isCustom
      ? `Are you sure you want to permanently delete the custom plugin "${name}"?\nThis cannot be undone.`
      : `⚠️ WARNING: "${name}" is a built-in plugin.\nDeleting it will remove it from the running system until the server restarts.\n\nAre you sure you want to continue?`;
    if (!window.confirm(msg)) return;
    try {
      await axios.delete(`/api/plugins/${name}`);
      loadData();
    } catch (err) {
      const detail = err?.response?.data?.detail || err?.message || 'Delete failed';
      alert(`❌ Delete failed: ${detail}`);
    }
  };

  const handleTogglePlugin = async (name, currentlyEnabled) => {
    try {
      const endpoint = currentlyEnabled ? '/api/plugins/disable' : '/api/plugins/enable';
      await axios.post(endpoint, { plugin_name: name });
      loadData();
    } catch (err) {
      const msg = err?.response?.data?.detail || err?.message || 'Toggle failed';
      alert(`❌ ${msg}`);
    }
  };

  const knownPlugins = plugins.length > 0 ? plugins : [];

  return (
    <div className="fade-in">
      <div className="page-header" style={{ marginBottom: 28 }}>
        <div>
          <h1 className="page-title">Plugins & Domains</h1>
          <p className="page-subtitle">Install dynamic plugins or create custom domains to configure the platform</p>
        </div>
        <div style={{ display: 'flex', gap: 12 }}>
          <button 
            className="btn-primary" 
            onClick={() => setShowModal(true)}
            style={{ padding: '10px 20px', background: 'linear-gradient(135deg, var(--accent-primary), var(--accent-secondary))' }}
          >
            ✨ Create Custom Domain Plugin
          </button>
        </div>
      </div>

      {showModal && (
        <div style={{
          position: 'fixed', top: 0, left: 0, right: 0, bottom: 0,
          background: 'rgba(0,0,0,0.6)', backdropFilter: 'blur(4px)',
          display: 'flex', alignItems: 'center', justifyContent: 'center',
          zIndex: 1000, padding: 20
        }}>
          <div className="glass-card fade-in" style={{
            maxWidth: 600, width: '100%', padding: 28,
            maxHeight: '90vh', overflowY: 'auto',
            border: '1px solid rgba(99,102,241,0.25)'
          }}>
            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: 20 }}>
              <h2 style={{ fontSize: 18, fontWeight: 800, color: 'var(--text-primary)' }}>✨ Define New Domain Plugin</h2>
              <button onClick={() => setShowModal(false)} style={{ background: 'none', border: 'none', color: 'var(--text-muted)', fontSize: 20, cursor: 'pointer' }}>×</button>
            </div>
            
            <form onSubmit={handleCreatePlugin} style={{ display: 'flex', flexDirection: 'column', gap: 20 }}>
              {/* Template selector at the top */}
              <div style={{ background: 'rgba(255,255,255,0.03)', padding: '12px 16px', borderRadius: 8, border: '1px solid var(--border-subtle)' }}>
                <label className="form-label" style={{ marginBottom: 8, display: 'block', color: 'var(--accent-cyan)' }}>💡 Use a Requirement Template</label>
                <div style={{ display: 'flex', flexWrap: 'wrap', gap: 8 }}>
                  <button type="button" className="btn-secondary" onClick={() => applyTemplate('saas')} style={{ padding: '6px 12px', fontSize: 12 }}>💻 SaaS</button>
                  <button type="button" className="btn-secondary" onClick={() => applyTemplate('healthcare')} style={{ padding: '6px 12px', fontSize: 12 }}>🏥 Healthcare</button>
                  <button type="button" className="btn-secondary" onClick={() => applyTemplate('solar')} style={{ padding: '6px 12px', fontSize: 12 }}>☀️ Solar Energy</button>
                  <button type="button" className="btn-secondary" onClick={() => applyTemplate('manufacturing')} style={{ padding: '6px 12px', fontSize: 12 }}>🏭 Manufacturing</button>
                </div>
              </div>

              {/* SECTION 1: Common Configuration */}
              <div style={{ borderBottom: '1px solid rgba(255,255,255,0.08)', paddingBottom: 16 }}>
                <h3 style={{ fontSize: 14, fontWeight: 700, color: 'var(--accent-primary)', marginBottom: 12, textTransform: 'uppercase', letterSpacing: '0.05em' }}>
                  Section 1: Common Configuration
                </h3>
                <div style={{ display: 'flex', flexDirection: 'column', gap: 12 }}>
                  <div>
                    <label className="form-label">Domain Name</label>
                    <input 
                      type="text" required className="form-input" 
                      value={formName} onChange={e => setFormName(e.target.value)} 
                      placeholder="e.g. Solar Energy, Healthcare, Manufacturing"
                    />
                  </div>

                  <div>
                    <label className="form-label">Description</label>
                    <textarea 
                      required className="form-input" rows={2}
                      value={formDesc} onChange={e => setFormDesc(e.target.value)} 
                      placeholder="e.g. Find organizations likely to purchase commercial solar panels."
                    />
                  </div>

                  <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: 12 }}>
                    <div>
                      <label className="form-label">Target Geography (Comma-separated)</label>
                      <input type="text" className="form-input" value={formGeography} onChange={e => setFormGeography(e.target.value)} placeholder="e.g. India, Mumbai" />
                    </div>
                    <div>
                      <label className="form-label">Org Types (Comma-separated)</label>
                      <input type="text" className="form-input" value={formOrgTypes} onChange={e => setFormOrgTypes(e.target.value)} placeholder="e.g. College, Research Lab" />
                    </div>
                  </div>

                  <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: 12 }}>
                    <div>
                      <label className="form-label">Keywords (Comma-separated)</label>
                      <input type="text" className="form-input" value={formKeywords} onChange={e => setFormKeywords(e.target.value)} placeholder="e.g. Solar, Renewable Energy" />
                    </div>
                    <div>
                      <label className="form-label">Triggers (Comma-separated)</label>
                      <input type="text" className="form-input" value={formTriggers} onChange={e => setFormTriggers(e.target.value)} placeholder="e.g. Campus Expansion, Grant" />
                    </div>
                  </div>

                  {/* Personas Sub-section */}
                  <div style={{ marginTop: 12 }}>
                    <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: 8 }}>
                      <label className="form-label" style={{ marginBottom: 0 }}>Target Personas</label>
                      <button type="button" className="btn-secondary" onClick={handleAddPersona} style={{ padding: '4px 10px', fontSize: 11 }}>➕ Add Persona</button>
                    </div>
                    <div style={{ display: 'flex', flexDirection: 'column', gap: 8 }}>
                      {formPersonas.map((p, idx) => (
                        <div key={idx} style={{ display: 'flex', gap: 8, alignItems: 'center' }}>
                          <input 
                            type="text" required placeholder="Role Name (e.g. Facility Manager)" className="form-input" style={{ flex: 2 }}
                            value={p.role} onChange={e => handleUpdatePersona(idx, 'role', e.target.value)}
                          />
                          <input 
                            type="text" required placeholder="Department" className="form-input" style={{ flex: 1.5 }}
                            value={p.department} onChange={e => handleUpdatePersona(idx, 'department', e.target.value)}
                          />
                          <select 
                            className="form-input" style={{ flex: 1 }}
                            value={p.seniority} onChange={e => handleUpdatePersona(idx, 'seniority', e.target.value)}
                          >
                            <option value="C-Level">C-Level</option>
                            <option value="VP">VP</option>
                            <option value="Director">Director</option>
                            <option value="Manager">Manager</option>
                            <option value="Staff">Staff</option>
                          </select>
                          <button type="button" onClick={() => handleRemovePersona(idx)} style={{ background: 'none', border: 'none', color: 'var(--accent-rose)', cursor: 'pointer', fontSize: 16 }}>×</button>
                        </div>
                      ))}
                    </div>
                  </div>
                </div>
              </div>

              {/* SECTION 2: Qualification Requirements */}
              <div>
                <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: 12 }}>
                  <h3 style={{ fontSize: 14, fontWeight: 700, color: 'var(--accent-primary)', marginBottom: 0, textTransform: 'uppercase', letterSpacing: '0.05em' }}>
                    Section 2: Qualification Requirements
                  </h3>
                  <button type="button" className="btn-secondary" onClick={handleAddRequirement} style={{ padding: '4px 10px', fontSize: 11 }}>➕ Add Requirement</button>
                </div>
                
                <div style={{ display: 'flex', flexDirection: 'column', gap: 8 }}>
                  {formRequirements.map((r, idx) => (
                    <div key={idx} style={{ display: 'flex', gap: 8, alignItems: 'center' }}>
                      <input 
                        type="text" required placeholder="Field (e.g. Employees, Location)" className="form-input" style={{ flex: 2 }}
                        value={r.field} onChange={e => handleUpdateRequirement(idx, 'field', e.target.value)}
                      />
                      <select 
                        className="form-input" style={{ flex: 1, minWidth: 70 }}
                        value={r.operator} onChange={e => handleUpdateRequirement(idx, 'operator', e.target.value)}
                      >
                        <option value="=">=</option>
                        <option value=">=">&gt;=</option>
                        <option value="<=">&lt;=</option>
                        <option value="contains">contains</option>
                      </select>
                      <input 
                        type="text" required placeholder="Value (e.g. 500, Mumbai)" className="form-input" style={{ flex: 2 }}
                        value={r.value} onChange={e => handleUpdateRequirement(idx, 'value', e.target.value)}
                      />
                      <button type="button" onClick={() => handleRemoveRequirement(idx)} style={{ background: 'none', border: 'none', color: 'var(--accent-rose)', cursor: 'pointer', fontSize: 16 }}>×</button>
                    </div>
                  ))}
                </div>
              </div>

              {/* Footer Buttons */}
              <div style={{ display: 'flex', gap: 10, justifyContent: 'flex-end', marginTop: 10, borderTop: '1px solid rgba(255,255,255,0.08)', paddingTop: 16 }}>
                <button type="button" className="btn-secondary" onClick={() => setShowModal(false)}>Cancel</button>
                <button type="submit" className="btn-primary" style={{ padding: '10px 20px', background: 'linear-gradient(135deg, var(--accent-primary), var(--accent-secondary))' }}>
                  💾 Save & Enable Plugin
                </button>
              </div>
            </form>
          </div>
        </div>
      )}

      {loading ? (
        <div style={{ textAlign: 'center', padding: 64 }}>
          <div className="spinner" style={{ margin: '0 auto', width: 32, height: 32 }} />
          <div style={{ color: 'var(--text-muted)', marginTop: 16 }}>Loading plugins...</div>
        </div>
      ) : (
        <>
          <div style={{ marginBottom: 28 }}>
            {knownPlugins.map((plugin, i) => (
              <PluginCard
                key={i}
                name={plugin.name || plugin}
                meta={plugin}
                capabilities={capabilities}
                enabled={plugin.enabled !== false}
                onDelete={handleDeletePlugin}
                onToggle={handleTogglePlugin}
              />
            ))}
          </div>

          {capabilities.length > 0 && (
            <CapabilityTable capabilities={capabilities} />
          )}
        </>
      )}
    </div>
  );
}
