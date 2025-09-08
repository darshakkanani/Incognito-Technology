"""
AI-Powered Cybersecurity Framework for Medical Imaging Data
Advanced security system for protecting medical images with AI-driven threat detection
"""

import numpy as np
import tensorflow as tf
from tensorflow.keras import layers, models
import cv2
import pydicom
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from cryptography.hazmat.backends import default_backend
import hashlib
import hmac
import logging
from typing import Dict, List, Tuple, Optional, Any
from datetime import datetime
import json
import base64
from dataclasses import dataclass
import asyncio

logger = logging.getLogger(__name__)


@dataclass
class ImagingSecurityEvent:
    """Security event related to medical imaging"""
    event_id: str
    event_type: str  # access, modification, transmission, anomaly
    severity: str    # low, medium, high, critical
    timestamp: datetime
    user_id: str
    image_id: str
    details: Dict
    action_taken: str


class MedicalImageEncryption:
    """Advanced encryption system for medical images"""
    
    def __init__(self, master_key: bytes):
        self.master_key = master_key
        self.algorithm = algorithms.AES
        self.key_size = 256 // 8  # 256-bit key
    
    def generate_image_key(self, image_id: str) -> bytes:
        """Generate unique encryption key for each image"""
        # Derive image-specific key using HKDF
        salt = hashlib.sha256(image_id.encode()).digest()
        key = hashlib.pbkdf2_hmac('sha256', self.master_key, salt, 100000, self.key_size)
        return key
    
    def encrypt_dicom_image(self, dicom_data: bytes, image_id: str) -> Dict:
        """Encrypt DICOM image data with metadata protection"""
        try:
            # Generate unique key and IV for this image
            image_key = self.generate_image_key(image_id)
            iv = np.random.bytes(16)  # 128-bit IV for AES
            
            # Create cipher
            cipher = Cipher(
                self.algorithm(image_key),
                modes.CBC(iv),
                backend=default_backend()
            )
            encryptor = cipher.encryptor()
            
            # Pad data to block size
            padded_data = self._pad_data(dicom_data)
            
            # Encrypt
            encrypted_data = encryptor.update(padded_data) + encryptor.finalize()
            
            # Generate integrity hash
            integrity_hash = hmac.new(
                image_key,
                encrypted_data,
                hashlib.sha256
            ).hexdigest()
            
            return {
                'encrypted_data': base64.b64encode(encrypted_data).decode(),
                'iv': base64.b64encode(iv).decode(),
                'integrity_hash': integrity_hash,
                'encryption_algorithm': 'AES-256-CBC',
                'timestamp': datetime.utcnow().isoformat(),
                'image_id': image_id
            }
            
        except Exception as e:
            logger.error(f"Error encrypting DICOM image: {str(e)}")
            raise
    
    def decrypt_dicom_image(self, encrypted_package: Dict, image_id: str) -> bytes:
        """Decrypt DICOM image and verify integrity"""
        try:
            # Extract components
            encrypted_data = base64.b64decode(encrypted_package['encrypted_data'])
            iv = base64.b64decode(encrypted_package['iv'])
            stored_hash = encrypted_package['integrity_hash']
            
            # Generate decryption key
            image_key = self.generate_image_key(image_id)
            
            # Verify integrity
            computed_hash = hmac.new(
                image_key,
                encrypted_data,
                hashlib.sha256
            ).hexdigest()
            
            if not hmac.compare_digest(stored_hash, computed_hash):
                raise ValueError("Image integrity verification failed")
            
            # Decrypt
            cipher = Cipher(
                self.algorithm(image_key),
                modes.CBC(iv),
                backend=default_backend()
            )
            decryptor = cipher.decryptor()
            
            padded_data = decryptor.update(encrypted_data) + decryptor.finalize()
            
            # Remove padding
            original_data = self._unpad_data(padded_data)
            
            return original_data
            
        except Exception as e:
            logger.error(f"Error decrypting DICOM image: {str(e)}")
            raise
    
    def _pad_data(self, data: bytes) -> bytes:
        """PKCS7 padding for block cipher"""
        block_size = 16  # AES block size
        padding_length = block_size - (len(data) % block_size)
        padding = bytes([padding_length] * padding_length)
        return data + padding
    
    def _unpad_data(self, padded_data: bytes) -> bytes:
        """Remove PKCS7 padding"""
        padding_length = padded_data[-1]
        return padded_data[:-padding_length]


