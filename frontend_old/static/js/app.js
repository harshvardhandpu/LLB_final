/**
 * Legal Document Analyzer - Frontend JavaScript
 * Handles file upload, API communication, and results display
 */

const API_URL = 'http://localhost:8080/api';

// DOM Elements
const uploadSection = document.getElementById('uploadSection');
const uploadBox = document.getElementById('uploadBox');
const fileInput = document.getElementById('fileInput');
const selectFileBtn = document.getElementById('selectFileBtn');
const selectedFile = document.getElementById('selectedFile');
const selectedFileName = document.getElementById('selectedFileName');
const loadingSection = document.getElementById('loadingSection');
const resultsSection = document.getElementById('resultsSection');
const errorSection = document.getElementById('errorSection');
const newFileBtn = document.getElementById('newFileBtn');
const retryBtn = document.getElementById('retryBtn');
const downloadBtn = document.getElementById('downloadBtn');
const errorContent = document.getElementById('errorContent');

let analysisResults = null;
let startTime = 0;

// Initialize event listeners
document.addEventListener('DOMContentLoaded', () => {
    setupEventListeners();
});

function setupEventListeners() {
    selectFileBtn.addEventListener('click', (e) => {
        e.stopPropagation();
        fileInput.click();
    });
    
    fileInput.addEventListener('change', handleFileSelect);

    uploadBox.addEventListener('click', () => fileInput.click());

    uploadBox.addEventListener('keydown', (e) => {
        if (e.key === 'Enter' || e.key === ' ') {
            e.preventDefault();
            fileInput.click();
        }
    });
    
    uploadBox.addEventListener('dragover', (e) => {
        e.preventDefault();
        uploadBox.classList.add('dragover');
    });
    
    uploadBox.addEventListener('dragleave', () => {
        uploadBox.classList.remove('dragover');
    });
    
    uploadBox.addEventListener('drop', (e) => {
        e.preventDefault();
        uploadBox.classList.remove('dragover');
        handleFiles(e.dataTransfer.files);
    });
    
    newFileBtn.addEventListener('click', resetUI);
    retryBtn.addEventListener('click', resetUI);
    downloadBtn.addEventListener('click', downloadReport);
}

/**
 * Handle file selection from input
 */
function handleFileSelect(e) {
    handleFiles(e.target.files);
}

/**
 * Handle file upload and analysis
 */
async function handleFiles(files) {
    if (files.length === 0) return;
    
    const file = files[0];

    updateSelectedFile(file);
    
    // Validate file
    if (!file.name.toLowerCase().endsWith('.pdf') && !file.name.toLowerCase().endsWith('.docx')) {
        showError('Only PDF and DOCX files are supported');
        return;
    }
    
    if (file.size > 50 * 1024 * 1024) {
        showError('File size exceeds 50MB limit');
        return;
    }
    
    // Show loading and start analysis
    showLoading();
    startTime = Date.now();
    
    try {
        const formData = new FormData();
        formData.append('file', file);
        
        const response = await fetch(`${API_URL}/documents/analyze`, {
            method: 'POST',
            body: formData
        });
        
        if (!response.ok) {
            const error = await response.json();
            throw new Error(error.error || 'Analysis failed');
        }
        
        analysisResults = await response.json();
        
        if (analysisResults.status === 'failed') {
            throw new Error(analysisResults.error || 'Analysis failed');
        }
        
        displayResults(analysisResults);
        
    } catch (error) {
        console.error('Analysis error:', error);
        showError(error.message || 'Failed to analyze document');
    }
}

/**
 * Display analysis results
 */
