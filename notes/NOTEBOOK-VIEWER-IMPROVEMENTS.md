# Notebook Viewer Improvements Plan

## Overview

This document outlines the approach for implementing two key improvements to the notebook viewing system:

1. **Automatic Code Cell Collapsing**: All code cells should be collapsed by default when viewed in the dashboard, regardless of their save state in the original notebook
2. **Fullscreen Notebook View**: Users should be able to expand the notebook iframe to fullscreen for better readability

## Current System Architecture

### Data Flow
```
Marimo Notebooks (.py) 
    ↓ [export-notebooks.sh]
HTML Files (__marimo__/)
    ↓ [build-notebooks.js]
Cleaned HTML + React Pages (dashboard/public/ + app/analysis/notebooks/)
    ↓ [Next.js rendering]
Dashboard Display (iframe embedding)
```

### Current Components
- **Export Script**: `scripts/export-notebooks.sh` - Uses marimo export to generate HTML
- **Build Script**: `scripts/build-dashboard.sh` - Orchestrates the build process  
- **HTML Processor**: `dashboard/scripts/build-notebooks.js` - Cleans HTML and creates React pages
- **Page Template**: Generated React pages with iframe embedding
- **Current Display**: ~70vh height iframe with header information

## Implementation Plan

### 1. Automatic Code Cell Collapsing

#### Understanding Marimo HTML Structure
From the sample HTML file analysis:
- Marimo uses a React-based frontend with cells defined in `window.__MARIMO_MOUNT_CONFIG__.notebook.cells`
- Each cell has a `config.hide_code` property that controls visibility
- The frontend renders based on this configuration
- Code cells are likely DOM elements that can be targeted with CSS/JavaScript

#### Approach: Post-Export HTML Modification
**Location**: Modify `dashboard/scripts/build-notebooks.js` in the `cleanMarimoHtml()` function

**Strategy**:
1. **CSS Injection**: Add CSS rules to hide all code cells by default
2. **JavaScript Injection**: Add toggle functionality for individual cells
3. **DOM Manipulation**: Inject expand/collapse controls

**Implementation Steps**:

```javascript
function cleanMarimoHtml(htmlContent) {
  let cleaned = htmlContent;
  
  // Existing preload removal code...
  
  // NEW: Inject code cell collapsing functionality
  const codeCollapseCSS = `
    <style id="mbon-code-collapse">
      /* Hide all code cells by default */
      .marimo-cell-code, [data-testid="code-editor"], .cm-editor {
        display: none !important;
      }
      
      /* Show code when explicitly expanded */
      .marimo-cell.code-expanded .marimo-cell-code,
      .marimo-cell.code-expanded [data-testid="code-editor"],
      .marimo-cell.code-expanded .cm-editor {
        display: block !important;
      }
      
      /* Add toggle button styling */
      .mbon-code-toggle {
        background: #f3f4f6;
        border: 1px solid #d1d5db;
        border-radius: 4px;
        padding: 4px 8px;
        font-size: 12px;
        cursor: pointer;
        margin-bottom: 8px;
      }
      .mbon-code-toggle:hover {
        background: #e5e7eb;
      }
    </style>
  `;

  const codeCollapseJS = `
    <script id="mbon-code-collapse-script">
      window.addEventListener('load', function() {
        // Wait for marimo to initialize
        setTimeout(function() {
          addCodeToggleButtons();
        }, 1000);
      });
      
      function addCodeToggleButtons() {
        // Find all cells with code
        const cells = document.querySelectorAll('.marimo-cell');
        cells.forEach(function(cell, index) {
          const codeEditor = cell.querySelector('.marimo-cell-code, [data-testid="code-editor"], .cm-editor');
          if (codeEditor && !cell.querySelector('.mbon-code-toggle')) {
            const toggleBtn = document.createElement('button');
            toggleBtn.className = 'mbon-code-toggle';
            toggleBtn.innerHTML = '📄 Show Code';
            toggleBtn.onclick = function() {
              if (cell.classList.contains('code-expanded')) {
                cell.classList.remove('code-expanded');
                toggleBtn.innerHTML = '📄 Show Code';
              } else {
                cell.classList.add('code-expanded');
                toggleBtn.innerHTML = '📄 Hide Code';
              }
            };
            
            // Insert toggle button before the cell content
            const cellContent = cell.querySelector('.marimo-cell-output') || cell.firstChild;
            if (cellContent) {
              cell.insertBefore(toggleBtn, cellContent);
            }
          }
        });
      }
    </script>
  `;
  
  // Inject before closing head tag
  cleaned = cleaned.replace('</head>', codeCollapseCSS + codeCollapseJS + '</head>');
  
  return cleaned;
}
```

#### Alternative Approach: Configuration Override
If DOM manipulation proves difficult, override the marimo configuration:

```javascript
// In cleanMarimoHtml function
// Override the notebook configuration to hide all code
cleaned = cleaned.replace(
  /("config":\s*{[^}]*"hide_code":\s*)(true|false)/g,
  '$1true'
);
```

### 2. Fullscreen Notebook View

#### Approach: React Component Enhancement
**Location**: Modify the generated notebook page template in `dashboard/scripts/build-notebooks.js`

