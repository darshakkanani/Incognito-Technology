/*
Electronic Health Records Smart Contract for Incognito Technology
Hyperledger Fabric chaincode for secure EHR management with audit trails
*/

package main

import (
	"encoding/json"
	"fmt"
	"log"
	"time"

	"github.com/hyperledger/fabric-contract-api-go/contractapi"
)

// EHRContract provides functions for managing Electronic Health Records
type EHRContract struct {
	contractapi.Contract
}

// EHRRecord represents an electronic health record
type EHRRecord struct {
	ID          string    `json:"id"`
	PatientID   string    `json:"patientId"`
	DoctorID    string    `json:"doctorId"`
	RecordType  string    `json:"recordType"`
	Data        string    `json:"data"`        // Encrypted health data
	Hash        string    `json:"hash"`        // Data integrity hash
	Timestamp   time.Time `json:"timestamp"`
	Permissions []string  `json:"permissions"` // List of authorized user IDs
	Status      string    `json:"status"`      // active, archived, deleted
}

// AccessLog represents an access log entry
type AccessLog struct {
	ID        string    `json:"id"`
	RecordID  string    `json:"recordId"`
	UserID    string    `json:"userId"`
	Action    string    `json:"action"`    // read, write, share, delete
	Timestamp time.Time `json:"timestamp"`
	IPAddress string    `json:"ipAddress"`
	Success   bool      `json:"success"`
}

// CreateEHRRecord creates a new EHR record on the blockchain
func (c *EHRContract) CreateEHRRecord(ctx contractapi.TransactionContextInterface, id string, patientID string, doctorID string, recordType string, encryptedData string, dataHash string) error {
	// Check if record already exists
	existing, err := ctx.GetStub().GetState(id)
	if err != nil {
		return fmt.Errorf("failed to read from world state: %v", err)
	}
	if existing != nil {
		return fmt.Errorf("record %s already exists", id)
	}

	// Create new EHR record
	record := EHRRecord{
		ID:          id,
		PatientID:   patientID,
		DoctorID:    doctorID,
		RecordType:  recordType,
		Data:        encryptedData,
		Hash:        dataHash,
		Timestamp:   time.Now(),
		Permissions: []string{patientID, doctorID}, // Patient and doctor have access by default
		Status:      "active",
	}

	recordJSON, err := json.Marshal(record)
	if err != nil {
		return err
	}

	// Store record on blockchain
	err = ctx.GetStub().PutState(id, recordJSON)
	if err != nil {
		return fmt.Errorf("failed to put to world state: %v", err)
	}

	// Log the creation
	err = c.logAccess(ctx, id, doctorID, "create", "", true)
	if err != nil {
		return fmt.Errorf("failed to log access: %v", err)
	}

	return nil
}

// ReadEHRRecord reads an EHR record from the blockchain
func (c *EHRContract) ReadEHRRecord(ctx contractapi.TransactionContextInterface, id string, userID string, ipAddress string) (*EHRRecord, error) {
	recordJSON, err := ctx.GetStub().GetState(id)
	if err != nil {
		return nil, fmt.Errorf("failed to read from world state: %v", err)
	}
	if recordJSON == nil {
		// Log failed access attempt
		c.logAccess(ctx, id, userID, "read", ipAddress, false)
		return nil, fmt.Errorf("record %s does not exist", id)
	}

	var record EHRRecord
	err = json.Unmarshal(recordJSON, &record)
	if err != nil {
		return nil, err
	}

	// Check permissions
	if !c.hasPermission(userID, record.Permissions) {
		// Log unauthorized access attempt
		c.logAccess(ctx, id, userID, "read", ipAddress, false)
		return nil, fmt.Errorf("user %s does not have permission to read record %s", userID, id)
	}

	// Log successful access
	err = c.logAccess(ctx, id, userID, "read", ipAddress, true)
	if err != nil {
		return nil, fmt.Errorf("failed to log access: %v", err)
	}

	return &record, nil
}

// UpdateEHRRecord updates an existing EHR record
func (c *EHRContract) UpdateEHRRecord(ctx contractapi.TransactionContextInterface, id string, userID string, encryptedData string, dataHash string, ipAddress string) error {
	record, err := c.ReadEHRRecord(ctx, id, userID, ipAddress)
	if err != nil {
		return err
	}

	// Check if user has write permission (only doctor and patient can update)
	if userID != record.DoctorID && userID != record.PatientID {
		c.logAccess(ctx, id, userID, "write", ipAddress, false)
		return fmt.Errorf("user %s does not have permission to update record %s", userID, id)
	}

	// Update record
	record.Data = encryptedData
	record.Hash = dataHash
	record.Timestamp = time.Now()

	recordJSON, err := json.Marshal(record)
	if err != nil {
		return err
	}

	err = ctx.GetStub().PutState(id, recordJSON)
	if err != nil {
		return fmt.Errorf("failed to put to world state: %v", err)
	}

	// Log the update
	err = c.logAccess(ctx, id, userID, "write", ipAddress, true)
	if err != nil {
		return fmt.Errorf("failed to log access: %v", err)
	}

	return nil
}