function displayResults(data) {
    // Hide loading, show results
    uploadSection.classList.add('hidden');
    loadingSection.classList.add('hidden');
    errorSection.classList.add('hidden');
    resultsSection.classList.remove('hidden');
    
    const analysisTime = ((Date.now() - startTime) / 1000).toFixed(2);
    const documentLength = Number(data.document_length) || 0;
    
    // Populate summary
    document.getElementById('summaryContent').textContent = data.summary || 'No summary generated';
    
    // Populate info
    document.getElementById('docSize').textContent = formatFileSize(documentLength);
    document.getElementById('analysisTime').textContent = `${analysisTime}s`;
    document.getElementById('fileName').textContent = data.fileName || 'Unknown';

    displayOverview(data.analysis_overview);
    displayPlainLanguageGuide(data.plain_language_guide);
    
    // Populate entities
    displayEntities(data.extracted_entities);
    
    // Populate clauses
    displayClauses(data.key_clauses);
    
    // Populate risks
    displayRisks(data.risks);
    
    // Populate pros and cons
    displayProsCons(data.pros, data.cons);

    // Populate obligations, questions and glossary
    displayObligations(data.obligations);
    displayQuestions(data.questions_to_ask);
    displayGlossary(data.glossary);
    
    // Populate simplified text
    document.getElementById('simplifiedContent').textContent = data.simplified_text || 'No simplified version available';
    
    // Scroll to results
    resultsSection.scrollIntoView({ behavior: 'smooth', block: 'start' });
}

function displayOverview(overview) {
    const overviewContent = document.getElementById('overviewContent');
    overviewContent.innerHTML = '';

    if (!overview || Object.keys(overview).length === 0) {
        overviewContent.innerHTML = renderEmptyState('No contract snapshot available');
        return;
    }

    const confidence = overview.analysis_confidence || {};
    const items = [
        ['Document type', overview.document_type || 'Unknown'],
        ['Signer role', formatLabel(overview.signer_context || 'signer')],
        ['Overall risk', formatLabel(overview.overall_risk_level || 'unknown')],
        ['Risk score', overview.risk_score != null ? `${overview.risk_score}/100` : 'N/A'],
        ['Readability', formatLabel(overview.readability_band || 'unknown')],
        ['Analysis confidence', confidence.label ? `${formatLabel(confidence.label)} (${Math.round((Number(confidence.score) || 0) * 100)}%)` : 'N/A']
    ];

    items.forEach(([label, value]) => {
        overviewContent.innerHTML += `
            <div class="overview-item">
                <strong>${escapeHtml(label)}</strong>
                <span>${escapeHtml(String(value))}</span>
            </div>
        `;
    });
}

function displayPlainLanguageGuide(guide) {
    const guideContent = document.getElementById('plainLanguageGuide');
    guideContent.innerHTML = '';

    if (!guide || Object.keys(guide).length === 0) {
        guideContent.innerHTML = renderEmptyState('No plain-language guide available');
        return;
    }

    const items = [
        ['What this is', guide.what_this_is],
        ['Why it matters', guide.why_it_matters],
        ['Biggest watchout', guide.biggest_watchout],
        ['Practical next step', guide.practical_next_step]
    ];

    items.forEach(([label, value]) => {
        guideContent.innerHTML += `
            <div class="guide-item">
                <strong>${escapeHtml(label)}</strong>
                <p>${escapeHtml(value || 'Not available')}</p>
            </div>
        `;
    });
}

/**
 * Display extracted entities
 */
function displayEntities(entities) {
    const entitiesContent = document.getElementById('entitiesContent');
    entitiesContent.innerHTML = '';
    
    if (!entities || Object.keys(entities).length === 0) {
        entitiesContent.innerHTML = renderEmptyState('No entities extracted');
        return;
    }

    let hasContent = false;

    for (const [key, value] of Object.entries(entities)) {
        if (Array.isArray(value) && value.length > 0) {
            hasContent = true;
            const html = `
                <div class="entity-group">
                    <strong>${formatLabel(key)}</strong>
                    <ul class="entity-list">
                        ${value.map(item => `<li>${escapeHtml(item)}</li>`).join('')}
                    </ul>
                </div>
            `;
            entitiesContent.innerHTML += html;
        } else if (typeof value === 'number' && value > 0) {
            hasContent = true;
            const html = `
                <div class="entity-group">
                    <strong>${formatLabel(key)}</strong>
                    <p>${value}</p>
                </div>
            `;
            entitiesContent.innerHTML += html;
        }
    }

    if (!hasContent) {
        entitiesContent.innerHTML = renderEmptyState('No entities extracted');
    }
}

/**
 * Display key clauses
 */
