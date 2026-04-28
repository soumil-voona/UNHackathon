import torch
import torch.nn as nn
import torch.optim as optim
import torchaudio
import torchaudio.transforms as T
import numpy as np
from torch.utils.data import Dataset, DataLoader, Subset
import os
from pathlib import Path
import librosa
import random
import shutil
import subprocess
import hashlib
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
TRAIN_AUDIO_EXTENSIONS = ("*.wav", "*.webm")


def resolve_ffmpeg_binary():
    """Find an ffmpeg binary across common PATH/Homebrew locations."""
    candidates = []

    path_bin = shutil.which("ffmpeg")
    if path_bin:
        candidates.append(Path(path_bin))

    for static_path in [
        Path("/opt/homebrew/bin/ffmpeg"),
        Path("/usr/local/bin/ffmpeg"),
    ]:
        if static_path.exists():
            candidates.append(static_path)

    try:
        brew_prefix = subprocess.run(
            ["brew", "--prefix", "ffmpeg"],
            capture_output=True,
            text=True,
            timeout=3,
        )
        if brew_prefix.returncode == 0:
            brew_bin = Path(brew_prefix.stdout.strip()) / "bin" / "ffmpeg"
            if brew_bin.exists():
                candidates.append(brew_bin)
    except Exception:
        pass

    for cellar_root in [Path("/opt/homebrew/Cellar/ffmpeg"), Path("/usr/local/Cellar/ffmpeg")]:
        if cellar_root.exists():
            cellar_bins = sorted(cellar_root.glob("*/bin/ffmpeg"), reverse=True)
            candidates.extend(cellar_bins)

    for candidate in candidates:
        if candidate.exists() and os.access(candidate, os.X_OK):
            return str(candidate)

    # Fallback: Python-packaged ffmpeg binary (imageio-ffmpeg).
    try:
        import imageio_ffmpeg

        bundled = Path(imageio_ffmpeg.get_ffmpeg_exe())
        if bundled.exists() and os.access(bundled, os.X_OK):
            return str(bundled)
    except Exception:
        pass

    return None


def extract_labels_from_dataset(dataset):
    """Extract integer class labels from a Dataset or Subset."""
    if hasattr(dataset, "labels"):
        return [int(label) for label in dataset.labels]

    if isinstance(dataset, Subset):
        base_dataset = dataset.dataset
        if hasattr(base_dataset, "labels"):
            return [int(base_dataset.labels[i]) for i in dataset.indices]

    labels = []
    for _, label in dataset:
        labels.append(int(label))
    return labels


def compute_class_weights(labels, num_classes=NUM_CLASSES):
    """Compute stable effective-number class weights for imbalanced learning."""
    if not labels:
        return torch.ones(num_classes, dtype=torch.float32)

    counts = np.bincount(labels, minlength=num_classes).astype(np.float32)
    nonzero = counts > 0
    weights = np.zeros(num_classes, dtype=np.float32)

    # Class-balanced weighting from effective number of samples.
    beta = 0.999
    effective_num = 1.0 - np.power(beta, counts[nonzero])
    weights_nonzero = (1.0 - beta) / np.maximum(effective_num, 1e-8)

    # Normalize observed-class weights to mean 1.0 and clamp extremes.
    weights_nonzero = weights_nonzero / np.mean(weights_nonzero)
    weights_nonzero = np.clip(weights_nonzero, 0.25, 6.0)
    weights[nonzero] = weights_nonzero

    return torch.tensor(weights, dtype=torch.float32)


class FocalLoss(nn.Module):
    """Multi-class focal loss with optional class weighting."""

    def __init__(self, weight=None, gamma=2.0):
        super().__init__()
        self.weight = weight
        self.gamma = gamma

    def forward(self, logits, targets):
        ce = nn.functional.cross_entropy(logits, targets, reduction="none", weight=self.weight)
        pt = torch.exp(-ce)
        focal = ((1 - pt) ** self.gamma) * ce
        return focal.mean()


