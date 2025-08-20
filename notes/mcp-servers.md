# Observable Plot Documentation Server Setup Guide

A guide to create a local documentation server that provides Claude Code with access to current Observable Plot documentation for enhanced accuracy and up-to-date API references.

## Overview

This guide will help you build a local HTTP server that provides Claude Code with access to:
- **Observable Plot official documentation** (observablehq.com/plot/)
- **GitHub repository content** (README, CHANGELOG, examples)
- **API references and TypeScript definitions**
- **Real examples and code snippets**

**Note**: While we'll keep an eye on MCP (Model Context Protocol) for future implementation, we're starting with a simple HTTP server approach that works immediately with Claude Code's existing WebFetch tool.

## Available Documentation Sources

Based on research, Observable Plot documentation is available through multiple free sources:

1. **Official Documentation Website**: `https://observablehq.com/plot/`
    - Comprehensive API docs
    - Interactive examples
    - Getting started guides

2. **GitHub Repository**: `https://github.com/observablehq/plot`
    - Source code and TypeScript definitions
    - README and CHANGELOG
    - Example files in `/docs` folder
    - Test examples showing real usage patterns

3. **GitHub API Access**: Free tier provides 60 requests/hour (5,000 with token)

## Architecture Overview

```
Claude Code ←→ WebFetch Tool ←→ Your HTTP Server ←→ Observable Plot Docs
                                      ↓
                               Local Cache/Database
```

## Implementation Approach

### Phase 1: Local HTTP Server (Current Implementation)

**Pros**: Works immediately with Claude Code, no MCP dependencies, easy to debug
**Cons**: Requires manual WebFetch calls (not a major limitation)

### Phase 2: MCP Migration (Future Consideration)

**Pros**: Tighter Claude Code integration, automatic tool discovery
**Cons**: Depends on MCP SDK stability and availability

We'll start with Phase 1 and migrate to MCP once it's proven stable and beneficial.

## Step-by-Step Implementation

### Step 1: Project Setup

```bash
# Create new Node.js project
mkdir observable-plot-docs-server
cd observable-plot-docs-server
npm init -y

# Install dependencies
npm install express cors
npm install cheerio axios node-fetch
npm install @types/node @types/express typescript ts-node --save-dev

# Create TypeScript config
npx tsc --init
```

### Step 2: Basic HTTP Server Structure

Create `src/server.ts`:

```typescript
import express from 'express';
import cors from 'cors';
import { DocumentationFetcher } from './documentation-fetcher';

class ObservablePlotDocsServer {
  private app: express.Application;
  private docFetcher: DocumentationFetcher;
  private port: number;

  constructor(port: number = 3001) {
    this.app = express();
    this.port = port;
    this.docFetcher = new DocumentationFetcher();
    this.setupMiddleware();
    this.setupRoutes();
  }

  private setupMiddleware() {
    this.app.use(cors());
    this.app.use(express.json());
  }

  private setupRoutes() {
    // Health check
    this.app.get('/health', (req, res) => {
      res.json({ status: 'OK', service: 'observable-plot-docs' });
    });

    // Search documentation
    this.app.get('/search/:query', async (req, res) => {
      try {
        const { query } = req.params;
        const { section = 'all' } = req.query;
        
        const results = await this.docFetcher.searchDocumentation(
          query, 
          section as string
        );
        
        res.json({
          query,
          section,
          results,
          count: results.length
        });
      } catch (error) {
        res.status(500).json({ 
          error: 'Search failed', 
          message: error.message 
        });
      }
    });

    // Get specific API documentation
    this.app.get('/api/:method', async (req, res) => {
      try {
        const { method } = req.params;
        const apiDoc = await this.docFetcher.getAPIDocumentation(method);
        
        res.json({
          method,
          documentation: apiDoc
        });
      } catch (error) {
        res.status(500).json({ 
          error: 'API lookup failed', 
          message: error.message 
        });
      }
    });

    // Get examples for specific mark types
    this.app.get('/examples/:markType', async (req, res) => {
      try {
        const { markType } = req.params;
        const examples = await this.docFetcher.getExamples(markType);
        
        res.json({
          markType,
          examples
        });
      } catch (error) {
        res.status(500).json({ 
          error: 'Examples lookup failed', 
          message: error.message 
        });
      }
    });
  }

  async start() {
    // Initialize documentation cache
    console.log('Initializing documentation cache...');
    await this.docFetcher.initialize();
    
    this.app.listen(this.port, () => {
      console.log(`Observable Plot docs server running on http://localhost:${this.port}`);
      console.log('Available endpoints:');
      console.log(`  GET /health`);
      console.log(`  GET /search/:query?section=api|examples|all`);
      console.log(`  GET /api/:method`);
      console.log(`  GET /examples/:markType`);
    });
  }
}

