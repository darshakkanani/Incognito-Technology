"""
Federated AI System for Electronic Health Records
Secure, privacy-preserving AI analysis across multiple healthcare institutions
"""

import numpy as np
import pandas as pd
import tensorflow as tf
from tensorflow.keras import layers, models
import tensorflow_federated as tff
from cryptography.fernet import Fernet
import hashlib
import json
import logging
from typing import Dict, List, Tuple, Optional, Any
from datetime import datetime
import asyncio
from dataclasses import dataclass

logger = logging.getLogger(__name__)


@dataclass
class FederatedClient:
    """Represents a healthcare institution in the federated network"""
    client_id: str
    institution_name: str
    public_key: str
    data_hash: str
    last_update: datetime
    model_version: str


class SecureEHRProcessor:
    """Secure processing of EHR data with encryption and anonymization"""
    
    def __init__(self, encryption_key: str):
        self.cipher = Fernet(encryption_key.encode())
        self.anonymization_map = {}
    
    def anonymize_patient_data(self, ehr_data: Dict) -> Dict:
        """Anonymize patient identifiable information"""
        anonymized = ehr_data.copy()
        
        # Generate anonymous patient ID
        patient_id = ehr_data.get('patient_id', '')
        if patient_id not in self.anonymization_map:
            self.anonymization_map[patient_id] = hashlib.sha256(
                f"{patient_id}_{datetime.now().isoformat()}".encode()
            ).hexdigest()[:16]
        
        anonymized['anonymous_id'] = self.anonymization_map[patient_id]
        
        # Remove direct identifiers
        sensitive_fields = ['patient_id', 'name', 'ssn', 'phone', 'email', 'address']
        for field in sensitive_fields:
            anonymized.pop(field, None)
        
        # Generalize quasi-identifiers
        if 'age' in anonymized:
            age = anonymized['age']
            anonymized['age_group'] = self._get_age_group(age)
            del anonymized['age']
        
        if 'zip_code' in anonymized:
            zip_code = anonymized['zip_code']
            anonymized['region'] = zip_code[:3] + "XX"  # Generalize to region
            del anonymized['zip_code']
        
        return anonymized
    
    def _get_age_group(self, age: int) -> str:
        """Convert age to age group for privacy"""
        if age < 18:
            return "0-17"
        elif age < 30:
            return "18-29"
        elif age < 50:
            return "30-49"
        elif age < 70:
            return "50-69"
        else:
            return "70+"
    
    def encrypt_sensitive_data(self, data: str) -> str:
        """Encrypt sensitive medical data"""
        return self.cipher.encrypt(data.encode()).decode()
    
    def decrypt_sensitive_data(self, encrypted_data: str) -> str:
        """Decrypt sensitive medical data"""
        return self.cipher.decrypt(encrypted_data.encode()).decode()


