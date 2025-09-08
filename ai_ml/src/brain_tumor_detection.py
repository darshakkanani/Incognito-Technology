"""
AI-Driven Deep Learning Framework for Early Detection of Brain Tumors
Advanced CNN models for MRI brain scan analysis and tumor classification
"""

import numpy as np
import tensorflow as tf
from tensorflow.keras import layers, models, applications
from tensorflow.keras.preprocessing.image import ImageDataGenerator
import cv2
import pydicom
import nibabel as nib
from sklearn.metrics import classification_report, confusion_matrix
import matplotlib.pyplot as plt
import seaborn as sns
from typing import Dict, List, Tuple, Optional, Any
from datetime import datetime
import logging
import json
import os
from dataclasses import dataclass

logger = logging.getLogger(__name__)


@dataclass
class TumorPrediction:
    """Brain tumor prediction result"""
    patient_id: str
    scan_id: str
    tumor_detected: bool
    tumor_type: str
    confidence: float
    tumor_location: Dict
    tumor_size_mm: float
    severity_level: str
    recommendations: List[str]
    processing_time: float
    model_version: str
    timestamp: str


class BrainMRIPreprocessor:
    """Advanced preprocessing for brain MRI scans"""
    
    def __init__(self, target_size: Tuple[int, int] = (224, 224)):
        self.target_size = target_size
        self.intensity_range = (0, 255)
        
    def preprocess_dicom(self, dicom_path: str) -> np.ndarray:
        """Preprocess DICOM brain MRI scan"""
        try:
            # Read DICOM file
            dicom_data = pydicom.dcmread(dicom_path)
            image = dicom_data.pixel_array.astype(np.float32)
            
            # Apply DICOM-specific preprocessing
            if hasattr(dicom_data, 'RescaleSlope') and hasattr(dicom_data, 'RescaleIntercept'):
                image = image * dicom_data.RescaleSlope + dicom_data.RescaleIntercept
            
            # Normalize intensity
            image = self._normalize_intensity(image)
            
            # Enhance contrast
            image = self._enhance_contrast(image)
            
            # Resize to target size
            image = cv2.resize(image, self.target_size)
            
            # Convert to 3-channel for CNN compatibility
            if len(image.shape) == 2:
                image = np.stack([image] * 3, axis=-1)
            
            return image
            
        except Exception as e:
            logger.error(f"Error preprocessing DICOM: {str(e)}")
            raise
    
    def preprocess_nifti(self, nifti_path: str, slice_idx: Optional[int] = None) -> np.ndarray:
        """Preprocess NIfTI brain scan"""
        try:
            # Load NIfTI file
            nifti_img = nib.load(nifti_path)
            image_data = nifti_img.get_fdata()
            
            # Select middle slice if not specified
            if slice_idx is None:
                slice_idx = image_data.shape[2] // 2
            
            # Extract 2D slice
            image = image_data[:, :, slice_idx].astype(np.float32)
            
            # Normalize and preprocess
            image = self._normalize_intensity(image)
            image = self._enhance_contrast(image)
            image = cv2.resize(image, self.target_size)
            
            # Convert to 3-channel
            if len(image.shape) == 2:
                image = np.stack([image] * 3, axis=-1)
            
            return image
            
        except Exception as e:
            logger.error(f"Error preprocessing NIfTI: {str(e)}")
            raise
    
    def _normalize_intensity(self, image: np.ndarray) -> np.ndarray:
        """Normalize image intensity to 0-255 range"""
        # Remove outliers (1st and 99th percentiles)
        p1, p99 = np.percentile(image, (1, 99))
        image = np.clip(image, p1, p99)
        
        # Normalize to 0-255
        image = (image - image.min()) / (image.max() - image.min()) * 255
        return image.astype(np.uint8)
    
    def _enhance_contrast(self, image: np.ndarray) -> np.ndarray:
        """Enhance image contrast using CLAHE"""
        clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8, 8))
        return clahe.apply(image.astype(np.uint8))
    
    def augment_training_data(self, images: np.ndarray, labels: np.ndarray) -> Tuple[np.ndarray, np.ndarray]:
        """Apply data augmentation for training"""
        datagen = ImageDataGenerator(
            rotation_range=15,
            width_shift_range=0.1,
            height_shift_range=0.1,
            shear_range=0.1,
            zoom_range=0.1,
            horizontal_flip=True,
            fill_mode='nearest'
        )
        
        augmented_images = []
        augmented_labels = []
        
        for i in range(len(images)):
            # Original image
            augmented_images.append(images[i])
            augmented_labels.append(labels[i])
            
            # Generate augmented versions
            img_reshaped = images[i].reshape((1,) + images[i].shape)
            aug_iter = datagen.flow(img_reshaped, batch_size=1)
            
            for _ in range(3):  # Generate 3 augmented versions
                aug_img = next(aug_iter)[0]
                augmented_images.append(aug_img)
                augmented_labels.append(labels[i])
        
        return np.array(augmented_images), np.array(augmented_labels)


