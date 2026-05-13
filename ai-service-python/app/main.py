"""
Legal Document Analyzer - AI Service
Python Flask microservice for NLP-based legal document analysis
"""

import json
import logging
import os
from flask import Flask, request, jsonify
from flask_cors import CORS
from transformers import pipeline
import torch
import re
from datetime import datetime

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = Flask(__name__)
CORS(app)

# Global NLP pipelines (loaded on startup)
nlp_models = {}

CLAUSE_TYPES = [
    'liability',
    'termination',
    'penalty',
    'indemnification',
    'confidentiality',
    'dispute resolution',
    'payment terms',
    'governing law'
]

CLAUSE_KEYWORDS = {
    'liability': ['liable', 'liability', 'damages', 'loss', 'consequential', 'indirect'],
    'termination': ['termination', 'terminate', 'terminated', 'expiry', 'expire', 'notice period', 'vacate'],
    'penalty': ['penalty', 'fine', 'damages', 'late payment', 'forfeit', 'liquidated'],
    'indemnification': ['indemnify', 'indemnification', 'hold harmless'],
    'confidentiality': ['confidential', 'confidentiality', 'non-disclosure', 'secret', 'proprietary information', 'disclose'],
    'dispute resolution': ['arbitration', 'dispute', 'conciliation', 'settled amicably', 'courts'],
    'payment terms': ['payment', 'rent', 'salary', 'deposit', 'fee', 'consideration', 'installment'],
    'governing law': ['governing law', 'jurisdiction', 'indian contract act', 'bns', 'laws of india']
}

SECTION_HEADING_HINTS = {
    'termination': ['termination', 'expiry', 'end of term'],
    'payment terms': ['rent', 'payment', 'remuneration', 'salary', 'deposit', 'consideration'],
    'liability': ['liability'],
    'indemnification': ['indemnification', 'indemnity'],
    'confidentiality': ['confidentiality', 'non-disclosure'],
    'dispute resolution': ['dispute', 'arbitration'],
    'governing law': ['governing law', 'jurisdiction'],
    'penalty': ['penalty', 'liquidated damages']
}

CLAUSE_THRESHOLDS = {
    'default': 0.56,
    'confidentiality': 0.62,
    'indemnification': 0.60
}

RESTRICTIVE_CONFIDENTIALITY_PATTERNS = [
    r'\bshall not disclose\b',
    r'\bmust not disclose\b',
    r'\bshall keep .* confidential\b',
    r'\bsole(?:ly)? for (?:the )?(?:purpose|benefit)\b',
    r'\bsole and exclusive benefit\b',
    r'\bexclusive benefit\b',
    r'\breturn (?:all )?(?:documents|materials|information)\b',
    r'\bdestroy (?:all )?(?:documents|materials|information)\b',
    r'\bnot (?:copy|duplicate|use|share)\b'
]

USER_RISK_TITLES = {
    'financial_risk': 'Financial exposure for the signer',
    'legal_risk': 'Legal exposure for the signer',
    'one_sided_risk': 'The clause favors the other party',
    'restriction_risk': 'The clause limits what the signer can do',
    'ambiguity_risk': 'The clause is unclear or open-ended',
    'missing_protection': 'The contract is missing a key protection',
    'exit_risk': 'The signer may face difficulty exiting the contract',
    'financial_lock_in_risk': 'The signer may have money tied up or delayed'
}

CLAUSE_TO_USER_RISK = {
    'payment terms': 'financial_risk',
    'penalty': 'financial_risk',
    'termination': 'exit_risk',
    'liability': 'legal_risk',
    'indemnification': 'legal_risk',
    'confidentiality': 'restriction_risk',
    'dispute resolution': 'legal_risk',
    'governing law': 'legal_risk'
}

# Legal keywords mapping for Indian context
INDIAN_LEGAL_KEYWORDS = {
    'liability': ['liability', 'liable', 'responsible', 'dayitva', 'zimmedari'],
    'termination': ['termination', 'terminate', 'samaapt', 'khatam', 'notics period'],
    'penalty': ['penalty', 'fine', 'dand', 'punitive damages', 'fine amount'],
    'indemnification': ['indemnify', 'hold harmless', 'raksha', 'pratiksha'],
    'confidentiality': ['confidential', 'secret', 'proprietary', 'rahasy'],
    'dispute': ['dispute', 'arbitration', 'litigation', 'rift', 'vivaad'],
    'payment': ['payment', 'fee', 'consideration', 'bhugtan', 'remunaration'],
    'governing_law': ['Indian Contract Act', 'BNS', 'Bharatiya Nyaya Sanhita', 'jurisdiction'],
    'default': ['default', 'breach', 'violation', 'utlanghan', 'ulhanghan']
}

LEGAL_TERM_GLOSSARY = {
    'indemnity': 'A promise to cover someone else for certain losses or claims.',
    'indemnify': 'To protect another party from certain losses, claims, or legal costs.',
    'liability': 'Legal responsibility for damage, loss, or breach.',
    'termination': 'How and when the contract can end.',
    'breach': 'A failure to do what the contract requires.',
    'jurisdiction': 'The court or legal place that can hear disputes.',
    'arbitration': 'A private dispute process instead of a normal court case.',
    'governing law': 'The law used to interpret the contract.',
    'confidentiality': 'A duty to keep certain information private.',
    'notice period': 'The amount of advance warning required before taking an action.',
    'liquidated damages': 'A fixed amount payable if a specific breach happens.',
    'security deposit': 'Money held as protection against damage, default, or dues.',
    'force majeure': 'Events outside a party’s control that may excuse delays or non-performance.',
    'warranty': 'A promise that something will meet a stated standard.',
    'specific performance': 'A court order forcing a party to do what it agreed to do.'
}

OBLIGATION_PATTERNS = [
    r'\bshall\b',
    r'\bmust\b',
    r'\bagrees? to\b',
    r'\bis required to\b',
    r'\bwill pay\b',
    r'\bmay terminate\b',
    r'\bshall pay\b'
]