const server = new ObservablePlotDocsServer();
server.start().catch(console.error);
```

### Step 3: Documentation Fetcher

Create `src/documentation-fetcher.ts`:

```typescript
import axios from 'axios';
import * as cheerio from 'cheerio';
import { promises as fs } from 'fs';
import path from 'path';

interface DocSection {
  title: string;
  url: string;
  content: string;
  examples?: string[];
}

export class DocumentationFetcher {
  private cache: Map<string, any> = new Map();
  private cacheDir = path.join(__dirname, '../cache');
  private initialized = false;

  constructor() {
    this.ensureCacheDir();
  }

  private async ensureCacheDir() {
    try {
      await fs.mkdir(this.cacheDir, { recursive: true });
    } catch (error) {
      // Directory exists
    }
  }

  async initialize() {
    if (this.initialized) return;
    
    console.log('Pre-loading core documentation...');
    
    // Pre-load common searches to warm the cache
    const commonQueries = [
      'scatter plot', 'bar chart', 'line chart', 'heatmap',
      'Plot.dot', 'Plot.bar', 'Plot.line', 'Plot.cell',
      'getting started', 'marks', 'scales'
    ];
    
    for (const query of commonQueries) {
      try {
        await this.searchDocumentation(query, 'all');
      } catch (error) {
        console.warn(`Failed to pre-load ${query}:`, error.message);
      }
    }
    
    this.initialized = true;
    console.log('Documentation cache initialized');
  }

  async getExamples(markType: string): Promise<string[]> {
    const cacheKey = `examples_${markType}`;
    
    if (this.cache.has(cacheKey)) {
      return this.cache.get(cacheKey);
    }

    const examples: string[] = [];
    
    try {
      // Search for specific mark type examples
      const searchResults = await this.searchDocumentation(markType, 'examples');
      
      searchResults.forEach(result => {
        if (result.examples) {
          examples.push(...result.examples);
        }
      });
      
      this.cache.set(cacheKey, examples);
    } catch (error) {
      console.warn(`Failed to get examples for ${markType}:`, error.message);
    }
    
    return examples;
  }

  async searchDocumentation(query: string, section: string): Promise<DocSection[]> {
    const cacheKey = `search_${query}_${section}`;
    
    if (this.cache.has(cacheKey)) {
      return this.cache.get(cacheKey);
    }

    const results: DocSection[] = [];

    // Search main documentation site
    if (section === "all" || section === "api") {
      const apiResults = await this.searchPlotWebsite(query);
      results.push(...apiResults);
    }

    // Search GitHub repository
    if (section === "all" || section === "examples") {
      const githubResults = await this.searchGitHubRepo(query);
      results.push(...githubResults);
    }

    this.cache.set(cacheKey, results);
    return results;
  }

  private async searchPlotWebsite(query: string): Promise<DocSection[]> {
    const baseUrl = "https://observablehq.com/plot";
    const sections = [
      "/what-is-plot",
      "/getting-started", 
      "/features/plots",
      "/features/marks",
      "/features/scales",
      "/features/transforms"
    ];

    const results: DocSection[] = [];

    for (const section of sections) {
      try {
        const response = await axios.get(`${baseUrl}${section}`);
        const $ = cheerio.load(response.data);
        
        const content = this.extractTextContent($);
        
        if (content.toLowerCase().includes(query.toLowerCase())) {
          results.push({
            title: $('h1').first().text() || section.replace("/", ""),
            url: `${baseUrl}${section}`,
            content: this.extractRelevantContent(content, query),
            examples: this.extractCodeExamples($)
          });
        }
      } catch (error) {
        console.warn(`Failed to fetch ${section}:`, error.message);
      }
    }

    return results;
  }

