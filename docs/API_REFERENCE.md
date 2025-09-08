# API Reference

## Base URLs
- **Development**: `http://localhost:8000`
- **Staging**: `https://staging-api.incognito-tech.com`
- **Production**: `https://api.incognito-tech.com`

## Authentication

### JWT Token Authentication
```http
Authorization: Bearer <jwt_token>
```

### Login Endpoint
```http
POST /auth/login
Content-Type: application/json

{
  "email": "user@example.com",
  "password": "password123"
}
```

## User Management

### Get User Profile
```http
GET /users/profile
Authorization: Bearer <jwt_token>
```

### Update User Profile
```http
PUT /users/profile
Authorization: Bearer <jwt_token>
Content-Type: application/json

{
  "first_name": "John",
  "last_name": "Doe",
  "phone": "+1234567890"
}
```

## EHR Management

### Get Patient Records
```http
GET /ehr/patients/{patient_id}/records
Authorization: Bearer <jwt_token>
```

### Create Medical Record
```http
POST /ehr/records
Authorization: Bearer <jwt_token>
Content-Type: application/json

{
  "patient_id": "uuid",
  "record_type": "diagnosis",
  "title": "Annual Checkup",
  "description": "Routine examination",
  "diagnosis_codes": ["Z00.00"]
}
```

## AI/ML Services

### Medical Image Analysis
```http
POST /ai/analyze/image
Authorization: Bearer <jwt_token>
Content-Type: multipart/form-data

image: <file>
analysis_type: "brain_tumor_detection"
```

### Threat Detection
```http
POST /ai/threat-detection
Authorization: Bearer <jwt_token>
Content-Type: application/json

{
  "data": "network_logs",
  "timestamp": "2024-01-01T00:00:00Z"
}
```

## Blockchain Services

### Create Audit Entry
```http
POST /blockchain/audit
Authorization: Bearer <jwt_token>
Content-Type: application/json

{
  "action": "record_access",
  "resource_id": "uuid",
  "user_id": "uuid",
  "timestamp": "2024-01-01T00:00:00Z"
}
```

### Verify Data Integrity
```http
GET /blockchain/verify/{hash}
Authorization: Bearer <jwt_token>
```

## Error Responses

### Standard Error Format
```json
{
  "error": {
    "code": "VALIDATION_ERROR",
    "message": "Invalid input data",
    "details": {
      "field": "email",
      "issue": "Invalid email format"
    }
  }
}
```

### HTTP Status Codes
- `200` - Success
- `201` - Created
- `400` - Bad Request
- `401` - Unauthorized
- `403` - Forbidden
- `404` - Not Found
- `500` - Internal Server Error
