"""
AI-powered threat detection system for Incognito Technology
Real-time security threat analysis using machine learning
"""

import numpy as np
import pandas as pd
import tensorflow as tf
from tensorflow.keras import layers, models
from sklearn.preprocessing import StandardScaler
from sklearn.ensemble import IsolationForest
import joblib
import logging
from typing import Dict, List, Tuple, Optional
from datetime import datetime
import json

logger = logging.getLogger(__name__)


class ThreatDetectionModel:
    """AI model for detecting security threats in healthcare systems"""
    
    def __init__(self, model_path: Optional[str] = None):
        self.model = None
        self.scaler = StandardScaler()
        self.anomaly_detector = IsolationForest(contamination=0.1, random_state=42)
        self.feature_columns = [
            'login_attempts', 'session_duration', 'data_access_frequency',
            'unusual_hours', 'geographic_anomaly', 'device_change',
            'privilege_escalation', 'data_volume', 'network_anomaly'
        ]
        
        if model_path:
            self.load_model(model_path)
        else:
            self._build_model()
    
    def _build_model(self):
        """Build the neural network model for threat detection"""
        self.model = models.Sequential([
            layers.Dense(128, activation='relu', input_shape=(len(self.feature_columns),)),
            layers.Dropout(0.3),
            layers.Dense(64, activation='relu'),
            layers.Dropout(0.2),
            layers.Dense(32, activation='relu'),
            layers.Dense(16, activation='relu'),
            layers.Dense(1, activation='sigmoid')  # Binary classification
        ])
        
        self.model.compile(
            optimizer='adam',
            loss='binary_crossentropy',
            metrics=['accuracy', 'precision', 'recall']
        )
        
        logger.info("Threat detection model built successfully")
    
    def preprocess_data(self, data: pd.DataFrame) -> np.ndarray:
        """Preprocess input data for model prediction"""
        # Ensure all required features are present
        for col in self.feature_columns:
            if col not in data.columns:
                data[col] = 0
        
        # Select and order features
        features = data[self.feature_columns].copy()
        
        # Handle missing values
        features = features.fillna(0)
        
        # Scale features
        features_scaled = self.scaler.fit_transform(features)
        
        return features_scaled
    
    def train(self, training_data: pd.DataFrame, labels: np.ndarray, 
              validation_split: float = 0.2, epochs: int = 100):
        """Train the threat detection model"""
        logger.info("Starting model training...")
        
        # Preprocess training data
        X_train = self.preprocess_data(training_data)
        
        # Train the model
        history = self.model.fit(
            X_train, labels,
            validation_split=validation_split,
            epochs=epochs,
            batch_size=32,
            verbose=1,
            callbacks=[
                tf.keras.callbacks.EarlyStopping(patience=10, restore_best_weights=True),
                tf.keras.callbacks.ReduceLROnPlateau(patience=5, factor=0.5)
            ]
        )
        
        # Train anomaly detector
        self.anomaly_detector.fit(X_train)
        
        logger.info("Model training completed")
        return history
    
    def predict_threat(self, data: Dict) -> Dict:
        """Predict threat level for given input data"""
        try:
            # Convert input to DataFrame
            df = pd.DataFrame([data])
            
            # Preprocess data
            features = self.preprocess_data(df)
            
            # Get threat probability
            threat_probability = self.model.predict(features)[0][0]
            
            # Get anomaly score
            anomaly_score = self.anomaly_detector.decision_function(features)[0]
            is_anomaly = self.anomaly_detector.predict(features)[0] == -1
            
            # Determine threat level
            threat_level = self._calculate_threat_level(threat_probability, anomaly_score)
            
            result = {
                'threat_probability': float(threat_probability),
                'anomaly_score': float(anomaly_score),
                'is_anomaly': bool(is_anomaly),
                'threat_level': threat_level,
                'timestamp': datetime.utcnow().isoformat(),
                'confidence': self._calculate_confidence(threat_probability, anomaly_score)
            }
            
            logger.info(f"Threat prediction completed: {threat_level}")
            return result
            
        except Exception as e:
            logger.error(f"Error in threat prediction: {str(e)}")
            return {
                'error': str(e),
                'threat_level': 'unknown',
                'timestamp': datetime.utcnow().isoformat()
            }
    
    def _calculate_threat_level(self, probability: float, anomaly_score: float) -> str:
        """Calculate threat level based on probability and anomaly score"""
        if probability > 0.8 or anomaly_score < -0.5:
            return 'critical'
        elif probability > 0.6 or anomaly_score < -0.3:
            return 'high'
        elif probability > 0.4 or anomaly_score < -0.1:
            return 'medium'
        elif probability > 0.2:
            return 'low'
        else:
            return 'minimal'
    
    def _calculate_confidence(self, probability: float, anomaly_score: float) -> float:
        """Calculate confidence score for the prediction"""
        # Combine probability confidence and anomaly detection confidence
        prob_confidence = abs(probability - 0.5) * 2  # Distance from uncertain (0.5)
        anomaly_confidence = min(abs(anomaly_score), 1.0)  # Normalized anomaly score
        
        return float((prob_confidence + anomaly_confidence) / 2)
    
    def save_model(self, path: str):
        """Save the trained model and preprocessors"""
        try:
            # Save Keras model
            self.model.save(f"{path}/threat_model.h5")
            
            # Save preprocessors
            joblib.dump(self.scaler, f"{path}/scaler.pkl")
            joblib.dump(self.anomaly_detector, f"{path}/anomaly_detector.pkl")
            
            # Save metadata
            metadata = {
                'feature_columns': self.feature_columns,
                'model_version': '1.0.0',
                'saved_at': datetime.utcnow().isoformat()
            }
            
            with open(f"{path}/metadata.json", 'w') as f:
                json.dump(metadata, f, indent=2)
            
            logger.info(f"Model saved successfully to {path}")
            
        except Exception as e:
            logger.error(f"Error saving model: {str(e)}")
            raise
    
    def load_model(self, path: str):
        """Load a pre-trained model and preprocessors"""
        try:
            # Load Keras model
            self.model = tf.keras.models.load_model(f"{path}/threat_model.h5")
            
            # Load preprocessors
            self.scaler = joblib.load(f"{path}/scaler.pkl")
            self.anomaly_detector = joblib.load(f"{path}/anomaly_detector.pkl")
            
            # Load metadata
            with open(f"{path}/metadata.json", 'r') as f:
                metadata = json.load(f)
                self.feature_columns = metadata['feature_columns']
            
            logger.info(f"Model loaded successfully from {path}")
            
        except Exception as e:
            logger.error(f"Error loading model: {str(e)}")
            raise


