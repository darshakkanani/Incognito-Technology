"""
AI-Driven Deep Learning Framework for Early Detection of Skin Diseases
Advanced computer vision models for dermatological image analysis
"""

import numpy as np
import tensorflow as tf
from tensorflow.keras import layers, models, applications
import cv2
from sklearn.metrics import classification_report, confusion_matrix
import matplotlib.pyplot as plt
from typing import Dict, List, Tuple, Optional, Any
from datetime import datetime
import logging
import json
from dataclasses import dataclass

logger = logging.getLogger(__name__)


@dataclass
class SkinDiseaseResult:
    """Skin disease detection result"""
    patient_id: str
    image_id: str
    disease_detected: bool
    disease_type: str
    confidence: float
    severity_level: str
    affected_area_percentage: float
    lesion_characteristics: Dict
    recommendations: List[str]
    urgency_level: str
    processing_time: float
    model_version: str
    timestamp: str


class SkinImagePreprocessor:
    """Preprocessing pipeline for dermatological images"""
    
    def __init__(self, target_size: Tuple[int, int] = (224, 224)):
        self.target_size = target_size
        
    def preprocess_skin_image(self, image: np.ndarray) -> np.ndarray:
        """Preprocess skin image for analysis"""
        try:
            # Resize image
            processed = cv2.resize(image, self.target_size)
            
            # Hair removal (simplified)
            processed = self._remove_hair_artifacts(processed)
            
            # Color normalization
            processed = self._normalize_skin_color(processed)
            
            # Enhance contrast
            processed = self._enhance_contrast(processed)
            
            # Normalize pixel values
            processed = processed.astype(np.float32) / 255.0
            
            return processed
            
        except Exception as e:
            logger.error(f"Error preprocessing skin image: {str(e)}")
            raise
    
    def _remove_hair_artifacts(self, image: np.ndarray) -> np.ndarray:
        """Remove hair artifacts from skin images"""
        # Convert to grayscale for hair detection
        gray = cv2.cvtColor(image, cv2.COLOR_RGB2GRAY)
        
        # Create kernel for morphological operations
        kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (17, 17))
        
        # Black hat operation to detect hair
        blackhat = cv2.morphologyEx(gray, cv2.MORPH_BLACKHAT, kernel)
        
        # Threshold to create hair mask
        _, hair_mask = cv2.threshold(blackhat, 10, 255, cv2.THRESH_BINARY)
        
        # Inpaint to remove hair
        result = cv2.inpaint(image, hair_mask, 1, cv2.INPAINT_TELEA)
        
        return result
    
    def _normalize_skin_color(self, image: np.ndarray) -> np.ndarray:
        """Normalize skin color variations"""
        # Convert to LAB color space
        lab = cv2.cvtColor(image, cv2.COLOR_RGB2LAB)
        
        # Apply CLAHE to L channel
        clahe = cv2.createCLAHE(clipLimit=3.0, tileGridSize=(8, 8))
        lab[:, :, 0] = clahe.apply(lab[:, :, 0])
        
        # Convert back to RGB
        normalized = cv2.cvtColor(lab, cv2.COLOR_LAB2RGB)
        
        return normalized
    
    def _enhance_contrast(self, image: np.ndarray) -> np.ndarray:
        """Enhance image contrast"""
        # Convert to YUV
        yuv = cv2.cvtColor(image, cv2.COLOR_RGB2YUV)
        
        # Apply histogram equalization to Y channel
        yuv[:, :, 0] = cv2.equalizeHist(yuv[:, :, 0])
        
        # Convert back to RGB
        enhanced = cv2.cvtColor(yuv, cv2.COLOR_YUV2RGB)
        
        return enhanced


