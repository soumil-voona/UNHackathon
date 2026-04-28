"""
Build a capped, class-balanced training folder from KaggleHub cache downloads.

This expects datasets.py to have downloaded:
- vbookshelf/respiratory-sound-database
- andrewmvd/covid19-cough-audio-classification
- ruchikashirsath/tb-audio
"""

import argparse
import csv
import random
import shutil
from collections import defaultdict
from pathlib import Path


DEFAULT_CACHE = Path.home() / ".cache" / "kagglehub" / "datasets"
RESPIRATORY_DIR = DEFAULT_CACHE / "vbookshelf" / "respiratory-sound-database" / "versions" / "2"
COVID_DIR = DEFAULT_CACHE / "andrewmvd" / "covid19-cough-audio-classification" / "versions" / "1"
TB_DIR = DEFAULT_CACHE / "ruchikashirsath" / "tb-audio" / "versions" / "1"

TARGET_CLASSES = [
    "Healthy",
    "Cold Cough",
    "COVID-19",
    "Asthma",
    "Bronchitis",
    "Tuberculosis",
    "Pneumonia",
]

RESPIRATORY_MAP = {
    "Healthy": "Healthy",
    "URTI": "Cold Cough",
    "Asthma": "Asthma",
    "Bronchitis": "Bronchitis",
    "COPD": "Bronchitis",
    "Bronchiectasis": "Bronchitis",
}

AUDIO_SUFFIXES = (".wav", ".webm")


def copy_capped(files_by_class, output_dir, max_per_class):
    rng = random.Random(42)
    output_dir = Path(output_dir)
    copied = defaultdict(int)

    for class_name in TARGET_CLASSES:
        class_dir = output_dir / class_name
        class_dir.mkdir(parents=True, exist_ok=True)

        files = list(files_by_class.get(class_name, []))
        rng.shuffle(files)
        if max_per_class > 0:
            files = files[:max_per_class]

        for source in files:
            source = Path(source)
            dest = class_dir / f"{source.parent.name}_{source.name}"
            try:
                shutil.copy2(source, dest)
                copied[class_name] += 1
            except OSError as exc:
                print(f"Skipped {source}: {exc}")

    return copied


def collect_respiratory(files_by_class):
    diagnosis_file = (
        RESPIRATORY_DIR
        / "Respiratory_Sound_Database"
        / "Respiratory_Sound_Database"
        / "patient_diagnosis.csv"
    )
    audio_dir = (
        RESPIRATORY_DIR
        / "Respiratory_Sound_Database"
        / "Respiratory_Sound_Database"
        / "audio_and_txt_files"
    )
    if not diagnosis_file.exists() or not audio_dir.exists():
        print("Respiratory dataset not found in KaggleHub cache")
        return

    patient_labels = {}
    with diagnosis_file.open(newline="") as f:
        for patient_id, diagnosis in csv.reader(f):
            class_name = RESPIRATORY_MAP.get(diagnosis)
            if class_name:
                patient_labels[patient_id] = class_name

    for audio_file in audio_dir.glob("*.wav"):
        patient_id = audio_file.name.split("_", 1)[0]
        class_name = patient_labels.get(patient_id)
        if class_name:
            files_by_class[class_name].append(audio_file)


def collect_covid(files_by_class, min_cough_detected):
    metadata_file = COVID_DIR / "metadata_compiled.csv"
    if not metadata_file.exists():
        print("COVID dataset metadata not found in KaggleHub cache")
        return

    with metadata_file.open(newline="") as f:
        for row in csv.DictReader(f):
            status = (row.get("status") or "").strip().lower()
            if status == "covid-19":
                class_name = "COVID-19"
            elif status == "healthy":
                class_name = "Healthy"
            else:
                continue

            try:
                cough_detected = float(row.get("cough_detected") or 0)
            except ValueError:
                cough_detected = 0
            if cough_detected < min_cough_detected:
                continue

            uuid = row.get("uuid")
            if not uuid:
                continue

            for suffix in AUDIO_SUFFIXES:
                audio_file = COVID_DIR / f"{uuid}{suffix}"
                if audio_file.exists():
                    files_by_class[class_name].append(audio_file)
                    break


def collect_tb(files_by_class):
    tb_root = TB_DIR / "Tuberculosis" / "raw_data"
    if not tb_root.exists():
        print("TB dataset not found in KaggleHub cache")
        return

    for audio_file in tb_root.rglob("*.wav"):
        files_by_class["Tuberculosis"].append(audio_file)


def main():
    parser = argparse.ArgumentParser(description="Build capped balanced audio_data from KaggleHub cache")
    parser.add_argument("--output-dir", default="audio_data_balanced")
    parser.add_argument("--max-per-class", type=int, default=200)
    parser.add_argument("--min-cough-detected", type=float, default=0.8)
    args = parser.parse_args()

    files_by_class = defaultdict(list)
    collect_respiratory(files_by_class)
    collect_covid(files_by_class, args.min_cough_detected)
    collect_tb(files_by_class)

    print("Available source files:")
    for class_name in TARGET_CLASSES:
        print(f"  {class_name}: {len(files_by_class[class_name])}")

    copied = copy_capped(files_by_class, args.output_dir, args.max_per_class)

    print(f"\nBuilt {args.output_dir}:")
    for class_name in TARGET_CLASSES:
        print(f"  {class_name}: {copied[class_name]}")


if __name__ == "__main__":
    main()