def initialize_models():
    """Initialize all NLP models on startup"""
    global nlp_models
    try:
        logger.info("Loading NLP models...")
        
        # Summarization pipeline
        nlp_models['summarizer'] = pipeline(
            "summarization",
            model="sshleifer/distilbart-cnn-12-6",
            device=0 if torch.cuda.is_available() else -1
        )
        
        # Zero-shot classification for clause types
        nlp_models['zero_shot_classifier'] = pipeline(
            "zero-shot-classification",
            model="valhalla/distilbart-mnli-12-3",
            device=0 if torch.cuda.is_available() else -1
        )

        logger.info("Models loaded successfully")
        return True
    except Exception as e:
        logger.error(f"Error loading models: {str(e)}")
        return False

def chunk_text(text, max_chunk_length=1024):
    """Split text into chunks for processing"""
    sentences = re.split(r'(?<=[.!?])\s+', text)
    chunks = []
    current_chunk = ""
    
    for sentence in sentences:
        if len(current_chunk) + len(sentence) < max_chunk_length:
            current_chunk += " " + sentence
        else:
            if current_chunk:
                chunks.append(current_chunk.strip())
            current_chunk = sentence
    
    if current_chunk:
        chunks.append(current_chunk.strip())
    
    return chunks

def normalize_whitespace(text):
    return re.sub(r'\s+', ' ', text or '').strip()

def split_into_legal_sections(text):
    """Split legal text into section-like blocks using headings and numbering."""
    lines = [line.strip() for line in text.splitlines()]
    sections = []
    current_lines = []
    current_heading = "Preamble"

    def flush():
        nonlocal current_lines, current_heading
        content = '\n'.join(line for line in current_lines if line).strip()
        if content:
            sections.append({
                'heading': current_heading,
                'text': content
            })
        current_lines = []

    for raw_line in lines:
        if not raw_line:
            if current_lines and current_lines[-1] != '':
                current_lines.append('')
            continue

        is_numbered_heading = bool(re.match(r'^\d+(?:\.\d+)*[\).\s-]+[A-Za-z]', raw_line))
        is_upper_heading = raw_line.isupper() and 3 <= len(raw_line.split()) <= 8

        if is_numbered_heading or is_upper_heading:
            flush()
            current_heading = raw_line
            current_lines = [raw_line]
        else:
            current_lines.append(raw_line)

    flush()

    if not sections:
        return [{'heading': 'Document', 'text': text.strip()}]

    return sections

def infer_clause_type_from_heading(heading):
    heading_lower = heading.lower()
    for clause_type, hints in SECTION_HEADING_HINTS.items():
        if any(hint in heading_lower for hint in hints):
            return clause_type
    return None

def keyword_score(text, clause_type):
    text_lower = text.lower()
    return sum(1 for keyword in CLAUSE_KEYWORDS.get(clause_type, []) if keyword in text_lower)

def section_definition_density(text):
    lower_text = text.lower()
    definition_markers = [
        '" means',
        "' means",
        'shall mean',
        'means ',
        'includes',
        'include '
    ]
    hits = sum(lower_text.count(marker) for marker in definition_markers)
    return hits / max(1, len(text.split()) / 40)

def is_definition_heavy(text, heading=''):
    heading_lower = heading.lower()
    if any(token in heading_lower for token in ['definition', 'interpretation']):
        return True
    return section_definition_density(text) > 1.5

def score_clause_candidates(text):
    return {
        clause_type: keyword_score(text, clause_type)
        for clause_type in CLAUSE_TYPES
    }

def detect_clause_type(section_text, heading):
    """Use heading hints first, then zero-shot classification with a rejection threshold."""
    heading_label = infer_clause_type_from_heading(heading)
    if heading_label:
        return {
            'type': heading_label,
            'confidence': 0.95,
            'severity_level': 'high',
            'explanation': f"Detected from section heading '{heading}'",
            'is_risky': heading_label in ['liability', 'penalty', 'termination']
        }

    try:
        result = nlp_models['zero_shot_classifier'](
            section_text[:700],
            CLAUSE_TYPES,
            multi_label=False
        )

        top_label = result['labels'][0]
        top_score = float(result['scores'][0])
        second_score = float(result['scores'][1]) if len(result['scores']) > 1 else 0.0
        margin = top_score - second_score
        candidate_scores = score_clause_candidates(section_text)
        keyword_hits = candidate_scores.get(top_label, 0)
        boosted_score = top_score + (0.04 * min(keyword_hits, 2))
        min_threshold = CLAUSE_THRESHOLDS.get(top_label, CLAUSE_THRESHOLDS['default'])

        if keyword_hits == 0 and boosted_score < (min_threshold + 0.04):
            return None

        if top_label == 'confidentiality' and keyword_hits < 2 and 'confidential' not in section_text.lower():
            return None

        if top_label == 'indemnification' and not re.search(r'\b(indemn\w+|hold harmless)\b', section_text, re.IGNORECASE):
            return None

        if boosted_score < min_threshold or margin < 0.10:
            return None

        severity = 'high' if boosted_score > 0.72 else ('medium' if boosted_score > 0.58 else 'low')
        return {
            'type': top_label,
            'confidence': min(boosted_score, 0.99),
            'severity_level': severity,
            'explanation': f"Detected {top_label} clause with {top_score:.1%} confidence",
            'is_risky': boosted_score > 0.6 and top_label in ['liability', 'penalty', 'termination']
        }
    except Exception as e:
        logger.warning(f"Classification error for section '{heading}': {str(e)}")
        return None

def has_termination_language(text):
    termination_patterns = [
        r'\btermination\b',
        r'\bterminate(?:d|s|ion)?\b',
        r'\bexpiry\b',
        r'\bexpire(?:s|d)?\b',
        r'\bnotice period\b',
        r'\bwritten notice\b',
        r'\bcease\b',
        r'\bvacate\b'
    ]
    text_lower = text.lower()
    return any(re.search(pattern, text_lower) for pattern in termination_patterns)

def extract_locations(text):
    locations = []
    location_patterns = [
        r'(?:residing at|resident of|registered office at|situated at|place of arbitration shall be|courts of)\s+([^.;\n]+)',
        r'\b(?:New Delhi|Delhi|Mumbai|Navi Mumbai|Bangalore|Bengaluru|Chennai|Hyderabad|Pune|Kolkata)\b'
    ]

    for pattern in location_patterns:
        matches = re.findall(pattern, text, re.IGNORECASE)
        for match in matches:
            value = normalize_whitespace(match if isinstance(match, str) else ' '.join(match))
            if value and value not in locations:
                locations.append(value[:120])

    return locations

