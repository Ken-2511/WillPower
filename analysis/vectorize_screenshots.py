"""
Vectorize all screenCap images using CLIP (clip-ViT-B-32).
Saves embeddings as .npz files in analysis/embeddings/screen/
"""

import os
import glob
import numpy as np
from pathlib import Path
from PIL import Image
from sentence_transformers import SentenceTransformer

SCRIPT_DIR = Path(__file__).parent
SCREENCAP_DIR = SCRIPT_DIR / "screenCap"
OUTPUT_DIR = SCRIPT_DIR / "embeddings" / "screen"
BATCH_SIZE = 64
MODEL_NAME = "clip-ViT-B-32"


def collect_images(screencap_dir: Path) -> list[str]:
    """Recursively collect all .png files from screenCap subdirectories."""
    paths = sorted(glob.glob(str(screencap_dir / "**" / "*.png"), recursive=True))
    print(f"Found {len(paths)} images in {screencap_dir}")
    return paths


def load_existing(output_dir: Path) -> set[str]:
    """Load paths already processed from existing .npz files."""
    already_done = set()
    if not output_dir.exists():
        return already_done
    for npz_file in output_dir.glob("*.npz"):
        data = np.load(npz_file, allow_pickle=True)
        already_done.update(data["paths"].tolist())
    return already_done


def encode_batch(model, image_paths: list[str]) -> tuple[np.ndarray, list[str]]:
    """Load and encode a batch of images. Skips images that fail to load."""
    images = []
    valid_paths = []
    for p in image_paths:
        try:
            img = Image.open(p).convert("RGB")
            images.append(img)
            valid_paths.append(p)
        except Exception as e:
            print(f"  Skip {p}: {e}")
    if not images:
        return np.array([]), []
    embeddings = model.encode(images, batch_size=BATCH_SIZE, show_progress_bar=False)
    return embeddings, valid_paths


def main():
    output_dir = OUTPUT_DIR
    output_dir.mkdir(parents=True, exist_ok=True)

    # Collect all image paths
    all_paths = collect_images(SCREENCAP_DIR)
    if not all_paths:
        print("No images found. Exiting.")
        return

    # Check what's already been processed
    already_done = load_existing(output_dir)
    new_paths = [p for p in all_paths if p not in already_done]
    print(f"Already processed: {len(already_done)}, New: {len(new_paths)}")

    if not new_paths:
        print("Nothing new to process.")
        return

    # Load model
    print(f"Loading model: {MODEL_NAME}")
    model = SentenceTransformer(MODEL_NAME)
    print("Model loaded.")

    # Process in batches, save per date folder
    # Group by date subfolder for organized output
    from collections import defaultdict
    by_date = defaultdict(list)
    for p in new_paths:
        # Extract date from path: .../screenCap/2026-02-11/filename.png
        date = Path(p).parent.name
        by_date[date].append(p)

    for date, paths in sorted(by_date.items()):
        print(f"\nProcessing {date}: {len(paths)} images")
        all_embeddings = []
        all_valid_paths = []

        for i in range(0, len(paths), BATCH_SIZE):
            batch = paths[i : i + BATCH_SIZE]
            print(f"  Batch {i // BATCH_SIZE + 1}/{(len(paths) - 1) // BATCH_SIZE + 1} ({len(batch)} images)")
            emb, valid = encode_batch(model, batch)
            if len(valid) > 0:
                all_embeddings.append(emb)
                all_valid_paths.extend(valid)

        if all_valid_paths:
            embeddings = np.vstack(all_embeddings)
            out_file = output_dir / f"{date}.npz"

            # If file exists, merge with existing data
            if out_file.exists():
                existing = np.load(out_file, allow_pickle=True)
                embeddings = np.vstack([existing["embeddings"], embeddings])
                all_valid_paths = existing["paths"].tolist() + all_valid_paths

            np.savez_compressed(
                out_file,
                embeddings=embeddings,
                paths=np.array(all_valid_paths),
            )
            print(f"  Saved {len(all_valid_paths)} embeddings to {out_file}")

    print("\nDone!")


if __name__ == "__main__":
    main()
