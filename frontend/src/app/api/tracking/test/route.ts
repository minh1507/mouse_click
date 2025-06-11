import { NextRequest, NextResponse } from 'next/server';

// Test API endpoint to verify backend connectivity
export async function GET(request: NextRequest) {
  try {
    console.log('Testing backend connection...');
    
    // Gọi endpoint test của backend
    const response = await fetch('http://localhost:8000/api/tracking/test/', {
      method: 'GET',
      headers: {
        'Accept': 'application/json',
      },
    });
    
    // Log raw response
    console.log(`Backend response status: ${response.status}`);
    
    // Kiểm tra response status
    if (!response.ok) {
      console.error(`Backend returned error status: ${response.status}`);
      const text = await response.text();
      console.error('Response text:', text);
      return NextResponse.json(
        { error: `Backend error: ${response.status}`, responseText: text },
        { status: response.status }
      );
    }
    
    const data = await response.json();
    console.log('Backend test response:', data);
    
    return NextResponse.json({
      backendStatus: data,
      message: "Connection test successful"
    });
  } catch (error) {
    console.error('Error testing backend connection:', error);
    return NextResponse.json(
      { error: `Connection test failed: ${error instanceof Error ? error.message : String(error)}` },
      { status: 500 }
    );
  }
} 