def deduplicate_preserve_order(items):
    seen = set()
    result = []
    for item in items:
        normalized = normalize_whitespace(item)
        if normalized and normalized.lower() not in seen:
            seen.add(normalized.lower())
            result.append(normalized)
    return result

def detect_document_context(text):
    lower_text = (text or '').lower()
    if any(token in lower_text for token in ['tenant', 'landlord', 'lease', 'rent']):
        return 'tenant'
    if any(token in lower_text for token in ['employee', 'employer', 'employment']):
        return 'employee'
    if any(token in lower_text for token in ['buyer', 'seller', 'purchase']):
        return 'buyer'
    return 'signer'

def user_label_for_context(context):
    return {
        'tenant': 'tenant',
        'employee': 'employee',
        'buyer': 'buyer',
        'signer': 'signer'
    }.get(context, 'signer')

def other_party_label_for_context(context):
    return {
        'tenant': 'landlord',
        'employee': 'employer',
        'buyer': 'seller',
        'signer': 'other party'
    }.get(context, 'other party')

def detect_document_type(text):
    lower_text = (text or '').lower()
    document_signals = {
        'Rental / Lease Agreement': ['tenant', 'landlord', 'lease', 'rent', 'security deposit'],
        'Employment Agreement': ['employee', 'employer', 'salary', 'employment', 'termination of employment'],
        'Non-Disclosure Agreement': ['confidentiality', 'confidential information', 'non-disclosure'],
        'Service Agreement': ['services', 'service provider', 'scope of work', 'deliverables'],
        'Sale / Purchase Agreement': ['buyer', 'seller', 'purchase price', 'agreement of sale']
    }

    scored = []
    for label, keywords in document_signals.items():
        score = sum(1 for keyword in keywords if keyword in lower_text)
        scored.append((score, label))

    scored.sort(reverse=True)
    return scored[0][1] if scored and scored[0][0] > 0 else 'General Legal Agreement'

def compute_readability_band(text):
    sentences = [segment.strip() for segment in re.split(r'[.!?]+', text or '') if segment.strip()]
    words = re.findall(r'\b\w+\b', text or '')
    average_sentence_length = len(words) / max(1, len(sentences))

    if average_sentence_length >= 28:
        return 'complex'
    if average_sentence_length >= 20:
        return 'moderate'
    return 'accessible'

def compute_analysis_confidence(text, clauses, risks, entities):
    section_count = len(split_into_legal_sections(text))
    entity_score = min(3, len(entities.get('parties', [])) + len(entities.get('dates', [])) + len(entities.get('amounts', [])))
    clause_score = min(4, len(clauses))
    risk_score = min(3, len(risks))
    structure_bonus = 2 if section_count >= 4 else 1 if section_count >= 2 else 0
    total_score = entity_score + clause_score + risk_score + structure_bonus

    if total_score >= 9:
        return {'label': 'high', 'score': 0.89}
    if total_score >= 6:
        return {'label': 'medium', 'score': 0.74}
    return {'label': 'low', 'score': 0.58}

def build_risk(
    risk_type,
    severity_level,
    affected_clause,
    recommendation,
    clause,
    why_this_is_risky,
    impact_on_user,
    what_user_should_check,
    risk_title=None
):
    return {
        'type': risk_type,
        'risk_category': risk_type,
        'risk_title': risk_title or USER_RISK_TITLES.get(risk_type, 'Contract risk for the signer'),
        'description': why_this_is_risky,
        'severity_level': severity_level,
        'affected_clause': affected_clause,
        'recommendation': recommendation,
        'clause': clause,
        'why_this_is_risky': why_this_is_risky,
        'impact_on_user': impact_on_user,
        'what_user_should_check': what_user_should_check
    }

def contains_money_reference(text):
    return bool(re.search(r'(?:Rs\.?|₹|\$)\s*[\d,]+', text or '', re.IGNORECASE))

def mentions_other_party_control(text, other_party_label):
    signals = [
        'sole discretion',
        'exclusive right',
        'sole and exclusive benefit',
        'sole benefit',
        'exclusive benefit',
        'sole remedy',
        f'only the {other_party_label}'
    ]
    lower_text = (text or '').lower()
    return any(signal in lower_text for signal in signals)

def generate_clause_risk(section_text, heading, clause_type, context):
    user_label = user_label_for_context(context)
    other_party_label = other_party_label_for_context(context)
    combined = f"{heading} {section_text}".lower()
    affected_clause = heading[:100] if heading else clause_type
    clause_excerpt = section_text[:170]

    if clause_type == 'payment terms':
        if re.search(r'\bdeposit\b', combined) and contains_money_reference(combined):
            return build_risk(
                'financial_lock_in_risk',
                'medium',
                affected_clause,
                'Check when the deposit must be returned, what deductions are allowed, and whether the refund timeline is clearly written.',
                clause_excerpt,
                f"This clause may require the {user_label} to pay money upfront and wait for the other party to return it later.",
                f"The {user_label} may face cash flow pressure or have difficulty recovering the deposit if deductions are broad or unclear.",
                'Look for refund conditions, deduction rights, timelines, and proof required for recovery.',
                'Deposit or advance payment may be hard to recover'
            )
        if contains_money_reference(combined):
            return build_risk(
                'financial_risk',
                'medium',
                affected_clause,
                'Check the due dates, extra charges, interest, taxes, and whether the payment terms can change later.',
                clause_excerpt,
                f"This clause imposes a payment obligation on the {user_label}.",
                f"If the amount, timing, or extra charges are strict, the {user_label} may face payment pressure or default risk.",
                'Confirm the total payable amount, due date, penalties, and whether any charges are hidden.',
                'Payment obligation may increase the signer\'s financial burden'
            )

    if clause_type == 'termination':
        return build_risk(
            'exit_risk',
            'medium',
            affected_clause,
            'Check who can terminate, how much notice is required, and whether refunds, dues, or return obligations are clearly addressed.',
            clause_excerpt,
            f"This clause controls how the {user_label} can exit the contract or be removed from it.",
            f"If the {other_party_label} has stronger termination rights, the {user_label} may lose money, access, possession, or continuity on short notice.",
            'Check for equal termination rights, notice periods, cure opportunities, and post-termination obligations.',
            'Termination terms may put the signer at a disadvantage'
        )

    if clause_type in ['liability', 'indemnification']:
        return build_risk(
            'legal_risk',
            'high',
            affected_clause,
            'Check whether liability is capped, whether the indemnity is one-sided, and what events trigger payment or legal responsibility.',
            clause_excerpt,
            f"This clause can make the {user_label} legally or financially responsible if something goes wrong.",
            f"The {user_label} may have to bear losses, damages, claims, or legal costs, sometimes even beyond the contract value.",
            'Look for liability caps, exclusions, one-sided indemnity language, and whether indirect losses are covered.',
            'Liability or indemnity exposure may be broad'
        )

    if clause_type == 'confidentiality':
        return build_risk(
            'restriction_risk',
            'medium',
            affected_clause,
            'Check what information is covered, how long the obligation lasts, and whether ordinary use or disclosure is unreasonably restricted.',
            clause_excerpt,
            f"This clause limits what the {user_label} can share, use, or keep after signing.",
            f"If the restriction is broad, the {user_label} could face breach claims for ordinary business or personal conduct.",
            'Look for the scope of confidential information, duration, return obligations, and exceptions for legal disclosure.',
            'Confidentiality duties may be too restrictive'
        )

    if clause_type in ['dispute resolution', 'governing law']:
        return build_risk(
            'legal_risk',
            'medium',
            affected_clause,
            'Check where disputes must be resolved, whether arbitration and court clauses are consistent, and whether the venue is practical for you.',
            clause_excerpt,
            f"This clause decides how the {user_label} must enforce rights or defend a dispute.",
            f"If the chosen process or location favors the {other_party_label}, the {user_label} may face higher cost and inconvenience.",
            'Look for exclusive jurisdiction, arbitration seat, governing law, and any mismatch between arbitration and court clauses.',
            'Dispute handling terms may be difficult for the signer'
        )

    return None

