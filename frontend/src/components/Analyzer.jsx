import { useState, useRef } from 'react';

const API_URL = 'http://localhost:8080/api';

function Analyzer({ user, onLogout }) {
  const [file, setFile] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  const [results, setResults] = useState(null);
  const [startTime, setStartTime] = useState(0);
  const fileInputRef = useRef(null);

  const formatFileSize = (bytes) => {
    if (!Number.isFinite(bytes) || bytes <= 0) return '0 KB';
    if (bytes >= 1024 * 1024) return `${(bytes / (1024 * 1024)).toFixed(2)} MB`;
    return `${(bytes / 1024).toFixed(2)} KB`;
  };

  const formatLabel = (text) => {
    if (!text) return '';
    return text.split('_').map(word => word.charAt(0).toUpperCase() + word.slice(1)).join(' ');
  };

  const handleFileSelect = (e) => {
    handleFiles(e.target.files);
  };

  const handleDrop = (e) => {
    e.preventDefault();
    e.currentTarget.classList.remove('dragover');
    handleFiles(e.dataTransfer.files);
  };

  const handleFiles = async (files) => {
    if (files.length === 0) return;
    const selected = files[0];
    setFile(selected);

    if (!selected.name.toLowerCase().endsWith('.pdf') && !selected.name.toLowerCase().endsWith('.docx')) {
      setError('Only PDF and DOCX files are supported');
      return;
    }
    if (selected.size > 50 * 1024 * 1024) {
      setError('File size exceeds 50MB limit');
      return;
    }

    setLoading(true);
    setError('');
    setStartTime(Date.now());

    try {
      const formData = new FormData();
      formData.append('file', selected);
      
      const response = await fetch(`${API_URL}/documents/analyze`, {
        method: 'POST',
        headers: {
          'Authorization': `Bearer ${localStorage.getItem('token')}`
        },
        body: formData
      });
      
      if (!response.ok) {
        const err = await response.json();
        throw new Error(err.error || 'Analysis failed');
      }
      
      const data = await response.json();
      if (data.status === 'failed') {
        throw new Error(data.error || 'Analysis failed');
      }
      
      data.fileName = selected.name;
      setResults(data);

      // Save to MongoDB via auth-service
      try {
        await fetch('http://localhost:5001/api/analyses', {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
            'Authorization': `Bearer ${localStorage.getItem('token')}`
          },
          body: JSON.stringify(data)
        });
      } catch (saveErr) {
        console.error("Failed to save analysis to history:", saveErr);
      }

    } catch (err) {
      setError(err.message || 'Failed to analyze document');
    } finally {
      setLoading(false);
    }
  };

  const resetUI = () => {
    setFile(null);
    setResults(null);
    setError('');
    if (fileInputRef.current) fileInputRef.current.value = '';
  };

  const downloadReport = () => {
    if (!results) return;
    const dataStr = JSON.stringify(results, null, 2);
    const dataBlob = new Blob([dataStr], { type: 'application/json' });
    const url = URL.createObjectURL(dataBlob);
    const link = document.createElement('a');
    link.href = url;
    link.download = `legal-analysis-${new Date().toISOString().split('T')[0]}.json`;
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
    URL.revokeObjectURL(url);
  };

  return (
    <div className="page-shell">
      <div className="ambient ambient-left" aria-hidden="true"></div>
      <div className="ambient ambient-right" aria-hidden="true"></div>

      <div className="container">
        <header className="hero">
          <div className="hero-copy">
            <p className="eyebrow">LexiCore AI: Premium Legal Intelligence</p>
            <h1>Review complex legal documents with a sharper, modern lens.</h1>
            <p className="subtitle">Welcome back, <strong>{user?.username}</strong>. LexiCore is ready to transform your complex contracts into structured, actionable insights.</p>

            <div className="hero-actions">
              <button className="btn btn-primary" onClick={() => document.getElementById('uploadSection').scrollIntoView({behavior: 'smooth'})}>Analyze Document</button>
              <div className="hero-trust">
                <span className="trust-dot"></span>
                Enterprise-grade document intelligence suite
              </div>
            </div>

            <div className="hero-highlights">
              <div className="highlight-card">
                <span className="highlight-label">Engine</span>
                <strong>Lexi-Vision v2.4</strong>
              </div>
              <div className="highlight-card">
                <span className="highlight-label">Output</span>
                <strong>Plain English guidance</strong>
              </div>
              <div className="highlight-card">
                <span className="highlight-label">Context</span>
                <strong>Indian legal workflows</strong>
              </div>
            </div>
          </div>

          <aside className="hero-panel" aria-label="Product overview">
            <div className="panel-badge">Analysis Console</div>
            <div className="hero-panel-card hero-panel-primary">
              <p className="panel-kicker">What you get</p>
              <ul className="panel-list">
                <li>Risk severity breakdown</li>
                <li>Key clause extraction</li>
                <li>Entity and obligation spotting</li>
                <li>Readable contract explanation</li>
              </ul>
            </div>
            <div className="hero-panel-grid">
              <div className="hero-metric">
                <span className="metric-value">50MB</span>
                <span className="metric-label">PDF or DOCX support</span>
              </div>
              <div className="hero-metric">
                <span className="metric-value">TL;DR</span>
                <span className="metric-label">Fast first-pass summary</span>
              </div>
            </div>
            <div style={{ marginTop: 'auto', paddingTop: '40px', borderTop: '1px solid rgba(255, 255, 255, 0.08)' }}>
              <button className="btn btn-secondary" onClick={onLogout} style={{ width: '100%', minHeight: '44px' }}>Logout</button>
            </div>
          </aside>
        </header>

        <main className="main-content">
          <section className="process-strip" aria-label="How it works">
            <div className="process-step">
              <span className="step-index">01</span>
              <div>
                <h2>Upload</h2>
                <p>Drop a contract, lease, employment agreement, or vendor document.</p>
              </div>
            </div>
            <div className="process-step">
              <span className="step-index">02</span>
              <div>
                <h2>Analyze</h2>
                <p>The app extracts clauses, entities, obligations, and risky language.</p>
              </div>
            </div>
            <div className="process-step">
              <span className="step-index">03</span>
              <div>
                <h2>Review</h2>
                <p>Use the summary and flagged issues as a faster review starting point.</p>
              </div>
            </div>
          </section>

          {!loading && !results && !error && (
            <section className="upload-section" id="uploadSection">
              <div className="upload-container">
                <div 
                  className="upload-box" 
                  role="button" 
                  tabIndex="0" 
                  aria-label="Upload a legal document"
                  onClick={() => fileInputRef.current?.click()}
                  onDragOver={(e) => { e.preventDefault(); e.currentTarget.classList.add('dragover'); }}
                  onDragLeave={(e) => e.currentTarget.classList.remove('dragover')}
                  onDrop={handleDrop}
                >
                  <div className="upload-box-glow" aria-hidden="true"></div>
                  <div className="upload-box-content">
                    <div className="upload-icon">
                      <svg width="32" height="32" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.5" strokeLinecap="round" strokeLinejoin="round"><path d="M12 2v8"/><path d="m16 6-4-4-4 4"/><rect width="20" height="8" x="2" y="14" rx="2"/><path d="M6 18h.01"/><path d="M10 18h.01"/></svg>
                    </div>
                    <p className="section-kicker">Secure review workspace</p>
                    <h2>Upload your document for AI-assisted legal analysis</h2>
                    <p className="upload-description">Drag and drop your legal document or click anywhere in this panel to select a file for analysis.</p>

                    <div className="upload-meta">
                      <span className="meta-chip">PDF / DOCX</span>
                      <span className="meta-chip">Up to 50MB</span>
                      <span className="meta-chip">Summary + risk review</span>
                    </div>

                    <input type="file" ref={fileInputRef} onChange={handleFileSelect} accept=".pdf,.docx" hidden />
                    <button className="btn btn-primary" onClick={(e) => { e.stopPropagation(); fileInputRef.current?.click(); }}>Choose Document</button>

                    {file && (
                      <div className="selected-file" aria-live="polite">
                        <span className="selected-file-label">Selected file</span>
                        <strong>{file.name} • {formatFileSize(file.size)}</strong>
                      </div>
                    )}

                    <p className="upload-note">Works especially well for rental agreements, employment contracts, NDAs, vendor terms, and other formal legal documents.</p>
                  </div>
                </div>
              </div>
            </section>
          )}

          {loading && (
            <section className="loading-section" role="status" aria-live="polite">
              <div className="loading-orb">
                <div className="spinner"></div>
              </div>
              <p>Analyzing your document...</p>
              <p className="loading-subtext">Extracting entities, classifying clauses, and reviewing risk patterns in the uploaded contract.</p>
            </section>
          )}

          {error && (
            <section className="error-section" role="alert">
              <div className="error-message">
                <p className="section-kicker">Something went wrong</p>
                <h2>We could not analyze that document</h2>
                <p>{error}</p>
                <button className="btn btn-secondary" onClick={resetUI}>Try Again</button>
              </div>
            </section>
          )}

          {results && (
            <section className="results-section">
              <div className="results-topbar">
                <p className="section-kicker">Analysis report</p>
                <h2>Your legal review dashboard</h2>
                <p>Use this as a structured first pass before taking formal legal action or obtaining professional advice.</p>
              </div>

              <div className="card overview-card">
                <h2>Contract Snapshot</h2>
                <div className="overview-grid">
                  {results.analysis_overview ? (
                    <>
                      <div className="overview-item"><strong>Document type</strong><span>{results.analysis_overview.document_type || 'Unknown'}</span></div>
                      <div className="overview-item"><strong>Signer role</strong><span>{formatLabel(results.analysis_overview.signer_context || 'signer')}</span></div>
                      <div className="overview-item"><strong>Overall risk</strong><span>{formatLabel(results.analysis_overview.overall_risk_level || 'unknown')}</span></div>
                      <div className="overview-item"><strong>Risk score</strong><span>{results.analysis_overview.risk_score != null ? `${results.analysis_overview.risk_score}/100` : 'N/A'}</span></div>
                      <div className="overview-item"><strong>Readability</strong><span>{formatLabel(results.analysis_overview.readability_band || 'unknown')}</span></div>
                      <div className="overview-item"><strong>Analysis confidence</strong><span>{results.analysis_overview.analysis_confidence?.label ? `${formatLabel(results.analysis_overview.analysis_confidence.label)} (${Math.round((Number(results.analysis_overview.analysis_confidence.score) || 0) * 100)}%)` : 'N/A'}</span></div>
                    </>
                  ) : (
                    <div className="empty-state">No contract snapshot available</div>
                  )}
                </div>
              </div>

              <div className="card summary-card">
                <h2>Document Summary</h2>
                <div className="summary-content">{results.summary || 'No summary generated'}</div>
              </div>

              <div className="card info-card">
                <h2>Key Information</h2>
                <div className="info-grid">
                  <div className="info-item"><strong>Document Size</strong><span>{formatFileSize(results.document_length)}</span></div>
                  <div className="info-item"><strong>Analysis Time</strong><span>{((Date.now() - startTime) / 1000).toFixed(2)}s</span></div>
                  <div className="info-item"><strong>File Name</strong><span>{results.fileName || file?.name || 'Unknown'}</span></div>
                </div>
              </div>

              {results.risks && results.risks.length > 0 && (
                <div className="card risk-card">
                  <h2>Risk Analysis</h2>
                  <div className="risks-content">
                    {results.risks.map((risk, index) => (
                      <div className="risk-item" key={`risk-${index}`}>
                        <div>
                          <span className="risk-type">{formatLabel(risk.type)}</span>
                          <span className={`risk-severity risk-severity-${risk.severity_level || 'medium'}`}>
                            {formatLabel(risk.severity_level || 'medium')} Severity
                          </span>
                        </div>
                        <h3>{risk.risk_title}</h3>
                        <p><strong>Why it's risky:</strong> {risk.why_this_is_risky}</p>
                        <p><strong>Recommendation:</strong> {risk.recommendation}</p>
                        <div style={{ background: 'rgba(0,0,0,0.2)', padding: '10px', borderRadius: '6px', fontSize: '0.9rem', fontStyle: 'italic', borderLeft: '3px solid var(--danger)' }}>
                          "{risk.clause}"
                        </div>
                      </div>
                    ))}
                  </div>
                </div>
              )}

              {results.key_clauses && results.key_clauses.length > 0 && (
                <div className="card clause-card">
                  <h2>Key Clauses Detected</h2>
                  <div className="clauses-content">
                    {results.key_clauses.map((clause, index) => (
                      <div className={`clause-item ${clause.is_risky ? 'risky-clause' : ''}`} key={`clause-${index}`}>
                        <div>
                          <span className="clause-type">{formatLabel(clause.type)}</span>
                          {clause.is_risky && (
                            <span className="risk-severity risk-severity-high" style={{ marginLeft: '10px' }}>Risky</span>
                          )}
                        </div>
                        <p><strong>Section:</strong> {clause.section}</p>
                        <p style={{ color: 'var(--text-muted)' }}>{clause.explanation}</p>
                        <div style={{ background: 'rgba(0,0,0,0.2)', padding: '10px', borderRadius: '6px', fontSize: '0.9rem', fontFamily: 'var(--font-mono, monospace)', borderLeft: '3px solid var(--primary-soft)' }}>
                          "{clause.text}..."
                        </div>
                      </div>
                    ))}
                  </div>
                </div>
              )}

              <div className="action-buttons">
                <button className="btn btn-primary" onClick={downloadReport}>Download Report</button>
                <button className="btn btn-secondary" onClick={resetUI}>Analyze Another</button>
              </div>
            </section>
          )}
        </main>

        <footer className="footer" style={{ textAlign: 'center', marginTop: '64px', opacity: 0.6 }}>
          <p>&copy; 2024 LexiCore AI. Premium Document Intelligence.</p>
          <p style={{ fontSize: '0.85rem', marginTop: '8px' }}>This tool is for information extraction only and does not constitute professional legal advice.</p>
        </footer>
      </div>
    </div>
  );
}

export default Analyzer;
