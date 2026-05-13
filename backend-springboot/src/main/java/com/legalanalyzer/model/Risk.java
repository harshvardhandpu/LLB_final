package com.legalanalyzer.model;

import com.fasterxml.jackson.annotation.JsonProperty;
import lombok.AllArgsConstructor;
import lombok.Data;
import lombok.NoArgsConstructor;

/**
 * Represents an identified risk in the legal document
 */
@Data
@NoArgsConstructor
@AllArgsConstructor
public class Risk {

    private String type; // e.g., "high_penalty", "one_sided", "missing_clause", "unusual_clause"

    @JsonProperty("risk_category")
    private String riskCategory;

    @JsonProperty("risk_title")
    private String riskTitle;

    private String description;

    @JsonProperty("severity_level")
    private String severityLevel; // "critical", "high", "medium", "low"

    @JsonProperty("affected_clause")
    private String affectedClause;

    private String recommendation;

    private String clause;

    @JsonProperty("why_this_is_risky")
    private String whyThisIsRisky;

    @JsonProperty("impact_on_user")
    private String impactOnUser;

    @JsonProperty("what_user_should_check")
    private String whatUserShouldCheck;
}
