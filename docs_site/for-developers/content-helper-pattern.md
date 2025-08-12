# Content Helper Pattern

Technical implementation guide for the content helper pattern used throughout the MBON dashboard.

## Architecture Overview

The content helper pattern separates presentational text from component logic, enabling non-technical collaborators to safely edit content while maintaining type safety and preventing runtime errors.

### Design Goals

- **Collaboration**: Enable scientists to edit content without touching code
- **Safety**: Prevent breaking changes from content edits
- **Maintainability**: Keep text content organized and discoverable
- **Type Safety**: Preserve TypeScript benefits while allowing text changes

## File Structure

```
app/
├── [page-name]/
│   ├── page.tsx          # Component logic, styling, and structure  
│   └── page.content.tsx  # Text content only
└── page.tsx              # Homepage component
└── page.content.tsx      # Homepage content
```

## Implementation Pattern

### Content Helper File Structure

```typescript title="page.content.tsx"
/**
 * CONTENT HELPER FILE - Safe for non-programmers to edit
 * 
 * This file contains only the text content for [Page Name].
 * You can safely edit any text between the quotes without breaking the website.
 * 
 * EDITING RULES:
 * - Only edit text between quotes: "like this text"
 * - Do NOT change anything outside the quotes
 * - Do NOT delete the commas or brackets
 */

export const PageNameContent = {
  // Page header
  header: {
    title: "Page Title",
    titleHighlight: " Highlighted Part", // Gets gradient styling
    subtitle: "Page description that appears under the title."
  },

  // Main sections organized by visual layout
  researchFocus: {
    title: "Section Title", 
    description: "Section description text."
  },

  // Status messages and UI text
  statusMessages: {
    loading: "Loading data...",
    error: "Unable to load content",
    success: "Content loaded successfully"
  }
}
```

### Component Integration

```typescript title="page.tsx"
'use client';

import { useState } from 'react';
import { PageNameContent } from './page.content';

export default function PageName() {
  return (
    <div className="page-container">
      {/* Hero Section */}
      <div className="text-center mb-8">
        <h1 className="section-heading text-4xl">
          {PageNameContent.header.title}
          <span className="gradient-text">
            {PageNameContent.header.titleHighlight}
          </span>
        </h1>
        <p className="section-description">
          {PageNameContent.header.subtitle}
        </p>
      </div>

      {/* Research Focus */}
      <div className="bg-blue-50 rounded-xl p-6">
        <h2 className="font-semibold text-blue-900 mb-3">
          {PageNameContent.researchFocus.title}
        </h2>
        <p className="text-blue-800">
          {PageNameContent.researchFocus.description}
        </p>
      </div>
    </div>
  );
}
```

## Best Practices

### Content Organization

1. **Group by visual sections**: Mirror the page layout in content structure
2. **Use descriptive keys**: `header.title` not `h1Text` or `titleString`
3. **Keep structure flat**: Avoid deep nesting that confuses editors
4. **Add helpful comments**: Explain what each section represents

```typescript
// ✅ Good: Clear structure with comments
export const Content = {
  // Hero section at top of page
  hero: {
    title: "Marine Biodiversity",
    subtitle: "Research description goes here"
  },
  
  // Research question callout box
  research: {
    question: "What are we investigating?",
    hypothesis: "Our working hypothesis"
  }
}

// ❌ Avoid: Confusing structure
export const Content = {
  strings: {
    text1: "Marine Biodiversity",
    desc: "Research description goes here"
  },
  research: {
    section: {
      content: {
        question: "What are we investigating?"
      }
    }
  }
}
```

### Type Safety Considerations

```typescript
// ✅ Good: Simple string types
export const Content = {
  title: "Marine Biodiversity",
  count: "42 species detected", // Numbers as descriptive strings
  status: "Analysis complete"
}

// ❌ Avoid: Complex types that confuse editors
export const Content = {
  title: "Marine Biodiversity",
  species: ["Fish", "Dolphin"],        // Arrays are hard to edit
  isComplete: true,                    // Booleans are confusing
  config: { showTitle: true },         // Objects complicate structure
  component: <div>Content</div>        // Never include JSX
}
```

### Handling Dynamic Content

For content that includes dynamic values, separate static text from dynamic data:

```typescript
// Content helper - static text only
export const Content = {
  statusMessages: {
    lastUpdated: "Last updated: ",      // Note trailing space
    recordCount: "Total records: ",
    dateRange: "Data from " // Will be: "Data from 2018-2021"
  }
}

// Component - combine static + dynamic
function Component({ date, count, startYear, endYear }) {
  return (
    <>
      <p>{Content.statusMessages.lastUpdated}{date.toLocaleDateString()}</p>
      <p>{Content.statusMessages.recordCount}{count.toLocaleString()}</p>
      <p>{Content.statusMessages.dateRange}{startYear}-{endYear}</p>
    </>
  );
}
```

