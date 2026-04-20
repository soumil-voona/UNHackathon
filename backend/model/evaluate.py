"""
Evaluation and metrics utilities for the Cough Classifier model.
Provides functions for model evaluation, confusion matrices, and performance analysis.
"""

import torch
import numpy as np
from sklearn.metrics import (
    confusion_matrix, classification_report, accuracy_score,
    precision_score, recall_score, f1_score, roc_auc_score,
    roc_curve, auc
)
from pathlib import Path
import matplotlib.pyplot as plt
import seaborn as sns
from torch.utils.data import DataLoader
from backend.main import CoughClassifier, CoughClassifierTrainer, CoughAudioDataset, DISEASE_CLASSES, NUM_CLASSES


def evaluate_model_on_dataset(model, test_loader, device):
    """
    Evaluate model on a test dataset.
    
    Args:
        model: The model to evaluate
        test_loader: DataLoader with test data
        device: Device to use
        
    Returns:
        dict: Dictionary with evaluation metrics
    """
    model.eval()
    all_preds = []
    all_labels = []
    all_probs = []
    
    with torch.no_grad():
        for spectrograms, labels in test_loader:
            spectrograms = spectrograms.to(device)
            labels = labels.to(device)
            
            outputs = model(spectrograms)
            probs = torch.softmax(outputs, dim=1)
            _, predicted = torch.max(outputs, 1)
            
            all_preds.extend(predicted.cpu().numpy())
            all_labels.extend(labels.cpu().numpy())
            all_probs.extend(probs.cpu().numpy())
    
    all_preds = np.array(all_preds)
    all_labels = np.array(all_labels)
    all_probs = np.array(all_probs)
    
    # Calculate metrics
    accuracy = accuracy_score(all_labels, all_preds)
    precision = precision_score(all_labels, all_preds, average='weighted', zero_division=0)
    recall = recall_score(all_labels, all_preds, average='weighted', zero_division=0)
    f1 = f1_score(all_labels, all_preds, average='weighted', zero_division=0)
    
    return {
        'accuracy': accuracy,
        'precision': precision,
        'recall': recall,
        'f1': f1,
        'predictions': all_preds,
        'labels': all_labels,
        'probabilities': all_probs,
        'confusion_matrix': confusion_matrix(all_labels, all_preds),
        'classification_report': classification_report(all_labels, all_preds, target_names=list(DISEASE_CLASSES.values()))
    }


def plot_confusion_matrix(cm, save_path='confusion_matrix.png'):
    """
    Plot and save confusion matrix.
    
    Args:
        cm: Confusion matrix (numpy array)
        save_path: Path to save the figure
    """
    plt.figure(figsize=(10, 8))
    sns.heatmap(
        cm,
        annot=True,
        fmt='d',
        cmap='Blues',
        xticklabels=list(DISEASE_CLASSES.values()),
        yticklabels=list(DISEASE_CLASSES.values()),
        cbar_kws={'label': 'Count'}
    )
    plt.title('Confusion Matrix')
    plt.ylabel('True Label')
    plt.xlabel('Predicted Label')
    plt.xticks(rotation=45, ha='right')
    plt.yticks(rotation=0)
    plt.tight_layout()
    plt.savefig(save_path, dpi=300, bbox_inches='tight')
    print(f"Confusion matrix saved to {save_path}")
    plt.close()


def plot_class_distribution(predictions, true_labels, save_path='class_distribution.png'):
    """
    Plot class distribution of predictions vs true labels.
    
    Args:
        predictions: Model predictions
        true_labels: True labels
        save_path: Path to save the figure
    """
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(12, 5))
    
    # True labels distribution
    unique, counts = np.unique(true_labels, return_counts=True)
    ax1.bar([DISEASE_CLASSES[i] for i in unique], counts)
    ax1.set_title('True Label Distribution')
    ax1.set_ylabel('Count')
    ax1.tick_params(axis='x', rotation=45)
    
    # Predictions distribution
    unique, counts = np.unique(predictions, return_counts=True)
    ax2.bar([DISEASE_CLASSES[i] for i in unique], counts)
    ax2.set_title('Predicted Label Distribution')
    ax2.set_ylabel('Count')
    ax2.tick_params(axis='x', rotation=45)
    
    plt.tight_layout()
    plt.savefig(save_path, dpi=300, bbox_inches='tight')
    print(f"Class distribution plot saved to {save_path}")
    plt.close()


