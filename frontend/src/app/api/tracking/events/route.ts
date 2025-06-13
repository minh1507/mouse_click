import { NextRequest, NextResponse } from 'next/server';

// Helper to validate UUID format
function isValidUUID(uuid: string) {
  const uuidRegex = /^[0-9a-f]{8}-[0-9a-f]{4}-[1-5][0-9a-f]{3}-[89ab][0-9a-f]{3}-[0-9a-f]{12}$/i;
  return uuidRegex.test(uuid);
}

// API proxy endpoint for tracking events
export async function POST(request: NextRequest) {
  try {
    // Log request body
    const rawBody = await request.text();

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

    // Đảm bảo dữ liệu hợp lệ
    const processedData = Array.isArray(body) 
      ? body.map(ensureValidData)
      : ensureValidData(body);
    
    // Chuyển tiếp request đến backend
    const response = await fetch('http://localhost:8000/api/tracking/events/', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'Accept': 'application/json',
      },
      body: JSON.stringify(processedData),
    });
    
    // Kiểm tra response status
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

    return NextResponse.json(data, { status: response.status });
  } catch (error) {
    console.error('Error forwarding tracking event:', error);
    return NextResponse.json(
      { error: 'Failed to process tracking event', details: error instanceof Error ? error.message : String(error) },
      { status: 500 }
    );
  }
}

// Ensure data has valid session_id and timestamp
function ensureValidData(data: any) {
  if (typeof data !== 'object' || data === null) {
    return {
      event_type: 'unknown',
      session_id: crypto.randomUUID(),
      timestamp: new Date().toISOString(),
      url: '',
      data: { original: data }
    };
  }
  
  // Create a copy to avoid modifying the original
  const result = { ...data };
  
  // Ensure valid session_id in UUID format
  if (!result.session_id || !isValidUUID(result.session_id)) {
    result.session_id = crypto.randomUUID();
  }
  
  // Add timestamp if not present
  if (!result.timestamp) {
    result.timestamp = new Date().toISOString();
  }
  
  // Ensure event_type exists
  if (!result.event_type) {
    result.event_type = 'custom';
  }
  
  return result;
} 