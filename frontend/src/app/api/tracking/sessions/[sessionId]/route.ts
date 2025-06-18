import { NextRequest, NextResponse } from 'next/server';

// Sử dụng URL tuyệt đối cho API
const API_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000/api';

// API proxy endpoint for updating tracking sessions
export async function PUT(
  request: NextRequest,
  { params }: { params: { sessionId: string } }
) {
  try {
    const sessionId = params.sessionId;
    
    // Chuyển tiếp request đến backend
    const response = await fetch(`http://backend:8000/api/tracking/sessions/${sessionId}/`, {
      method: 'PUT',
      headers: {
        'Content-Type': 'application/json',
      },
    });
    
    const data = await response.json();
    
    return NextResponse.json(data, { status: response.status });
  } catch (error) {
    console.error('Error updating tracking session:', error);
    return NextResponse.json(
      { error: 'Failed to update tracking session' },
      { status: 500 }
    );
  }
}

export async function PATCH(
  request: NextRequest,
  { params }: { params: { sessionId: string } }
) {
  try {
    const sessionId = params.sessionId;
    
    // Parse request body
    const body = await request.json();
    console.log('Received PATCH request body:', body);

    // Send request to backend through nginx
    const response = await fetch(`${API_URL}/tracking/sessions/${sessionId}/`, {
      method: 'PATCH',
      headers: {
        'Content-Type': 'application/json',
        'Accept': 'application/json',
      },
      body: JSON.stringify(body),
    });

    // Log response for debugging
    console.log('Backend response status:', response.status);
    const responseText = await response.text();
    console.log('Backend response text:', responseText);

    // Parse response text as JSON
    let responseData;
    try {
      responseData = JSON.parse(responseText);
    } catch (e) {
      console.error('Error parsing response as JSON:', e);
      return NextResponse.json(
        { error: 'Invalid JSON response from backend' },
        { status: 500 }
      );
    }

    return NextResponse.json(responseData, { status: response.status });
  } catch (error) {
    console.error('Error updating session:', error);
    return NextResponse.json(
      { error: 'Failed to update session', details: error instanceof Error ? error.message : String(error) },
      { status: 500 }
    );
  }
} 