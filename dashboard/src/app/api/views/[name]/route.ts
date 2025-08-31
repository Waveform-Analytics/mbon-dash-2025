/**
 * API route to serve view JSON files
 */

import { NextResponse } from 'next/server';
import fs from 'fs/promises';
import path from 'path';

export async function GET(
  request: Request,
  { params }: { params: Promise<{ name: string }> }
) {
  try {
    const { name } = await params;
    
    // Validate filename to prevent directory traversal
    if (!name.match(/^[a-z_]+\.json$/)) {
      return NextResponse.json(
        { error: 'Invalid view name' },
        { status: 400 }
      );
    }
    
    // Try multiple possible paths for views directory
    const possiblePaths = [
      // New top-level data directory (recommended)
      path.join(process.cwd(), '..', 'data', 'views', name),
      // Legacy python/data directory (fallback)
      path.join(process.cwd(), '..', 'python', 'data', 'views', name),
      // Current directory fallback (for development)
      path.join(process.cwd(), 'data', 'views', name),
    ];
    
    let viewPath: string | null = null;
    
    // Find the first path that exists
    for (const possiblePath of possiblePaths) {
      try {
        await fs.access(possiblePath);
        viewPath = possiblePath;
        break;
      } catch {
        // Continue to next path
      }
    }
    
    if (!viewPath) {
      return NextResponse.json(
        { error: 'View not found in any expected location' },
        { status: 404 }
      );
    }
    
    // Read and return the JSON file
    const data = await fs.readFile(viewPath, 'utf-8');
    const json = JSON.parse(data);
    
    return NextResponse.json(json);
  } catch (error) {
    console.error('Error loading view:', error);
    return NextResponse.json(
      { error: 'Internal server error' },
      { status: 500 }
    );
  }
}