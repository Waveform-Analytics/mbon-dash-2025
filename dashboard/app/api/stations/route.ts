import { NextRequest, NextResponse } from 'next/server';
import fs from 'fs/promises';
import path from 'path';

export async function GET(request: NextRequest) {
  try {
    // Read the stations data from the secure location
    const dataPath = path.join(process.cwd(), 'data', 'stations', 'stations.json');
    const fileContent = await fs.readFile(dataPath, 'utf8');
    const stationsData = JSON.parse(fileContent);

    // You could add authentication/authorization here
    // For example: check API key, session, etc.
    
    return NextResponse.json(stationsData);
  } catch (error) {
    console.error('Error reading stations data:', error);
    return NextResponse.json(
      { error: 'Failed to load stations data' }, 
      { status: 500 }
    );
  }
}