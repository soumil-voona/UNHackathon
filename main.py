import torch
import torch.nn as nn
import torch.optim as optim
import torchaudio
import torchaudio.transforms as T
import numpy as np
from torch.utils.data import Dataset, DataLoader
import os
from pathlib import Path
import librosa
import warnings
warnings.filterwarnings('ignore')

# Disease classifications based on provided datasets:
# 1. vbookshelf/respiratory-sound-database: Healthy, Asthma, Bronchitis, URTI (Cold Cough)
# 2. andrewmvd/covid19-cough-audio-classification: COVID-19, Healthy, Other
# 3. ruchikashirsath/tb-audio: Tuberculosis, Pneumonia, and other respiratory conditions

DISEASE_CLASSES = {
    0: "Healthy",           # From all datasets
    1: "Cold Cough",        # Mapped from URTI (Respiratory Sound Database)
    2: "COVID-19",          # From COVID-19 Cough Classification dataset
    3: "Asthma",            # From Respiratory Sound Database
    4: "Bronchitis",        # From Respiratory Sound Database
    5: "Tuberculosis",      # From TB Audio dataset
    6: "Pneumonia"          # From TB Audio dataset
}

NUM_CLASSES = len(DISEASE_CLASSES)
SAMPLE_RATE = 16000
N_MELS = 64
N_FFT = 400
HOP_LENGTH = 160


class CoughAudioDataset(Dataset):
    """
    Custom Dataset for loading and processing cough audio files.
    Expects audio files organized in folders by disease class.
    """
    def __init__(self, audio_dir, sample_rate=SAMPLE_RATE, n_mels=N_MELS):
        self.audio_dir = Path(audio_dir)
        self.sample_rate = sample_rate
        self.n_mels = n_mels
        self.audio_files = []
        self.labels = []
        
        # Load audio file paths and labels
        for class_idx, class_name in DISEASE_CLASSES.items():
            class_dir = self.audio_dir / class_name
            if class_dir.exists():
                audio_files = list(class_dir.glob("*.wav")) + list(class_dir.glob("*.mp3"))
                for audio_file in audio_files:
                    self.audio_files.append(str(audio_file))
                    self.labels.append(class_idx)
        
        # Mel-spectrogram transform
        self.mel_transform = T.MelSpectrogram(
            sample_rate=sample_rate,
            n_mels=n_mels,
            n_fft=N_FFT,
            hop_length=HOP_LENGTH
        )
        self.amplitude_to_db = T.AmplitudeToDB()
        
    def __len__(self):
        return len(self.audio_files)
    
    def __getitem__(self, idx):
        audio_path = self.audio_files[idx]
        label = self.labels[idx]
        
        # Load audio
        try:
            waveform, sr = torchaudio.load(audio_path)
            
            # Resample if necessary
            if sr != self.sample_rate:
                resampler = T.Resample(sr, self.sample_rate)
                waveform = resampler(waveform)
            
            # Normalize duration (3 seconds)
            target_length = self.sample_rate * 3
            if waveform.shape[1] < target_length:
                waveform = torch.nn.functional.pad(waveform, (0, target_length - waveform.shape[1]))
            else:
                waveform = waveform[:, :target_length]
            
            # Convert to mel-spectrogram
            mel_spec = self.mel_transform(waveform)
            mel_spec = self.amplitude_to_db(mel_spec)
            
            # Normalize
            mel_spec = (mel_spec - mel_spec.mean()) / (mel_spec.std() + 1e-5)
            
            return mel_spec, label
        except Exception as e:
            print(f"Error loading {audio_path}: {e}")
            # Return a dummy zero tensor if loading fails
            return torch.zeros(1, self.n_mels, 282), 0