## Migration Guide

### Converting Existing Pages

1. **Create content file**:
```bash
# For existing page at app/analysis/page.tsx
touch app/analysis/page.content.tsx
```

2. **Extract all user-facing strings**:
```typescript
// Before: Hardcoded strings
<h1>Acoustic Analysis Results</h1>
<p>This analysis examines correlations between indices...</p>

// After: Content helper
<h1>{AnalysisContent.header.title}</h1>
<p>{AnalysisContent.header.description}</p>
```

3. **Import content helper**:
```typescript
import { AnalysisContent } from './page.content';
```

4. **Test thoroughly**:
   - Verify page renders correctly
   - Check TypeScript compilation
   - Test with content edits

### Migration Checklist

- [ ] Content file created with proper header comment
- [ ] All user-facing strings extracted
- [ ] Content organized by visual sections
- [ ] Helper imported in main component
- [ ] All hardcoded strings replaced
- [ ] TypeScript compilation successful
- [ ] Page renders without errors
- [ ] Test content edit works correctly

## Validation and Quality Control

### Automated Checks

Consider adding these validations to your CI/CD pipeline:

```javascript
// Example content validation script
function validateContentFile(filePath) {
  const content = fs.readFileSync(filePath, 'utf8');
  
  // Check for common errors
  const hasValidExport = content.includes('export const');
  const hasComments = content.includes('CONTENT HELPER FILE');
  const validStructure = content.match(/{\s*[^}]*}/);
  
  if (!hasValidExport || !hasComments || !validStructure) {
    throw new Error(`Invalid content file: ${filePath}`);
  }
}
```

### Content Review Process

1. **Syntax validation**: Ensure valid TypeScript
2. **Structure validation**: Verify exported object structure
3. **Content review**: Check scientific accuracy and clarity
4. **Build testing**: Confirm pages render correctly
5. **Deployment**: Merge to production

## Advanced Patterns

### Conditional Content

For content that varies based on application state:

```typescript
// Content helper
export const Content = {
  states: {
    loading: "Loading species data...",
    empty: "No species detected in this time period",
    error: "Unable to load species information"
  }
}

// Component
function SpeciesList({ data, loading, error }) {
  if (loading) return <div>{Content.states.loading}</div>;
  if (error) return <div>{Content.states.error}</div>;  
  if (!data.length) return <div>{Content.states.empty}</div>;
  
  // Render data...
}
```

### Multi-Language Support (Future)

The pattern can be extended for internationalization:

```typescript
// en/page.content.tsx
export const PageContent = {
  title: "Marine Biodiversity",
  subtitle: "Acoustic monitoring research"
}

// es/page.content.tsx  
export const PageContent = {
  title: "Biodiversidad Marina",
  subtitle: "Investigación de monitoreo acústico"
}
```

## Testing Strategies

### Unit Tests

```typescript
import { PageContent } from './page.content';

describe('PageContent', () => {
  it('exports required content sections', () => {
    expect(PageContent.header).toBeDefined();
    expect(PageContent.header.title).toBeTruthy();
    expect(PageContent.header.subtitle).toBeTruthy();
  });

  it('contains valid string content', () => {
    expect(typeof PageContent.header.title).toBe('string');
    expect(PageContent.header.title.length).toBeGreaterThan(0);
  });
});
```

### Integration Tests

```typescript
import { render } from '@testing-library/react';
import PageComponent from './page';

test('renders content from helper', () => {
  const { getByText } = render(<PageComponent />);
  
  // Test that content helper strings appear in rendered output
  expect(getByText(/Marine Biodiversity/)).toBeInTheDocument();
  expect(getByText(/Research description/)).toBeInTheDocument();
});
```

## Maintenance

### Regular Tasks

- **Content audits**: Review scientific accuracy quarterly
- **Structure reviews**: Ensure content files stay organized
- **Performance monitoring**: Check for large content files
- **User feedback**: Gather input from scientist users

### Evolution Considerations

The pattern can evolve to support:

- **Rich text formatting**: Markdown support for longer descriptions
- **Media integration**: References to images and videos
- **Version control**: Content change tracking and rollback
- **CMS integration**: Future connection to content management systems

---

!!! info "Implementation Status"
    The content helper pattern is fully implemented across all dashboard pages. See the [Content Editing Guide](../for-scientists/content-editing.md) for user-facing documentation.

*Next: [API Reference](api-reference.md) | Previous: [Architecture](architecture.md)*