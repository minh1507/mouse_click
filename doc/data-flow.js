// Mouse Tracking Data Flow Diagram
// Use this with a mermaid renderer

const dataFlowDiagram = `
sequenceDiagram
    participant User
    participant Browser
    participant Tracker
    participant API
    participant Kafka
    participant SparkStream
    participant SparkBatch
    participant MongoDB
    participant HDFS
    participant ML
    participant Dashboard

    User->>Browser: Interacts with website
    Browser->>Tracker: Mouse events (move, click, hover)
    Tracker->>Tracker: Buffer events (100ms)
    Tracker->>API: Send event batch
    API->>Kafka: Stream data
    
    par Real-time Processing
        Kafka->>SparkStream: Continuous data stream
        SparkStream->>SparkStream: Process & enrich data
        SparkStream->>MongoDB: Store session data
        MongoDB->>Dashboard: Real-time visualization
    and Batch Processing
        Kafka->>HDFS: Archive raw data
        HDFS->>SparkBatch: Scheduled batch jobs
        SparkBatch->>SparkBatch: Aggregate & analyze
        SparkBatch->>ML: Train behavior models
        ML->>MongoDB: Store model results
    end
    
    Dashboard->>User: Display insights
`;

// Export for use in documentation
module.exports = dataFlowDiagram; 