class RealTimeThreatMonitor:
    """Real-time threat monitoring system"""
    
    def __init__(self, model: ThreatDetectionModel):
        self.model = model
        self.alert_thresholds = {
            'critical': 0.9,
            'high': 0.7,
            'medium': 0.5
        }
    
    def monitor_user_activity(self, user_id: str, activity_data: Dict) -> Dict:
        """Monitor user activity for potential threats"""
        # Extract features from activity data
        features = self._extract_features(activity_data)
        
        # Predict threat
        prediction = self.model.predict_threat(features)
        
        # Check if alert should be triggered
        should_alert = self._should_trigger_alert(prediction)
        
        if should_alert:
            self._trigger_alert(user_id, prediction, activity_data)
        
        return {
            'user_id': user_id,
            'prediction': prediction,
            'alert_triggered': should_alert,
            'timestamp': datetime.utcnow().isoformat()
        }
    
    def _extract_features(self, activity_data: Dict) -> Dict:
        """Extract relevant features from activity data"""
        return {
            'login_attempts': activity_data.get('failed_logins', 0),
            'session_duration': activity_data.get('session_minutes', 0),
            'data_access_frequency': activity_data.get('data_accesses', 0),
            'unusual_hours': 1 if activity_data.get('outside_hours', False) else 0,
            'geographic_anomaly': 1 if activity_data.get('location_change', False) else 0,
            'device_change': 1 if activity_data.get('new_device', False) else 0,
            'privilege_escalation': 1 if activity_data.get('elevated_access', False) else 0,
            'data_volume': activity_data.get('data_mb', 0),
            'network_anomaly': 1 if activity_data.get('suspicious_network', False) else 0
        }
    
    def _should_trigger_alert(self, prediction: Dict) -> bool:
        """Determine if an alert should be triggered"""
        threat_level = prediction.get('threat_level', 'minimal')
        confidence = prediction.get('confidence', 0)
        
        return (threat_level in ['critical', 'high'] and confidence > 0.7) or \
               (threat_level == 'medium' and confidence > 0.8)
    
    def _trigger_alert(self, user_id: str, prediction: Dict, activity_data: Dict):
        """Trigger security alert"""
        alert = {
            'alert_id': f"threat_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}_{user_id}",
            'user_id': user_id,
            'threat_level': prediction['threat_level'],
            'confidence': prediction['confidence'],
            'activity_summary': activity_data,
            'timestamp': datetime.utcnow().isoformat(),
            'status': 'active'
        }
        
        logger.warning(f"Security alert triggered: {alert}")
        
        # TODO: Send alert to security team
        # TODO: Store alert in database
        # TODO: Trigger automated response if needed
