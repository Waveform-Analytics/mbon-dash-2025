# Observable Plot MCP Server Setup Guide

A comprehensive guide to create a free MCP (Model Context Protocol) server that connects Claude Code to Observable Plot documentation for enhanced accuracy and up-to-date API references.

## Overview

This guide will help you build an MCP server that provides Claude Code with access to:
- **Observable Plot official documentation** (observablehq.com/plot/)
- **GitHub repository content** (README, CHANGELOG, examples)
- **API references and TypeScript definitions**
- **Real examples and code snippets**

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
Claude Code ←→ Your MCP Server ←→ Observable Plot Docs
                     ↓
              Local Cache/Database
```

## Implementation Approach

### Option 1: Simple Web Scraper MCP (Recommended for Start)

**Pros**: Easy to implement, always current
**Cons**: Requires web requests, potential rate limiting

### Option 2: GitHub API + Website Hybrid

**Pros**: More reliable, uses official APIs
**Cons**: Slightly more complex setup

### Option 3: Pre-cached Documentation

**Pros**: Fastest response times, no rate limits
**Cons**: Requires periodic updates

## Step-by-Step Implementation

### Step 1: Project Setup

```bash
# Create new Node.js project
mkdir observable-plot-mcp
cd observable-plot-mcp
npm init -y

# Install dependencies
npm install @anthropic/mcp-sdk
npm install cheerio axios node-fetch
npm install @types/node typescript ts-node --save-dev

# Create TypeScript config
npx tsc --init
```

### Step 2: Basic MCP Server Structure

Create `src/server.ts`:

```typescript
import { MCPServer } from '@anthropic/mcp-sdk';
import { DocumentationFetcher } from './documentation-fetcher';

class ObservablePlotMCPServer {
  private server: MCPServer;
  private docFetcher: DocumentationFetcher;

  constructor() {
    this.server = new MCPServer({
      name: "observable-plot-docs",
      version: "1.0.0"
    });
    
    this.docFetcher = new DocumentationFetcher();
    this.setupHandlers();
  }

  private setupHandlers() {
    // Register available tools
    this.server.setRequestHandler('tools/list', async () => ({
      tools: [
        {
          name: "search_plot_docs",
          description: "Search Observable Plot documentation",
          inputSchema: {
            type: "object",
            properties: {
              query: { type: "string", description: "Search query" },
              section: { 
                type: "string", 
                enum: ["api", "examples", "getting-started", "all"],
                description: "Documentation section to search"
              }
            },
            required: ["query"]
          }
        },
        {
          name: "get_plot_api",
          description: "Get specific Observable Plot API documentation",
          inputSchema: {
            type: "object",
            properties: {
              method: { type: "string", description: "API method or mark type" }
            },
            required: ["method"]
          }
        }
      ]
    }));

    // Handle tool calls
    this.server.setRequestHandler('tools/call', async (request) => {
      const { name, arguments: args } = request.params;

      switch (name) {
        case "search_plot_docs":
          return await this.handleSearchDocs(args.query, args.section);
        case "get_plot_api":
          return await this.handleGetAPI(args.method);
        default:
          throw new Error(`Unknown tool: ${name}`);
      }
    });
  }

  private async handleSearchDocs(query: string, section: string = "all") {
    const results = await this.docFetcher.searchDocumentation(query, section);
    return {
      content: [{
        type: "text",
        text: JSON.stringify(results, null, 2)
      }]
    };
  }

  private async handleGetAPI(method: string) {
    const apiDoc = await this.docFetcher.getAPIDocumentation(method);
    return {
      content: [{
        type: "text", 
        text: apiDoc
      }]
    };
  }

  async start() {
    await this.server.connect();
    console.log("Observable Plot MCP Server started");
  }
}

const server = new ObservablePlotMCPServer();
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
  "name": "observable-plot-mcp",
  "version": "1.0.0",
  "type": "module",
  "scripts": {
    "build": "tsc",
    "start": "node dist/server.js",
    "dev": "ts-node src/server.ts"
  },
  "dependencies": {
    "@anthropic/mcp-sdk": "latest",
    "axios": "^1.0.0",
    "cheerio": "^1.0.0"
  },
  "devDependencies": {
    "@types/node": "^20.0.0",
    "typescript": "^5.0.0",
    "ts-node": "^10.0.0"
  }
}
```

## Usage with Claude Code

### Step 5: Connect to Claude Code

1. **Build and start your MCP server**:
```bash
npm run build
npm start
```

2. **Configure Claude Code** to connect to your MCP server by updating your Claude Code configuration to include your MCP server endpoint.

3. **Test the connection** by asking Claude Code Observable Plot questions.

## Example Queries

Once set up, you can ask Claude Code questions like:

- "How do I create a scatter plot with Observable Plot?"
- "What are the latest features in Observable Plot?"
- "Show me examples of using the dot mark"
- "What's the current API for Plot.plot()?"

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

- MCP Server: Free to develop and run
- Observable Plot docs: Publicly available
- GitHub API: 60 requests/hour free (5,000 with free token)
- Hosting: Can run locally or use free tier services

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

1. **Start Simple**: Begin with the basic scraper approach
2. **Test Thoroughly**: Verify Claude Code can connect and get responses
3. **Iterate**: Add more sophisticated features based on usage
4. **Monitor**: Track what documentation Claude Code requests most
5. **Optimize**: Improve based on actual usage patterns

This approach will give Claude Code access to current, comprehensive Observable Plot documentation, significantly improving its accuracy when helping with Plot-related coding tasks.