function displayClauses(clauses) {
    const clausesContent = document.getElementById('clausesContent');
    clausesContent.innerHTML = '';
    
    if (!clauses || clauses.length === 0) {
        clausesContent.innerHTML = renderEmptyState('No clauses identified');
        return;
    }
    
    clauses.forEach(clause => {
        const severityClass = clause.severity_level ? clause.severity_level.toLowerCase() : 'low';
        const confidence = Number(clause.confidence) || 0;
        const html = `
            <div class="clause-item">
                <div>
                    <span class="clause-type">${escapeHtml(clause.type || 'Unknown')}</span>
                    <span class="clause-severity clause-severity-${severityClass}">
                        ${clause.severity_level || 'N/A'}
                    </span>
                </div>
                <div class="clause-text">"${escapeHtml(clause.text ? clause.text.substring(0, 150) : '')}"</div>
                <div class="clause-meta">
                    ${escapeHtml(clause.section || 'N/A')}
                    <span class="clause-confidence">${(confidence * 100).toFixed(0)}% confident</span>
                </div>
            </div>
        `;
        clausesContent.innerHTML += html;
    });
}

/**
 * Display identified risks
 */
function displayRisks(risks) {
    const risksContent = document.getElementById('risksContent');
    risksContent.innerHTML = '';
    
    if (!risks || risks.length === 0) {
        risksContent.innerHTML = renderEmptyState('No major risks identified');
        return;
    }
    
    risks.forEach(risk => {
        const severityClass = risk.severity_level ? risk.severity_level.toLowerCase() : 'medium';
        const riskTitle = risk.risk_title || risk.type || 'Unknown';
        const riskCategory = risk.risk_category ? formatLabel(risk.risk_category) : formatLabel(risk.type || 'risk');
        const whyThisIsRisky = risk.why_this_is_risky || risk.description || '';
        const impactOnUser = risk.impact_on_user || '';
        const whatUserShouldCheck = risk.what_user_should_check || risk.recommendation || 'Review this clause carefully';
        const html = `
            <div class="risk-item">
                <div>
                    <span class="risk-type">${escapeHtml(riskTitle)}</span>
                    <span class="risk-severity risk-severity-${severityClass}">
                        ${risk.severity_level || 'MEDIUM'}
                    </span>
                </div>
                <div class="risk-description">
                    <strong>Category:</strong> ${escapeHtml(riskCategory)}
                </div>
                <div class="risk-description">
                    <strong>Why this is risky:</strong> ${escapeHtml(whyThisIsRisky)}
                </div>
                ${impactOnUser ? `<div class="risk-description"><strong>Impact on user:</strong> ${escapeHtml(impactOnUser)}</div>` : ''}
                ${risk.affected_clause ? `<div class="risk-clause">Clause: ${escapeHtml(risk.affected_clause.substring(0, 100))}</div>` : ''}
                <div class="risk-recommendation">
                    <strong>What to check:</strong> ${escapeHtml(whatUserShouldCheck)}
                </div>
            </div>
        `;
        risksContent.innerHTML += html;
    });
}

/**
 * Display pros and cons
 */
function displayProsCons(pros, cons) {
    const prosList = document.getElementById('prosList');
    const consList = document.getElementById('consList');
    
    prosList.innerHTML = '';
    consList.innerHTML = '';
    
    if (pros && pros.length > 0) {
        pros.forEach(pro => {
            const li = document.createElement('li');
            li.textContent = pro;
            prosList.appendChild(li);
        });
    } else {
        prosList.innerHTML = '<li>Review the document for potential advantages</li>';
    }
    
    if (cons && cons.length > 0) {
        cons.forEach(con => {
            const li = document.createElement('li');
            li.textContent = con;
            consList.appendChild(li);
        });
    } else {
        consList.innerHTML = '<li>No critical disadvantages detected</li>';
    }
}

function displayObligations(obligations) {
    const obligationsContent = document.getElementById('obligationsContent');
    obligationsContent.innerHTML = '';

    if (!obligations || obligations.length === 0) {
        obligationsContent.innerHTML = renderEmptyState('No key obligations extracted');
        return;
    }

    obligations.forEach(obligation => {
        obligationsContent.innerHTML += `
            <div class="obligation-item">
                <div class="obligation-topline">
                    <span class="obligation-party">${escapeHtml(obligation.responsible_party || 'Signer')}</span>
                    <span class="obligation-importance obligation-${escapeHtml((obligation.importance || 'medium').toLowerCase())}">
                        ${escapeHtml(obligation.importance || 'medium')}
                    </span>
                </div>
                <div class="obligation-action">${escapeHtml(obligation.action || 'No action captured')}</div>
                <div class="obligation-meta">
                    <span>${escapeHtml(obligation.section || 'Unknown section')}</span>
                    <span>${escapeHtml(obligation.due_or_trigger || 'Not clearly stated')}</span>
                </div>
            </div>
        `;
    });
}

