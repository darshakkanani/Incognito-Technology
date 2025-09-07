// Incognito Technology MongoDB Initialization Script
// For unstructured data, logs, and real-time analytics

// Switch to the incognito_logs database
db = db.getSiblingDB('incognito_logs');

// Create collections with validation schemas

// System Logs Collection
db.createCollection("system_logs", {
  validator: {
    $jsonSchema: {
      bsonType: "object",
      required: ["timestamp", "level", "service", "message"],
      properties: {
        timestamp: {
          bsonType: "date",
          description: "Log timestamp - required"
        },
        level: {
          bsonType: "string",
          enum: ["DEBUG", "INFO", "WARN", "ERROR", "CRITICAL"],
          description: "Log level - required"
        },
        service: {
          bsonType: "string",
          description: "Service name that generated the log - required"
        },
        message: {
          bsonType: "string",
          description: "Log message - required"
        },
        metadata: {
          bsonType: "object",
          description: "Additional log metadata"
        },
        user_id: {
          bsonType: "string",
          description: "User ID if applicable"
        },
        session_id: {
          bsonType: "string",
          description: "Session ID if applicable"
        },
        ip_address: {
          bsonType: "string",
          description: "IP address if applicable"
        },
        trace_id: {
          bsonType: "string",
          description: "Distributed tracing ID"
        }
      }
    }
  }
});

// Security Events Collection
db.createCollection("security_events", {
  validator: {
    $jsonSchema: {
      bsonType: "object",
      required: ["timestamp", "event_type", "severity", "source"],
      properties: {
        timestamp: {
          bsonType: "date",
          description: "Event timestamp - required"
        },
        event_type: {
          bsonType: "string",
          enum: ["login_attempt", "failed_login", "suspicious_activity", "data_access", "permission_change", "threat_detected"],
          description: "Type of security event - required"
        },
        severity: {
          bsonType: "string",
          enum: ["low", "medium", "high", "critical"],
          description: "Event severity - required"
        },
        source: {
          bsonType: "string",
          description: "Source of the event - required"
        },
        user_id: {
          bsonType: "string",
          description: "User ID involved in the event"
        },
        ip_address: {
          bsonType: "string",
          description: "Source IP address"
        },
        user_agent: {
          bsonType: "string",
          description: "User agent string"
        },
        details: {
          bsonType: "object",
          description: "Additional event details"
        },
        response_actions: {
          bsonType: "array",
          description: "Actions taken in response to the event"
        },
        resolved: {
          bsonType: "bool",
          description: "Whether the event has been resolved"
        }
      }
    }
  }
});

// AI Model Performance Metrics
db.createCollection("ai_metrics", {
  validator: {
    $jsonSchema: {
      bsonType: "object",
      required: ["timestamp", "model_id", "metric_type", "value"],
      properties: {
        timestamp: {
          bsonType: "date",
          description: "Metric timestamp - required"
        },
        model_id: {
          bsonType: "string",
          description: "AI model identifier - required"
        },
        metric_type: {
          bsonType: "string",
          enum: ["accuracy", "precision", "recall", "f1_score", "inference_time", "throughput", "error_rate"],
          description: "Type of metric - required"
        },
        value: {
          bsonType: "number",
          description: "Metric value - required"
        },
        dataset: {
          bsonType: "string",
          description: "Dataset used for evaluation"
        },
        model_version: {
          bsonType: "string",
          description: "Model version"
        },
        environment: {
          bsonType: "string",
          enum: ["development", "staging", "production"],
          description: "Environment where metric was collected"
        }
      }
    }
  }
});

// Blockchain Transaction Logs
db.createCollection("blockchain_logs", {
  validator: {
    $jsonSchema: {
      bsonType: "object",
      required: ["timestamp", "transaction_hash", "operation", "status"],
      properties: {
        timestamp: {
          bsonType: "date",
          description: "Transaction timestamp - required"
        },
        transaction_hash: {
          bsonType: "string",
          description: "Blockchain transaction hash - required"
        },
        operation: {
          bsonType: "string",
          enum: ["identity_creation", "access_grant", "audit_log", "data_hash_storage"],
          description: "Type of blockchain operation - required"
        },
        status: {
          bsonType: "string",
          enum: ["pending", "confirmed", "failed"],
          description: "Transaction status - required"
        },
        block_number: {
          bsonType: "number",
          description: "Block number where transaction was included"
        },
        gas_used: {
          bsonType: "number",
          description: "Gas used for the transaction"
        },
        contract_address: {
          bsonType: "string",
          description: "Smart contract address"
        },
        function_called: {
          bsonType: "string",
          description: "Smart contract function called"
        },
        input_data: {
          bsonType: "object",
          description: "Transaction input data"
        },
        error_message: {
          bsonType: "string",
          description: "Error message if transaction failed"
        }
      }
    }
  }
});

// Medical Image Metadata
db.createCollection("medical_images", {
  validator: {
    $jsonSchema: {
      bsonType: "object",
      required: ["timestamp", "patient_id", "image_type", "file_path"],
      properties: {
        timestamp: {
          bsonType: "date",
          description: "Image creation timestamp - required"
        },
        patient_id: {
          bsonType: "string",
          description: "Patient identifier - required"
        },
        image_type: {
          bsonType: "string",
          enum: ["xray", "mri", "ct_scan", "ultrasound", "mammogram", "skin_photo"],
          description: "Type of medical image - required"
        },
        file_path: {
          bsonType: "string",
          description: "Encrypted file storage path - required"
        },
        dicom_metadata: {
          bsonType: "object",
          description: "DICOM metadata if applicable"
        },
        ai_analysis: {
          bsonType: "object",
          description: "AI analysis results"
        },
        annotations: {
          bsonType: "array",
          description: "Medical annotations and findings"
        },
        quality_score: {
          bsonType: "number",
          minimum: 0,
          maximum: 1,
          description: "Image quality score"
        },
        encryption_key_id: {
          bsonType: "string",
          description: "Reference to encryption key"
        }
      }
    }
  }
});