class FederatedEHRModel:
    """Federated learning model for EHR analysis"""
    
    def __init__(self, model_config: Dict):
        self.model_config = model_config
        self.global_model = None
        self.clients = {}
        self.current_round = 0
        self.performance_history = []
        
        self._build_model()
    
    def _build_model(self):
        """Build the neural network for EHR analysis"""
        
        # Input layers for different EHR data types
        demographic_input = layers.Input(shape=(10,), name='demographics')
        vitals_input = layers.Input(shape=(20,), name='vitals')
        lab_input = layers.Input(shape=(50,), name='lab_results')
        medication_input = layers.Input(shape=(100,), name='medications')
        
        # Process each input type
        demo_processed = layers.Dense(32, activation='relu')(demographic_input)
        vitals_processed = layers.Dense(64, activation='relu')(vitals_input)
        lab_processed = layers.Dense(128, activation='relu')(lab_input)
        med_processed = layers.Dense(64, activation='relu')(medication_input)
        
        # Combine all features
        combined = layers.Concatenate()([
            demo_processed, vitals_processed, lab_processed, med_processed
        ])
        
        # Main processing layers
        x = layers.Dense(256, activation='relu')(combined)
        x = layers.Dropout(0.3)(x)
        x = layers.Dense(128, activation='relu')(x)
        x = layers.Dropout(0.2)(x)
        x = layers.Dense(64, activation='relu')(x)
        
        # Multiple output heads for different predictions
        risk_prediction = layers.Dense(1, activation='sigmoid', name='risk_score')(x)
        diagnosis_prediction = layers.Dense(20, activation='softmax', name='diagnosis')(x)
        readmission_prediction = layers.Dense(1, activation='sigmoid', name='readmission')(x)
        
        self.global_model = models.Model(
            inputs=[demographic_input, vitals_input, lab_input, medication_input],
            outputs=[risk_prediction, diagnosis_prediction, readmission_prediction]
        )
        
        self.global_model.compile(
            optimizer='adam',
            loss={
                'risk_score': 'binary_crossentropy',
                'diagnosis': 'categorical_crossentropy',
                'readmission': 'binary_crossentropy'
            },
            metrics={
                'risk_score': ['accuracy', 'auc'],
                'diagnosis': ['accuracy', 'top_k_categorical_accuracy'],
                'readmission': ['accuracy', 'precision', 'recall']
            }
        )
        
        logger.info("Federated EHR model built successfully")
    
    def register_client(self, client: FederatedClient):
        """Register a new healthcare institution as a federated client"""
        self.clients[client.client_id] = client
        logger.info(f"Registered client: {client.institution_name}")
    
    def federated_training_round(self, client_updates: Dict[str, Any]) -> Dict:
        """Perform one round of federated learning"""
        logger.info(f"Starting federated training round {self.current_round + 1}")
        
        # Collect model updates from clients
        client_weights = []
        client_sizes = []
        
        for client_id, update in client_updates.items():
            if client_id in self.clients:
                client_weights.append(update['model_weights'])
                client_sizes.append(update['data_size'])
        
        if not client_weights:
            logger.warning("No client updates received")
            return {"status": "failed", "reason": "no_updates"}
        
        # Perform federated averaging
        global_weights = self._federated_averaging(client_weights, client_sizes)
        
        # Update global model
        self.global_model.set_weights(global_weights)
        
        # Evaluate global model performance
        performance = self._evaluate_global_model(client_updates)
        self.performance_history.append(performance)
        
        self.current_round += 1
        
        return {
            "status": "success",
            "round": self.current_round,
            "performance": performance,
            "global_model_weights": global_weights
        }
    
    def _federated_averaging(self, client_weights: List, client_sizes: List) -> List:
        """Perform federated averaging of client model weights"""
        total_size = sum(client_sizes)
        
        # Initialize averaged weights
        avg_weights = []
        
        for layer_idx in range(len(client_weights[0])):
            # Weight each client's contribution by their data size
            layer_avg = np.zeros_like(client_weights[0][layer_idx])
            
            for client_idx, weights in enumerate(client_weights):
                weight = client_sizes[client_idx] / total_size
                layer_avg += weight * weights[layer_idx]
            
            avg_weights.append(layer_avg)
        
        return avg_weights
    
    def _evaluate_global_model(self, client_updates: Dict) -> Dict:
        """Evaluate global model performance"""
        # Aggregate performance metrics from clients
        total_accuracy = 0
        total_loss = 0
        total_samples = 0
        
        for client_id, update in client_updates.items():
            if 'performance' in update:
                perf = update['performance']
                samples = update['data_size']
                
                total_accuracy += perf.get('accuracy', 0) * samples
                total_loss += perf.get('loss', 0) * samples
                total_samples += samples
        
        if total_samples > 0:
            avg_accuracy = total_accuracy / total_samples
            avg_loss = total_loss / total_samples
        else:
            avg_accuracy = 0
            avg_loss = float('inf')
        
        return {
            "accuracy": avg_accuracy,
            "loss": avg_loss,
            "participating_clients": len(client_updates),
            "total_samples": total_samples,
            "timestamp": datetime.utcnow().isoformat()
        }
    
    def predict_patient_risk(self, ehr_data: Dict) -> Dict:
        """Predict patient risk using the global federated model"""
        try:
            # Preprocess EHR data
            processed_data = self._preprocess_ehr_data(ehr_data)
            
            # Make predictions
            predictions = self.global_model.predict(processed_data)
            
            risk_score = float(predictions[0][0])
            diagnosis_probs = predictions[1][0].tolist()
            readmission_risk = float(predictions[2][0])
            
            # Get top 3 diagnosis predictions
            diagnosis_classes = [
                'Diabetes', 'Hypertension', 'Heart Disease', 'Stroke', 'Cancer',
                'Pneumonia', 'COPD', 'Kidney Disease', 'Liver Disease', 'Depression',
                'Anxiety', 'Arthritis', 'Osteoporosis', 'Asthma', 'Obesity',
                'Anemia', 'Thyroid Disorder', 'Migraine', 'Epilepsy', 'Other'
            ]
            
            top_diagnoses = sorted(
                zip(diagnosis_classes, diagnosis_probs),
                key=lambda x: x[1],
                reverse=True
            )[:3]
            
            return {
                "patient_id": ehr_data.get("anonymous_id", "unknown"),
                "risk_score": risk_score,
                "risk_level": self._get_risk_level(risk_score),
                "top_diagnoses": [
                    {"condition": diag, "probability": prob}
                    for diag, prob in top_diagnoses
                ],
                "readmission_risk": readmission_risk,
                "recommendations": self._generate_recommendations(risk_score, top_diagnoses),
                "model_version": f"federated_v{self.current_round}",
                "timestamp": datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Error in patient risk prediction: {str(e)}")
            return {
                "error": str(e),
                "patient_id": ehr_data.get("anonymous_id", "unknown"),
                "timestamp": datetime.utcnow().isoformat()
            }
    
    def _preprocess_ehr_data(self, ehr_data: Dict) -> List[np.ndarray]:
        """Preprocess EHR data for model input"""
        # Extract and normalize different data types
        demographics = self._extract_demographics(ehr_data)
        vitals = self._extract_vitals(ehr_data)
        lab_results = self._extract_lab_results(ehr_data)
        medications = self._extract_medications(ehr_data)
        
        return [
            np.array([demographics]),
            np.array([vitals]),
            np.array([lab_results]),
            np.array([medications])
        ]
    
    def _extract_demographics(self, ehr_data: Dict) -> List[float]:
        """Extract demographic features"""
        # Age group encoding
        age_groups = {"0-17": 0, "18-29": 1, "30-49": 2, "50-69": 3, "70+": 4}
        age_encoded = age_groups.get(ehr_data.get("age_group", "30-49"), 2)
        
        # Gender encoding
        gender_encoded = 1 if ehr_data.get("gender", "").lower() == "female" else 0
        
        # Other demographic features
        features = [
            age_encoded / 4.0,  # Normalized age group
            gender_encoded,
            ehr_data.get("bmi", 25.0) / 50.0,  # Normalized BMI
            1 if ehr_data.get("smoking", False) else 0,
            1 if ehr_data.get("alcohol", False) else 0,
            ehr_data.get("exercise_hours", 0) / 10.0,  # Normalized exercise
            0, 0, 0, 0  # Padding for additional features
        ]
        
        return features[:10]
    
    def _extract_vitals(self, ehr_data: Dict) -> List[float]:
        """Extract vital signs features"""
        vitals = ehr_data.get("vitals", {})
        
        features = [
            vitals.get("systolic_bp", 120) / 200.0,
            vitals.get("diastolic_bp", 80) / 120.0,
            vitals.get("heart_rate", 70) / 150.0,
            vitals.get("temperature", 98.6) / 110.0,
            vitals.get("respiratory_rate", 16) / 30.0,
            vitals.get("oxygen_saturation", 98) / 100.0,
            vitals.get("weight", 70) / 200.0,
            vitals.get("height", 170) / 220.0,
        ]
        
        # Pad to 20 features
        features.extend([0] * (20 - len(features)))
        return features[:20]
    
    def _extract_lab_results(self, ehr_data: Dict) -> List[float]:
        """Extract laboratory results features"""
        labs = ehr_data.get("lab_results", {})
        
        # Common lab values with normalization
        features = [
            labs.get("glucose", 100) / 300.0,
            labs.get("cholesterol", 200) / 400.0,
            labs.get("hdl", 50) / 100.0,
            labs.get("ldl", 100) / 200.0,
            labs.get("triglycerides", 150) / 500.0,
            labs.get("hemoglobin", 14) / 20.0,
            labs.get("hematocrit", 42) / 60.0,
            labs.get("white_blood_cells", 7000) / 15000.0,
            labs.get("platelets", 250000) / 500000.0,
            labs.get("creatinine", 1.0) / 5.0,
        ]
        
        # Pad to 50 features
        features.extend([0] * (50 - len(features)))
        return features[:50]
    
    def _extract_medications(self, ehr_data: Dict) -> List[float]:
        """Extract medication features"""
        medications = ehr_data.get("medications", [])
        
        # Common medication categories (binary encoding)
        med_categories = [
            "antihypertensive", "diabetes", "cholesterol", "anticoagulant",
            "antidepressant", "pain_relief", "antibiotic", "steroid",
            "thyroid", "heart", "respiratory", "gastrointestinal"
        ]
        
        features = []
        for category in med_categories:
            has_med = any(category in med.lower() for med in medications)
            features.append(1 if has_med else 0)
        
        # Pad to 100 features
        features.extend([0] * (100 - len(features)))
        return features[:100]
    
    def _get_risk_level(self, risk_score: float) -> str:
        """Convert risk score to risk level"""
        if risk_score >= 0.8:
            return "Critical"
        elif risk_score >= 0.6:
            return "High"
        elif risk_score >= 0.4:
            return "Moderate"
        elif risk_score >= 0.2:
            return "Low"
        else:
            return "Minimal"
    
    def _generate_recommendations(self, risk_score: float, top_diagnoses: List) -> List[str]:
        """Generate clinical recommendations based on predictions"""
        recommendations = []
        
        if risk_score >= 0.7:
            recommendations.append("Immediate medical attention recommended")
            recommendations.append("Consider hospitalization or intensive monitoring")
        elif risk_score >= 0.5:
            recommendations.append("Schedule follow-up within 1-2 weeks")
            recommendations.append("Monitor vital signs closely")
        
        # Diagnosis-specific recommendations
        for diagnosis, prob in top_diagnoses:
            if prob > 0.3:
                if "diabetes" in diagnosis.lower():
                    recommendations.append("Monitor blood glucose levels")
                    recommendations.append("Consider diabetes management consultation")
                elif "heart" in diagnosis.lower():
                    recommendations.append("Cardiology consultation recommended")
                    recommendations.append("Monitor cardiac markers")
                elif "hypertension" in diagnosis.lower():
                    recommendations.append("Blood pressure monitoring required")
                    recommendations.append("Lifestyle modifications advised")
        
        return list(set(recommendations))  # Remove duplicates


class FederatedEHROrchestrator:
    """Orchestrates federated learning across multiple healthcare institutions"""
    
    def __init__(self):
        self.model = None
        self.processor = None
        self.active_clients = {}
        self.training_schedule = {}
    
    async def initialize_federation(self, config: Dict):
        """Initialize the federated learning system"""
        self.processor = SecureEHRProcessor(config['encryption_key'])
        self.model = FederatedEHRModel(config['model_config'])
        
        logger.info("Federated EHR system initialized")
    
    async def coordinate_training_round(self) -> Dict:
        """Coordinate a federated training round across all clients"""
        logger.info("Coordinating federated training round")
        
        # Collect updates from all active clients
        client_updates = {}
        
        for client_id, client in self.active_clients.items():
            try:
                # In a real implementation, this would make API calls to client institutions
                update = await self._get_client_update(client_id)
                if update:
                    client_updates[client_id] = update
            except Exception as e:
                logger.error(f"Failed to get update from client {client_id}: {str(e)}")
        
        # Perform federated training round
        result = self.model.federated_training_round(client_updates)
        
        # Distribute updated global model to clients
        if result['status'] == 'success':
            await self._distribute_global_model(result['global_model_weights'])
        
        return result
    
    async def _get_client_update(self, client_id: str) -> Optional[Dict]:
        """Get model update from a specific client (mock implementation)"""
        # This would be replaced with actual API calls to client institutions
        return {
            "model_weights": self.model.global_model.get_weights(),
            "data_size": np.random.randint(100, 1000),
            "performance": {
                "accuracy": np.random.uniform(0.7, 0.9),
                "loss": np.random.uniform(0.1, 0.5)
            }
        }
    
    async def _distribute_global_model(self, global_weights: List):
        """Distribute updated global model to all clients"""
        for client_id in self.active_clients:
            try:
                # In a real implementation, this would send the model to client institutions
                logger.info(f"Distributed global model to client {client_id}")
            except Exception as e:
                logger.error(f"Failed to distribute model to client {client_id}: {str(e)}")
