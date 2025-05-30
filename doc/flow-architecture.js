// Mouse Tracking System Architecture Flowchart
// Use this with a mermaid renderer (like mermaid.live or GitHub markdown)

const flowchart = `
graph TD
    A[Client Browser] -->|Mouse Events| B[JavaScript Tracker]
    B -->|WebSocket| C[Data Collection Service]
    B -->|Batch API| C
    C -->|Stream| D[Apache Kafka]
    D -->|Real-time| E[Spark Streaming]
    D -->|Batch| F[Spark Processing]
    E -->|Process| G[MongoDB - Session Data]
    F -->|Store| H[HDFS - Data Warehouse]
    G -->|Index| I[Elasticsearch]
    H -->|Feed| J[Spark MLlib]
    I -->|Query| K[Analytics API]
    J -->|Models| K
    K -->|Visualize| L[Dashboard]
    L -->|D3.js| M[Heatmaps]
    L -->|D3.js| N[Path Analysis]
    L -->|Tableau| O[Business Reports]
    
    subgraph "Data Collection"
        A
        B
        C
    end
    
    subgraph "Data Processing"
        D
        E
        F
    end
    
    subgraph "Data Storage"
        G
        H
        I
    end
    
    subgraph "Analysis & Visualization"
        J
        K
        L
        M
        N
        O
    end
`;

// Export for use in documentation
module.exports = flowchart; 