class BrainTumorCNN:
    """Advanced CNN model for brain tumor detection and classification"""
    
    def __init__(self, input_shape: Tuple[int, int, int] = (224, 224, 3)):
        self.input_shape = input_shape
        self.model = None
        self.history = None
        self.class_names = ['No Tumor', 'Glioma', 'Meningioma', 'Pituitary Tumor']
        
        self._build_model()
    
    def _build_model(self):
        """Build advanced CNN architecture for brain tumor detection"""
        
        # Use EfficientNetB3 as backbone with custom head
        base_model = applications.EfficientNetB3(
            weights='imagenet',
            include_top=False,
            input_shape=self.input_shape
        )
        
        # Freeze base model initially
        base_model.trainable = False
        
        # Custom classification head
        inputs = tf.keras.Input(shape=self.input_shape)
        
        # Preprocessing layers
        x = layers.Rescaling(1./255)(inputs)
        
        # Base model
        x = base_model(x, training=False)
        
        # Global average pooling
        x = layers.GlobalAveragePooling2D()(x)
        
        # Dense layers with dropout
        x = layers.Dense(512, activation='relu')(x)
        x = layers.BatchNormalization()(x)
        x = layers.Dropout(0.5)(x)
        
        x = layers.Dense(256, activation='relu')(x)
        x = layers.BatchNormalization()(x)
        x = layers.Dropout(0.3)(x)
        
        x = layers.Dense(128, activation='relu')(x)
        x = layers.Dropout(0.2)(x)
        
        # Output layers
        tumor_detection = layers.Dense(1, activation='sigmoid', name='tumor_detection')(x)
        tumor_classification = layers.Dense(len(self.class_names), activation='softmax', name='tumor_classification')(x)
        
        # Create model
        self.model = tf.keras.Model(inputs, [tumor_detection, tumor_classification])
        
        # Compile model
        self.model.compile(
            optimizer=tf.keras.optimizers.Adam(learning_rate=0.001),
            loss={
                'tumor_detection': 'binary_crossentropy',
                'tumor_classification': 'categorical_crossentropy'
            },
            metrics={
                'tumor_detection': ['accuracy', 'precision', 'recall'],
                'tumor_classification': ['accuracy', 'top_k_categorical_accuracy']
            }
        )
        
        logger.info("Brain tumor CNN model built successfully")
    
    def train(self, train_images: np.ndarray, train_labels: Dict, 
              val_images: np.ndarray, val_labels: Dict, epochs: int = 50):
        """Train the brain tumor detection model"""
        
        # Callbacks
        callbacks = [
            tf.keras.callbacks.EarlyStopping(
                monitor='val_loss',
                patience=10,
                restore_best_weights=True
            ),
            tf.keras.callbacks.ReduceLROnPlateau(
                monitor='val_loss',
                factor=0.5,
                patience=5,
                min_lr=1e-7
            ),
            tf.keras.callbacks.ModelCheckpoint(
                'best_brain_tumor_model.h5',
                monitor='val_loss',
                save_best_only=True
            )
        ]
        
        # Train model
        self.history = self.model.fit(
            train_images,
            train_labels,
            validation_data=(val_images, val_labels),
            epochs=epochs,
            batch_size=32,
            callbacks=callbacks,
            verbose=1
        )
        
        # Fine-tune with unfrozen base model
        self._fine_tune_model(train_images, train_labels, val_images, val_labels)
        
        logger.info("Brain tumor model training completed")
    
    def _fine_tune_model(self, train_images: np.ndarray, train_labels: Dict,
                        val_images: np.ndarray, val_labels: Dict):
        """Fine-tune the model with unfrozen base layers"""
        
        # Unfreeze base model
        self.model.layers[2].trainable = True  # EfficientNet base model
        
        # Use lower learning rate for fine-tuning
        self.model.compile(
            optimizer=tf.keras.optimizers.Adam(learning_rate=0.0001),
            loss={
                'tumor_detection': 'binary_crossentropy',
                'tumor_classification': 'categorical_crossentropy'
            },
            metrics={
                'tumor_detection': ['accuracy', 'precision', 'recall'],
                'tumor_classification': ['accuracy', 'top_k_categorical_accuracy']
            }
        )
        
        # Fine-tune for fewer epochs
        fine_tune_history = self.model.fit(
            train_images,
            train_labels,
            validation_data=(val_images, val_labels),
            epochs=20,
            batch_size=16,
            verbose=1
        )
        
        logger.info("Model fine-tuning completed")
    
    def predict_tumor(self, brain_scan: np.ndarray, patient_id: str, scan_id: str) -> TumorPrediction:
        """Predict brain tumor from MRI scan"""
        start_time = datetime.now()
        
        try:
            # Ensure correct input shape
            if len(brain_scan.shape) == 3:
                brain_scan = np.expand_dims(brain_scan, axis=0)
            
            # Make predictions
            predictions = self.model.predict(brain_scan, verbose=0)
            tumor_detection_prob = float(predictions[0][0])
            tumor_classification_probs = predictions[1][0]
            
            # Determine if tumor is detected
            tumor_detected = tumor_detection_prob > 0.5
            
            # Get tumor type
            tumor_type_idx = np.argmax(tumor_classification_probs)
            tumor_type = self.class_names[tumor_type_idx]
            tumor_type_confidence = float(tumor_classification_probs[tumor_type_idx])
            
            # Calculate overall confidence
            confidence = tumor_detection_prob if tumor_detected else (1 - tumor_detection_prob)
            
            # Estimate tumor location and size (simplified)
            tumor_location, tumor_size = self._analyze_tumor_characteristics(brain_scan[0])
            
            # Determine severity
            severity_level = self._determine_severity(tumor_detected, tumor_type, tumor_size, confidence)
            
            # Generate recommendations
            recommendations = self._generate_recommendations(tumor_detected, tumor_type, severity_level)
            
            processing_time = (datetime.now() - start_time).total_seconds()
            
            return TumorPrediction(
                patient_id=patient_id,
                scan_id=scan_id,
                tumor_detected=tumor_detected,
                tumor_type=tumor_type if tumor_detected else "No Tumor",
                confidence=confidence,
                tumor_location=tumor_location,
                tumor_size_mm=tumor_size,
                severity_level=severity_level,
                recommendations=recommendations,
                processing_time=processing_time,
                model_version="BrainTumorCNN_v2.0",
                timestamp=datetime.utcnow().isoformat()
            )
            
        except Exception as e:
            logger.error(f"Error in tumor prediction: {str(e)}")
            return TumorPrediction(
                patient_id=patient_id,
                scan_id=scan_id,
                tumor_detected=False,
                tumor_type="Error",
                confidence=0.0,
                tumor_location={},
                tumor_size_mm=0.0,
                severity_level="unknown",
                recommendations=[f"Error in analysis: {str(e)}"],
                processing_time=(datetime.now() - start_time).total_seconds(),
                model_version="BrainTumorCNN_v2.0",
                timestamp=datetime.utcnow().isoformat()
            )
    
    def _analyze_tumor_characteristics(self, brain_scan: np.ndarray) -> Tuple[Dict, float]:
        """Analyze tumor location and size (simplified implementation)"""
        
        # Convert to grayscale for analysis
        if len(brain_scan.shape) == 3:
            gray_scan = cv2.cvtColor(brain_scan.astype(np.uint8), cv2.COLOR_RGB2GRAY)
        else:
            gray_scan = brain_scan.astype(np.uint8)
        
        # Apply threshold to identify potential tumor regions
        _, thresh = cv2.threshold(gray_scan, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
        
        # Find contours
        contours, _ = cv2.findContours(thresh, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        
        if contours:
            # Find largest contour (potential tumor)
            largest_contour = max(contours, key=cv2.contourArea)
            
            # Calculate centroid
            M = cv2.moments(largest_contour)
            if M["m00"] != 0:
                cx = int(M["m10"] / M["m00"])
                cy = int(M["m01"] / M["m00"])
            else:
                cx, cy = 0, 0
            
            # Estimate size (area to diameter conversion)
            area = cv2.contourArea(largest_contour)
            diameter_pixels = 2 * np.sqrt(area / np.pi)
            diameter_mm = diameter_pixels * 0.5  # Assuming 0.5mm per pixel
            
            # Determine brain region
            height, width = gray_scan.shape
            region = self._determine_brain_region(cx, cy, width, height)
            
            location = {
                "center_x": cx,
                "center_y": cy,
                "region": region,
                "hemisphere": "left" if cx < width // 2 else "right"
            }
            
            return location, diameter_mm
        
        return {}, 0.0
    
    def _determine_brain_region(self, x: int, y: int, width: int, height: int) -> str:
        """Determine brain region based on coordinates"""
        # Simplified brain region mapping
        regions = {
            (0, 0.33, 0, 0.33): "frontal",
            (0.33, 0.67, 0, 0.33): "parietal",
            (0.67, 1.0, 0, 0.33): "occipital",
            (0, 0.5, 0.33, 0.67): "temporal",
            (0.5, 1.0, 0.33, 0.67): "temporal",
            (0, 1.0, 0.67, 1.0): "cerebellum"
        }
        
        x_norm = x / width
        y_norm = y / height
        
        for (x_min, x_max, y_min, y_max), region in regions.items():
            if x_min <= x_norm <= x_max and y_min <= y_norm <= y_max:
                return region
        
        return "central"
    
    def _determine_severity(self, tumor_detected: bool, tumor_type: str, 
                          tumor_size: float, confidence: float) -> str:
        """Determine tumor severity level"""
        if not tumor_detected:
            return "none"
        
        # Size-based severity
        if tumor_size > 30:  # > 3cm
            size_severity = "high"
        elif tumor_size > 15:  # > 1.5cm
            size_severity = "medium"
        else:
            size_severity = "low"
        
        # Type-based severity
        type_severity_map = {
            "Glioma": "high",
            "Meningioma": "medium",
            "Pituitary Tumor": "medium",
            "No Tumor": "none"
        }
        type_severity = type_severity_map.get(tumor_type, "medium")
        
        # Confidence-based adjustment
        if confidence < 0.7:
            return "uncertain"
        
        # Combined severity
        if size_severity == "high" or type_severity == "high":
            return "high"
        elif size_severity == "medium" or type_severity == "medium":
            return "medium"
        else:
            return "low"
    
    def _generate_recommendations(self, tumor_detected: bool, tumor_type: str, 
                                severity_level: str) -> List[str]:
        """Generate clinical recommendations"""
        recommendations = []
        
        if not tumor_detected:
            recommendations.extend([
                "No tumor detected in current scan",
                "Continue regular monitoring as per clinical guidelines",
                "Consider follow-up scan in 6-12 months if symptoms persist"
            ])
        else:
            recommendations.append(f"{tumor_type} detected - requires immediate medical attention")
            
            if severity_level == "high":
                recommendations.extend([
                    "Urgent neurosurgical consultation required",
                    "Consider immediate hospitalization",
                    "Comprehensive neurological evaluation needed",
                    "Discuss treatment options including surgery, radiation, or chemotherapy"
                ])
            elif severity_level == "medium":
                recommendations.extend([
                    "Neurosurgical consultation within 1-2 weeks",
                    "Additional imaging studies may be required",
                    "Monitor for neurological symptoms",
                    "Discuss treatment planning with oncology team"
                ])
            else:
                recommendations.extend([
                    "Follow-up with neurologist within 2-4 weeks",
                    "Monitor for symptom progression",
                    "Consider repeat imaging in 3-6 months",
                    "Discuss observation vs. intervention options"
                ])
            
            # Type-specific recommendations
            if tumor_type == "Glioma":
                recommendations.append("Genetic testing for treatment planning may be beneficial")
            elif tumor_type == "Pituitary Tumor":
                recommendations.append("Endocrine evaluation recommended")
                recommendations.append("Visual field testing advised")
        
        return recommendations
    
    def generate_report(self, prediction: TumorPrediction) -> Dict:
        """Generate comprehensive diagnostic report"""
        return {
            "patient_information": {
                "patient_id": prediction.patient_id,
                "scan_id": prediction.scan_id,
                "analysis_date": prediction.timestamp
            },
            "findings": {
                "tumor_detected": prediction.tumor_detected,
                "tumor_type": prediction.tumor_type,
                "confidence_level": f"{prediction.confidence:.2%}",
                "location": prediction.tumor_location,
                "estimated_size_mm": prediction.tumor_size_mm,
                "severity": prediction.severity_level
            },
            "clinical_recommendations": prediction.recommendations,
            "technical_details": {
                "model_version": prediction.model_version,
                "processing_time_seconds": prediction.processing_time,
                "analysis_method": "Deep Learning CNN with EfficientNet backbone"
            },
            "disclaimer": [
                "This AI analysis is for diagnostic assistance only",
                "Results should be interpreted by qualified medical professionals",
                "Clinical correlation and additional testing may be required",
                "Not intended as a substitute for professional medical judgment"
            ]
        }
