package com.legalanalyzer.model;

import lombok.AllArgsConstructor;
import lombok.Data;
import lombok.NoArgsConstructor;

/**
 * Represents an uploaded legal document file
 */
@Data
@NoArgsConstructor
@AllArgsConstructor
public class DocumentUpload {

    private String fileName;

    private String fileType; // "pdf" or "docx"

    private long fileSize;

    private String uploadedPath;

    private String extractedText;

    private String uploadTimestamp;

    private String status; // "uploaded", "processing", "completed", "failed"

    private String errorMessage;
}