def extract_sections(text):
    """Extract document sections based on common legal structure"""
    sections = split_into_legal_sections(text)
    return {section['heading']: 1 for section in sections}

def extract_entities(text):
    """Extract key entities from legal document"""
    entities = {
        'parties': [],
        'dates': [],
        'amounts': [],
        'locations': [],
        'sections_found': 0
    }
    
    # Extract dates (basic pattern)
    date_patterns = [
        r'\d{1,2}[-/]\d{1,2}[-/]\d{4}',  # DD/MM/YYYY
        r'\d{4}[-/]\d{1,2}[-/]\d{1,2}',  # YYYY/MM/DD
        r'(?:January|February|March|April|May|June|July|August|September|October|November|December)\s+\d{1,2},?\s+\d{4}',
        r'\d{1,2}(?:st|nd|rd|th)\s+day of\s+(?:January|February|March|April|May|June|July|August|September|October|November|December),?\s+\d{4}'
    ]
    
    for pattern in date_patterns:
        dates = re.findall(pattern, text, re.IGNORECASE)
        entities['dates'].extend(dates)
    
    # Extract amounts (basic pattern)
    amount_patterns = [
        r'Rs\.?\s*[\d,]+(?:\.\d{2})?',
        r'₹\s*[\d,]+(?:\.\d{2})?',
        r'\$\s*[\d,]+(?:\.\d{2})?'
    ]
    
    for pattern in amount_patterns:
        amounts = re.findall(pattern, text)
        entities['amounts'].extend(amounts)
    
    # Extract parties using multiple common legal formats
    party_patterns = [
        r'BETWEEN\s+(.*?)\s+\(Hereinafter.*?\)\s+AND\s+(.*?)\s+\(Hereinafter',
        r'Between\s+(.*?)\s+(?:and|&)\s+(.*?)(?:Whereas|dated|WHEREAS)',
        r'FOR THE COMPANY:\s+[_\s]*([A-Za-z .]+).*?FOR THE EMPLOYEE:\s+[_\s]*([A-Za-z .]+)',
        r'LANDLORD:\s+[_\s]*([A-Za-z .]+).*?TENANT:\s+[_\s]*([A-Za-z .]+)'
    ]

    for pattern in party_patterns:
        match = re.search(pattern, text, re.IGNORECASE | re.DOTALL)
        if match:
            groups = [normalize_whitespace(group)[:120] for group in match.groups()]
            entities['parties'].extend(groups)

    entities['dates'] = deduplicate_preserve_order(entities['dates'])
    entities['amounts'] = deduplicate_preserve_order(entities['amounts'])
    entities['parties'] = deduplicate_preserve_order(entities['parties'])
    entities['locations'] = extract_locations(text)
    entities['sections_found'] = len(split_into_legal_sections(text))
    
    return entities

def classify_clauses(text):
    """Classify clauses in the document"""
    clauses = []

    sections = split_into_legal_sections(text)

    for index, section in enumerate(sections[:25], start=1):
        section_text = normalize_whitespace(section['text'])
        if len(section_text) < 60:
            continue

        detected = detect_clause_type(section_text, section['heading'])
        if detected:
            clauses.append({
                'type': detected['type'],
                'text': section_text[:240],
                'section': section['heading'] if section['heading'] else f"Section {index}",
                'severity_level': detected['severity_level'],
                'confidence': float(detected['confidence']),
                'explanation': detected['explanation'],
                'is_risky': detected['is_risky']
            })
    
    return clauses

