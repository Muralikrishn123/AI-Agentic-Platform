import { useState, useEffect, useRef } from 'react';
import { useLocation } from 'react-router-dom';
import axios from 'axios';

export default function AssistantBot() {
  const location = useLocation();
  
  // Chat Panel Toggle State
  const [isOpen, setIsOpen] = useState(false);
  const [messages, setMessages] = useState([
    {
      sender: 'bot',
      text: '👋 Hi! I am your AI Platform Assistant. I can help you use the platform or answer questions about your workflow results. Ask me anything!',
      timestamp: new Date()
    }
  ]);
  const [inputValue, setInputValue] = useState('');
  const [loading, setLoading] = useState(false);

  // Voice Capabilities State
  const [isListening, setIsListening] = useState(false);
  const [voiceEnabled, setVoiceEnabled] = useState(false);

  const messagesEndRef = useRef(null);
  const recognitionRef = useRef(null);

  // Extract workflow_id from URL path /results/:workflowId if on results page
  const workflowIdMatch = location.pathname.match(/\/results\/([a-zA-Z0-9-]+)/);
  const workflowId = workflowIdMatch ? workflowIdMatch[1] : null;

  // Initialize Speech Recognition
  useEffect(() => {
    const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
    if (SpeechRecognition) {
      const rec = new SpeechRecognition();
      rec.continuous = false;
      rec.interimResults = false;
      rec.lang = 'en-US';

      rec.onstart = () => {
        setIsListening(true);
      };

      rec.onresult = (event) => {
        const transcript = event.results[0][0].transcript;
        setInputValue(prev => (prev ? prev + ' ' : '') + transcript);
      };

      rec.onerror = (e) => {
        console.error('Speech recognition error:', e);
        setIsListening(false);
      };

      rec.onend = () => {
        setIsListening(false);
      };

      recognitionRef.current = rec;
    }
  }, []);

  // Auto-scroll messages to bottom
  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages, isOpen]);

  // Speak bot response using Web Speech Synthesis
  const speakText = (text) => {
    if (!voiceEnabled) return;
    // Cancel any ongoing speech
    window.speechSynthesis?.cancel();
    
    // Clean markdown formatting before speaking
    const cleanText = text.replace(/[*#`_\-]/g, '');
    const utterance = new SpeechSynthesisUtterance(cleanText);
    utterance.rate = 1.0;
    window.speechSynthesis?.speak(utterance);
  };

  const handleSendMessage = async (textToSend) => {
    const text = textToSend || inputValue;
    if (!text.trim() || loading) return;

    setMessages(prev => [...prev, { sender: 'user', text, timestamp: new Date() }]);
    if (!textToSend) setInputValue('');
    setLoading(true);

    try {
      const token = localStorage.getItem('token');
      const { data } = await axios.post('/api/chatbot/query', {
        query: text,
        workflow_id: workflowId,
        page_context: location.pathname
      }, {
        headers: token ? { Authorization: `Bearer ${token}` } : {}
      });

      if (data.success) {
        const reply = data.response;
        setMessages(prev => [...prev, { sender: 'bot', text: reply, timestamp: new Date() }]);
        speakText(reply);
      }
    } catch (err) {
      setMessages(prev => [
        ...prev,
        { sender: 'bot', text: '⚠️ Sorry, I could not generate a response. Please check your backend connection.', timestamp: new Date() }
      ]);
    } finally {
      setLoading(false);
    }
  };

  const toggleListen = () => {
    if (!recognitionRef.current) {
      alert('Speech recognition is not supported in this browser. Try Chrome or Edge.');
      return;
    }
    if (isListening) {
      recognitionRef.current.stop();
    } else {
      recognitionRef.current.start();
    }
  };

  // Quick prompt suggestions
  const getSuggestions = () => {
    if (workflowId) {
      return [
        'Why did these prospects match?',
        'Explain the qualification requirements',
        'Summarize this workflow output',
        'Who is the top matched prospect?'
      ];
    }
    return [
      'How does this platform work?',
      'How do I create a custom plugin?',
      'How do I configure target settings?',
      'Explain Human-In-The-Loop approvals'
    ];
  };

  return (
    <>
      {/* Floating Toggle Button */}
      <button
        onClick={() => {
          setIsOpen(!isOpen);
          // Cancel speech when closing
          if (isOpen) window.speechSynthesis?.cancel();
        }}
        style={{
          position: 'fixed', bottom: 24, right: 24, zIndex: 1000,
          width: 56, height: 56, borderRadius: '50%',
          background: 'linear-gradient(135deg, var(--accent-primary), var(--accent-secondary))',
          color: '#fff', border: 'none', cursor: 'pointer',
          display: 'flex', alignItems: 'center', justifyContent: 'center',
          boxShadow: '0 8px 24px rgba(99,102,241,0.4), var(--shadow-glow)',
          transition: 'transform 0.2s',
          animation: isOpen ? 'none' : 'float-pulse 2s infinite'
        }}
        onMouseEnter={e => e.currentTarget.style.transform = 'scale(1.08)'}
        onMouseLeave={e => e.currentTarget.style.transform = 'scale(1)'}
      >
        {isOpen ? (
          <span style={{ fontSize: 24, fontWeight: 300 }}>✕</span>
        ) : (
          <div style={{ position: 'relative' }}>
            <span style={{ fontSize: 26 }}>💬</span>
            <span style={{
              position: 'absolute', top: -2, right: -2,
              width: 10, height: 10, borderRadius: '50%',
              background: 'var(--accent-emerald)', border: '2px solid var(--bg-card)'
            }} />
          </div>
        )}
      </button>

      {/* Chat Side Drawer */}
      {isOpen && (
        <div className="glass-card" style={{
          position: 'fixed', bottom: 92, right: 24, zIndex: 999,
          width: 380, height: 500, maxHeight: 'calc(100vh - 120px)',
          display: 'flex', flexDirection: 'column',
          boxShadow: '0 12px 40px rgba(0,0,0,0.5), var(--shadow-glow)',
          border: '1px solid rgba(99,102,241,0.25)',
          overflow: 'hidden', animation: 'slide-up 0.25s cubic-bezier(0.16, 1, 0.3, 1)'
        }}>
          {/* Header */}
          <div style={{
            padding: '16px 20px',
            background: 'linear-gradient(90deg, rgba(99,102,241,0.15), rgba(168,85,247,0.15))',
            borderBottom: '1px solid var(--border-subtle)',
            display: 'flex', alignItems: 'center', justifyContent: 'space-between'
          }}>
            <div style={{ display: 'flex', alignItems: 'center', gap: 10 }}>
              <div style={{
                width: 30, height: 30, borderRadius: '50%',
                background: 'linear-gradient(135deg, var(--accent-primary), var(--accent-secondary))',
                display: 'flex', alignItems: 'center', justifyContent: 'center', fontSize: 14
              }}>🤖</div>
              <div>
                <div style={{ fontSize: 13.5, fontWeight: 700, color: 'var(--text-primary)' }}>AI Assistant</div>
                <div style={{ fontSize: 10.5, color: 'var(--accent-emerald)', display: 'flex', alignItems: 'center', gap: 4 }}>
                  <span style={{ width: 6, height: 6, borderRadius: '50%', background: 'var(--accent-emerald)', display: 'inline-block' }} />
                  {workflowId ? 'Context: Results page' : 'Online'}
                </div>
              </div>
            </div>

            {/* Voice Control Buttons */}
            <div style={{ display: 'flex', gap: 8 }}>
              {/* Speaker Toggle */}
              <button
                type="button"
                onClick={() => {
                  setVoiceEnabled(!voiceEnabled);
                  if (voiceEnabled) window.speechSynthesis?.cancel();
                }}
                title={voiceEnabled ? 'Disable Voice Response' : 'Enable Voice Response'}
                style={{
                  background: voiceEnabled ? 'rgba(99,102,241,0.2)' : 'none',
                  border: voiceEnabled ? '1px solid rgba(99,102,241,0.4)' : 'none',
                  borderRadius: 6, width: 30, height: 30, cursor: 'pointer',
                  color: voiceEnabled ? 'var(--accent-primary)' : 'var(--text-muted)',
                  fontSize: 14, display: 'flex', alignItems: 'center', justifyContent: 'center',
                  transition: 'all 0.2s'
                }}
              >
                {voiceEnabled ? '🔊' : '🔇'}
              </button>
            </div>
          </div>

          {/* Messages list */}
          <div style={{ flex: 1, overflowY: 'auto', padding: '16px 20px', display: 'flex', flexDirection: 'column', gap: 12 }}>
            {messages.map((m, i) => {
              const isBot = m.sender === 'bot';
              return (
                <div key={i} style={{
                  display: 'flex',
                  justifyContent: isBot ? 'flex-start' : 'flex-end',
                  alignItems: 'flex-start', gap: 8
                }}>
                  {isBot && (
                    <div style={{
                      width: 24, height: 24, borderRadius: '50%', flexShrink: 0,
                      background: 'rgba(99,102,241,0.1)', border: '1px solid rgba(99,102,241,0.3)',
                      display: 'flex', alignItems: 'center', justifyContent: 'center', fontSize: 11
                    }}>🤖</div>
                  )}
                  <div style={{
                    maxWidth: '80%', padding: '10px 14px', borderRadius: 12,
                    fontSize: 12.5, lineHeight: 1.5,
                    background: isBot ? 'var(--bg-input)' : 'linear-gradient(135deg, var(--accent-primary), var(--accent-secondary))',
                    color: isBot ? 'var(--text-secondary)' : '#fff',
                    border: isBot ? '1px solid var(--border-subtle)' : 'none',
                    borderRadiusTopLeft: isBot ? 2 : 12,
                    borderRadiusTopRight: isBot ? 12 : 2,
                    whiteSpace: 'pre-wrap'
                  }}>
                    {m.text}
                  </div>
                </div>
              );
            })}
            {loading && (
              <div style={{ display: 'flex', alignItems: 'center', gap: 8 }}>
                <div style={{
                  width: 24, height: 24, borderRadius: '50%',
                  background: 'rgba(99,102,241,0.1)', border: '1px solid rgba(99,102,241,0.3)',
                  display: 'flex', alignItems: 'center', justifyContent: 'center', fontSize: 11
                }}>🤖</div>
                <div style={{ padding: '10px 14px', background: 'var(--bg-input)', borderRadius: 12, display: 'flex', gap: 4 }}>
                  <div className="dot-pulse" style={{ width: 6, height: 6, borderRadius: '50%', background: 'var(--text-muted)', animation: 'pulse-dot 1.2s infinite' }} />
                  <div className="dot-pulse" style={{ width: 6, height: 6, borderRadius: '50%', background: 'var(--text-muted)', animation: 'pulse-dot 1.2s infinite 0.2s' }} />
                  <div className="dot-pulse" style={{ width: 6, height: 6, borderRadius: '50%', background: 'var(--text-muted)', animation: 'pulse-dot 1.2s infinite 0.4s' }} />
                </div>
              </div>
            )}
            <div ref={messagesEndRef} />
          </div>

          {/* Quick Action Suggestions */}
          <div style={{
            padding: '8px 16px', display: 'flex', gap: 6, overflowX: 'auto',
            borderTop: '1px solid var(--border-subtle)', background: 'rgba(0,0,0,0.1)',
            whiteSpace: 'nowrap'
          }}>
            {getSuggestions().map((s, i) => (
              <button
                key={i}
                type="button"
                onClick={() => handleSendMessage(s)}
                style={{
                  padding: '5px 10px', fontSize: 11, borderRadius: 14,
                  background: 'var(--bg-input)', border: '1px solid var(--border-subtle)',
                  color: 'var(--accent-primary)', cursor: 'pointer', fontFamily: 'Inter, sans-serif',
                  transition: 'all 0.15s'
                }}
                onMouseEnter={e => e.currentTarget.style.borderColor = 'var(--accent-primary)'}
                onMouseLeave={e => e.currentTarget.style.borderColor = 'var(--border-subtle)'}
              >
                {s}
              </button>
            ))}
          </div>

          {/* Input Bar */}
          <form
            onSubmit={(e) => { e.preventDefault(); handleSendMessage(); }}
            style={{
              padding: '12px 16px', borderTop: '1px solid var(--border-subtle)',
              display: 'flex', gap: 8, alignItems: 'center'
            }}
          >
            {/* Mic Toggle Button */}
            <button
              type="button"
              onClick={toggleListen}
              title={isListening ? 'Stop Listening' : 'Start Voice Input'}
              style={{
                background: isListening ? 'rgba(239,68,68,0.2)' : 'none',
                border: isListening ? '1px solid rgba(239,68,68,0.4)' : 'none',
                borderRadius: '50%', width: 36, height: 36, cursor: 'pointer',
                display: 'flex', alignItems: 'center', justifyContent: 'center',
                fontSize: 16, transition: 'all 0.2s', position: 'relative'
              }}
            >
              {isListening ? (
                <>
                  🎤
                  <span style={{
                    position: 'absolute', top: 4, right: 4,
                    width: 6, height: 6, borderRadius: '50%',
                    background: '#ef4444', animation: 'blink 1s infinite'
                  }} />
                </>
              ) : '🎤'}
            </button>

            <input
              type="text"
              className="form-input"
              value={inputValue}
              onChange={e => setInputValue(e.target.value)}
              placeholder={isListening ? 'Listening...' : 'Ask assistant...'}
              style={{ flex: 1, margin: 0, fontSize: 13, height: 36 }}
            />

            <button
              type="submit"
              disabled={loading || !inputValue.trim()}
              className="btn-primary"
              style={{
                width: 36, height: 36, padding: 0, borderRadius: '50%',
                display: 'flex', alignItems: 'center', justifyContent: 'center',
                flexShrink: 0
              }}
            >
              ➔
            </button>
          </form>
        </div>
      )}

      {/* Global CSS Styles for Assistant */}
      <style>{`
        @keyframes float-pulse {
          0%, 100% { transform: translateY(0); box-shadow: 0 8px 24px rgba(99,102,241,0.4); }
          50% { transform: translateY(-4px); box-shadow: 0 12px 32px rgba(99,102,241,0.6); }
        }
        @keyframes slide-up {
          from { opacity: 0; transform: translateY(20px); }
          to { opacity: 1; transform: translateY(0); }
        }
        @keyframes pulse-dot {
          0%, 100% { transform: scale(1); opacity: 0.6; }
          50% { transform: scale(1.2); opacity: 1; }
        }
      `}</style>
    </>
  );
}
