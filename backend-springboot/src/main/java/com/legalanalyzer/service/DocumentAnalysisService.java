package com.legalanalyzer.service;

import com.legalanalyzer.model.AnalysisResponse;
import com.legalanalyzer.model.KeyClause;
import com.legalanalyzer.model.Risk;
import com.legalanalyzer.util.AIServiceClient;
import com.legalanalyzer.util.DocumentParser;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.stereotype.Service;
import org.springframework.web.multipart.MultipartFile;

import java.io.IOException;
import java.util.*;

/**
 * Service class handling legal document analysis
 */
@Service
public class DocumentAnalysisService {

    @Autowired
    private DocumentParser documentParser;

    @Autowired
    private AIServiceClient aiServiceClient;

    /**
     * Main method to analyze a legal document
     */
    public AnalysisResponse analyzeDocument(MultipartFile file) throws IOException {
        AnalysisResponse response = new AnalysisResponse();
        response.setFileName(file.getOriginalFilename());
        response.setAnalysisTimestamp(System.currentTimeMillis());
        response.setStatus("processing");

        try {
            // Extract text from file
            String extractedText = documentParser.extractText(file);
            response.setOriginalText(extractedText);
            response.setDocumentLength(extractedText.length());

            // Limit text for processing (max 16k tokens roughly = ~64k chars)
            String processText = extractedText.length() > 65000 
                ? extractedText.substring(0, 65000) 
                : extractedText;

            // Call AI service for complete analysis
            Map<String, Object> analysisResult = aiServiceClient.analyzeDocument(processText);

            if (analysisResult.containsKey("error")) {
                response.setStatus("failed");
                response.setError(analysisResult.get("error").toString());
                return response;
            }

            // Populate response from AI service results
            response.setSummary(getString(analysisResult, "summary"));
            response.setSimplifiedText(getString(analysisResult, "simplified_text"));
            response.setExtractedEntities(getMap(analysisResult, "extracted_entities"));
            response.setAnalysisOverview(getMap(analysisResult, "analysis_overview"));
            response.setPlainLanguageGuide(getMap(analysisResult, "plain_language_guide"));
            response.setObligations(getMapList(analysisResult, "obligations"));
            response.setQuestionsToAsk(getStringList(analysisResult, "questions_to_ask"));
            response.setGlossary(getStringMapList(analysisResult, "glossary"));

            // Process clauses
            List<KeyClause> keyClauses = processKeyClauses(getList(analysisResult, "key_clauses"));
            response.setKeyClauses(keyClauses);

            // Process risks
            List<Risk> risks = processRisks(getList(analysisResult, "risks"));
            response.setRisks(risks);

            // Process pros and cons
            response.setPros(getStringList(analysisResult, "pros"));
            response.setCons(getStringList(analysisResult, "cons"));

            response.setStatus("completed");

        } catch (Exception e) {
            response.setStatus("failed");
            response.setError("Analysis failed: " + e.getMessage());
        }

        return response;
    }

    /**
     * Process insurance key clauses from AI response
     */
    private List<KeyClause> processKeyClauses(List<?> clausesList) {
        List<KeyClause> result = new ArrayList<>();
        if (clausesList == null) return result;

        for (Object clause : clausesList) {
            if (clause instanceof Map) {
                @SuppressWarnings("unchecked")
                Map<String, Object> clauseMap = (Map<String, Object>) clause;
                KeyClause keyClause = new KeyClause();
                keyClause.setType(getString(clauseMap, "type"));
                keyClause.setText(getString(clauseMap, "text"));
                keyClause.setSection(getString(clauseMap, "section"));
                keyClause.setSeverityLevel(getString(clauseMap, "severity_level"));
                keyClause.setConfidence(getDouble(clauseMap, "confidence"));
                keyClause.setExplanation(getString(clauseMap, "explanation"));
                keyClause.setRisky(getBoolean(clauseMap, "is_risky"));
                result.add(keyClause);
            }
        }
        return result;
    }

    /**
     * Process risks from AI response
     */
    private List<Risk> processRisks(List<?> risksList) {
        List<Risk> result = new ArrayList<>();
        if (risksList == null) return result;

        for (Object risk : risksList) {
            if (risk instanceof Map) {
                @SuppressWarnings("unchecked")
                Map<String, Object> riskMap = (Map<String, Object>) risk;
                Risk riskObj = new Risk();
                riskObj.setType(getString(riskMap, "type"));
                riskObj.setRiskCategory(getString(riskMap, "risk_category"));
                riskObj.setRiskTitle(getString(riskMap, "risk_title"));
                riskObj.setDescription(getString(riskMap, "description"));
                riskObj.setSeverityLevel(getString(riskMap, "severity_level"));
                riskObj.setAffectedClause(getString(riskMap, "affected_clause"));
                riskObj.setRecommendation(getString(riskMap, "recommendation"));
                riskObj.setClause(getString(riskMap, "clause"));
                riskObj.setWhyThisIsRisky(getString(riskMap, "why_this_is_risky"));
                riskObj.setImpactOnUser(getString(riskMap, "impact_on_user"));
                riskObj.setWhatUserShouldCheck(getString(riskMap, "what_user_should_check"));
                result.add(riskObj);
            }
        }
        return result;
    }

    // Helper methods for type conversion
    private String getString(Map<String, Object> map, String key) {
        Object value = map.get(key);
        return value != null ? value.toString() : "";
    }

    @SuppressWarnings("unchecked")
    private Map<String, Object> getMap(Map<String, Object> map, String key) {
        Object value = map.get(key);
        return value instanceof Map ? (Map<String, Object>) value : new HashMap<>();
    }

    @SuppressWarnings("unchecked")
    private List<?> getList(Map<String, Object> map, String key) {
        Object value = map.get(key);
        return value instanceof List ? (List<?>) value : new ArrayList<>();
    }

    private List<String> getStringList(Map<String, Object> map, String key) {
        List<String> result = new ArrayList<>();
        List<?> list = getList(map, key);
        for (Object item : list) {
            result.add(item != null ? item.toString() : "");
        }
        return result;
    }

    @SuppressWarnings("unchecked")
    private List<Map<String, Object>> getMapList(Map<String, Object> map, String key) {
        List<Map<String, Object>> result = new ArrayList<>();
        List<?> list = getList(map, key);
        for (Object item : list) {
            if (item instanceof Map) {
                result.add((Map<String, Object>) item);
            }
        }
        return result;
    }

    @SuppressWarnings("unchecked")
    private List<Map<String, String>> getStringMapList(Map<String, Object> map, String key) {
        List<Map<String, String>> result = new ArrayList<>();
        List<?> list = getList(map, key);
        for (Object item : list) {
            if (item instanceof Map<?, ?> rawMap) {
                Map<String, String> converted = new HashMap<>();
                rawMap.forEach((mapKey, mapValue) ->
                    converted.put(
                        mapKey != null ? mapKey.toString() : "",
                        mapValue != null ? mapValue.toString() : ""
                    )
                );
                result.add(converted);
            }
        }
        return result;
    }

    private Double getDouble(Map<String, Object> map, String key) {
        Object value = map.get(key);
        if (value instanceof Number) {
            return ((Number) value).doubleValue();
        }
        return 0.0;
    }

    private boolean getBoolean(Map<String, Object> map, String key) {
        Object value = map.get(key);
        return value instanceof Boolean && (Boolean) value;
    }
}
