import { NextRequest, NextResponse } from 'next/server';
import fs from 'fs/promises';
import path from 'path';

export async function GET(request: NextRequest) {
  try {
    // Read the stations locations data from the secure location
    const dataPath = path.join(process.cwd(), 'data', 'stations', 'stations_locations.json');
    const fileContent = await fs.readFile(dataPath, 'utf8');
    const locationsData = JSON.parse(fileContent);

    // You could add authentication/authorization here
    // For example: check API key, session, etc.
    
    return NextResponse.json(locationsData);
  } catch (error) {
    console.error('Error reading stations locations data:', error);
    return NextResponse.json(
      { error: 'Failed to load stations locations data' }, 
      { status: 500 }
    );
  }
}