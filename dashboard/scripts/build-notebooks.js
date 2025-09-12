#!/usr/bin/env node

const fs = require('fs');
const path = require('path');

// Paths
const MARIMO_DIR = path.join(__dirname, '../../python/scripts/notebooks/__marimo__');
const PYTHON_NOTEBOOKS_DIR = path.join(__dirname, '../../python/scripts/notebooks');
const NOTEBOOKS_DIR = path.join(__dirname, '../app/analysis/notebooks');
const NOTEBOOKS_JSON = path.join(__dirname, '../public/analysis/notebooks/notebooks.json');
const PUBLIC_HTML_DIR = path.join(__dirname, '../public/analysis/notebooks/html');

// Ensure notebooks directory exists
if (!fs.existsSync(NOTEBOOKS_DIR)) {
  fs.mkdirSync(NOTEBOOKS_DIR, { recursive: true });
}

function parseNotebookMetadata(pythonFilePath) {
  try {
    const content = fs.readFileSync(pythonFilePath, 'utf-8');
    
    // Look for the first @app.cell(hide_code=True) with mo.md containing markdown
    const markdownCellMatch = content.match(/@app\.cell\(hide_code=True\)\s*\ndef _\([^)]*\):\s*mo\.md\(\s*r?"""([^"]*(?:"""[^"]*)*?)"""/s);
    
    if (!markdownCellMatch) {
      return null;
    }
    
    const markdownContent = markdownCellMatch[1];
    
    // Extract title (first # heading) - handle multiline and trim whitespace
    const titleMatch = markdownContent.match(/^#\s+(.+?)(?:\n|$)/m);
    const title = titleMatch ? titleMatch[1].trim() : null;
    
    // Extract purpose (line starting with **Purpose**)
    const purposeMatch = markdownContent.match(/\*\*Purpose\*\*:\s*(.+?)(?:\n|$)/);
    const purpose = purposeMatch ? purposeMatch[1].trim() : null;
    
    // Extract key outputs (line starting with **Key Outputs**)
    const keyOutputsMatch = markdownContent.match(/\*\*Key Outputs\*\*:\s*(.+?)(?:\n|$)/);
    const keyOutputs = keyOutputsMatch ? keyOutputsMatch[1].trim() : null;
    
    return {
      title,
      purpose,
      keyOutputs,
      fullMarkdown: markdownContent.trim()
    };
  } catch (error) {
    console.warn(`Failed to parse notebook metadata from ${pythonFilePath}:`, error.message);
    return null;
  }
}

function extractMetadata(htmlContent, filename) {
  // Try to find corresponding Python file
  const pythonFilename = filename.replace(/\.html$/, '.py');
  const pythonFilePath = path.join(PYTHON_NOTEBOOKS_DIR, pythonFilename);
  
  let metadata = null;
  if (fs.existsSync(pythonFilePath)) {
    metadata = parseNotebookMetadata(pythonFilePath);
  }
  
  // Fallback to filename-based extraction if Python parsing fails
  const fallbackTitle = filename.replace(/^\d+[-_]/, '').replace(/\.html$/, '')
    .split(/[-_]/)
    .map(word => word.charAt(0).toUpperCase() + word.slice(1))
    .join(' ');
  
  const title = metadata?.title || fallbackTitle;
  const purpose = metadata?.purpose || `Interactive marimo notebook: ${title}`;
  const keyOutputs = metadata?.keyOutputs || 'Analysis results and visualizations';

  // Extract order from filename (e.g., "01_data_prep.html" -> 1)
  const orderMatch = filename.match(/^(\d+)/);
  const order = orderMatch ? parseInt(orderMatch[1]) : 999;

  return {
    slug: filename.replace(/\.html$/, ''),
    title,
    purpose,
    keyOutputs,
    description: purpose, // Keep for backward compatibility
    filename,
    order,
    lastModified: fs.statSync(path.join(MARIMO_DIR, filename)).mtime.toISOString(),
    fullMarkdown: metadata?.fullMarkdown
  };
}

function createNotebookPage(notebook) {
  const pageContent = `'use client';

import { motion } from 'framer-motion';
import { ArrowLeft, Target, FlaskConical } from 'lucide-react';
import Link from 'next/link';

export default function NotebookPage() {

  return (
    <div className="min-h-screen bg-background flex flex-col">
      <div className="container mx-auto px-4 py-4 flex-shrink-0">
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.6 }}
          className="mb-4"
        >
          <Link 
            href="/analysis" 
            className="inline-flex items-center text-primary hover:text-primary/80 transition-colors mb-2"
          >
            <ArrowLeft className="h-4 w-4 mr-2" />
            Back to Analysis
          </Link>
          <div className="mb-4">
            <h1 className="text-3xl font-bold text-primary mb-2">${notebook.title}</h1>
            
            <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
              <motion.div
                className="bg-card rounded-lg border p-3"
                initial={{ opacity: 0, x: -20 }}
                animate={{ opacity: 1, x: 0 }}
                transition={{ duration: 0.6, delay: 0.1 }}
              >
                <div className="flex items-center mb-1">
                  <Target className="h-4 w-4 text-chart-1 mr-2" />
                  <span className="font-semibold text-xs">PURPOSE</span>
                </div>
                <p className="text-xs text-muted-foreground">${notebook.purpose}</p>
              </motion.div>

              <motion.div
                className="bg-card rounded-lg border p-3"
                initial={{ opacity: 0, x: 20 }}
                animate={{ opacity: 1, x: 0 }}
                transition={{ duration: 0.6, delay: 0.2 }}
              >
                <div className="flex items-center mb-1">
                  <FlaskConical className="h-4 w-4 text-chart-2 mr-2" />
                  <span className="font-semibold text-xs">KEY OUTPUTS</span>
                </div>
                <p className="text-xs text-muted-foreground">${notebook.keyOutputs}</p>
              </motion.div>
            </div>
          </div>
        </motion.div>
      </div>

      <motion.div
        initial={{ opacity: 0, y: 30 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.6, delay: 0.3 }}
        className="flex-grow container mx-auto px-4 pb-4"
        style={{ minHeight: '70vh' }}
      >
        <div 
          className="bg-card rounded-lg shadow-lg border overflow-hidden relative h-full"
          style={{ minHeight: '70vh' }}
        >
          <iframe
            src="/analysis/notebooks/html/${notebook.filename}"
            className="w-full h-full border-0"
            title="${notebook.title}"
            sandbox="allow-scripts allow-same-origin allow-forms"
            style={{ minHeight: '70vh' }}
          />
        </div>
      </motion.div>
    </div>
  );
}
`;

  const notebookDir = path.join(NOTEBOOKS_DIR, notebook.slug);
  if (!fs.existsSync(notebookDir)) {
    fs.mkdirSync(notebookDir, { recursive: true });
  }
  
  fs.writeFileSync(path.join(notebookDir, 'page.tsx'), pageContent);
  console.log(`Created page for: ${notebook.title}`);
}

function cleanMarimoHtml(htmlContent) {
  // Remove problematic preload links that cause console errors
  let cleaned = htmlContent;
  
  // Remove preload links for CDN resources
  cleaned = cleaned.replace(
    /<link[^>]*rel=["']preload["'][^>]*cdn\.jsdelivr\.net[^>]*>/gi,
    ''
  );
  
  // Remove modulepreload links that might cause issues
  cleaned = cleaned.replace(
    /<link[^>]*rel=["']modulepreload["'][^>]*cdn\.jsdelivr\.net[^>]*>/gi,
    ''
  );
  
  return cleaned;
}

function copyHtmlFiles(notebooks) {
  // Ensure public directories exist
  if (!fs.existsSync(PUBLIC_HTML_DIR)) {
    fs.mkdirSync(PUBLIC_HTML_DIR, { recursive: true });
  }
  
  const publicJsonDir = path.dirname(NOTEBOOKS_JSON);
  if (!fs.existsSync(publicJsonDir)) {
    fs.mkdirSync(publicJsonDir, { recursive: true });
  }

  notebooks.forEach(notebook => {
    const srcPath = path.join(MARIMO_DIR, notebook.filename);
    const destPath = path.join(PUBLIC_HTML_DIR, notebook.filename);
    
    // Read, clean, and write the HTML
    const htmlContent = fs.readFileSync(srcPath, 'utf-8');
    const cleanedHtml = cleanMarimoHtml(htmlContent);
    fs.writeFileSync(destPath, cleanedHtml);
    
    console.log(`Copied and cleaned HTML file: ${notebook.filename}`);
  });
}

function main() {
  console.log('Building marimo notebook pages...');
  
  if (!fs.existsSync(MARIMO_DIR)) {
    console.error(`Marimo directory not found: ${MARIMO_DIR}`);
    process.exit(1);
  }

  // Find all HTML files in the marimo directory
  const htmlFiles = fs.readdirSync(MARIMO_DIR)
    .filter(file => file.endsWith('.html'));

  if (htmlFiles.length === 0) {
    console.log('No HTML files found in marimo directory');
    return;
  }

  // Process each HTML file
  const notebooks = [];
  
  for (const htmlFile of htmlFiles) {
    const htmlPath = path.join(MARIMO_DIR, htmlFile);
    const htmlContent = fs.readFileSync(htmlPath, 'utf-8');
    const metadata = extractMetadata(htmlContent, htmlFile);
    
    notebooks.push(metadata);
    createNotebookPage(metadata);
  }

  // Sort notebooks by order
  notebooks.sort((a, b) => a.order - b.order);

  // Copy HTML files to public access location
  copyHtmlFiles(notebooks);

  // Write notebooks metadata JSON
  fs.writeFileSync(NOTEBOOKS_JSON, JSON.stringify(notebooks, null, 2));

  console.log(`✅ Successfully processed ${notebooks.length} notebooks:`);
  notebooks.forEach(nb => console.log(`  - ${nb.title} (${nb.slug})`));
}

if (require.main === module) {
  main();
}

module.exports = { main };