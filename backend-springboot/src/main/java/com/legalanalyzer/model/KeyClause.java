package com.legalanalyzer.model;

import com.fasterxml.jackson.annotation.JsonProperty;
import lombok.AllArgsConstructor;
import lombok.Data;
import lombok.NoArgsConstructor;

/**
 * Represents a classified clause from the legal document
 */
@Data
@NoArgsConstructor
@AllArgsConstructor
public class KeyClause {

    private String type; // e.g., "liability", "termination", "penalty", "indemnification"

    private String text;

    private String section;

    @JsonProperty("severity_level")
    private String severityLevel; // "high", "medium", "low"

    private Double confidence;

    private String explanation;

    @JsonProperty("is_risky")
    private boolean isRisky;
}