def summarize_text(text):
    """Generate abstractive summary of document"""
    try:
        sections = split_into_legal_sections(text)
        if not sections:
            return "Unable to summarize empty document"

        meaningful_sections = [
            section for section in sections
            if len(normalize_whitespace(section['text'])) > 80 and not is_definition_heavy(section['text'], section['heading'])
        ]
        selected_sections = meaningful_sections[:2]
        if len(meaningful_sections) > 3:
            selected_sections.append(meaningful_sections[len(meaningful_sections) // 2])
        if meaningful_sections:
            selected_sections.append(meaningful_sections[-1])

        if not selected_sections:
            selected_sections = sections[:3]

        unique_section_texts = []
        seen_texts = set()
        for section in selected_sections:
            normalized = normalize_whitespace(section['text'])
            if normalized and normalized not in seen_texts:
                seen_texts.add(normalized)
                unique_section_texts.append(normalized)

        chunk_summaries = []
        for chunk in unique_section_texts[:4]:
            summary_result = nlp_models['summarizer'](
                chunk[:1000],
                max_length=75,
                min_length=22,
                do_sample=False
            )
            if summary_result:
                chunk_summaries.append(summary_result[0]['summary_text'])

        if not chunk_summaries:
            return "No summary available"

        if len(chunk_summaries) == 1:
            return chunk_summaries[0]

        combined = " ".join(chunk_summaries)
        final_summary = nlp_models['summarizer'](
            combined[:1200],
            max_length=95,
            min_length=32,
            do_sample=False
        )
        return final_summary[0]['summary_text'] if final_summary else combined[:500]
    except Exception as e:
        logger.error(f"Summarization error: {str(e)}")
        return f"Summary generation failed: {str(e)}"

def simplify_text(text):
    """Generate a more readable plain-English explanation."""
    simplification_map = {
        r'\bhereunto\b': 'to this',
        r'\bhereby\b': 'by this',
        r'\bwherefore\b': 'for this reason',
        r'\bheretofore\b': 'before now',
        r'\bahereafter\b': 'from now on',
        r'\bnotwithstanding\b': 'despite',
        r'\bpursuant to\b': 'according to',
        r'\bin accordance with\b': 'as per',
        r'\bindemnify\b': 'protect from harm',
        r'\bladministration\b': 'management',
        r'\bvendor\b': 'seller',
        r'\bcontractee\b': 'person hired',
        r'\bvizard\b': 'that is',
        r'\bstipulated\b': 'agreed',
        r'\bseverally\b': 'separately',
        r'\bjointly and severally\b': 'together and separately'
    }

    simplified = text
    for legal_term, plain_term in simplification_map.items():
        simplified = re.sub(legal_term, plain_term, simplified, flags=re.IGNORECASE)

    sections = split_into_legal_sections(simplified)
    explanations = []
    seen_clause_types = set()

    for section in sections[:8]:
        heading = normalize_whitespace(section['heading'])
        body = normalize_whitespace(section['text'])
        if len(body) < 40:
            continue

        detected = detect_clause_type(body, heading) if len(body) >= 60 else None
        if detected:
            clause_type = detected['type']
            if clause_type in seen_clause_types and len(explanations) >= 3:
                continue
            seen_clause_types.add(clause_type)
            short_body = body[:150].rstrip(' ,.;:')
            if clause_type == 'confidentiality':
                explanation = f"{heading}: This clause explains what information must be kept private and how it may be used or shared."
            elif clause_type == 'termination':
                explanation = f"{heading}: This clause explains how the agreement can end and what notice or conditions must be met."
            elif clause_type == 'payment terms':
                explanation = f"{heading}: This clause describes what must be paid, when it is due, and any related financial conditions."
            elif clause_type == 'dispute resolution':
                explanation = f"{heading}: This clause explains how disagreements will be resolved and where disputes may be taken."
            elif clause_type == 'indemnification':
                explanation = f"{heading}: This clause says who must protect the other party from certain losses, claims, or legal costs."
            elif clause_type == 'liability':
                explanation = f"{heading}: This clause sets limits on who is responsible if something goes wrong."
            else:
                explanation = f"{heading}: In simple terms, this part says {short_body}."
            explanations.append(explanation)
        else:
            short_body = body[:130].rstrip(' ,.;:')
            explanations.append(f"{heading}: In simple terms, this part says {short_body}.")

        if len(explanations) >= 5:
            break

    if explanations:
        return " ".join(explanations)[:2200]

    return simplified[:2000]

def analyze_risks(text):
    """Analyze and identify signer-focused risks in the document."""
    risks = []
    sections = split_into_legal_sections(text)
    section_map = [(section['heading'], normalize_whitespace(section['text'])) for section in sections]
    full_text = '\n'.join(section_text for _, section_text in section_map)
    context = detect_document_context(full_text)
    has_termination = any(
        infer_clause_type_from_heading(heading) == 'termination' or has_termination_language(section_text)
        for heading, section_text in section_map
    )
    has_dispute_resolution = any(
        infer_clause_type_from_heading(heading) == 'dispute resolution'
        or re.search(r'\b(arbitration|arbitrator|dispute|conciliation|courts?)\b', section_text, re.IGNORECASE)
        for heading, section_text in section_map
    )
    has_notice = any(
        re.search(r'\bnotice\b', f"{heading} {section_text}", re.IGNORECASE)
        for heading, section_text in section_map
    )

    for heading, section_text in section_map:
        combined = f"{heading} {section_text}".lower()
        clause_type = infer_clause_type_from_heading(heading)
        if not clause_type:
            detected = detect_clause_type(section_text, heading)
            clause_type = detected['type'] if detected else None

        if clause_type:
            mapped_risk = generate_clause_risk(section_text, heading, clause_type, context)
            if mapped_risk:
                risks.append(mapped_risk)

        penalty_match = re.search(r'(?:penalty|fine|damages?).{0,80}?(?:Rs\.?|₹)\s*[\d,]+', combined, re.IGNORECASE)
        if penalty_match:
            risks.append(build_risk(
                'financial_risk',
                'high',
                penalty_match.group(0)[:100],
                'Check the penalty trigger, grace period, cap, and whether the amount could be challenged as excessive or unfair in practice.',
                section_text[:150],
                'This clause can increase the signer\'s payment burden through a penalty, fine, or damages amount.',
                'Even a short delay or breach could become expensive for the signer, especially if the amount keeps increasing.',
                'Verify whether the penalty is proportional, whether it applies automatically, and whether Indian-law reasonableness concerns may arise.',
                'Penalty or damages clause may become costly for the signer'
            ))

        if re.search(r'\b(?:deposit|security deposit|advance)\b', combined, re.IGNORECASE) and contains_money_reference(combined):
            risks.append(build_risk(
                'financial_lock_in_risk',
                'medium',
                heading[:100],
                'Check refund conditions, deductions, supporting records, and whether there is a firm deadline for return of the money.',
                section_text[:150],
                'This clause may lock up the signer\'s money as a deposit, security amount, or advance payment.',
                'The signer may struggle to recover the money if the other party has broad deduction rights or the refund process is vague.',
                'Look for refund timing, deduction grounds, inspection rights, and proof requirements.',
                'Deposit recovery may be uncertain'
            ))

        if (
            mentions_other_party_control(combined, other_party_label_for_context(context))
            or ('termination' in combined and 'only' in combined and 'notice' in combined)
        ):
            other_party = other_party_label_for_context(context)
            risks.append(build_risk(
                'one_sided_risk',
                'medium',
                heading[:100],
                'Check whether the same rights, remedies, and decision-making powers are available to both sides.',
                section_text[:150],
                f'This clause appears to give the {other_party} more control than the signer.',
                'If a dispute or breach occurs, the signer may have fewer rights, remedies, or negotiation options.',
                'Look for exclusive rights, sole discretion, unilateral termination, or benefits reserved only for the other party.',
                'The other party may have stronger contractual control'
            ))

        confidentiality_signal = (
            infer_clause_type_from_heading(heading) == 'confidentiality'
            or keyword_score(section_text, 'confidentiality') >= 2
        )
        restrictive_match = None
        if confidentiality_signal:
            for pattern in RESTRICTIVE_CONFIDENTIALITY_PATTERNS:
                restrictive_match = re.search(pattern, combined, re.IGNORECASE)
                if restrictive_match:
                    break

        if restrictive_match:
            risks.append(build_risk(
                'restriction_risk',
                'medium',
                restrictive_match.group(0)[:100],
                'Check whether the restrictions are necessary, limited in scope, and supported by practical exceptions.',
                section_text[:150],
                'This clause restricts what the signer can disclose, use, keep, or return.',
                'The signer may face breach allegations if the restriction is too broad or continues for too long.',
                'Look for scope, duration, exceptions, and whether return or deletion duties are realistic.',
                'Strict confidentiality or use restrictions may limit the signer'
            ))

        if re.search(r'\b(indefinite|perpetual|forever)\b', combined, re.IGNORECASE):
            risks.append(build_risk(
                'restriction_risk',
                'medium',
                heading[:100],
                'Check whether the obligation has a clear end date or review mechanism.',
                section_text[:150],
                'This clause creates an obligation that may continue indefinitely or for an unusually long time.',
                'The signer may remain bound long after the main commercial purpose has ended.',
                'Ask whether the duration can be limited, renewed expressly, or tied to a clear event.',
                'The signer may be locked into a long-running obligation'
            ))

        if re.search(r'\b(reasonable efforts|sole discretion|as deemed necessary|from time to time)\b', combined, re.IGNORECASE):
            risks.append(build_risk(
                'ambiguity_risk',
                'low',
                heading[:100],
                'Ask for objective standards, timelines, and defined triggers instead of open-ended wording.',
                section_text[:150],
                'This clause uses vague or subjective language that can be interpreted in different ways.',
                'If the contract is enforced later, the signer may face uncertainty about what was actually required.',
                'Look for undefined standards, discretionary language, and terms that do not explain when or how they apply.',
                'Unclear wording may later be used against the signer'
            ))

        if re.search(r'\b(unlimited liability|without limitation|all losses whatsoever)\b', combined, re.IGNORECASE):
            risks.append(build_risk(
                'legal_risk',
                'high',
                heading[:100],
                'Check whether liability is capped to a realistic amount and whether indirect or remote losses are excluded.',
                section_text[:150],
                'This clause may expose the signer to very broad liability.',
                'The signer could face claims larger than the contract value or beyond what was reasonably expected.',
                'Look for liability caps, exclusions, and whether the clause is one-sided.',
                'Liability may be unlimited or too broad'
            ))

        if re.search(r'\b(indemnif\w+|hold harmless)\b', combined, re.IGNORECASE) and not re.search(r'\bneither party\b|\bboth parties\b', combined, re.IGNORECASE):
            risks.append(build_risk(
                'legal_risk',
                'high',
                heading[:100],
                'Check whether the indemnity is mutual, limited to direct losses, and tied to clear trigger events.',
                section_text[:150],
                'This clause may require the signer to protect the other party against claims or losses.',
                'The signer may have to pay legal costs, damages, or third-party claims even where responsibility is disputed.',
                'Look for who indemnifies whom, what losses are covered, and whether there is a monetary cap.',
                'Indemnity may shift legal and financial burden to the signer'
            ))

        if re.search(r'\bcourts? of [a-z ]+\b', combined, re.IGNORECASE):
            risks.append(build_risk(
                'one_sided_risk',
                'medium',
                heading[:100],
                'Check whether the selected court city is workable for you and whether it matches the arbitration clause, if any.',
                section_text[:150],
                'This clause chooses a court location for disputes.',
                'If the location is inconvenient, the signer may spend more time and money enforcing rights or defending a case.',
                'Look for exclusive jurisdiction wording, venue mismatch, and whether the location was chosen mainly for the other party\'s convenience.',
                'Dispute venue may be inconvenient for the signer'
            ))

    # Check for missing critical clauses only after structural and phrase-based review
    if not has_termination:
        risks.insert(0, build_risk(
            'missing_protection',
            'critical',
            'N/A',
            'Add clear termination rights, notice periods, cure rights, and settlement steps before signing.',
            'Missing',
            'The contract does not clearly explain how the signer can exit or how the relationship can be ended.',
            'The signer may get stuck in the contract or face avoidable disputes when trying to leave.',
            'Check whether termination, notice, refund, and post-exit obligations are clearly written.',
            'No clear termination protection was found'
        ))

    if not has_dispute_resolution:
        risks.append(build_risk(
            'missing_protection',
            'high',
            'N/A',
            'Add a clear dispute mechanism covering negotiation, arbitration or courts, and venue.',
            'Missing',
            'The contract does not clearly explain how disputes will be handled.',
            'If conflict arises, the signer may face delay, uncertainty, and higher legal cost.',
            'Check whether dispute resolution, arbitration, jurisdiction, and governing law are clearly specified.',
            'No clear dispute resolution safeguard was found'
        ))

    if has_termination and not has_notice:
        risks.append(build_risk(
            'missing_protection',
            'medium',
            'N/A',
            'Ask for a written notice process with timelines, service method, and cure opportunity.',
            'Missing',
            'The contract refers to termination but does not clearly describe how notice should be given.',
            'The signer may lose protection if the other party claims notice was valid without a clear process.',
            'Check for notice period, delivery method, email or address details, and cure rights.',
            'Notice procedure is unclear or missing'
        ))

    # Deduplicate near-identical risks
    unique_risks = []
    seen = set()
    for risk in risks:
        key = (
            risk['risk_category'],
            risk['affected_clause'].lower(),
            risk['risk_title'].lower()
        )
        if key not in seen:
            seen.add(key)
            unique_risks.append(risk)

    return unique_risks

def analyze_pros_cons(text):
    """Extract pros and cons from document"""
    pros = []
    cons = []
    
    # Favorable terms patterns
    pro_patterns = [
        'warranty provided',
        'liability limited',
        'termination at will',
        'free termination',
        'competitive pricing',
        'performance guarantee',
        'renewal option'
    ]
    
    # Unfavorable terms patterns
    con_patterns = [
        'non-refundable',
        'exclusive rights',
        'indefinite term',
        'unlawful termination penalties',
        'binding arbitration',
        'limitation of liability',
        'automatic renewal',
        'high penalties'
    ]
    
    text_lower = text.lower()
    
    for pro in pro_patterns:
        if pro in text_lower:
            pros.append(f"✓ {pro.title()}")
    
    for con in con_patterns:
        if con in text_lower:
            cons.append(f"✗ {con.title()}")
    
    if not pros:
        pros.append("✓ Document structure follows standard legal format")
    if not cons:
        cons.append("✗ Review recommended for potential unfavorable terms")
    
    return pros, cons

def extract_due_or_trigger(sentence):
    match = re.search(
        r'\b(within \d+ days?|after \d+ days?|before [^.,;]+|on or before [^.,;]+|upon [^.,;]+|monthly|annually|immediately|at any time|with \d+ days? notice)\b',
        sentence,
        re.IGNORECASE
    )
    return normalize_whitespace(match.group(0)) if match else 'Not clearly stated'

def infer_responsible_party(sentence, context):
    lower_sentence = sentence.lower()
    label_map = {
        'tenant': ['tenant', 'lessee'],
        'landlord': ['landlord', 'lessor'],
        'employee': ['employee'],
        'employer': ['employer', 'company'],
        'buyer': ['buyer', 'purchaser'],
        'seller': ['seller', 'vendor']
    }

    for party, terms in label_map.items():
        if any(term in lower_sentence for term in terms):
            return party.title()

    context_map = {
        'tenant': 'Tenant / Signer',
        'employee': 'Employee / Signer',
        'buyer': 'Buyer / Signer',
        'signer': 'Signer'
    }
    return context_map.get(context, 'Signer')

def extract_obligations(text):
    obligations = []
    context = detect_document_context(text)
    sections = split_into_legal_sections(text)

    for section in sections[:18]:
        sentences = re.split(r'(?<=[.!?])\s+', normalize_whitespace(section['text']))
        for sentence in sentences:
            if len(sentence) < 35:
                continue
            if not any(re.search(pattern, sentence, re.IGNORECASE) for pattern in OBLIGATION_PATTERNS):
                continue

            importance = 'medium'
            if re.search(r'\b(pay|penalty|liable|indemnif|terminate|notice)\b', sentence, re.IGNORECASE):
                importance = 'high'
            elif re.search(r'\bmay\b', sentence, re.IGNORECASE):
                importance = 'low'

            obligations.append({
                'responsible_party': infer_responsible_party(sentence, context),
                'action': normalize_whitespace(sentence[:180]),
                'due_or_trigger': extract_due_or_trigger(sentence),
                'importance': importance,
                'section': section['heading'][:100],
                'source_excerpt': normalize_whitespace(sentence[:220])
            })

    unique = []
    seen = set()
    for obligation in obligations:
        key = (obligation['responsible_party'].lower(), obligation['action'].lower())
        if key not in seen:
            seen.add(key)
            unique.append(obligation)

    return unique[:8]

def generate_glossary(text):
    lower_text = (text or '').lower()
    glossary = []

    for term, meaning in LEGAL_TERM_GLOSSARY.items():
        if term in lower_text:
            glossary.append({
                'term': term.title(),
                'meaning': meaning
            })

    return glossary[:10]

def build_analysis_overview(text, entities, clauses, risks):
    context = detect_document_context(text)
    confidence = compute_analysis_confidence(text, clauses, risks, entities)
    critical_or_high = sum(1 for risk in risks if risk.get('severity_level') in ['critical', 'high'])
    total_sections = len(split_into_legal_sections(text))
    document_type = detect_document_type(text)
    readability = compute_readability_band(text)

    if critical_or_high >= 3:
        overall_risk = 'high'
        risk_score = 82
    elif critical_or_high >= 1 or len(risks) >= 4:
        overall_risk = 'medium'
        risk_score = 61
    else:
        overall_risk = 'low'
        risk_score = 34

    return {
        'document_type': document_type,
        'signer_context': user_label_for_context(context),
        'overall_risk_level': overall_risk,
        'risk_score': risk_score,
        'analysis_confidence': confidence,
        'readability_band': readability,
        'section_count': total_sections,
        'key_clause_count': len(clauses),
        'top_risk_count': critical_or_high
    }

def build_plain_language_guide(summary, risks, obligations, overview):
    first_risk = risks[0] if risks else None
    first_obligation = obligations[0] if obligations else None
    role = overview.get('signer_context', 'signer')
    document_type = overview.get('document_type', 'legal agreement')

    what_this_is = f"This appears to be a {document_type.lower()} affecting the {role}. It sets out responsibilities, payment or conduct terms, and the conditions for continuing or ending the relationship."
    why_it_matters = summary if summary else "The document creates legal and financial obligations that can affect the signer if something goes wrong."
    biggest_watchout = first_risk.get('risk_title') if first_risk else 'No major red flag was automatically detected, but the contract still needs careful review.'
    practical_step = first_obligation.get('action') if first_obligation else 'Review payment, termination, liability, and dispute-related clauses carefully before signing.'

    return {
        'what_this_is': what_this_is,
        'why_it_matters': why_it_matters,
        'biggest_watchout': biggest_watchout,
        'practical_next_step': practical_step
    }

def build_questions_to_ask(risks, obligations, overview):
    questions = []
    if risks:
        for risk in risks[:4]:
            questions.append(risk.get('what_user_should_check') or risk.get('recommendation'))

    for obligation in obligations[:3]:
        if obligation.get('due_or_trigger') != 'Not clearly stated':
            questions.append(
                f"Can the timing for '{obligation.get('action', '')[:70]}' be made clearer than '{obligation.get('due_or_trigger')}'?"
            )

    if overview.get('overall_risk_level') in ['medium', 'high']:
        questions.append('Can the liability, penalty, or indemnity exposure be capped to a fixed and reasonable amount?')

    unique = []
    seen = set()
    for question in questions:
        normalized = normalize_whitespace(question)
        if normalized and normalized.lower() not in seen:
            seen.add(normalized.lower())
            unique.append(normalized)

    return unique[:6]

# ==================== API Endpoints ====================

@app.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return jsonify({
        'status': 'healthy',
        'service': 'Legal Document Analyzer AI Service',
        'version': '1.0.0',
        'timestamp': datetime.now().isoformat()
    })

@app.route('/analyze', methods=['POST'])
def analyze():
    """Main analysis endpoint"""
    try:
        data = request.get_json()
        text = data.get('text', '')
        
        if not text or len(text) < 50:
            return jsonify({'error': 'Invalid or empty text'}), 400
        
        logger.info(f"Processing document: {len(text)} characters")
        
        summary = summarize_text(text)
        simplified_text = simplify_text(text)
        key_clauses = classify_clauses(text)
        risks = analyze_risks(text)
        extracted_entities = extract_entities(text)
        obligations = extract_obligations(text)
        analysis_overview = build_analysis_overview(text, extracted_entities, key_clauses, risks)
        plain_language_guide = build_plain_language_guide(summary, risks, obligations, analysis_overview)
        glossary = generate_glossary(text)
        questions_to_ask = build_questions_to_ask(risks, obligations, analysis_overview)

        result = {
            'summary': summary,
            'simplified_text': simplified_text,
            'key_clauses': key_clauses,
            'risks': risks,
            'extracted_entities': extracted_entities,
            'analysis_overview': analysis_overview,
            'plain_language_guide': plain_language_guide,
            'obligations': obligations,
            'glossary': glossary,
            'questions_to_ask': questions_to_ask,
        }
        
        pros, cons = analyze_pros_cons(text)
        result['pros'] = pros
        result['cons'] = cons
        
        return jsonify(result)
    
    except Exception as e:
        logger.error(f"Analysis error: {str(e)}")
        return jsonify({'error': f'Analysis failed: {str(e)}'}), 500

@app.route('/extract-entities', methods=['POST'])
def extract_entities_endpoint():
    """Entity extraction endpoint"""
    try:
        data = request.get_json()
        text = data.get('text', '')
        
        if not text:
            return jsonify({'error': 'Empty text'}), 400
        
        entities = extract_entities(text)
        return jsonify(entities)
    
    except Exception as e:
        logger.error(f"Entity extraction error: {str(e)}")
        return jsonify({'error': str(e)}), 500

@app.route('/classify-clauses', methods=['POST'])
def classify_clauses_endpoint():
    """Clause classification endpoint"""
    try:
        data = request.get_json()
        text = data.get('text', '')
        
        if not text:
            return jsonify({'error': 'Empty text'}), 400
        
        clauses = classify_clauses(text)
        return jsonify({'key_clauses': clauses})
    
    except Exception as e:
        logger.error(f"Classification error: {str(e)}")
        return jsonify({'error': str(e)}), 500

@app.route('/summarize', methods=['POST'])
def summarize_endpoint():
    """Summarization endpoint"""
    try:
        data = request.get_json()
        text = data.get('text', '')
        
        if not text:
            return jsonify({'error': 'Empty text'}), 400
        
        summary = summarize_text(text)
        return jsonify({'summary': summary})
    
    except Exception as e:
        logger.error(f"Summarization error: {str(e)}")
        return jsonify({'error': str(e)}), 500

@app.route('/simplify', methods=['POST'])
def simplify_endpoint():
    """Text simplification endpoint"""
    try:
        data = request.get_json()
        text = data.get('text', '')
        
        if not text:
            return jsonify({'error': 'Empty text'}), 400
        
        simplified = simplify_text(text)
        return jsonify({'simplified_text': simplified})
    
    except Exception as e:
        logger.error(f"Simplification error: {str(e)}")
        return jsonify({'error': str(e)}), 500

@app.route('/risk-analysis', methods=['POST'])
def risk_analysis_endpoint():
    """Risk analysis endpoint"""
    try:
        data = request.get_json()
        text = data.get('text', '')
        
        if not text:
            return jsonify({'error': 'Empty text'}), 400
        
        risks = analyze_risks(text)
        pros, cons = analyze_pros_cons(text)
        
        return jsonify({
            'risks': risks,
            'pros': pros,
            'cons': cons
        })
    
    except Exception as e:
        logger.error(f"Risk analysis error: {str(e)}")
        return jsonify({'error': str(e)}), 500

@app.route('/test', methods=['GET'])
def test():
    """Test endpoint with sample analysis"""
    sample_text = """
    AGREEMENT OF SALE
    
    This Agreement made this 15th day of January, 2024
    
    BETWEEN
    
    Mr. Rajesh Kumar, aged 45 years, residing at 42, Delhi Road, New Delhi (Hereinafter called the "Seller")
    
    AND
    
    Ms. Priya Sharma, aged 38 years, residing at 15, Mumbai Street, Mumbai (Hereinafter called the "Buyer")
    
    Whereas, the Seller agrees to sell and the Buyer agrees to purchase the property as hereinafter mentioned.
    
    NOW THEREFORE, in consideration of mutual covenants and agreements:
    
    1. PROPERTY: The Seller hereby agrees to sell to the Buyer the property located at New Delhi.
    
    2. CONSIDERATION: The total consideration for the property shall be Rs. 50,00,000 (Fifty Lakhs only).
    
    3. PAYMENT TERMS: Payment shall be made in three installments as per the schedule attached.
    
    4. TERMINATION: This agreement may be terminated by either party with 30 days written notice.
    
    5. LIABILITY: Neither party shall be liable for any indirect damages or losses.
    
    6. GOVERNING LAW: This agreement shall be governed by the Indian Contract Act, 1872.
    """
    
    result = {
        'summary': summarize_text(sample_text),
        'simplified_text': simplify_text(sample_text),
        'key_clauses': classify_clauses(sample_text),
        'risks': analyze_risks(sample_text),
        'extracted_entities': extract_entities(sample_text),
    }
    
    pros, cons = analyze_pros_cons(sample_text)
    result['pros'] = pros
    result['cons'] = cons
    
    return jsonify(result)

if __name__ == '__main__':
    initialize_models()
    logger.info("Starting Legal Document Analyzer AI Service on port 5000")
    app.run(debug=os.environ.get("FLASK_DEBUG") == "1", host='0.0.0.0', port=5000)
