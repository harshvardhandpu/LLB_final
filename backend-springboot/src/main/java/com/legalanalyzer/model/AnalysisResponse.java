package com.legalanalyzer.model;

import com.fasterxml.jackson.annotation.JsonProperty;
import lombok.AllArgsConstructor;
import lombok.Data;
import lombok.NoArgsConstructor;

import java.util.List;
import java.util.Map;

/**
 * Main response object containing analyzed legal document information
 */
@Data
@NoArgsConstructor
@AllArgsConstructor
public class AnalysisResponse {

    private String fileName;

    private String originalText;

    private String summary;

    @JsonProperty("simplified_text")
    private String simplifiedText;

    @JsonProperty("key_clauses")
    private List<KeyClause> keyClauses;

    private List<Risk> risks;

    private List<String> pros;

    private List<String> cons;

    @JsonProperty("extracted_entities")
    private Map<String, Object> extractedEntities;

    @JsonProperty("analysis_overview")
    private Map<String, Object> analysisOverview;

    @JsonProperty("plain_language_guide")
    private Map<String, Object> plainLanguageGuide;

    private List<Map<String, Object>> obligations;

    @JsonProperty("questions_to_ask")
    private List<String> questionsToAsk;

    private List<Map<String, String>> glossary;

    @JsonProperty("analysis_timestamp")
    private long analysisTimestamp;

    @JsonProperty("document_length")
    private int documentLength;

    private String status;

    private String error;
}