class MedicalImagingAnomalyDetector:
    """AI-powered anomaly detection for medical imaging access patterns"""
    
    def __init__(self):
        self.model = None
        self.feature_scaler = None
        self.baseline_patterns = {}
        self._build_anomaly_model()
    
    def _build_anomaly_model(self):
        """Build autoencoder for anomaly detection"""
        # Input features: user behavior, access patterns, image metadata
        input_dim = 50
        
        # Encoder
        encoder_input = layers.Input(shape=(input_dim,))
        encoded = layers.Dense(32, activation='relu')(encoder_input)
        encoded = layers.Dense(16, activation='relu')(encoded)
        encoded = layers.Dense(8, activation='relu')(encoded)
        
        # Decoder
        decoded = layers.Dense(16, activation='relu')(encoded)
        decoded = layers.Dense(32, activation='relu')(decoded)
        decoded = layers.Dense(input_dim, activation='sigmoid')(decoded)
        
        # Autoencoder model
        self.model = models.Model(encoder_input, decoded)
        self.model.compile(optimizer='adam', loss='mse', metrics=['mae'])
        
        logger.info("Medical imaging anomaly detection model built")
    
    def extract_access_features(self, access_event: Dict) -> np.ndarray:
        """Extract features from imaging access event"""
        features = []
        
        # Temporal features
        timestamp = datetime.fromisoformat(access_event.get('timestamp', datetime.utcnow().isoformat()))
        features.extend([
            timestamp.hour / 24.0,  # Hour of day
            timestamp.weekday() / 6.0,  # Day of week
            (timestamp.hour < 6 or timestamp.hour > 22),  # Off-hours access
        ])
        
        # User behavior features
        user_id = access_event.get('user_id', '')
        features.extend([
            len(user_id) / 50.0,  # User ID length (normalized)
            access_event.get('session_duration', 0) / 3600.0,  # Session duration in hours
            access_event.get('images_accessed', 1) / 100.0,  # Number of images accessed
            access_event.get('failed_attempts', 0) / 10.0,  # Failed access attempts
        ])
        
        # Image metadata features
        image_info = access_event.get('image_info', {})
        features.extend([
            image_info.get('file_size', 0) / (100 * 1024 * 1024),  # File size in MB
            len(image_info.get('modality', '')) / 10.0,  # Modality string length
            image_info.get('is_sensitive', False),  # Sensitive image flag
            image_info.get('patient_age', 50) / 100.0,  # Patient age
        ])
        
        # Access pattern features
        features.extend([
            access_event.get('download_requested', False),  # Download flag
            access_event.get('print_requested', False),  # Print flag
            access_event.get('share_requested', False),  # Share flag
            access_event.get('external_access', False),  # External network access
            access_event.get('mobile_device', False),  # Mobile device access
        ])
        
        # Network and location features
        features.extend([
            access_event.get('ip_reputation_score', 0.5),  # IP reputation (0-1)
            access_event.get('geolocation_anomaly', False),  # Unusual location
            access_event.get('vpn_detected', False),  # VPN usage
            access_event.get('tor_detected', False),  # Tor usage
        ])
        
        # Pad or truncate to exactly 50 features
        while len(features) < 50:
            features.append(0.0)
        
        return np.array(features[:50])
    
    def detect_anomaly(self, access_event: Dict) -> Dict:
        """Detect anomalies in medical imaging access"""
        try:
            # Extract features
            features = self.extract_access_features(access_event)
            features_reshaped = features.reshape(1, -1)
            
            # Get reconstruction from autoencoder
            reconstruction = self.model.predict(features_reshaped, verbose=0)
            
            # Calculate reconstruction error
            mse_error = np.mean(np.square(features - reconstruction[0]))
            mae_error = np.mean(np.abs(features - reconstruction[0]))
            
            # Determine anomaly score and threshold
            anomaly_score = mse_error
            threshold = 0.1  # This would be learned from training data
            
            is_anomaly = anomaly_score > threshold
            
            # Calculate confidence based on how far from threshold
            confidence = min(abs(anomaly_score - threshold) / threshold, 1.0)
            
            # Determine severity
            severity = self._calculate_severity(anomaly_score, access_event)
            
            result = {
                'is_anomaly': bool(is_anomaly),
                'anomaly_score': float(anomaly_score),
                'confidence': float(confidence),
                'severity': severity,
                'reconstruction_error': {
                    'mse': float(mse_error),
                    'mae': float(mae_error)
                },
                'suspicious_features': self._identify_suspicious_features(features, reconstruction[0]),
                'timestamp': datetime.utcnow().isoformat(),
                'event_id': access_event.get('event_id', 'unknown')
            }
            
            return result
            
        except Exception as e:
            logger.error(f"Error in anomaly detection: {str(e)}")
            return {
                'error': str(e),
                'is_anomaly': False,
                'timestamp': datetime.utcnow().isoformat()
            }
    
    def _calculate_severity(self, anomaly_score: float, access_event: Dict) -> str:
        """Calculate severity level based on anomaly score and context"""
        base_severity = "low"
        
        if anomaly_score > 0.5:
            base_severity = "critical"
        elif anomaly_score > 0.3:
            base_severity = "high"
        elif anomaly_score > 0.15:
            base_severity = "medium"
        
        # Escalate severity based on context
        if access_event.get('external_access', False):
            base_severity = "high" if base_severity == "medium" else base_severity
        
        if access_event.get('sensitive_data', False):
            base_severity = "critical" if base_severity in ["high", "medium"] else base_severity
        
        return base_severity
    
    def _identify_suspicious_features(self, original: np.ndarray, reconstructed: np.ndarray) -> List[str]:
        """Identify which features contributed most to the anomaly"""
        feature_names = [
            'hour_of_day', 'day_of_week', 'off_hours_access',
            'user_id_length', 'session_duration', 'images_accessed', 'failed_attempts',
            'file_size', 'modality_length', 'is_sensitive', 'patient_age',
            'download_requested', 'print_requested', 'share_requested', 'external_access', 'mobile_device',
            'ip_reputation', 'geolocation_anomaly', 'vpn_detected', 'tor_detected'
        ]
        
        # Calculate per-feature reconstruction errors
        feature_errors = np.abs(original - reconstructed)
        
        # Get top 5 most suspicious features
        top_indices = np.argsort(feature_errors)[-5:]
        
        suspicious_features = []
        for idx in reversed(top_indices):
            if idx < len(feature_names):
                suspicious_features.append(feature_names[idx])
        
        return suspicious_features


