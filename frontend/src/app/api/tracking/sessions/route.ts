import { NextRequest, NextResponse } from 'next/server';

// Sử dụng URL tuyệt đối cho API
const API_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000/api';

// API proxy endpoint for tracking sessions
export async function POST(request: NextRequest) {
  try {
    // Parse request body
    const body = await request.json();
    console.log('Received request body:', body);

    // Validate and transform data
    let sessionData;
    if (Array.isArray(body)) {
      // If body is an array, take the first item
      sessionData = body[0];
      console.log('Converting array to single object:', sessionData);
    } else if (typeof body === 'object' && body !== null) {
      sessionData = body;
    } else {
      return NextResponse.json(
        { error: 'Invalid request format. Expected object or array' },
        { status: 400 }
      );
    }

    // Validate required fields
    if (!sessionData.session_id) {
      return NextResponse.json(
        { error: 'session_id is required' },
        { status: 400 }
      );
    }

    // Prepare data for backend
    const data = {
      session_id: sessionData.session_id,
      event_type: sessionData.event_type || 'session_start',
      data: sessionData.data || {}
    };

    console.log('Sending data to backend:', data);

    // Send request to backend
    const response = await fetch(`${API_URL}/tracking/events/`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'Accept': 'application/json',
      },
      body: JSON.stringify(data),
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
    console.error('Error processing session:', error);
    return NextResponse.json(
      { error: 'Failed to process session', details: error instanceof Error ? error.message : String(error) },
      { status: 500 }
    );
  }
}

export async function PATCH(request: NextRequest) {
  try {
    // Extract session ID from URL
    const url = new URL(request.url);
    const sessionId = url.pathname.split('/').pop();
    
    if (!sessionId) {
      return NextResponse.json(
        { error: 'Session ID is required' },
        { status: 400 }
      );
    }

    // Parse request body
    const body = await request.json();
    console.log('Received PATCH request body:', body);

    // Send request to backend
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

export async function GET(request: NextRequest) {
  try {
    const { searchParams } = new URL(request.url);
    const sessionId = searchParams.get('session_id');

    const url = sessionId
      ? `${API_URL}/tracking/sessions/${sessionId}/`
      : `${API_URL}/tracking/sessions/`;

    console.log('Fetching from URL:', url);

    const response = await fetch(url, {
      method: 'GET',
      headers: {
        'Content-Type': 'application/json',
        'Accept': 'application/json',
      },
    });

    console.log('Backend response status:', response.status);
    const responseText = await response.text();
    console.log('Backend response text:', responseText);

    if (!response.ok) {
      let errorMessage = 'Failed to fetch session';
      try {
        const errorData = JSON.parse(responseText);
        errorMessage = errorData.error || errorMessage;
      } catch (e) {
        console.error('Error parsing error response:', e);
      }
      throw new Error(errorMessage);
    }

    // Parse successful response
    let result;
    try {
      result = JSON.parse(responseText);
    } catch (e) {
      console.error('Error parsing success response:', e);
      result = { status: 'success' };
    }

    return NextResponse.json(result);
  } catch (error) {
    console.error('Error fetching session:', error);
    return NextResponse.json(
      { error: error instanceof Error ? error.message : 'Failed to fetch session' },
      { status: 500 }
    );
  }
} 