class CoughClassifier(nn.Module):
    """
    CNN-based classifier for cough audio classification.
    Uses mel-spectrograms as input features.
    """
    def __init__(self, num_classes=NUM_CLASSES):
        super(CoughClassifier, self).__init__()
        
        # Convolutional blocks
        self.conv1 = nn.Conv2d(1, 32, kernel_size=3, stride=1, padding=1)
        self.bn1 = nn.BatchNorm2d(32)
        self.pool1 = nn.MaxPool2d(2, 2)
        
        self.conv2 = nn.Conv2d(32, 64, kernel_size=3, stride=1, padding=1)
        self.bn2 = nn.BatchNorm2d(64)
        self.pool2 = nn.MaxPool2d(2, 2)
        
        self.conv3 = nn.Conv2d(64, 128, kernel_size=3, stride=1, padding=1)
        self.bn3 = nn.BatchNorm2d(128)
        self.pool3 = nn.MaxPool2d(2, 2)
        
        self.conv4 = nn.Conv2d(128, 256, kernel_size=3, stride=1, padding=1)
        self.bn4 = nn.BatchNorm2d(256)
        self.pool4 = nn.MaxPool2d(2, 2)
        
        # Adaptive average pooling for variable input sizes
        self.adaptive_pool = nn.AdaptiveAvgPool2d((1, 1))
        
        # Fully connected layers
        self.fc1 = nn.Linear(256, 128)
        self.dropout1 = nn.Dropout(0.5)
        self.fc2 = nn.Linear(128, 64)
        self.dropout2 = nn.Dropout(0.3)
        self.fc3 = nn.Linear(64, num_classes)
        
        self.relu = nn.ReLU()
    
    def forward(self, x):
        # Convolutional layers with batch normalization and pooling
        x = self.relu(self.bn1(self.conv1(x)))
        x = self.pool1(x)
        
        x = self.relu(self.bn2(self.conv2(x)))
        x = self.pool2(x)
        
        x = self.relu(self.bn3(self.conv3(x)))
        x = self.pool3(x)
        
        x = self.relu(self.bn4(self.conv4(x)))
        x = self.pool4(x)
        
        # Adaptive pooling
        x = self.adaptive_pool(x)
        x = x.view(x.size(0), -1)
        
        # Fully connected layers
        x = self.relu(self.fc1(x))
        x = self.dropout1(x)
        x = self.relu(self.fc2(x))
        x = self.dropout2(x)
        x = self.fc3(x)
        
        return x


class CoughClassifierTrainer:
    """
    Trainer class for the cough classifier model.
    Handles training, validation, and inference.
    """
    def __init__(self, model, device='cpu', learning_rate=0.001):
        self.model = model.to(device)
        self.device = device
        self.optimizer = optim.Adam(model.parameters(), lr=learning_rate)
        self.criterion = nn.CrossEntropyLoss()
        self.scheduler = optim.lr_scheduler.ReduceLROnPlateau(
            self.optimizer, mode='min', factor=0.5, patience=5, verbose=True
        )
    
    def train_epoch(self, train_loader):
        """Train for one epoch"""
        self.model.train()
        total_loss = 0.0
        correct = 0
        total = 0
        
        for spectrograms, labels in train_loader:
            spectrograms = spectrograms.to(self.device)
            labels = labels.to(self.device)
            
            self.optimizer.zero_grad()
            outputs = self.model(spectrograms)
            loss = self.criterion(outputs, labels)
            loss.backward()
            self.optimizer.step()
            
            total_loss += loss.item()
            _, predicted = torch.max(outputs.data, 1)
            total += labels.size(0)
            correct += (predicted == labels).sum().item()
        
        avg_loss = total_loss / len(train_loader)
        accuracy = 100 * correct / total
        return avg_loss, accuracy
    
    def validate(self, val_loader):
        """Validate the model"""
        self.model.eval()
        total_loss = 0.0
        correct = 0
        total = 0
        
        with torch.no_grad():
            for spectrograms, labels in val_loader:
                spectrograms = spectrograms.to(self.device)
                labels = labels.to(self.device)
                
                outputs = self.model(spectrograms)
                loss = self.criterion(outputs, labels)
                
                total_loss += loss.item()
                _, predicted = torch.max(outputs.data, 1)
                total += labels.size(0)
                correct += (predicted == labels).sum().item()
        
        avg_loss = total_loss / len(val_loader)
        accuracy = 100 * correct / total
        return avg_loss, accuracy
    
    def train(self, train_loader, val_loader, epochs=50):
        """Train the model for multiple epochs"""
        best_val_loss = float('inf')
        patience = 10
        patience_counter = 0
        
        print("Starting training...")
        for epoch in range(epochs):
            train_loss, train_acc = self.train_epoch(train_loader)
            val_loss, val_acc = self.validate(val_loader)
            
            print(f"Epoch {epoch+1}/{epochs}")
            print(f"  Train Loss: {train_loss:.4f}, Train Acc: {train_acc:.2f}%")
            print(f"  Val Loss: {val_loss:.4f}, Val Acc: {val_acc:.2f}%")
            
            self.scheduler.step(val_loss)
            
            if val_loss < best_val_loss:
                best_val_loss = val_loss
                patience_counter = 0
                self.save_model("best_cough_classifier.pt")
            else:
                patience_counter += 1
                if patience_counter >= patience:
                    print(f"Early stopping at epoch {epoch+1}")
                    break
    
    def predict(self, audio_path):
        """Predict the disease class for a given audio file"""
        self.model.eval()
        
        # Load and process audio
        waveform, sr = torchaudio.load(audio_path)
        
        if sr != SAMPLE_RATE:
            resampler = T.Resample(sr, SAMPLE_RATE)
            waveform = resampler(waveform)
        
        # Normalize duration
        target_length = SAMPLE_RATE * 3
        if waveform.shape[1] < target_length:
            waveform = torch.nn.functional.pad(waveform, (0, target_length - waveform.shape[1]))
        else:
            waveform = waveform[:, :target_length]
        
        # Convert to mel-spectrogram
        mel_transform = T.MelSpectrogram(
            sample_rate=SAMPLE_RATE,
            n_mels=N_MELS,
            n_fft=N_FFT,
            hop_length=HOP_LENGTH
        )
        amplitude_to_db = T.AmplitudeToDB()
        
        mel_spec = mel_transform(waveform)
        mel_spec = amplitude_to_db(mel_spec)
        mel_spec = (mel_spec - mel_spec.mean()) / (mel_spec.std() + 1e-5)
        mel_spec = mel_spec.unsqueeze(0).to(self.device)
        
        with torch.no_grad():
            output = self.model(mel_spec)
            probabilities = torch.softmax(output, dim=1)
            predicted_class = torch.argmax(output, dim=1).item()
            confidence = probabilities[0, predicted_class].item()
        
        return DISEASE_CLASSES[predicted_class], confidence, {
            DISEASE_CLASSES[i]: probabilities[0, i].item() for i in range(NUM_CLASSES)
        }
    
    def save_model(self, path):
        """Save the model to disk"""
        torch.save(self.model.state_dict(), path)
        print(f"Model saved to {path}")
    
    def load_model(self, path):
        """Load the model from disk"""
        self.model.load_state_dict(torch.load(path, map_location=self.device))
        print(f"Model loaded from {path}")