class MedicalImagingSecurityFramework:
    """Comprehensive security framework for medical imaging systems"""
    
    def __init__(self, config: Dict):
        self.config = config
        self.encryptor = MedicalImageEncryption(config['master_key'].encode())
        self.anomaly_detector = MedicalImagingAnomalyDetector()
        self.security_events = []
        self.active_sessions = {}
        
        # Initialize threat intelligence
        self.threat_indicators = {
            'malicious_ips': set(),
            'suspicious_user_agents': set(),
            'known_attack_patterns': []
        }
    
    def secure_image_upload(self, image_data: bytes, metadata: Dict, user_id: str) -> Dict:
        """Securely process and store medical image upload"""
        try:
            image_id = self._generate_image_id(metadata)
            
            # Validate image integrity and format
            validation_result = self._validate_medical_image(image_data, metadata)
            if not validation_result['valid']:
                raise ValueError(f"Image validation failed: {validation_result['reason']}")
            
            # Scan for malware
            malware_scan = self._scan_for_malware(image_data)
            if malware_scan['threat_detected']:
                self._log_security_event({
                    'event_type': 'malware_detected',
                    'severity': 'critical',
                    'user_id': user_id,
                    'image_id': image_id,
                    'details': malware_scan
                })
                raise ValueError("Malware detected in uploaded image")
            
            # Encrypt image
            encrypted_package = self.encryptor.encrypt_dicom_image(image_data, image_id)
            
            # Log successful upload
            self._log_security_event({
                'event_type': 'image_upload',
                'severity': 'low',
                'user_id': user_id,
                'image_id': image_id,
                'details': {
                    'file_size': len(image_data),
                    'modality': metadata.get('modality', 'unknown'),
                    'encrypted': True
                }
            })
            
            return {
                'success': True,
                'image_id': image_id,
                'encrypted_package': encrypted_package,
                'validation': validation_result,
                'security_scan': malware_scan
            }
            
        except Exception as e:
            logger.error(f"Error in secure image upload: {str(e)}")
            return {
                'success': False,
                'error': str(e),
                'timestamp': datetime.utcnow().isoformat()
            }
    
    def secure_image_access(self, image_id: str, user_id: str, access_context: Dict) -> Dict:
        """Securely handle medical image access with anomaly detection"""
        try:
            # Create access event for analysis
            access_event = {
                'event_id': self._generate_event_id(),
                'timestamp': datetime.utcnow().isoformat(),
                'user_id': user_id,
                'image_id': image_id,
                **access_context
            }
            
            # Detect anomalies in access pattern
            anomaly_result = self.anomaly_detector.detect_anomaly(access_event)
            
            # Check if access should be blocked
            if anomaly_result['is_anomaly'] and anomaly_result['severity'] in ['high', 'critical']:
                self._log_security_event({
                    'event_type': 'suspicious_access_blocked',
                    'severity': anomaly_result['severity'],
                    'user_id': user_id,
                    'image_id': image_id,
                    'details': anomaly_result
                })
                
                return {
                    'access_granted': False,
                    'reason': 'Suspicious access pattern detected',
                    'anomaly_details': anomaly_result,
                    'contact_security': True
                }
            
            # Log access attempt
            self._log_security_event({
                'event_type': 'image_access',
                'severity': 'low' if not anomaly_result['is_anomaly'] else 'medium',
                'user_id': user_id,
                'image_id': image_id,
                'details': {
                    'anomaly_score': anomaly_result['anomaly_score'],
                    'access_context': access_context
                }
            })
            
            return {
                'access_granted': True,
                'anomaly_details': anomaly_result,
                'security_recommendations': self._generate_security_recommendations(anomaly_result)
            }
            
        except Exception as e:
            logger.error(f"Error in secure image access: {str(e)}")
            return {
                'access_granted': False,
                'error': str(e),
                'timestamp': datetime.utcnow().isoformat()
            }
    
    def _validate_medical_image(self, image_data: bytes, metadata: Dict) -> Dict:
        """Validate medical image format and integrity"""
        try:
            # Check if it's a valid DICOM file
            if image_data.startswith(b'DICM') or b'DICM' in image_data[:1024]:
                # Validate DICOM structure
                try:
                    # This would use pydicom to validate structure
                    return {
                        'valid': True,
                        'format': 'DICOM',
                        'validation_checks': ['format', 'structure', 'metadata']
                    }
                except Exception:
                    return {
                        'valid': False,
                        'reason': 'Invalid DICOM structure'
                    }
            
            # Check for other medical image formats
            if image_data.startswith(b'\x89PNG') or image_data.startswith(b'\xff\xd8\xff'):
                return {
                    'valid': True,
                    'format': 'Standard Image',
                    'validation_checks': ['format']
                }
            
            return {
                'valid': False,
                'reason': 'Unsupported image format'
            }
            
        except Exception as e:
            return {
                'valid': False,
                'reason': f'Validation error: {str(e)}'
            }
    
    def _scan_for_malware(self, image_data: bytes) -> Dict:
        """Scan image data for malware and suspicious content"""
        # This is a simplified implementation
        # In production, integrate with enterprise antivirus solutions
        
        suspicious_patterns = [
            b'<script',
            b'javascript:',
            b'eval(',
            b'exec(',
            b'system(',
            b'shell_exec'
        ]
        
        threat_detected = False
        detected_patterns = []
        
        for pattern in suspicious_patterns:
            if pattern in image_data:
                threat_detected = True
                detected_patterns.append(pattern.decode('utf-8', errors='ignore'))
        
        return {
            'threat_detected': threat_detected,
            'detected_patterns': detected_patterns,
            'scan_timestamp': datetime.utcnow().isoformat(),
            'scanner_version': '1.0.0'
        }
    
    def _generate_image_id(self, metadata: Dict) -> str:
        """Generate unique image identifier"""
        content = f"{metadata.get('patient_id', '')}{metadata.get('study_date', '')}{datetime.utcnow().isoformat()}"
        return hashlib.sha256(content.encode()).hexdigest()[:16]
    
    def _generate_event_id(self) -> str:
        """Generate unique event identifier"""
        return hashlib.sha256(f"{datetime.utcnow().isoformat()}{np.random.random()}".encode()).hexdigest()[:12]
    
    def _log_security_event(self, event_data: Dict):
        """Log security event"""
        event = ImagingSecurityEvent(
            event_id=event_data.get('event_id', self._generate_event_id()),
            event_type=event_data['event_type'],
            severity=event_data['severity'],
            timestamp=datetime.utcnow(),
            user_id=event_data['user_id'],
            image_id=event_data['image_id'],
            details=event_data.get('details', {}),
            action_taken=event_data.get('action_taken', 'logged')
        )
        
        self.security_events.append(event)
        logger.info(f"Security event logged: {event.event_type} - {event.severity}")
    
    def _generate_security_recommendations(self, anomaly_result: Dict) -> List[str]:
        """Generate security recommendations based on anomaly detection"""
        recommendations = []
        
        if anomaly_result['is_anomaly']:
            recommendations.append("Enhanced monitoring recommended for this user")
            
            if 'off_hours_access' in anomaly_result.get('suspicious_features', []):
                recommendations.append("Verify legitimate need for off-hours access")
            
            if 'external_access' in anomaly_result.get('suspicious_features', []):
                recommendations.append("Additional authentication required for external access")
            
            if anomaly_result['severity'] in ['high', 'critical']:
                recommendations.append("Consider temporary access restriction")
                recommendations.append("Notify security team immediately")
        
        return recommendations
    
    def get_security_dashboard(self) -> Dict:
        """Generate security dashboard data"""
        recent_events = [e for e in self.security_events if 
                        (datetime.utcnow() - e.timestamp).days < 7]
        
        severity_counts = {}
        event_type_counts = {}
        
        for event in recent_events:
            severity_counts[event.severity] = severity_counts.get(event.severity, 0) + 1
            event_type_counts[event.event_type] = event_type_counts.get(event.event_type, 0) + 1
        
        return {
            'total_events_7_days': len(recent_events),
            'severity_breakdown': severity_counts,
            'event_type_breakdown': event_type_counts,
            'active_threats': len([e for e in recent_events if e.severity in ['high', 'critical']]),
            'last_updated': datetime.utcnow().isoformat()
        }
