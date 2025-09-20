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
import { ArrowLeft, Target, FlaskConical, Maximize2, Minimize2, X } from 'lucide-react';
import Link from 'next/link';
import { useState, useEffect, useRef } from 'react';

export default function NotebookPage() {
  const [isFullscreen, setIsFullscreen] = useState(false);
  const iframeRef = useRef(null);

  // Handle ESC key for fullscreen exit
  useEffect(() => {
    const handleKeyPress = (event: KeyboardEvent) => {
      if (event.key === 'Escape' && isFullscreen) {
        setIsFullscreen(false);
      }
    };

    if (isFullscreen) {
      document.addEventListener('keydown', handleKeyPress);
      document.body.style.overflow = 'hidden';
    } else {
      document.body.style.overflow = 'unset';
    }

    return () => {
      document.removeEventListener('keydown', handleKeyPress);
      document.body.style.overflow = 'unset';
    };
  }, [isFullscreen]);

  const toggleFullscreen = () => {
    setIsFullscreen(!isFullscreen);
  };

  return (
    <div className="min-h-screen bg-background flex flex-col">
      {/* Header - Hidden in fullscreen */}
      {!isFullscreen && (
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
              <div className="flex items-center mb-2">
                <div className="w-10 h-10 bg-primary text-primary-foreground rounded-full flex items-center justify-center text-lg font-bold mr-4">
                  ${String(notebook.order).padStart(2, '0')}
                </div>
                <div>
                  <div className="text-sm text-muted-foreground">Notebook ${String(notebook.order).padStart(2, '0')}</div>
                  <h1 className="text-3xl font-bold text-primary">${notebook.title}</h1>
                </div>
              </div>
              
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
      )}

      {/* Notebook Container */}
      <motion.div
        initial={{ opacity: 0, y: 30 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.6, delay: 0.3 }}
        className={isFullscreen ? 
          "fixed inset-0 z-50 bg-background" : 
          "flex-grow container mx-auto px-4 pb-4"
        }
        style={{ minHeight: isFullscreen ? '100vh' : '70vh' }}
      >
        <div 
          className={
            "bg-card rounded-lg shadow-lg border overflow-hidden relative h-full " +
            (isFullscreen ? "rounded-none shadow-none border-0" : "")
          }
          style={{ minHeight: isFullscreen ? '100vh' : '70vh' }}
        >
          {/* Fullscreen Controls */}
          <div className="absolute top-4 right-4 z-10 flex gap-2">
            {isFullscreen && (
              <button
                onClick={toggleFullscreen}
                className="bg-white/90 hover:bg-white border rounded-lg p-2 shadow-lg transition-all backdrop-blur-sm"
                title="Exit Fullscreen (ESC)"
                aria-label="Exit Fullscreen"
              >
                <X className="h-5 w-5 text-gray-700" />
              </button>
            )}
            
            <button
              onClick={toggleFullscreen}
              className="bg-white/90 hover:bg-white border rounded-lg p-2 shadow-lg transition-all backdrop-blur-sm"
              title={isFullscreen ? "Exit Fullscreen" : "Enter Fullscreen"}
              aria-label={isFullscreen ? "Exit Fullscreen" : "Enter Fullscreen"}
            >
              {isFullscreen ? 
                <Minimize2 className="h-5 w-5 text-gray-700" /> : 
                <Maximize2 className="h-5 w-5 text-gray-700" />
              }
            </button>
          </div>

          {/* Iframe */}
          <iframe
            ref={iframeRef}
            src="/analysis/notebooks/html/${notebook.filename}"
            className="w-full h-full border-0"
            title="${notebook.title}"
            sandbox="allow-scripts allow-same-origin allow-forms"
            style={{ 
              minHeight: isFullscreen ? '100vh' : '70vh',
              borderRadius: isFullscreen ? '0' : 'inherit'
            }}
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
  
  // MBON Enhancement: Add code cell collapsing functionality
  const codeCollapseCSS = `
    <style id="mbon-code-collapse">
      /* Hide all code cells by default */
      .marimo-cell-code, 
      [data-testid="code-editor"], 
      .cm-editor,
      .marimo-cell-editor {
        display: none !important;
      }
      
      /* Show code when explicitly expanded */
      .marimo-cell.mbon-code-expanded .marimo-cell-code,
      .marimo-cell.mbon-code-expanded [data-testid="code-editor"],
      .marimo-cell.mbon-code-expanded .cm-editor,
      .marimo-cell.mbon-code-expanded .marimo-cell-editor {
        display: block !important;
      }
      
      /* Toggle button styling */
      .mbon-code-toggle {
        background: #f8fafc;
        border: 1px solid #e2e8f0;
        border-radius: 6px;
        padding: 6px 12px;
        font-size: 12px;
        font-weight: 500;
        cursor: pointer;
        margin: 8px 0;
        color: #475569;
        transition: all 0.2s ease;
        display: inline-flex;
        align-items: center;
        gap: 6px;
      }
      .mbon-code-toggle:hover {
        background: #f1f5f9;
        border-color: #cbd5e1;
        color: #334155;
      }
      .mbon-code-toggle:focus {
        outline: 2px solid #3b82f6;
        outline-offset: 2px;
      }
      
      /* Icon styling */
      .mbon-code-icon {
        width: 14px;
        height: 14px;
        fill: currentColor;
      }
    </style>
  `;

  const codeCollapseJS = `
    <script id="mbon-code-collapse-script">
      // Wait for page to load and marimo to initialize
      window.addEventListener('load', function() {
        // Use multiple checks to ensure marimo is ready
        let attempts = 0;
        const maxAttempts = 20;
        
        function initializeCodeCollapse() {
          attempts++;
          
          // Check if marimo content is loaded
          const marimoRoot = document.querySelector('#root');
          const hasMarimoContent = marimoRoot && marimoRoot.children.length > 0;
          
          if (hasMarimoContent || attempts >= maxAttempts) {
            addCodeToggleButtons();
          } else {
            // Wait a bit more for marimo to initialize
            setTimeout(initializeCodeCollapse, 200);
          }
        }
        
        // Start initialization after a short delay
        setTimeout(initializeCodeCollapse, 500);
      });
      
      function addCodeToggleButtons() {
        // Multiple selectors to catch different marimo versions
        const cellSelectors = [
          '.marimo-cell',
          '[data-testid="marimo-cell"]',
          '.cell',
          '[class*="cell"]'
        ];
        
        let cellsFound = [];
        
        // Try each selector
        cellSelectors.forEach(selector => {
          const cells = document.querySelectorAll(selector);
          if (cells.length > 0) {
            cellsFound = Array.from(cells);
          }
        });
        
        // Fallback: look for code editors directly
        if (cellsFound.length === 0) {
          const codeEditors = document.querySelectorAll('.cm-editor, [data-testid="code-editor"]');
          codeEditors.forEach(editor => {
            // Find parent container that might be the cell
            let cell = editor.closest('div[class*="cell"]') || editor.parentElement;
            while (cell && !cell.classList.contains('marimo-cell') && cell.parentElement) {
              cell = cell.parentElement;
            }
            if (cell) cellsFound.push(cell);
          });
        }
        
        console.log('MBON: Found', cellsFound.length, 'potential code cells');
        
        cellsFound.forEach(function(cell, index) {
          // Check if this cell has code content
          const hasCode = cell.querySelector('.cm-editor, [data-testid="code-editor"], .marimo-cell-code, .marimo-cell-editor');
          
          if (hasCode && !cell.querySelector('.mbon-code-toggle')) {
            const toggleBtn = document.createElement('button');
            toggleBtn.className = 'mbon-code-toggle';
            toggleBtn.setAttribute('aria-label', 'Toggle code visibility');
            toggleBtn.setAttribute('type', 'button');
            
            // Add icon and text
            toggleBtn.innerHTML = '<svg class="mbon-code-icon" viewBox="0 0 16 16" fill="currentColor"><path d="M5.854 4.854a.5.5 0 1 0-.708-.708l-3.5 3.5a.5.5 0 0 0 0 .708l3.5 3.5a.5.5 0 0 0 .708-.708L2.707 8l3.147-3.146zm4.292 0a.5.5 0 0 1 .708-.708l3.5 3.5a.5.5 0 0 1 0 .708l-3.5 3.5a.5.5 0 0 1-.708-.708L13.293 8l-3.147-3.146z"/></svg>Show Code';
            
            toggleBtn.onclick = function(e) {
              e.preventDefault();
              e.stopPropagation();
              
              if (cell.classList.contains('mbon-code-expanded')) {
                cell.classList.remove('mbon-code-expanded');
                toggleBtn.innerHTML = '<svg class="mbon-code-icon" viewBox="0 0 16 16" fill="currentColor"><path d="M5.854 4.854a.5.5 0 1 0-.708-.708l-3.5 3.5a.5.5 0 0 0 0 .708l3.5 3.5a.5.5 0 0 0 .708-.708L2.707 8l3.147-3.146zm4.292 0a.5.5 0 0 1 .708-.708l3.5 3.5a.5.5 0 0 1 0 .708l-3.5 3.5a.5.5 0 0 1-.708-.708L13.293 8l-3.147-3.146z"/></svg>Show Code';
              } else {
                cell.classList.add('mbon-code-expanded');
                toggleBtn.innerHTML = '<svg class="mbon-code-icon" viewBox="0 0 16 16" fill="currentColor"><path d="M16 8A8 8 0 1 1 0 8a8 8 0 0 1 16 0zM5.354 4.646a.5.5 0 1 0-.708.708L7.293 8l-2.647 2.646a.5.5 0 0 0 .708.708L8 8.707l2.646 2.647a.5.5 0 0 0 .708-.708L8.707 8l2.647-2.646a.5.5 0 0 0-.708-.708L8 7.293 5.354 4.646z"/></svg>Hide Code';
              }
            };
            
            // Insert toggle button at the beginning of the cell
            cell.insertBefore(toggleBtn, cell.firstChild);
            console.log('MBON: Added toggle button to cell', index + 1);
          }
        });
        
        console.log('MBON: Code collapse initialization complete');
      }
    </script>
  `;
  
  // Inject before closing head tag
  cleaned = cleaned.replace('</head>', codeCollapseCSS + codeCollapseJS + '</head>');
  
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