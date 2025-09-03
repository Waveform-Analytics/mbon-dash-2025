import { NextResponse } from 'next/server';

export async function GET() {
  try {
    // Load real PCA data directly from CDN
    const CDN_BASE_URL = process.env.NEXT_PUBLIC_CDN_BASE_URL || 'https://waveformdata.work';
    const response = await fetch(`${CDN_BASE_URL}/views/pca_analysis.json`);
    
    if (!response.ok) {
      throw new Error(`Failed to fetch PCA data from CDN: ${response.status}`);
    }
    
    const pcaData = await response.json();
    
    return NextResponse.json(pcaData, {
      headers: {
        'Cache-Control': 'no-cache, no-store, must-revalidate',
        'Pragma': 'no-cache', 
        'Expires': '0'
      }
    });
  } catch (error) {
    console.error('Error loading PCA data:', error);
    
    return NextResponse.json(
      { error: 'Failed to load PCA analysis data' },
      { status: 500 }
    );
  }
}