#### Features Required:
1. **Fullscreen Toggle Button**: Expand/collapse icon in top-right corner
2. **Fullscreen Mode**: 100vw/100vh iframe with minimal UI
3. **Easy Exit**: ESC key + close button
4. **Responsive Design**: Works on different screen sizes

#### Implementation:

**Enhanced Page Template**:
```javascript
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
    const handleKeyPress = (event) => {
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
          {/* Existing header content */}
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
            {/* Rest of header content... */}
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
                className="bg-white/90 hover:bg-white border rounded-lg p-2 shadow-lg transition-all"
                title="Exit Fullscreen (ESC)"
              >
                <X className="h-5 w-5" />
              </button>
            )}
            
            <button
              onClick={toggleFullscreen}
              className="bg-white/90 hover:bg-white border rounded-lg p-2 shadow-lg transition-all"
              title={isFullscreen ? "Exit Fullscreen" : "Enter Fullscreen"}
            >
              {isFullscreen ? 
                <Minimize2 className="h-5 w-5" /> : 
                <Maximize2 className="h-5 w-5" />
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
}`;
```

### 3. Enhanced UI/UX Features

#### Additional Improvements:
1. **Loading States**: Show loading spinner while notebook loads
2. **Error Handling**: Handle iframe loading errors gracefully
3. **Mobile Responsive**: Ensure fullscreen works on mobile devices
4. **Keyboard Navigation**: Tab through controls, arrow key navigation
5. **Accessibility**: Proper ARIA labels, screen reader support

#### CSS Enhancements:
```css
/* Add to global styles or component styles */
.notebook-fullscreen-overlay {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  z-index: 9999;
  background: white;
}

.notebook-controls {
  position: absolute;
  top: 1rem;
  right: 1rem;
  z-index: 10;
  display: flex;
  gap: 0.5rem;
}

.notebook-control-btn {
  background: rgba(255, 255, 255, 0.9);
  backdrop-filter: blur(4px);
  border: 1px solid rgba(0, 0, 0, 0.1);
  border-radius: 8px;
  padding: 8px;
  cursor: pointer;
  transition: all 0.2s ease;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
}

.notebook-control-btn:hover {
  background: rgba(255, 255, 255, 1);
  transform: translateY(-1px);
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
}
```

## Testing Strategy

### Code Cell Collapsing Tests:
1. **Multiple Notebooks**: Test across different notebook types (01_data_prep, 02_temporal_aggregation, etc.)
2. **Cell Variations**: Ensure it works with different cell types (markdown, code, mixed)
3. **Browser Compatibility**: Test in Chrome, Firefox, Safari, Edge
4. **Toggle Functionality**: Verify individual cell expand/collapse works
5. **Performance**: Ensure no impact on notebook loading time

### Fullscreen Tests:
1. **Entry/Exit**: Test both button and ESC key functionality
2. **Mobile Devices**: Verify fullscreen on tablets and phones
3. **Screen Resolutions**: Test on different monitor sizes
4. **Browser Fullscreen**: Ensure compatibility with browser native fullscreen
5. **Navigation**: Verify back button and URL handling in fullscreen mode

## Implementation Timeline

### Phase 1: Code Cell Collapsing (2-3 hours)
1. ✅ Analyze marimo HTML structure
2. Implement HTML processing modifications
3. Test toggle functionality
4. Refine CSS/JS for smooth UX

### Phase 2: Fullscreen Functionality (2-3 hours)
1. Update React page template
2. Implement fullscreen logic
3. Add keyboard shortcuts
4. Test responsive behavior

### Phase 3: Integration & Testing (1-2 hours)
1. Update build process
2. Test complete workflow
3. Validate across multiple notebooks
4. Document usage

## Benefits

### Code Cell Collapsing:
- **Cleaner Reading Experience**: Focus on outputs and explanations
- **Reduced Cognitive Load**: Less visual noise for non-technical users
- **Flexible Access**: Technical users can still view code when needed
- **Consistent Presentation**: Uniform appearance regardless of notebook save state

### Fullscreen Functionality:
- **Better Readability**: Larger viewing area for complex visualizations
- **Improved Analysis**: Better for detailed data examination
- **Professional Presentation**: Clean, distraction-free viewing
- **Enhanced User Experience**: Modern, intuitive interface

## Technical Considerations

### Code Cell Collapsing:
- **Marimo Updates**: Solution should be resilient to marimo version changes
- **DOM Targeting**: May need to adjust selectors as marimo evolves
- **Performance**: Minimal impact on page load times
- **Accessibility**: Toggle buttons must be keyboard accessible

### Fullscreen:
- **Z-index Management**: Ensure fullscreen appears above all other elements
- **URL State**: Consider preserving fullscreen state in URL for sharing
- **Mobile Safari**: Special handling for iOS fullscreen behavior
- **Print Functionality**: Ensure notebooks can still be printed

## Future Enhancements

1. **Code Cell Themes**: Syntax highlighting themes for expanded code
2. **Copy Code Button**: Easy code copying from expanded cells
3. **Cell Linking**: Direct links to specific cells
4. **Presentation Mode**: Auto-advance through cells
5. **Export Functions**: PDF export from fullscreen view
6. **Split View**: Side-by-side code and output viewing

This implementation plan provides a comprehensive approach to both requested improvements while maintaining the existing workflow and ensuring a smooth user experience.