class SkinDiseaseCNN:
    """CNN model for skin disease detection and classification"""
    
    def __init__(self, input_shape: Tuple[int, int, int] = (224, 224, 3)):
        self.input_shape = input_shape
        self.model = None
        self.disease_classes = [
            'Melanoma', 'Basal Cell Carcinoma', 'Squamous Cell Carcinoma',
            'Actinic Keratosis', 'Seborrheic Keratosis', 'Nevus',
            'Dermatofibroma', 'Vascular Lesion', 'Benign Keratosis',
            'Normal Skin'
        ]
        
        self._build_model()
    
    def _build_model(self):
        """Build CNN architecture for skin disease classification"""
        
        # Use EfficientNetB4 as backbone
        base_model = applications.EfficientNetB4(
            weights='imagenet',
            include_top=False,
            input_shape=self.input_shape
        )
        
        base_model.trainable = False
        
        # Custom head for skin disease classification
        inputs = tf.keras.Input(shape=self.input_shape)
        
        # Data augmentation layers
        x = layers.RandomFlip("horizontal")(inputs)
        x = layers.RandomRotation(0.1)(x)
        x = layers.RandomZoom(0.1)(x)
        
        # Preprocessing
        x = layers.Rescaling(1./255)(x)
        
        # Base model
        x = base_model(x, training=False)
        
        # Global average pooling
        x = layers.GlobalAveragePooling2D()(x)
        
        # Dense layers
        x = layers.Dense(512, activation='relu')(x)
        x = layers.BatchNormalization()(x)
        x = layers.Dropout(0.5)(x)
        
        x = layers.Dense(256, activation='relu')(x)
        x = layers.BatchNormalization()(x)
        x = layers.Dropout(0.3)(x)
        
        # Output layer
        outputs = layers.Dense(len(self.disease_classes), activation='softmax')(x)
        
        self.model = tf.keras.Model(inputs, outputs)
        
        # Compile model
        self.model.compile(
            optimizer=tf.keras.optimizers.Adam(learning_rate=0.001),
            loss='categorical_crossentropy',
            metrics=['accuracy', 'top_k_categorical_accuracy']
        )
        
        logger.info("Skin disease CNN model built successfully")
    
    def predict_skin_disease(self, skin_image: np.ndarray, patient_id: str, image_id: str) -> SkinDiseaseResult:
        """Predict skin disease from dermatological image"""
        start_time = datetime.now()
        
        try:
            # Ensure correct input shape
            if len(skin_image.shape) == 3:
                skin_image = np.expand_dims(skin_image, axis=0)
            
            # Make prediction
            predictions = self.model.predict(skin_image, verbose=0)
            class_probabilities = predictions[0]
            
            # Get top prediction
            predicted_class_idx = np.argmax(class_probabilities)
            predicted_disease = self.disease_classes[predicted_class_idx]
            confidence = float(class_probabilities[predicted_class_idx])
            
            # Determine if disease is detected
            disease_detected = predicted_disease != 'Normal Skin' and confidence > 0.5
            
            # Analyze lesion characteristics
            lesion_chars = self._analyze_lesion_characteristics(skin_image[0])
            
            # Calculate affected area
            affected_area = self._calculate_affected_area(skin_image[0])
            
            # Determine severity and urgency
            severity_level = self._determine_severity(predicted_disease, confidence, lesion_chars)
            urgency_level = self._determine_urgency(predicted_disease, severity_level, confidence)
            
            # Generate recommendations
            recommendations = self._generate_recommendations(predicted_disease, severity_level, urgency_level)
            
            processing_time = (datetime.now() - start_time).total_seconds()
            
            return SkinDiseaseResult(
                patient_id=patient_id,
                image_id=image_id,
                disease_detected=disease_detected,
                disease_type=predicted_disease,
                confidence=confidence,
                severity_level=severity_level,
                affected_area_percentage=affected_area,
                lesion_characteristics=lesion_chars,
                recommendations=recommendations,
                urgency_level=urgency_level,
                processing_time=processing_time,
                model_version="SkinDiseaseCNN_v2.0",
                timestamp=datetime.utcnow().isoformat()
            )
            
        except Exception as e:
            logger.error(f"Error in skin disease prediction: {str(e)}")
            return SkinDiseaseResult(
                patient_id=patient_id,
                image_id=image_id,
                disease_detected=False,
                disease_type="Error",
                confidence=0.0,
                severity_level="unknown",
                affected_area_percentage=0.0,
                lesion_characteristics={},
                recommendations=[f"Error in analysis: {str(e)}"],
                urgency_level="unknown",
                processing_time=(datetime.now() - start_time).total_seconds(),
                model_version="SkinDiseaseCNN_v2.0",
                timestamp=datetime.utcnow().isoformat()
            )
    
    def _analyze_lesion_characteristics(self, image: np.ndarray) -> Dict:
        """Analyze lesion characteristics (ABCDE criteria)"""
        # Convert to uint8 for OpenCV operations
        if image.max() <= 1.0:
            image_uint8 = (image * 255).astype(np.uint8)
        else:
            image_uint8 = image.astype(np.uint8)
        
        # Convert to grayscale
        gray = cv2.cvtColor(image_uint8, cv2.COLOR_RGB2GRAY)
        
        # Apply threshold to segment lesion
        _, binary = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
        
        # Find contours
        contours, _ = cv2.findContours(binary, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        
        if not contours:
            return {"error": "No lesion detected"}
        
        # Get largest contour (main lesion)
        main_contour = max(contours, key=cv2.contourArea)
        
        # Calculate characteristics
        area = cv2.contourArea(main_contour)
        perimeter = cv2.arcLength(main_contour, True)
        
        # Asymmetry (simplified)
        moments = cv2.moments(main_contour)
        if moments["m00"] != 0:
            cx = int(moments["m10"] / moments["m00"])
            cy = int(moments["m01"] / moments["m00"])
        else:
            cx, cy = 0, 0
        
        # Border irregularity
        hull = cv2.convexHull(main_contour)
        hull_area = cv2.contourArea(hull)
        solidity = area / hull_area if hull_area > 0 else 0
        
        # Color variation (simplified)
        mask = np.zeros(gray.shape, np.uint8)
        cv2.drawContours(mask, [main_contour], -1, 255, -1)
        color_std = np.std(image_uint8[mask == 255])
        
        # Diameter estimation
        diameter = np.sqrt(4 * area / np.pi)
        
        return {
            "area_pixels": float(area),
            "perimeter": float(perimeter),
            "diameter_pixels": float(diameter),
            "asymmetry_score": 1.0 - solidity,  # Lower solidity = more asymmetric
            "border_irregularity": 1.0 - solidity,
            "color_variation": float(color_std / 255.0),
            "centroid": {"x": cx, "y": cy},
            "solidity": float(solidity)
        }
    
    def _calculate_affected_area(self, image: np.ndarray) -> float:
        """Calculate percentage of skin area affected"""
        # This is a simplified calculation
        # In practice, would use more sophisticated segmentation
        
        if image.max() <= 1.0:
            image_uint8 = (image * 255).astype(np.uint8)
        else:
            image_uint8 = image.astype(np.uint8)
        
        gray = cv2.cvtColor(image_uint8, cv2.COLOR_RGB2GRAY)
        _, binary = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
        
        total_pixels = gray.shape[0] * gray.shape[1]
        lesion_pixels = np.sum(binary == 0)  # Assuming lesions are darker
        
        percentage = (lesion_pixels / total_pixels) * 100
        return min(percentage, 100.0)  # Cap at 100%
    
    def _determine_severity(self, disease_type: str, confidence: float, lesion_chars: Dict) -> str:
        """Determine severity level based on disease type and characteristics"""
        
        # High-risk diseases
        high_risk_diseases = ['Melanoma', 'Basal Cell Carcinoma', 'Squamous Cell Carcinoma']
        
        if disease_type in high_risk_diseases:
            if confidence > 0.8:
                return "high"
            elif confidence > 0.6:
                return "medium-high"
            else:
                return "medium"
        
        # Medium-risk diseases
        medium_risk_diseases = ['Actinic Keratosis']
        
        if disease_type in medium_risk_diseases:
            return "medium"
        
        # Low-risk diseases
        if disease_type in ['Seborrheic Keratosis', 'Nevus', 'Dermatofibroma']:
            # Check for concerning characteristics
            if lesion_chars.get('diameter_pixels', 0) > 100:  # Large lesion
                return "medium"
            elif lesion_chars.get('asymmetry_score', 0) > 0.5:  # Highly asymmetric
                return "medium"
            else:
                return "low"
        
        return "low"
    
    def _determine_urgency(self, disease_type: str, severity_level: str, confidence: float) -> str:
        """Determine urgency level for medical consultation"""
        
        if disease_type == 'Melanoma' and confidence > 0.7:
            return "immediate"
        
        if disease_type in ['Basal Cell Carcinoma', 'Squamous Cell Carcinoma'] and confidence > 0.8:
            return "urgent"
        
        if severity_level == "high":
            return "urgent"
        elif severity_level in ["medium-high", "medium"]:
            return "moderate"
        else:
            return "routine"
    
    def _generate_recommendations(self, disease_type: str, severity_level: str, urgency_level: str) -> List[str]:
        """Generate clinical recommendations"""
        recommendations = []
        
        # General recommendations based on urgency
        if urgency_level == "immediate":
            recommendations.extend([
                "Seek immediate dermatological consultation",
                "Consider emergency department evaluation if no dermatologist available",
                "Avoid sun exposure to affected area"
            ])
        elif urgency_level == "urgent":
            recommendations.extend([
                "Schedule dermatologist appointment within 1-2 weeks",
                "Monitor for changes in size, color, or symptoms",
                "Photograph lesion for comparison"
            ])
        elif urgency_level == "moderate":
            recommendations.extend([
                "Schedule dermatologist appointment within 4-6 weeks",
                "Monitor lesion for changes",
                "Use sun protection"
            ])
        else:
            recommendations.extend([
                "Routine dermatological follow-up recommended",
                "Continue regular skin self-examinations",
                "Use broad-spectrum sunscreen"
            ])
        
        # Disease-specific recommendations
        if disease_type == "Melanoma":
            recommendations.extend([
                "Biopsy likely required for definitive diagnosis",
                "Staging workup may be necessary",
                "Discuss family history with healthcare provider"
            ])
        elif disease_type in ["Basal Cell Carcinoma", "Squamous Cell Carcinoma"]:
            recommendations.extend([
                "Biopsy recommended for confirmation",
                "Discuss treatment options (surgery, radiation, topical therapy)",
                "Regular skin cancer screening advised"
            ])
        elif disease_type == "Actinic Keratosis":
            recommendations.extend([
                "Consider topical treatments or cryotherapy",
                "Increased sun protection essential",
                "Regular monitoring for progression"
            ])
        
        return recommendations
    
    def generate_dermatology_report(self, result: SkinDiseaseResult) -> Dict:
        """Generate comprehensive dermatology report"""
        return {
            "patient_information": {
                "patient_id": result.patient_id,
                "image_id": result.image_id,
                "analysis_date": result.timestamp
            },
            "clinical_findings": {
                "primary_diagnosis": result.disease_type,
                "confidence_level": f"{result.confidence:.2%}",
                "severity_assessment": result.severity_level,
                "urgency_classification": result.urgency_level,
                "affected_area_percentage": f"{result.affected_area_percentage:.1f}%"
            },
            "lesion_analysis": {
                "characteristics": result.lesion_characteristics,
                "abcde_assessment": self._generate_abcde_assessment(result.lesion_characteristics)
            },
            "recommendations": {
                "immediate_actions": [r for r in result.recommendations if "immediate" in r.lower()],
                "follow_up_care": [r for r in result.recommendations if "follow" in r.lower()],
                "preventive_measures": [r for r in result.recommendations if "sun" in r.lower() or "protection" in r.lower()]
            },
            "technical_details": {
                "model_version": result.model_version,
                "processing_time_seconds": result.processing_time,
                "analysis_method": "Deep Learning CNN with EfficientNet backbone"
            },
            "disclaimer": [
                "This AI analysis is for screening and educational purposes only",
                "Results must be interpreted by qualified dermatologists",
                "Clinical examination and possible biopsy may be required",
                "Not intended to replace professional medical diagnosis"
            ]
        }
    
    def _generate_abcde_assessment(self, lesion_chars: Dict) -> Dict:
        """Generate ABCDE melanoma assessment"""
        if not lesion_chars or "error" in lesion_chars:
            return {"assessment": "Unable to perform ABCDE analysis"}
        
        # Asymmetry
        asymmetry_score = lesion_chars.get('asymmetry_score', 0)
        asymmetry = "Concerning" if asymmetry_score > 0.5 else "Normal"
        
        # Border
        border_score = lesion_chars.get('border_irregularity', 0)
        border = "Irregular" if border_score > 0.5 else "Regular"
        
        # Color
        color_variation = lesion_chars.get('color_variation', 0)
        color = "Varied" if color_variation > 0.3 else "Uniform"
        
        # Diameter
        diameter = lesion_chars.get('diameter_pixels', 0)
        diameter_mm = diameter * 0.1  # Rough conversion
        diameter_assessment = "Large (>6mm)" if diameter_mm > 6 else "Small (<6mm)"
        
        # Evolution (cannot assess from single image)
        evolution = "Requires clinical history"
        
        return {
            "asymmetry": asymmetry,
            "border": border,
            "color": color,
            "diameter": diameter_assessment,
            "evolution": evolution,
            "overall_concern": "High" if any(x in ["Concerning", "Irregular", "Varied", "Large"] 
                                           for x in [asymmetry, border, color, diameter_assessment]) else "Low"
        }
