/**
 * API route for serving processed data files in development
 * This proxy allows the frontend to access local data files without CORS issues
 */

import { NextRequest, NextResponse } from 'next/server';
import { readFile } from 'fs/promises';
import { join } from 'path';

export async function GET(
  request: NextRequest,
  { params }: { params: { path: string[] } }
) {
  try {
    // Get the file path from the URL params
    const filePath = params.path.join('/');
    
    // Construct the full path to the data file
    const dataPath = join(process.cwd(), 'data', 'cdn', 'processed', filePath);
    
    // Read the file
    const fileContent = await readFile(dataPath, 'utf-8');
    
    // Parse as JSON to validate it's valid JSON
    const jsonData = JSON.parse(fileContent);
    
    // Return the JSON response with proper headers
    return NextResponse.json(jsonData, {
      headers: {
        'Cache-Control': 'public, max-age=300', // Cache for 5 minutes
        'Content-Type': 'application/json',
      },
    });
  } catch (error) {
    console.error('Error serving data file:', error);
    
    // Return appropriate error response
    if ((error as any).code === 'ENOENT') {
      return NextResponse.json(
        { error: 'File not found' },
        { status: 404 }
      );
    }
    
    return NextResponse.json(
      { error: 'Internal server error' },
      { status: 500 }
    );
  }
}