import { NextRequest, NextResponse } from 'next/server';

// API proxy endpoint for updating tracking sessions
export async function PUT(
  request: NextRequest,
  { params }: { params: { sessionId: string } }
) {
  try {
    const sessionId = params.sessionId;
    
    // Chuyển tiếp request đến backend
    const response = await fetch(`http://localhost:8000/api/tracking/sessions/${sessionId}/`, {
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