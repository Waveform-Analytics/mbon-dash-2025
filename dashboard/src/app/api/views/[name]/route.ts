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
    
    // Path to Python views directory
    const viewPath = path.join(
      process.cwd(),
      '..',
      'python',
      'data',
      'views',
      name
    );
    
    // Check if file exists
    try {
      await fs.access(viewPath);
    } catch {
      return NextResponse.json(
        { error: 'View not found' },
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