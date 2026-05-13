package com.legalanalyzer.util;

import com.fasterxml.jackson.databind.ObjectMapper;
import org.apache.hc.client5.http.classic.HttpClient;
import org.apache.hc.client5.http.classic.methods.HttpPost;
import org.apache.hc.client5.http.impl.classic.HttpClients;
import org.apache.hc.core5.http.ContentType;
import org.apache.hc.core5.http.io.entity.StringEntity;
import org.apache.hc.core5.http.io.entity.EntityUtils;
import org.springframework.beans.factory.annotation.Value;
import org.springframework.stereotype.Component;

import java.io.IOException;
import java.util.HashMap;
import java.util.Map;

/**
 * Utility class for communicating with AI service
 */
@Component
public class AIServiceClient {

    @Value("${ai.service.url}")
    private String aiServiceUrl;

    @Value("${ai.service.analyze-endpoint}")
    private String analyzeEndpoint;

    @Value("${ai.service.extract-entities-endpoint}")
    private String extractEntitiesEndpoint;

    @Value("${ai.service.classify-clauses-endpoint}")
    private String classifyClausesEndpoint;

    @Value("${ai.service.summarize-endpoint}")
    private String summarizeEndpoint;

    @Value("${ai.service.simplify-endpoint}")
    private String simplifyEndpoint;

    @Value("${ai.service.risk-analysis-endpoint}")
    private String riskAnalysisEndpoint;

    private final ObjectMapper objectMapper = new ObjectMapper();
    private final HttpClient httpClient = HttpClients.createDefault();

    /**
     * Send complete analysis request to AI service
     */
    public Map<String, Object> analyzeDocument(String text) throws IOException {
        return sendRequest(aiServiceUrl + analyzeEndpoint, Map.of("text", text));
    }

    /**
     * Extract entities from document
     */
    public Map<String, Object> extractEntities(String text) throws IOException {
        return sendRequest(aiServiceUrl + extractEntitiesEndpoint, Map.of("text", text));
    }

    /**
     * Classify clauses in document
     */
    public Map<String, Object> classifyClauses(String text) throws IOException {
        return sendRequest(aiServiceUrl + classifyClausesEndpoint, Map.of("text", text));
    }

    /**
     * Summarize document
     */
    public Map<String, Object> summarizeDocument(String text) throws IOException {
        return sendRequest(aiServiceUrl + summarizeEndpoint, Map.of("text", text));
    }

    /**
     * Simplify legal text
     */
    public Map<String, Object> simplifyText(String text) throws IOException {
        return sendRequest(aiServiceUrl + simplifyEndpoint, Map.of("text", text));
    }

    /**
     * Analyze risks in document
     */
    public Map<String, Object> analyzeRisks(String text) throws IOException {
        return sendRequest(aiServiceUrl + riskAnalysisEndpoint, Map.of("text", text));
    }

    /**
     * Generic method to send HTTP POST request to AI service
     */
    @SuppressWarnings("unchecked")
    private Map<String, Object> sendRequest(String url, Map<String, String> payload) throws IOException {
        HttpPost httpPost = new HttpPost(url);
        httpPost.setHeader("Content-Type", "application/json");

        String jsonPayload = objectMapper.writeValueAsString(payload);
        httpPost.setEntity(new StringEntity(jsonPayload, ContentType.APPLICATION_JSON));

        try {
            return httpClient.execute(httpPost, response -> {
                var entity = response.getEntity();
                if (entity != null) {
                    String responseBody = EntityUtils.toString(entity);
                    return objectMapper.readValue(responseBody, Map.class);
                } else {
                    Map<String, Object> errorResponse = new HashMap<>();
                    errorResponse.put("error", "Empty response from AI service");
                    return errorResponse;
                }
            });
        } catch (Exception e) {
            Map<String, Object> errorResponse = new HashMap<>();
            errorResponse.put("error", "Failed to connect to AI service: " + e.getMessage());
            return errorResponse;
        }
    }
}
