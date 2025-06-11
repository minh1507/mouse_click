import { NextRequest, NextResponse } from 'next/server';

// Helper to validate UUID format
function isValidUUID(uuid: string) {
  const uuidRegex = /^[0-9a-f]{8}-[0-9a-f]{4}-[1-5][0-9a-f]{3}-[89ab][0-9a-f]{3}-[0-9a-f]{12}$/i;
  return uuidRegex.test(uuid);
}

// Simplified API proxy endpoint for tracking events
export async function POST(request: NextRequest) {
  try {
    // Parse request body
    const rawBody = await request.text();
    console.log('Raw request body:', rawBody);
    
    let body;
    try {
      body = JSON.parse(rawBody);
    } catch (e) {
      console.error('Invalid JSON in request body:', e);
      return NextResponse.json(
        { error: 'Invalid JSON in request body' },
        { status: 400 }
      );
    }
    
    // Ensure we have a valid session_id in UUID format
    if (!body.session_id || !isValidUUID(body.session_id)) {
      // Generate a proper UUID if not provided or invalid
      body.session_id = crypto.randomUUID();
      console.log('Generated new session_id:', body.session_id);
    }
    
    // Add timestamp if not present
    if (!body.timestamp) {
      body.timestamp = new Date().toISOString();
    }
    
    console.log('Sending to simple-event endpoint:', body);
    
    // Send to simplified backend endpoint
    const response = await fetch('http://localhost:8000/api/tracking/simple-event/', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'Accept': 'application/json',
      },
      body: JSON.stringify(body),
    });
    
    // Handle response
    if (!response.ok) {
      console.error(`Backend returned error status: ${response.status}`);
      const text = await response.text();
      console.error('Response text:', text);
      return NextResponse.json(
        { error: `Backend error: ${response.status}`, details: text },
        { status: response.status }
      );
    }
    
    const data = await response.json();
    console.log('Backend response:', data);
    
    return NextResponse.json(data, { status: response.status });
  } catch (error) {
    console.error('Error processing tracking event:', error);
    return NextResponse.json(
      { error: 'Failed to process tracking event', details: error instanceof Error ? error.message : String(error) },
      { status: 500 }
    );
  }
} 