import { NextRequest, NextResponse } from 'next/server';

// API proxy endpoint for tracking sessions
export async function POST(request: NextRequest) {
  try {
    // Chuyển tiếp request đến backend
    const response = await fetch('http://localhost:8000/api/tracking/sessions/', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'User-Agent': request.headers.get('user-agent') || '',
        'Referer': request.headers.get('referer') || '',
      },
    });
    
    const data = await response.json();
    
    return NextResponse.json(data, { status: response.status });
  } catch (error) {
    console.error('Error creating tracking session:', error);
    return NextResponse.json(
      { error: 'Failed to create tracking session' },
      { status: 500 }
    );
  }
} 