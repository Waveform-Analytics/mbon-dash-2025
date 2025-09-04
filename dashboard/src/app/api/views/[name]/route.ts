/**
 * API route to serve view JSON files
 */

import { NextRequest, NextResponse } from 'next/server';

const CDN_BASE_URL = process.env.NEXT_PUBLIC_CDN_BASE_URL || 'https://waveformdata.work';

export async function GET(
  request: NextRequest,
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
    
    // Try to fetch from CDN first
    try {
      const cdnUrl = `${CDN_BASE_URL}/views/${name}`;
      console.log(`API /api/views/${name}: Trying CDN: ${cdnUrl}`);
      
      const cdnResponse = await fetch(cdnUrl);
      if (cdnResponse.ok) {
        const data = await cdnResponse.json();
        console.log(`API /api/views/${name}: Successfully loaded from CDN`);
        return NextResponse.json(data);
      } else {
        console.log(`API /api/views/${name}: CDN returned ${cdnResponse.status}`);
      }
    } catch (cdnError) {
      console.log(`API /api/views/${name}: CDN error:`, cdnError);
    }
    
    // If CDN fails, return error (we're not using local files anymore)
    return NextResponse.json(
      { error: 'View not available - CDN access failed' },
      { status: 404 }
    );
    
  } catch (error) {
    console.error('Error in /api/views route:', error);
    return NextResponse.json(
      { error: 'Internal server error' },
      { status: 500 }
    );
  }
}