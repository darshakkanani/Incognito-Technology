-- Incognito Technology PostgreSQL Database Schema
-- HIPAA/GDPR Compliant Healthcare Database Design

-- Enable required extensions
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
CREATE EXTENSION IF NOT EXISTS "pgcrypto";
CREATE EXTENSION IF NOT EXISTS "pg_trgm";

-- Create schemas for different domains
CREATE SCHEMA IF NOT EXISTS users;
CREATE SCHEMA IF NOT EXISTS healthcare;
CREATE SCHEMA IF NOT EXISTS audit;
CREATE SCHEMA IF NOT EXISTS security;

-- Users and Authentication Schema
CREATE TABLE users.roles (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    name VARCHAR(50) UNIQUE NOT NULL,
    description TEXT,
    permissions JSONB NOT NULL DEFAULT '{}',
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

CREATE TABLE users.users (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    email VARCHAR(255) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    first_name VARCHAR(100) NOT NULL,
    last_name VARCHAR(100) NOT NULL,
    phone VARCHAR(20),
    role_id UUID REFERENCES users.roles(id),
    is_active BOOLEAN DEFAULT true,
    is_verified BOOLEAN DEFAULT false,
    last_login TIMESTAMP WITH TIME ZONE,
    failed_login_attempts INTEGER DEFAULT 0,
    locked_until TIMESTAMP WITH TIME ZONE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    deleted_at TIMESTAMP WITH TIME ZONE
);

CREATE TABLE users.user_sessions (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID REFERENCES users.users(id) ON DELETE CASCADE,
    token_hash VARCHAR(255) NOT NULL,
    expires_at TIMESTAMP WITH TIME ZONE NOT NULL,
    ip_address INET,
    user_agent TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Healthcare Schema
CREATE TABLE healthcare.organizations (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    name VARCHAR(255) NOT NULL,
    type VARCHAR(50) NOT NULL, -- hospital, clinic, lab, etc.
    license_number VARCHAR(100),
    address JSONB,
    contact_info JSONB,
    compliance_certifications JSONB,
    is_active BOOLEAN DEFAULT true,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

CREATE TABLE healthcare.doctors (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID REFERENCES users.users(id) ON DELETE CASCADE,
    organization_id UUID REFERENCES healthcare.organizations(id),
    license_number VARCHAR(100) UNIQUE NOT NULL,
    specialization VARCHAR(100),
    department VARCHAR(100),
    qualifications JSONB,
    is_verified BOOLEAN DEFAULT false,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

CREATE TABLE healthcare.patients (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID REFERENCES users.users(id) ON DELETE CASCADE,
    patient_id VARCHAR(50) UNIQUE NOT NULL, -- Hospital-specific ID
    date_of_birth DATE NOT NULL,
    gender VARCHAR(20),
    blood_type VARCHAR(5),
    emergency_contact JSONB,
    insurance_info JSONB,
    blockchain_identity_hash VARCHAR(66), -- Ethereum address
    consent_blockchain_storage BOOLEAN DEFAULT false,
    consent_ai_analysis BOOLEAN DEFAULT false,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

CREATE TABLE healthcare.medical_records (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    patient_id UUID REFERENCES healthcare.patients(id) ON DELETE CASCADE,
    doctor_id UUID REFERENCES healthcare.doctors(id),
    organization_id UUID REFERENCES healthcare.organizations(id),
    record_type VARCHAR(50) NOT NULL, -- diagnosis, prescription, lab_result, imaging
    title VARCHAR(255) NOT NULL,
    description TEXT,
    diagnosis_codes JSONB, -- ICD-10 codes
    medications JSONB,
    lab_results JSONB,
    imaging_data JSONB,
    ai_analysis_results JSONB,
    blockchain_hash VARCHAR(66), -- Hash stored on blockchain
    encryption_key_id VARCHAR(100), -- Reference to encryption key
    is_sensitive BOOLEAN DEFAULT false,
    access_level INTEGER DEFAULT 1, -- 1=normal, 2=restricted, 3=highly_restricted
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

CREATE TABLE healthcare.appointments (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    patient_id UUID REFERENCES healthcare.patients(id) ON DELETE CASCADE,
    doctor_id UUID REFERENCES healthcare.doctors(id),
    organization_id UUID REFERENCES healthcare.organizations(id),
    appointment_date TIMESTAMP WITH TIME ZONE NOT NULL,
    duration_minutes INTEGER DEFAULT 30,
    status VARCHAR(20) DEFAULT 'scheduled', -- scheduled, completed, cancelled, no_show
    reason TEXT,
    notes TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- AI/ML Schema
CREATE TABLE healthcare.ai_models (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    name VARCHAR(100) NOT NULL,
    version VARCHAR(20) NOT NULL,
    model_type VARCHAR(50) NOT NULL, -- threat_detection, diagnosis, federated_learning
    description TEXT,
    accuracy_metrics JSONB,
    training_data_hash VARCHAR(66),
    model_file_path VARCHAR(500),
    is_active BOOLEAN DEFAULT true,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

CREATE TABLE healthcare.ai_predictions (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    model_id UUID REFERENCES healthcare.ai_models(id),
    patient_id UUID REFERENCES healthcare.patients(id),
    medical_record_id UUID REFERENCES healthcare.medical_records(id),
    input_data_hash VARCHAR(66),
    prediction_results JSONB NOT NULL,
    confidence_score DECIMAL(5,4),
    processing_time_ms INTEGER,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Security and Audit Schema
CREATE TABLE audit.access_logs (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID REFERENCES users.users(id),
    resource_type VARCHAR(50) NOT NULL,
    resource_id UUID,
    action VARCHAR(50) NOT NULL, -- create, read, update, delete, login, logout
    ip_address INET,
    user_agent TEXT,
    success BOOLEAN NOT NULL,
    error_message TEXT,
    additional_data JSONB,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

CREATE TABLE audit.data_changes (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    table_name VARCHAR(100) NOT NULL,
    record_id UUID NOT NULL,
    user_id UUID REFERENCES users.users(id),
    operation VARCHAR(10) NOT NULL, -- INSERT, UPDATE, DELETE
    old_values JSONB,
    new_values JSONB,
    blockchain_hash VARCHAR(66), -- Hash of change stored on blockchain
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

CREATE TABLE security.threat_detections (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    detection_type VARCHAR(50) NOT NULL, -- anomaly, intrusion, data_breach
    severity VARCHAR(20) NOT NULL, -- low, medium, high, critical
    source_ip INET,
    target_resource VARCHAR(100),
    description TEXT,
    ai_model_used VARCHAR(100),
    confidence_score DECIMAL(5,4),
    is_false_positive BOOLEAN,
    response_actions JSONB,
    resolved_at TIMESTAMP WITH TIME ZONE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Blockchain Integration Tables
CREATE TABLE audit.blockchain_transactions (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    transaction_hash VARCHAR(66) UNIQUE NOT NULL,
    block_number BIGINT,
    contract_address VARCHAR(42),
    function_name VARCHAR(100),
    data_hash VARCHAR(66),
    gas_used BIGINT,
    transaction_fee DECIMAL(20,8),
    status VARCHAR(20) DEFAULT 'pending', -- pending, confirmed, failed
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    confirmed_at TIMESTAMP WITH TIME ZONE
);

-- Indexes for performance
CREATE INDEX idx_users_email ON users.users(email);
CREATE INDEX idx_users_role ON users.users(role_id);
CREATE INDEX idx_patients_patient_id ON healthcare.patients(patient_id);
CREATE INDEX idx_medical_records_patient ON healthcare.medical_records(patient_id);
CREATE INDEX idx_medical_records_doctor ON healthcare.medical_records(doctor_id);
CREATE INDEX idx_medical_records_created ON healthcare.medical_records(created_at);
CREATE INDEX idx_access_logs_user ON audit.access_logs(user_id);
CREATE INDEX idx_access_logs_created ON audit.access_logs(created_at);
CREATE INDEX idx_threat_detections_severity ON security.threat_detections(severity);
CREATE INDEX idx_blockchain_tx_hash ON audit.blockchain_transactions(transaction_hash);

-- Full-text search indexes
CREATE INDEX idx_medical_records_search ON healthcare.medical_records USING gin(to_tsvector('english', title || ' ' || description));

-- Insert default roles
INSERT INTO users.roles (name, description, permissions) VALUES
('super_admin', 'System Administrator', '{"all": true}'),
('hospital_admin', 'Hospital Administrator', '{"manage_organization": true, "view_all_patients": true, "manage_doctors": true}'),
('doctor', 'Medical Doctor', '{"view_patients": true, "create_records": true, "update_records": true, "ai_analysis": true}'),
('nurse', 'Registered Nurse', '{"view_patients": true, "create_basic_records": true, "update_basic_records": true}'),
('patient', 'Patient', '{"view_own_records": true, "manage_consent": true}'),
('researcher', 'Medical Researcher', '{"view_anonymized_data": true, "run_ai_models": true}'),
('auditor', 'Compliance Auditor', '{"view_audit_logs": true, "generate_reports": true}');

-- Create triggers for audit logging
CREATE OR REPLACE FUNCTION audit.log_data_changes()
RETURNS TRIGGER AS $$
BEGIN
    IF TG_OP = 'DELETE' THEN
        INSERT INTO audit.data_changes (table_name, record_id, operation, old_values)
        VALUES (TG_TABLE_NAME, OLD.id, TG_OP, row_to_json(OLD));
        RETURN OLD;
    ELSIF TG_OP = 'UPDATE' THEN
        INSERT INTO audit.data_changes (table_name, record_id, operation, old_values, new_values)
        VALUES (TG_TABLE_NAME, NEW.id, TG_OP, row_to_json(OLD), row_to_json(NEW));
        RETURN NEW;
    ELSIF TG_OP = 'INSERT' THEN
        INSERT INTO audit.data_changes (table_name, record_id, operation, new_values)
        VALUES (TG_TABLE_NAME, NEW.id, TG_OP, row_to_json(NEW));
        RETURN NEW;
    END IF;
    RETURN NULL;
END;
$$ LANGUAGE plpgsql;

-- Apply audit triggers to sensitive tables
CREATE TRIGGER audit_users_changes AFTER INSERT OR UPDATE OR DELETE ON users.users
    FOR EACH ROW EXECUTE FUNCTION audit.log_data_changes();

CREATE TRIGGER audit_medical_records_changes AFTER INSERT OR UPDATE OR DELETE ON healthcare.medical_records
    FOR EACH ROW EXECUTE FUNCTION audit.log_data_changes();

CREATE TRIGGER audit_patients_changes AFTER INSERT OR UPDATE OR DELETE ON healthcare.patients
    FOR EACH ROW EXECUTE FUNCTION audit.log_data_changes();

-- Row Level Security (RLS) for HIPAA compliance
ALTER TABLE healthcare.medical_records ENABLE ROW LEVEL SECURITY;
ALTER TABLE healthcare.patients ENABLE ROW LEVEL SECURITY;

-- RLS Policies (examples - to be expanded based on specific requirements)
CREATE POLICY patient_own_records ON healthcare.medical_records
    FOR ALL TO patient_role
    USING (patient_id IN (
        SELECT id FROM healthcare.patients WHERE user_id = current_user_id()
    ));

-- Function to get current user ID (to be implemented in application layer)
CREATE OR REPLACE FUNCTION current_user_id()
RETURNS UUID AS $$
BEGIN
    -- This should be set by the application layer
    RETURN current_setting('app.current_user_id', true)::UUID;
END;
$$ LANGUAGE plpgsql;
