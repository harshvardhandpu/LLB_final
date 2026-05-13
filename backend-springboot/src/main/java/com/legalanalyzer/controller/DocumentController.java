package com.legalanalyzer.controller;

import com.legalanalyzer.model.AnalysisResponse;
import com.legalanalyzer.service.DocumentAnalysisService;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.http.HttpStatus;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.*;
import org.springframework.web.multipart.MultipartFile;

import java.io.IOException;
import java.util.HashMap;
import java.util.Map;

/**
 * REST API Controller for document analysis endpoints
 */
@RestController
@RequestMapping("/documents")
@CrossOrigin(origins = "*")
public class DocumentController {

    @Autowired
    private DocumentAnalysisService documentAnalysisService;

    /**
     * Upload and analyze a legal document
     * POST /api/documents/analyze
     */
    @PostMapping("/analyze")
    public ResponseEntity<?> uploadAndAnalyze(@RequestParam("file") MultipartFile file) {
        try {
            // Validate file
            if (file.isEmpty()) {
                return ResponseEntity.badRequest()
                    .body(Map.of("error", "File is empty"));
            }

            String fileName = file.getOriginalFilename();
            if (fileName == null || (!fileName.toLowerCase().endsWith(".pdf") && 
                !fileName.toLowerCase().endsWith(".docx"))) {
                return ResponseEntity.badRequest()
                    .body(Map.of("error", "Only PDF and DOCX files are supported"));
            }

            // Analyze document
            AnalysisResponse analysisResponse = documentAnalysisService.analyzeDocument(file);

            if ("failed".equals(analysisResponse.getStatus())) {
                return ResponseEntity.status(HttpStatus.INTERNAL_SERVER_ERROR)
                    .body(analysisResponse);
            }

            return ResponseEntity.ok(analysisResponse);

        } catch (IOException e) {
            Map<String, Object> errorResponse = new HashMap<>();
            errorResponse.put("error", "File processing failed: " + e.getMessage());
            errorResponse.put("status", "failed");
            return ResponseEntity.status(HttpStatus.INTERNAL_SERVER_ERROR)
                .body(errorResponse);
        }
    }

    /**
     * Health check endpoint
     * GET /api/documents/health
     */
    @GetMapping("/health")
    public ResponseEntity<?> health() {
        return ResponseEntity.ok(Map.of(
            "status", "healthy",
            "service", "Legal Document Analyzer API",
            "version", "1.0.0"
        ));
    }

    /**
     * Get API documentation
     * GET /api/documents/docs
     */
    @GetMapping("/docs")
    public ResponseEntity<?> getDocs() {
        Map<String, Object> docs = new HashMap<>();
        docs.put("title", "Legal Document Analyzer API");
        docs.put("version", "1.0.0");
        
        Map<String, Object> endpoints = new HashMap<>();
        
        Map<String, Object> analyze = new HashMap<>();
        analyze.put("method", "POST");
        analyze.put("path", "/api/documents/analyze");
        analyze.put("description", "Upload and analyze a legal document");
        analyze.put("parameters", Map.of(
            "file", "MultipartFile (PDF or DOCX)"
        ));
        endpoints.put("analyze", analyze);
        
        docs.put("endpoints", endpoints);
        return ResponseEntity.ok(docs);
    }
}
