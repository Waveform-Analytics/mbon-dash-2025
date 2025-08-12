# Content Editing Guide

Learn how to safely edit the text content of the MBON dashboard without programming knowledge.

## Overview

The MBON dashboard separates scientific content from technical code, making it easy for you to update research descriptions, methodology text, and other content without needing to understand programming.

!!! tip "Safe Editing Zone"
    All editable content is stored in special "content helper" files that end with `.content.tsx`. These files contain only text and are safe for non-programmers to edit.

## Finding Content Files

Content files are located in the dashboard source code:

1. Navigate to `src/app/` in the project folder
2. Look for files ending in `.content.tsx`

### Available Content Files

| Page | Content File | What You Can Edit |
|------|-------------|------------------|
| Homepage | `page.content.tsx` | Main title, metrics labels, navigation cards |
| Acoustic Analysis | `acoustic-biodiversity/page.content.tsx` | Research questions, analysis descriptions |
| Environmental Factors | `environmental-factors/page.content.tsx` | Environmental analysis text |
| Glossary | `acoustic-glossary/page.content.tsx` | Index guide descriptions |
| Stations | `stations/page.content.tsx` | Station information text |
| Species | `species/page.content.tsx` | Species analysis descriptions |
| Temporal Patterns | `temporal/page.content.tsx` | Time series analysis text |
| Data Explorer | `explorer/page.content.tsx` | Explorer tool descriptions |

## Editing Rules

When editing these files, follow these simple but important rules:

### ✅ Safe to Edit

- **Text between quotes**: `"This text is safe to edit"`
- **Scientific descriptions and methodology**
- **Research questions and hypotheses** 
- **Data interpretation notes**
- **Acknowledgments and citations**

### ❌ Never Change

- **Anything outside the quotes**: `title:`, `{`, `}`, `,`
- **File structure**: Brackets, commas, colons
- **Property names**: The words before the colon
- **Other file types**: Only edit `.content.tsx` files

## Example Edit

Here's a safe way to update content:

=== "Before"
    ```typescript
    header: {
      title: "Acoustic Indices as Biodiversity Proxies",
      subtitle: "Analysis to identify which acoustic indices best predict marine soundscape biodiversity patterns."
    }
    ```

=== "After (✅ Good)"
    ```typescript
    header: {
      title: "Acoustic Indices as Marine Biodiversity Indicators", 
      subtitle: "Statistical analysis identifying which acoustic indices most accurately predict species presence and community structure."
    }
    ```

=== "Wrong (❌ Bad)"
    ```typescript
    header: {
      title: Acoustic Indices as Marine Biodiversity Indicators,  // Missing quotes!
      subtitle: "Statistical analysis identifying indices."
    }
    // Missing comma and closing bracket!
    ```

## Common Content Areas

### Page Headers
Every page has a header section with title and subtitle:

```typescript
header: {
  title: "Main Page Title",
  titleHighlight: " Highlighted Part", // This gets special styling
  subtitle: "Description that appears under the main title"
}
```

### Research Questions
Many pages have research focus sections:

```typescript
researchFocus: {
  title: "Research Question",
  description: "What specific question are we investigating?"
}
```

### Analysis Descriptions
Scientific analysis sections:

```typescript
analysisName: {
  title: "Name of Analysis",
  status: "(Planned)" or "(In Progress)" or "(Complete)",
  description: "What this analysis does and why it matters scientifically"
}
```

## Making Changes Live

### During Development
1. Save the `.content.tsx` file after editing
2. The website will automatically update if running locally
3. Refresh your browser to see changes

### For Production
1. Save your changes
2. Commit the files to the Git repository
3. The live website will update automatically via deployment

## Scientific Writing Tips

### Content Guidelines
- **Be concise but informative** - Dashboard space is limited
- **Define acronyms** on first use (e.g., "Principal Component Analysis (PCA)")
- **Include units** for all measurements (°C, meters, Hz, etc.)
- **Reference timeframes** when discussing datasets (2018, 2021)
- **Use consistent terminology** with published literature

### Research Context
When updating research descriptions:

- **State the biological relevance** of each analysis
- **Explain the practical implications** for marine monitoring
- **Connect to broader MBON goals** and ecosystem assessment
- **Mention limitations or assumptions** where appropriate

### Data References
When describing datasets:

- **Specify time periods**: "2018 and 2021 deployment periods"
- **Include station context**: "three stations (9M, 14M, 37M) in May River"
- **Mention data types**: "manual species annotations" vs "acoustic indices"
- **Note processing steps**: "2-hour samples from continuous recordings"

## Troubleshooting

### Common Issues

!!! warning "Page Shows 'undefined'"
    **Problem**: Text appears as "undefined" on the website
    
    **Solution**: Check that all text is properly enclosed in quotes

!!! error "Syntax Error"
    **Problem**: Website shows an error or won't load
    
    **Solution**: Verify all commas and brackets are intact - compare with working examples

!!! info "Changes Not Showing"
    **Problem**: Edits aren't appearing on the website
    
    **Solution**: Save the file and refresh your browser. Check the browser console for errors.

### Getting Help

| Issue Type | Contact |
|------------|---------|
| **Scientific accuracy** | Project lead scientist |
| **Technical problems** | Development team |
| **Urgent fixes** | Check GitHub issues or contact maintainer |

## File Safety Checklist

Before saving any content file, verify:

- [ ] All text is enclosed in quotes
- [ ] Commas appear after each section (except the last one)
- [ ] Opening and closing brackets match
- [ ] No extra or missing characters
- [ ] File ends with the closing bracket and semicolon

---

!!! success "Ready to Edit"
    You're now ready to safely edit dashboard content! Start with small changes and always double-check your syntax. The content helper pattern ensures your scientific expertise can improve the dashboard without technical risks.

*For technical implementation details, see the [Content Helper Pattern Guide](../for-developers/content-helper-pattern.md).*