  private async searchGitHubRepo(query: string): Promise<DocSection[]> {
    const results: DocSection[] = [];
    
    try {
      // Search README
      const readmeResponse = await axios.get(
        "https://raw.githubusercontent.com/observablehq/plot/main/README.md"
      );
      
      if (readmeResponse.data.toLowerCase().includes(query.toLowerCase())) {
        results.push({
          title: "README",
          url: "https://github.com/observablehq/plot/blob/main/README.md",
          content: this.extractRelevantContent(readmeResponse.data, query)
        });
      }

      // Search CHANGELOG
      const changelogResponse = await axios.get(
        "https://raw.githubusercontent.com/observablehq/plot/main/CHANGELOG.md"
      );
      
      if (changelogResponse.data.toLowerCase().includes(query.toLowerCase())) {
        results.push({
          title: "CHANGELOG",
          url: "https://github.com/observablehq/plot/blob/main/CHANGELOG.md", 
          content: this.extractRelevantContent(changelogResponse.data, query)
        });
      }

    } catch (error) {
      console.warn("Failed to search GitHub:", error.message);
    }

    return results;
  }

  async getAPIDocumentation(method: string): Promise<string> {
    const cacheKey = `api_${method}`;
    
    if (this.cache.has(cacheKey)) {
      return this.cache.get(cacheKey);
    }

    // Try to get TypeScript definitions from GitHub
    try {
      const response = await axios.get(
        "https://raw.githubusercontent.com/observablehq/plot/main/src/index.js"
      );
      
      const content = response.data;
      const methodRegex = new RegExp(`export.*${method}.*\\{[\\s\\S]*?\\}`, 'gm');
      const matches = content.match(methodRegex);
      
      if (matches) {
        const result = `API Documentation for ${method}:\n\n${matches[0]}`;
        this.cache.set(cacheKey, result);
        return result;
      }
    } catch (error) {
      console.warn(`Failed to get API docs for ${method}:`, error.message);
    }

    return `No specific API documentation found for ${method}. Try searching the general documentation.`;
  }

  private extractTextContent($: cheerio.CheerioAPI): string {
    // Remove script tags, style tags, etc.
    $('script, style, nav, footer').remove();
    return $('body').text().replace(/\s+/g, ' ').trim();
  }

  private extractRelevantContent(content: string, query: string, contextSize: number = 500): string {
    const lowerContent = content.toLowerCase();
    const lowerQuery = query.toLowerCase();
    const index = lowerContent.indexOf(lowerQuery);
    
    if (index === -1) return content.substring(0, 1000);
    
    const start = Math.max(0, index - contextSize);
    const end = Math.min(content.length, index + query.length + contextSize);
    
    return "..." + content.substring(start, end) + "...";
  }

  private extractCodeExamples($: cheerio.CheerioAPI): string[] {
    const examples: string[] = [];
    
    $('pre code, .highlight code').each((_, element) => {
      const code = $(element).text().trim();
      if (code.includes('Plot.') && code.length > 20) {
        examples.push(code);
      }
    });
    
    return examples.slice(0, 3); // Limit to 3 examples
  }
}
```

### Step 4: Package Configuration

Update `package.json`:

```json
{
  "name": "observable-plot-docs-server",
  "version": "1.0.0",
  "type": "commonjs",
  "scripts": {
    "build": "tsc",
    "start": "node dist/server.js",
    "dev": "ts-node src/server.ts"
  },
  "dependencies": {
    "express": "^4.18.0",
    "cors": "^2.8.5",
    "axios": "^1.0.0",
    "cheerio": "^1.0.0",
    "node-fetch": "^3.0.0"
  },
  "devDependencies": {
    "@types/node": "^20.0.0",
    "@types/express": "^4.17.0",
    "@types/cors": "^2.8.0",
    "typescript": "^5.0.0",
    "ts-node": "^10.0.0"
  }
}
```

## Usage with Claude Code

### Step 5: Start and Test Your Server

1. **Build and start your server**:
```bash
npm run build
npm start