function displayQuestions(questions) {
    const questionsContent = document.getElementById('questionsContent');
    questionsContent.innerHTML = '';

    if (!questions || questions.length === 0) {
        questionsContent.innerHTML = '<li>No suggested follow-up questions were generated.</li>';
        return;
    }

    questions.forEach(question => {
        questionsContent.innerHTML += `<li>${escapeHtml(question)}</li>`;
    });
}

function displayGlossary(glossary) {
    const glossaryContent = document.getElementById('glossaryContent');
    glossaryContent.innerHTML = '';

    if (!glossary || glossary.length === 0) {
        glossaryContent.innerHTML = renderEmptyState('No glossary terms were detected in this document');
        return;
    }

    glossary.forEach(item => {
        glossaryContent.innerHTML += `
            <div class="glossary-item">
                <strong>${escapeHtml(item.term || 'Term')}</strong>
                <p>${escapeHtml(item.meaning || 'Meaning unavailable')}</p>
            </div>
        `;
    });
}

/**
 * Show loading state
 */
function showLoading() {
    uploadSection.classList.add('hidden');
    loadingSection.classList.remove('hidden');
    resultsSection.classList.add('hidden');
    errorSection.classList.add('hidden');
}

/**
 * Show error message
 */
function showError(message) {
    uploadSection.classList.add('hidden');
    loadingSection.classList.add('hidden');
    resultsSection.classList.add('hidden');
    errorSection.classList.remove('hidden');
    errorContent.textContent = message;
}

/**
 * Reset UI to initial state
 */
function resetUI() {
    uploadSection.classList.remove('hidden');
    loadingSection.classList.add('hidden');
    resultsSection.classList.add('hidden');
    errorSection.classList.add('hidden');
    fileInput.value = '';
    selectedFile.classList.add('hidden');
    selectedFileName.textContent = 'No file selected';
    analysisResults = null;
}

/**
 * Download analysis report as JSON
 */
function downloadReport() {
    if (!analysisResults) return;
    
    const dataStr = JSON.stringify(analysisResults, null, 2);
    const dataBlob = new Blob([dataStr], { type: 'application/json' });
    const url = URL.createObjectURL(dataBlob);
    
    const link = document.createElement('a');
    link.href = url;
    link.download = `legal-analysis-${new Date().toISOString().split('T')[0]}.json`;
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
    URL.revokeObjectURL(url);
}

/**
 * Utility: Format label text (snake_case to Title Case)
 */
function formatLabel(text) {
    return text
        .split('_')
        .map(word => word.charAt(0).toUpperCase() + word.slice(1))
        .join(' ');
}

/**
 * Utility: Render a consistent empty state block
 */
function renderEmptyState(message) {
    return `<div class="empty-state">${escapeHtml(message)}</div>`;
}

/**
 * Utility: Show selected file details before upload completes
 */
function updateSelectedFile(file) {
    if (!file) {
        selectedFile.classList.add('hidden');
        selectedFileName.textContent = 'No file selected';
        return;
    }

    selectedFile.classList.remove('hidden');
    selectedFileName.textContent = `${file.name} • ${formatFileSize(file.size)}`;
}

/**
 * Utility: Format bytes as a readable string
 */
function formatFileSize(bytes) {
    if (!Number.isFinite(bytes) || bytes <= 0) {
        return '0 KB';
    }

    if (bytes >= 1024 * 1024) {
        return `${(bytes / (1024 * 1024)).toFixed(2)} MB`;
    }

    return `${(bytes / 1024).toFixed(2)} KB`;
}

/**
 * Utility: Escape HTML special characters
 */
function escapeHtml(text) {
    const value = String(text ?? '');
    const map = {
        '&': '&amp;',
        '<': '&lt;',
        '>': '&gt;',
        '"': '&quot;',
        "'": '&#039;'
    };
    return value.replace(/[&<>"']/g, m => map[m]);
}

console.log('Legal Document Analyzer Frontend Loaded');