class CoughAudioDataset(Dataset):
    """
    Custom Dataset for loading and processing cough audio files.
    Expects audio files organized in folders by disease class.
    """
    def __init__(self, audio_dir, sample_rate=SAMPLE_RATE, n_mels=N_MELS, max_samples=None):
        self.audio_dir = Path(audio_dir)
        self.sample_rate = sample_rate
        self.n_mels = n_mels
        self.audio_files = []
        self.labels = []
        self.ffmpeg_bin = resolve_ffmpeg_binary()
        self.converted_cache_dir = self.audio_dir / ".converted_webm"
        self.converted_cache_dir.mkdir(exist_ok=True)
        self._ffmpeg_warning_shown = False
        
        # Load audio file paths and labels using stable training formats.
        for class_idx, class_name in DISEASE_CLASSES.items():
            class_dir = self.audio_dir / class_name
            if class_dir.exists():
                audio_files = []
                for pattern in TRAIN_AUDIO_EXTENSIONS:
                    audio_files.extend(class_dir.glob(pattern))
                for audio_file in audio_files:
                    prepared_file = self._prepare_training_file(audio_file)
                    if prepared_file is not None:
                        self.audio_files.append(str(prepared_file))
                        self.labels.append(class_idx)
        
        # Limit dataset size if max_samples is specified.
        # Shuffle before truncation to avoid class-order bias (e.g., all Healthy samples).
        if max_samples and len(self.audio_files) > max_samples:
            indices = list(range(len(self.audio_files)))
            random.Random(42).shuffle(indices)
            selected = indices[:max_samples]
            self.audio_files = [self.audio_files[i] for i in selected]
            self.labels = [self.labels[i] for i in selected]

        # Remove files that cannot be decoded by either torchaudio or librosa.
        valid_files = []
        valid_labels = []
        skipped_count = 0
        for audio_file, label in zip(self.audio_files, self.labels):
            try:
                torchaudio.load(audio_file)
                valid_files.append(audio_file)
                valid_labels.append(label)
                continue
            except Exception:
                pass

            try:
                librosa.load(audio_file, sr=None, mono=True)
                valid_files.append(audio_file)
                valid_labels.append(label)
            except Exception:
                skipped_count += 1

        self.audio_files = valid_files
        self.labels = valid_labels
        if skipped_count:
            print(f"Skipped {skipped_count} unreadable training files")

        # Mel-spectrogram transform
        self.mel_transform = T.MelSpectrogram(
            sample_rate=sample_rate,
            n_mels=n_mels,
            n_fft=N_FFT,
            hop_length=HOP_LENGTH
        )
        self.amplitude_to_db = T.AmplitudeToDB()
        self.target_length = self.sample_rate * 3
        # Keep a consistent fallback shape for unreadable files.
        self.fallback_time_bins = self.mel_transform(torch.zeros(1, self.target_length)).shape[-1]

    def _prepare_training_file(self, audio_file: Path):
        """Convert WebM files to cached WAV for stable training decode."""
        if audio_file.suffix.lower() != ".webm":
            return audio_file

        if not self.ffmpeg_bin:
            if not self._ffmpeg_warning_shown:
                print("Warning: ffmpeg not found; WebM files may be skipped if decoders cannot read them.")
                self._ffmpeg_warning_shown = True
            return audio_file

        digest = hashlib.md5(str(audio_file).encode("utf-8")).hexdigest()[:12]
        cached_wav = self.converted_cache_dir / f"{audio_file.stem}_{digest}.wav"
        if cached_wav.exists():
            return cached_wav

        try:
            result = subprocess.run(
                [
                    self.ffmpeg_bin,
                    "-i",
                    str(audio_file),
                    "-acodec",
                    "pcm_s16le",
                    "-ar",
                    str(self.sample_rate),
                    str(cached_wav),
                    "-y",
                ],
                capture_output=True,
                text=True,
                timeout=30,
            )
            if result.returncode != 0:
                print(f"Warning: failed to convert {audio_file.name}; keeping original WebM.")
                return audio_file
            return cached_wav
        except Exception as exc:
            print(f"Warning: failed to convert {audio_file.name} ({exc}); keeping original WebM.")
            return audio_file

    def __len__(self):
        return len(self.audio_files)
    
    def __getitem__(self, idx):
        audio_path = self.audio_files[idx]
        label = self.labels[idx]
        
        # Load audio
        try:
            waveform, sr = torchaudio.load(audio_path)
        except Exception:
            # Fallback decoder for formats that torchaudio may not handle reliably.
            try:
                audio_data, sr = librosa.load(audio_path, sr=None, mono=True)
                waveform = torch.FloatTensor(audio_data).unsqueeze(0)
            except Exception as e:
                print(f"Error loading {audio_path}: {e}")
                return torch.zeros(1, self.n_mels, self.fallback_time_bins), label

        try:
            
            # Convert stereo/multi-channel to mono for consistent tensor shapes.
            if waveform.shape[0] > 1:
                waveform = waveform.mean(dim=0, keepdim=True)

            # Resample if necessary
            if sr != self.sample_rate:
                resampler = T.Resample(sr, self.sample_rate)
                waveform = resampler(waveform)
            
            # Normalize duration (3 seconds)
            if waveform.shape[1] < self.target_length:
                waveform = torch.nn.functional.pad(waveform, (0, self.target_length - waveform.shape[1]))
            else:
                waveform = waveform[:, :self.target_length]
            
            # Convert to mel-spectrogram
            mel_spec = self.mel_transform(waveform)
            mel_spec = self.amplitude_to_db(mel_spec)
            
            # Normalize
            mel_spec = (mel_spec - mel_spec.mean()) / (mel_spec.std() + 1e-5)
            
            return mel_spec, label
        except Exception as e:
            print(f"Error loading {audio_path}: {e}")
            # Return a dummy zero tensor if preprocessing fails.
            return torch.zeros(1, self.n_mels, self.fallback_time_bins), label


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
        self.class_weights = None
        
        # Cache transforms for faster inference
        self.mel_transform = T.MelSpectrogram(
            sample_rate=SAMPLE_RATE,
            n_mels=N_MELS,
            n_fft=N_FFT,
            hop_length=HOP_LENGTH
        )
        self.amplitude_to_db = T.AmplitudeToDB()
    
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

        train_labels = extract_labels_from_dataset(train_loader.dataset)
        self.class_weights = compute_class_weights(train_labels, NUM_CLASSES).to(self.device)
        self.criterion = FocalLoss(weight=self.class_weights, gamma=2.0)

        print("Class counts (train split):")
        counts = np.bincount(train_labels, minlength=NUM_CLASSES)
        for idx, class_name in DISEASE_CLASSES.items():
            print(f"  {class_name}: {int(counts[idx])}")
        print("Class weights:")
        for idx, class_name in DISEASE_CLASSES.items():
            print(f"  {class_name}: {self.class_weights[idx].item():.4f}")
        
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
        import time as timing_module
        import subprocess
        import tempfile
        import shutil
        from pathlib import Path as PathlibPath
        
        t0 = timing_module.time()
        
        # Verify file exists
        audio_file = PathlibPath(audio_path)
        if not audio_file.exists():
            raise FileNotFoundError(f"Audio file not found: {audio_path}")

        temp_wav_path = None
        suffix = audio_file.suffix.lower()
        if suffix not in {'.wav', '.webm'}:
            raise RuntimeError("Only WAV and WebM inputs are supported for prediction.")

        # Convert WebM to a temporary WAV file just for this inference call.
        if suffix == '.webm':
            ffmpeg_bin = shutil.which("ffmpeg")
            if not ffmpeg_bin:
                raise RuntimeError("WebM input requires ffmpeg to be available on PATH.")

            with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as tmp_file:
                temp_wav_path = PathlibPath(tmp_file.name)

            try:
                result = subprocess.run(
                    [ffmpeg_bin, '-i', str(audio_file), '-acodec', 'pcm_s16le', '-ar', str(SAMPLE_RATE), str(temp_wav_path), '-y'],
                    capture_output=True,
                    text=True,
                    timeout=20,
                )
                if result.returncode != 0:
                    raise RuntimeError(f"ffmpeg failed: {result.stderr.strip()}")
                audio_file = temp_wav_path
                audio_path = str(audio_file)
            except Exception:
                if temp_wav_path is not None and temp_wav_path.exists():
                    temp_wav_path.unlink(missing_ok=True)
                raise
        
        print(f"  Loading audio from: {audio_file.absolute()}")

        try:
            self.model.eval()

            # Load audio - prioritize torchaudio for speed
            try:
                print(f"  Loading audio with torchaudio...")
                waveform, sr = torchaudio.load(audio_path)
                print(f"  Loaded in {timing_module.time()-t0:.2f}s (sr={sr}Hz)")
            except Exception as e:
                print(f"  Torchaudio failed, trying librosa: {e}")
                try:
                    audio_data, sr = librosa.load(audio_path, sr=None, mono=False)
                    waveform = torch.FloatTensor(audio_data).unsqueeze(0) if audio_data.ndim == 1 else torch.FloatTensor(audio_data)
                    print(f"  Loaded in {timing_module.time()-t0:.2f}s (sr={sr}Hz)")
                except Exception as e2:
                    raise RuntimeError(f"Failed to load audio: {e2}")

            t1 = timing_module.time()

            # Convert to mono if stereo
            if waveform.shape[0] > 1:
                waveform = waveform.mean(dim=0, keepdim=True)

            # Resample if necessary
            if sr != SAMPLE_RATE:
                print(f"  Resampling from {sr}Hz to {SAMPLE_RATE}Hz...")
                resampler = T.Resample(sr, SAMPLE_RATE).to(self.device)
                waveform = waveform.to(self.device)
                waveform = resampler(waveform)
            else:
                waveform = waveform.to(self.device)

            # Normalize duration to 3 seconds
            target_length = SAMPLE_RATE * 3
            if waveform.shape[1] < target_length:
                waveform = torch.nn.functional.pad(waveform, (0, target_length - waveform.shape[1]))
            else:
                waveform = waveform[:, :target_length]

            print(f"  Audio prep in {timing_module.time()-t1:.2f}s")
            t2 = timing_module.time()

            # Convert to mel-spectrogram using cached transforms
            mel_spec = self.mel_transform(waveform)
            mel_spec = self.amplitude_to_db(mel_spec)
            mel_spec = (mel_spec - mel_spec.mean()) / (mel_spec.std() + 1e-5)
            mel_spec = mel_spec.unsqueeze(0)  # Add batch dimension

            print(f"  MelSpec in {timing_module.time()-t2:.2f}s")
            t3 = timing_module.time()

            with torch.no_grad():
                output = self.model(mel_spec)
                probabilities = torch.softmax(output, dim=1)
                predicted_class = torch.argmax(output, dim=1).item()
                confidence = probabilities[0, predicted_class].item()

            print(f"  Inference in {timing_module.time()-t3:.2f}s")

            return DISEASE_CLASSES[predicted_class], confidence, {
                DISEASE_CLASSES[i]: probabilities[0, i].item() for i in range(NUM_CLASSES)
            }
        finally:
            if temp_wav_path is not None and temp_wav_path.exists():
                temp_wav_path.unlink(missing_ok=True)
    
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