def main():
    """
    Main function demonstrating model usage.
    """
    # Check if GPU is available
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    print(f"Using device: {device}")
    
    # Initialize model and trainer
    model = CoughClassifier(num_classes=NUM_CLASSES)
    trainer = CoughClassifierTrainer(model, device=device, learning_rate=0.001)
    
    # Example: If you have training data in the following structure:
    # audio_data/
    #   ├── Healthy/
    #   ├── Cold Cough/
    #   ├── COVID-19/
    #   ├── Asthma/
    #   ├── Bronchitis/
    #   └── Whooping Cough/
    
    audio_dir = "audio_data"
    
    if os.path.exists(audio_dir):
        # Create dataset and dataloaders
        dataset = CoughAudioDataset(audio_dir)
        train_size = int(0.8 * len(dataset))
        val_size = len(dataset) - train_size
        train_dataset, val_dataset = torch.utils.data.random_split(
            dataset, [train_size, val_size]
        )
        
        train_loader = DataLoader(train_dataset, batch_size=16, shuffle=True)
        val_loader = DataLoader(val_dataset, batch_size=16, shuffle=False)
        
        # Train the model
        trainer.train(train_loader, val_loader, epochs=50)
        
        # Save the trained model
        trainer.save_model("cough_classifier.pt")
    else:
        print(f"Audio data directory '{audio_dir}' not found.")
        print("To train the model, please organize your audio files in the following structure:")
        print("audio_data/")
        for class_name in DISEASE_CLASSES.values():
            print(f"  ├── {class_name}/")
        print("      └── *.wav (or *.mp3)")
    
    # Example: Make a prediction on a single audio file
    # Uncomment the following lines if you have a sample audio file
    # trainer.load_model("cough_classifier.pt")
    # disease, confidence, all_probs = trainer.predict("path/to/your/audio.wav")
    # print(f"\nPredicted Disease: {disease}")
    # print(f"Confidence: {confidence:.2%}")
    # print(f"All Probabilities: {all_probs}")


if __name__ == "__main__":
    main()