// ShareEHRRecord grants access permission to another user
func (c *EHRContract) ShareEHRRecord(ctx contractapi.TransactionContextInterface, recordID string, ownerID string, targetUserID string, ipAddress string) error {
	record, err := c.ReadEHRRecord(ctx, recordID, ownerID, ipAddress)
	if err != nil {
		return err
	}

	// Only patient can share their records
	if ownerID != record.PatientID {
		c.logAccess(ctx, recordID, ownerID, "share", ipAddress, false)
		return fmt.Errorf("only the patient can share their records")
	}

	// Check if user already has permission
	if c.hasPermission(targetUserID, record.Permissions) {
		return fmt.Errorf("user %s already has access to record %s", targetUserID, recordID)
	}

	// Add permission
	record.Permissions = append(record.Permissions, targetUserID)

	recordJSON, err := json.Marshal(record)
	if err != nil {
		return err
	}

	err = ctx.GetStub().PutState(recordID, recordJSON)
	if err != nil {
		return fmt.Errorf("failed to put to world state: %v", err)
	}

	// Log the sharing
	err = c.logAccess(ctx, recordID, ownerID, "share", ipAddress, true)
	if err != nil {
		return fmt.Errorf("failed to log access: %v", err)
	}

	return nil
}

// RevokeAccess removes access permission from a user
func (c *EHRContract) RevokeAccess(ctx contractapi.TransactionContextInterface, recordID string, ownerID string, targetUserID string, ipAddress string) error {
	record, err := c.ReadEHRRecord(ctx, recordID, ownerID, ipAddress)
	if err != nil {
		return err
	}

	// Only patient can revoke access (except for doctor)
	if ownerID != record.PatientID {
		return fmt.Errorf("only the patient can revoke access to their records")
	}

	// Cannot revoke doctor's access
	if targetUserID == record.DoctorID {
		return fmt.Errorf("cannot revoke doctor's access to patient records")
	}

	// Remove permission
	newPermissions := []string{}
	for _, userID := range record.Permissions {
		if userID != targetUserID {
			newPermissions = append(newPermissions, userID)
		}
	}

	record.Permissions = newPermissions

	recordJSON, err := json.Marshal(record)
	if err != nil {
		return err
	}

	err = ctx.GetStub().PutState(recordID, recordJSON)
	if err != nil {
		return fmt.Errorf("failed to put to world state: %v", err)
	}

	// Log the revocation
	err = c.logAccess(ctx, recordID, ownerID, "revoke", ipAddress, true)
	if err != nil {
		return fmt.Errorf("failed to log access: %v", err)
	}

	return nil
}

// GetAccessLogs retrieves access logs for a specific record
func (c *EHRContract) GetAccessLogs(ctx contractapi.TransactionContextInterface, recordID string, userID string) ([]*AccessLog, error) {
	// Check if user has permission to view logs
	record, err := c.ReadEHRRecord(ctx, recordID, userID, "")
	if err != nil {
		return nil, err
	}

	// Only patient and doctor can view access logs
	if userID != record.PatientID && userID != record.DoctorID {
		return nil, fmt.Errorf("user %s does not have permission to view access logs", userID)
	}

	// Query access logs
	queryString := fmt.Sprintf(`{"selector":{"recordId":"%s"}}`, recordID)
	resultsIterator, err := ctx.GetStub().GetQueryResult(queryString)
	if err != nil {
		return nil, err
	}
	defer resultsIterator.Close()

	var logs []*AccessLog
	for resultsIterator.HasNext() {
		queryResponse, err := resultsIterator.Next()
		if err != nil {
			return nil, err
		}

		var log AccessLog
		err = json.Unmarshal(queryResponse.Value, &log)
		if err != nil {
			return nil, err
		}
		logs = append(logs, &log)
	}

	return logs, nil
}

// Helper function to check if user has permission
func (c *EHRContract) hasPermission(userID string, permissions []string) bool {
	for _, permittedUser := range permissions {
		if permittedUser == userID {
			return true
		}
	}
	return false
}

// Helper function to log access attempts
func (c *EHRContract) logAccess(ctx contractapi.TransactionContextInterface, recordID string, userID string, action string, ipAddress string, success bool) error {
	logID := fmt.Sprintf("log_%s_%s_%d", recordID, userID, time.Now().UnixNano())
	
	accessLog := AccessLog{
		ID:        logID,
		RecordID:  recordID,
		UserID:    userID,
		Action:    action,
		Timestamp: time.Now(),
		IPAddress: ipAddress,
		Success:   success,
	}

	logJSON, err := json.Marshal(accessLog)
	if err != nil {
		return err
	}

	return ctx.GetStub().PutState(logID, logJSON)
}

// GetAllRecordsForPatient retrieves all records for a specific patient
func (c *EHRContract) GetAllRecordsForPatient(ctx contractapi.TransactionContextInterface, patientID string, userID string) ([]*EHRRecord, error) {
	// Check if user has permission (patient themselves or their doctor)
	if userID != patientID {
		// TODO: Add logic to check if userID is one of patient's doctors
		return nil, fmt.Errorf("user %s does not have permission to view patient records", userID)
	}

	queryString := fmt.Sprintf(`{"selector":{"patientId":"%s","status":"active"}}`, patientID)
	resultsIterator, err := ctx.GetStub().GetQueryResult(queryString)
	if err != nil {
		return nil, err
	}
	defer resultsIterator.Close()

	var records []*EHRRecord
	for resultsIterator.HasNext() {
		queryResponse, err := resultsIterator.Next()
		if err != nil {
			return nil, err
		}

		var record EHRRecord
		err = json.Unmarshal(queryResponse.Value, &record)
		if err != nil {
			return nil, err
		}
		records = append(records, &record)
	}

	return records, nil
}

func main() {
	ehrContract := new(EHRContract)

	cc, err := contractapi.NewChaincode(ehrContract)
	if err != nil {
		log.Panicf("Error creating EHR chaincode: %v", err)
	}

	if err := cc.Start(); err != nil {
		log.Panicf("Error starting EHR chaincode: %v", err)
	}
}
