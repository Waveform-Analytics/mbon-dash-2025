import { NextRequest, NextResponse } from 'next/server';
import fs from 'fs/promises';
import path from 'path';

export async function GET(
  request: NextRequest,
  { params }: { params: Promise<{ viewName: string }> }
) {
  try {
    const { viewName } = await params;
    
    // Sanitize the view name to prevent directory traversal
    const sanitizedViewName = viewName.replace(/[^a-zA-Z0-9_-]/g, '');
    if (sanitizedViewName !== viewName) {
      return NextResponse.json(
        { error: 'Invalid view name' },
        { status: 400 }
      );
    }
    
    // Construct path to the view file
    const fileName = `${sanitizedViewName}.json`;
    const dataPath = path.join(process.cwd(), '..', 'data', 'views', fileName);
    
    // Check if file exists
    try {
      await fs.access(dataPath);
    } catch {
      return NextResponse.json(
        { error: `View '${viewName}' not found` },
        { status: 404 }
      );
    }
    
    // Read and parse the JSON file
    const fileContent = await fs.readFile(dataPath, 'utf8');
    const viewData = JSON.parse(fileContent);
    
    console.log(`[API] Successfully served view: ${viewName} from local file`);
    
    return NextResponse.json(viewData, {
      headers: {
        'Cache-Control': 'public, max-age=300, s-maxage=300', // 5 minute cache
      },
    });
    
  } catch (error) {
    console.error(`[API] Error serving view:`, error);
    
    return NextResponse.json(
      { 
        error: 'Failed to load view data',
        details: error instanceof Error ? error.message : 'Unknown error'
      },
      { status: 500 }
    );
  }
}