def evaluate_on_test_directory(model_path, test_directory, device='auto'):
    """
    Evaluate model on all audio files in a test directory.
    
    Args:
        model_path: Path to trained model
        test_directory: Path to test audio directory (organized by class)
        device: Device to use ('cuda', 'cpu', or 'auto')
    """
    if device == 'auto':
        device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    else:
        device = torch.device(device)
    
    print(f"Evaluating model on test directory: {test_directory}")
    print(f"Device: {device}\n")
    
    # Load model
    model = CoughClassifier(num_classes=NUM_CLASSES)
    trainer = CoughClassifierTrainer(model, device=device)
    
    if Path(model_path).exists():
        trainer.load_model(model_path)
    else:
        print(f"Error: Model file {model_path} not found")
        return
    
    # Load test dataset
    test_dataset = CoughAudioDataset(test_directory)
    test_loader = DataLoader(test_dataset, batch_size=16, shuffle=False)
    
    print(f"Test samples: {len(test_dataset)}\n")
    
    # Evaluate
    metrics = evaluate_model_on_dataset(model, test_loader, device)
    
    # Print results
    print("="*60)
    print("EVALUATION RESULTS")
    print("="*60)
    print(f"Accuracy:  {metrics['accuracy']:.4f}")
    print(f"Precision: {metrics['precision']:.4f}")
    print(f"Recall:    {metrics['recall']:.4f}")
    print(f"F1 Score:  {metrics['f1']:.4f}")
    print("\n" + "="*60)
    print("CLASSIFICATION REPORT")
    print("="*60)
    print(metrics['classification_report'])
    
    # Save visualizations
    plot_confusion_matrix(metrics['confusion_matrix'])
    plot_class_distribution(metrics['predictions'], metrics['labels'])
    
    return metrics


def per_class_metrics(predictions, true_labels):
    """
    Calculate per-class metrics.
    
    Args:
        predictions: Model predictions
        true_labels: True labels
        
    Returns:
        dict: Per-class metrics
    """
    per_class = {}
    
    for class_idx in range(NUM_CLASSES):
        class_name = DISEASE_CLASSES[class_idx]
        
        mask = true_labels == class_idx
        if mask.sum() == 0:
            continue
        
        tp = ((predictions == class_idx) & (true_labels == class_idx)).sum()
        fp = ((predictions == class_idx) & (true_labels != class_idx)).sum()
        fn = ((predictions != class_idx) & (true_labels == class_idx)).sum()
        
        precision = tp / (tp + fp) if (tp + fp) > 0 else 0
        recall = tp / (tp + fn) if (tp + fn) > 0 else 0
        f1 = 2 * (precision * recall) / (precision + recall) if (precision + recall) > 0 else 0
        
        per_class[class_name] = {
            'precision': precision,
            'recall': recall,
            'f1': f1,
            'tp': int(tp),
            'fp': int(fp),
            'fn': int(fn)
        }
    
    return per_class


def plot_per_class_performance(predictions, true_labels, save_path='per_class_performance.png'):
    """
    Plot per-class performance metrics.
    
    Args:
        predictions: Model predictions
        true_labels: True labels
        save_path: Path to save the figure
    """
    metrics = per_class_metrics(predictions, true_labels)
    
    classes = list(metrics.keys())
    precisions = [metrics[c]['precision'] for c in classes]
    recalls = [metrics[c]['recall'] for c in classes]
    f1s = [metrics[c]['f1'] for c in classes]
    
    x = np.arange(len(classes))
    width = 0.25
    
    fig, ax = plt.subplots(figsize=(12, 6))
    ax.bar(x - width, precisions, width, label='Precision')
    ax.bar(x, recalls, width, label='Recall')
    ax.bar(x + width, f1s, width, label='F1 Score')
    
    ax.set_xlabel('Disease Class')
    ax.set_ylabel('Score')
    ax.set_title('Per-Class Performance Metrics')
    ax.set_xticks(x)
    ax.set_xticklabels(classes, rotation=45, ha='right')
    ax.legend()
    ax.set_ylim([0, 1.1])
    ax.grid(axis='y', alpha=0.3)
    
    plt.tight_layout()
    plt.savefig(save_path, dpi=300, bbox_inches='tight')
    print(f"Per-class performance plot saved to {save_path}")
    plt.close()


if __name__ == "__main__":
    # Example usage
    # Evaluate on test directory
    # metrics = evaluate_on_test_directory(
    #     model_path="cough_classifier.pt",
    #     test_directory="audio_data",
    #     device='auto'
    # )
    
    # Per-class metrics
    # per_class = per_class_metrics(metrics['predictions'], metrics['labels'])
    # for class_name, metrics_dict in per_class.items():
    #     print(f"\n{class_name}:")
    #     print(f"  Precision: {metrics_dict['precision']:.4f}")
    #     print(f"  Recall: {metrics_dict['recall']:.4f}")
    #     print(f"  F1 Score: {metrics_dict['f1']:.4f}")
    
    print("Evaluation utilities ready. Import this module to use evaluation functions.")