# Or for development:
npm run dev
```

2. **Test endpoints manually**:
```bash
# Health check
curl http://localhost:3001/health

# Search for documentation
curl http://localhost:3001/search/scatter-plot

# Get API docs for specific method
curl http://localhost:3001/api/dot

# Get examples for mark type
curl http://localhost:3001/examples/scatter
```

3. **Use with Claude Code** via WebFetch:
   - When you need Observable Plot help, have Claude Code call:
   - `WebFetch("http://localhost:3001/search/YOUR_QUERY", "Get Observable Plot documentation")`

## Example Usage with Claude Code

Once your server is running, you can improve Claude Code's Observable Plot responses by having it fetch current documentation:

**Example 1: Getting scatter plot help**
```
You: "How do I create a scatter plot with Observable Plot?"
You to Claude Code: "Use WebFetch to get scatter plot docs from http://localhost:3001/search/scatter-plot first, then answer based on current docs"
```

**Example 2: Learning about specific marks**  
```
You: "Show me examples of using the dot mark"
You to Claude Code: "Get dot mark examples from http://localhost:3001/examples/dot"
```

**Example 3: API reference lookup**
```
You: "What's the current API for Plot.cell()?"
You to Claude Code: "Check http://localhost:3001/api/cell for the latest cell mark API"
```

This ensures Claude Code uses current, accurate Observable Plot documentation instead of potentially outdated training data.

## Enhancement Ideas

### Advanced Features to Add Later

1. **Caching Strategy**: Implement Redis or file-based caching
2. **Live Documentation**: Set up webhooks to update when Plot docs change
3. **Example Database**: Index all examples for better search
4. **TypeScript Integration**: Parse .d.ts files for precise API info
5. **Version Tracking**: Support multiple Plot versions

### Performance Optimizations

1. **Batch Requests**: Group multiple documentation fetches
2. **Intelligent Caching**: Cache based on content hash
3. **Background Updates**: Refresh cache periodically

## Cost Analysis

**Total Cost: FREE**

- HTTP Server: Free to develop and run locally
- Observable Plot docs: Publicly available
- GitHub API: 60 requests/hour free (5,000 with free token)  
- Hosting: Runs on your local machine

## Troubleshooting

### Common Issues

1. **Rate Limiting**: Implement exponential backoff
2. **CORS Issues**: Add proper headers for web scraping
3. **Cache Invalidation**: Set TTL for cached content
4. **Memory Usage**: Implement cache size limits

### Debugging Tips

1. Add verbose logging to see what's being fetched
2. Test individual documentation sources separately
3. Monitor cache hit rates
4. Check network connectivity and timeouts

## Next Steps

1. **Start Simple**: Begin with the HTTP server approach outlined above
2. **Test Thoroughly**: Verify Claude Code can fetch docs via WebFetch and provide better responses
3. **Iterate**: Add more sophisticated features based on what you find most useful
4. **Monitor**: Track what documentation you request most through Claude Code
5. **Future**: Consider migrating to MCP once the ecosystem matures

## Future MCP Migration

When MCP becomes stable and widely supported:

1. **Assess Benefits**: Does MCP provide significant advantages over WebFetch?
2. **Migration Path**: The DocumentationFetcher class can be reused with MCP protocol
3. **Tool Discovery**: MCP allows Claude Code to automatically discover available documentation tools
4. **Integration**: Tighter integration with Claude Code's tool ecosystem

This HTTP server approach gives you immediate access to current Observable Plot documentation, significantly improving Claude Code's accuracy for Plot-related tasks, while keeping the door open for MCP migration when appropriate.