// Federated Learning Sessions
db.createCollection("federated_learning", {
  validator: {
    $jsonSchema: {
      bsonType: "object",
      required: ["timestamp", "session_id", "participant_id", "round_number"],
      properties: {
        timestamp: {
          bsonType: "date",
          description: "Session timestamp - required"
        },
        session_id: {
          bsonType: "string",
          description: "Federated learning session ID - required"
        },
        participant_id: {
          bsonType: "string",
          description: "Participant organization ID - required"
        },
        round_number: {
          bsonType: "number",
          description: "Training round number - required"
        },
        model_updates: {
          bsonType: "object",
          description: "Model weight updates (encrypted)"
        },
        local_metrics: {
          bsonType: "object",
          description: "Local training metrics"
        },
        data_samples_count: {
          bsonType: "number",
          description: "Number of local data samples used"
        },
        training_time: {
          bsonType: "number",
          description: "Training time in milliseconds"
        },
        privacy_budget: {
          bsonType: "number",
          description: "Differential privacy budget used"
        }
      }
    }
  }
});

// API Usage Analytics
db.createCollection("api_analytics", {
  validator: {
    $jsonSchema: {
      bsonType: "object",
      required: ["timestamp", "endpoint", "method", "status_code", "response_time"],
      properties: {
        timestamp: {
          bsonType: "date",
          description: "Request timestamp - required"
        },
        endpoint: {
          bsonType: "string",
          description: "API endpoint - required"
        },
        method: {
          bsonType: "string",
          enum: ["GET", "POST", "PUT", "DELETE", "PATCH"],
          description: "HTTP method - required"
        },
        status_code: {
          bsonType: "number",
          description: "HTTP status code - required"
        },
        response_time: {
          bsonType: "number",
          description: "Response time in milliseconds - required"
        },
        user_id: {
          bsonType: "string",
          description: "User ID making the request"
        },
        ip_address: {
          bsonType: "string",
          description: "Client IP address"
        },
        user_agent: {
          bsonType: "string",
          description: "User agent string"
        },
        request_size: {
          bsonType: "number",
          description: "Request size in bytes"
        },
        response_size: {
          bsonType: "number",
          description: "Response size in bytes"
        },
        error_message: {
          bsonType: "string",
          description: "Error message if request failed"
        }
      }
    }
  }
});

// Create indexes for performance
db.system_logs.createIndex({ "timestamp": -1 });
db.system_logs.createIndex({ "level": 1, "timestamp": -1 });
db.system_logs.createIndex({ "service": 1, "timestamp": -1 });
db.system_logs.createIndex({ "user_id": 1, "timestamp": -1 });

db.security_events.createIndex({ "timestamp": -1 });
db.security_events.createIndex({ "event_type": 1, "timestamp": -1 });
db.security_events.createIndex({ "severity": 1, "timestamp": -1 });
db.security_events.createIndex({ "user_id": 1, "timestamp": -1 });
db.security_events.createIndex({ "ip_address": 1, "timestamp": -1 });

db.ai_metrics.createIndex({ "timestamp": -1 });
db.ai_metrics.createIndex({ "model_id": 1, "timestamp": -1 });
db.ai_metrics.createIndex({ "metric_type": 1, "timestamp": -1 });

db.blockchain_logs.createIndex({ "timestamp": -1 });
db.blockchain_logs.createIndex({ "transaction_hash": 1 });
db.blockchain_logs.createIndex({ "operation": 1, "timestamp": -1 });
db.blockchain_logs.createIndex({ "status": 1, "timestamp": -1 });

db.medical_images.createIndex({ "timestamp": -1 });
db.medical_images.createIndex({ "patient_id": 1, "timestamp": -1 });
db.medical_images.createIndex({ "image_type": 1, "timestamp": -1 });

db.federated_learning.createIndex({ "timestamp": -1 });
db.federated_learning.createIndex({ "session_id": 1, "round_number": 1 });
db.federated_learning.createIndex({ "participant_id": 1, "timestamp": -1 });

db.api_analytics.createIndex({ "timestamp": -1 });
db.api_analytics.createIndex({ "endpoint": 1, "timestamp": -1 });
db.api_analytics.createIndex({ "status_code": 1, "timestamp": -1 });
db.api_analytics.createIndex({ "user_id": 1, "timestamp": -1 });

// Create TTL indexes for log rotation (30 days retention)
db.system_logs.createIndex({ "timestamp": 1 }, { expireAfterSeconds: 2592000 });
db.api_analytics.createIndex({ "timestamp": 1 }, { expireAfterSeconds: 2592000 });

// Create text indexes for search
db.system_logs.createIndex({ "message": "text", "metadata": "text" });
db.security_events.createIndex({ "details": "text" });

// Insert sample data for testing
db.system_logs.insertOne({
  timestamp: new Date(),
  level: "INFO",
  service: "incognito-api",
  message: "Database initialization completed successfully",
  metadata: {
    component: "database",
    action: "initialization"
  }
});

db.security_events.insertOne({
  timestamp: new Date(),
  event_type: "data_access",
  severity: "low",
  source: "system_initialization",
  details: {
    action: "database_setup",
    collections_created: 7
  },
  resolved: true
});

print("MongoDB initialization completed successfully!");
print("Created collections: system_logs, security_events, ai_metrics, blockchain_logs, medical_images, federated_learning, api_analytics");
print("Created indexes for performance optimization");
print("Set up TTL indexes for automatic log rotation");
