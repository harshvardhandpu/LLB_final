package com.legalanalyzer.util;

import org.apache.pdfbox.Loader;
import org.apache.pdfbox.pdmodel.PDDocument;
import org.apache.pdfbox.text.PDFTextStripper;
import org.apache.poi.xwpf.usermodel.XWPFDocument;
import org.apache.poi.xwpf.usermodel.XWPFParagraph;
import org.springframework.stereotype.Component;
import org.springframework.web.multipart.MultipartFile;

import java.io.IOException;
import java.io.InputStream;
import java.util.stream.Collectors;

/**
 * Utility class for extracting text from PDF and DOCX files
 */
@Component
public class DocumentParser {

    /**
     * Extract text from uploaded file (PDF or DOCX)
     */
    public String extractText(MultipartFile file) throws IOException {
        String fileName = file.getOriginalFilename();
        
        if (fileName != null && fileName.toLowerCase().endsWith(".pdf")) {
            return extractTextFromPDF(file.getInputStream());
        } else if (fileName != null && fileName.toLowerCase().endsWith(".docx")) {
            return extractTextFromDOCX(file.getInputStream());
        } else {
            throw new IllegalArgumentException("Unsupported file format. Please upload PDF or DOCX files.");
        }
    }

    /**
     * Extract text from PDF file using PDFBox 3.x API
     */
    private String extractTextFromPDF(InputStream inputStream) throws IOException {
        // Read InputStream to byte array for PDFBox 3.x Loader.loadPDF()
        byte[] pdfBytes = inputStream.readAllBytes();
        try (PDDocument document = Loader.loadPDF(pdfBytes)) {
            PDFTextStripper stripper = new PDFTextStripper();
            return stripper.getText(document);
        }
    }

    /**
     * Extract text from DOCX file
     */
    private String extractTextFromDOCX(InputStream inputStream) throws IOException {
        try (XWPFDocument document = new XWPFDocument(inputStream)) {
            return document.getParagraphs()
                    .stream()
                    .map(XWPFParagraph::getText)
                    .collect(Collectors.joining("\n"));
        }
    }

    /**
     * Split long text into chunks for processing
     */
    public static String[] chunkText(String text, int chunkSize, int overlapSize) {
        if (text.length() <= chunkSize) {
            return new String[]{text};
        }

        StringBuilder sb = new StringBuilder();
        int chunks = (int) Math.ceil((double) text.length() / (chunkSize - overlapSize));
        String[] result = new String[chunks];

        for (int i = 0; i < chunks; i++) {
            int start = i * (chunkSize - overlapSize);
            int end = Math.min(start + chunkSize, text.length());
            result[i] = text.substring(start, end);
        }
        return result;
    }
}
