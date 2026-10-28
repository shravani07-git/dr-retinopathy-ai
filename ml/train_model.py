"""Training starter for APTOS/EyePACS-style 5-class DR data.

Expected CSV columns:
- id_code : image filename without extension (or filename if you adjust load path)
- diagnosis : integer 0..4

Example:
python train_model.py --csv ./train.csv --images ./train_images --epochs 8 --output ../backend/model/dr_efficientnet_b0.pt
"""
import argparse
from pathlib import Path

import pandas as pd
import torch
from PIL import Image
from sklearn.model_selection import train_test_split
from torch import nn
from torch.utils.data import DataLoader, Dataset
from torchvision import models, transforms


class DRDataset(Dataset):
    def __init__(self, frame, image_dir, transform):
        self.frame = frame.reset_index(drop=True)
        self.image_dir = Path(image_dir)
        self.transform = transform

    def __len__(self):
        return len(self.frame)

    def __getitem__(self, idx):
        row = self.frame.iloc[idx]
        name = str(row["id_code"])
        candidates = [self.image_dir / name, self.image_dir / f"{name}.png", self.image_dir / f"{name}.jpg", self.image_dir / f"{name}.jpeg"]
        path = next((p for p in candidates if p.exists()), None)
        if path is None:
            raise FileNotFoundError(f"Image not found for {name}")
        image = Image.open(path).convert("RGB")
        return self.transform(image), int(row["diagnosis"])


def main(args):
    device = "cuda" if torch.cuda.is_available() else "cpu"
    df = pd.read_csv(args.csv)
    train_df, val_df = train_test_split(df, test_size=0.2, stratify=df["diagnosis"], random_state=42)

    train_tf = transforms.Compose([
        transforms.Resize((256, 256)),
        transforms.RandomResizedCrop(224, scale=(0.82, 1.0)),
        transforms.RandomHorizontalFlip(),
        transforms.RandomRotation(12),
        transforms.ColorJitter(brightness=0.1, contrast=0.1),
        transforms.ToTensor(),
        transforms.Normalize([0.485, 0.456, 0.406], [0.229, 0.224, 0.225]),
    ])
    val_tf = transforms.Compose([
        transforms.Resize((224, 224)),
        transforms.ToTensor(),
        transforms.Normalize([0.485, 0.456, 0.406], [0.229, 0.224, 0.225]),
    ])

    train_loader = DataLoader(DRDataset(train_df, args.images, train_tf), batch_size=args.batch_size, shuffle=True, num_workers=2)
    val_loader = DataLoader(DRDataset(val_df, args.images, val_tf), batch_size=args.batch_size, shuffle=False, num_workers=2)

    model = models.efficientnet_b0(weights=models.EfficientNet_B0_Weights.DEFAULT)
    model.classifier[1] = nn.Linear(model.classifier[1].in_features, 5)
    model.to(device)

    counts = train_df["diagnosis"].value_counts().reindex(range(5), fill_value=1).sort_index().values
    weights = torch.tensor(len(train_df) / (5.0 * counts), dtype=torch.float32, device=device)
    criterion = nn.CrossEntropyLoss(weight=weights)
    optimizer = torch.optim.AdamW(model.parameters(), lr=args.lr, weight_decay=1e-4)

    best_acc = 0.0
    for epoch in range(1, args.epochs + 1):
        model.train()
        train_correct = train_total = 0
        for x, y in train_loader:
            x, y = x.to(device), y.to(device)
            optimizer.zero_grad()
            logits = model(x)
            loss = criterion(logits, y)
            loss.backward()
            optimizer.step()
            train_correct += (logits.argmax(1) == y).sum().item()
            train_total += y.size(0)

        model.eval()
        val_correct = val_total = 0
        with torch.no_grad():
            for x, y in val_loader:
                x, y = x.to(device), y.to(device)
                logits = model(x)
                val_correct += (logits.argmax(1) == y).sum().item()
                val_total += y.size(0)

        train_acc = train_correct / max(1, train_total)
        val_acc = val_correct / max(1, val_total)
        print(f"Epoch {epoch:02d} | train_acc={train_acc:.4f} | val_acc={val_acc:.4f}")

        if val_acc > best_acc:
            best_acc = val_acc
            Path(args.output).parent.mkdir(parents=True, exist_ok=True)
            torch.save(model.state_dict(), args.output)
            print(f"Saved best weights -> {args.output}")

    print(f"Best validation accuracy: {best_acc:.4f}")


if __name__ == "__main__":
    p = argparse.ArgumentParser()
    p.add_argument("--csv", required=True)
    p.add_argument("--images", required=True)
    p.add_argument("--epochs", type=int, default=8)
    p.add_argument("--batch-size", type=int, default=16)
    p.add_argument("--lr", type=float, default=2e-4)
    p.add_argument("--output", default="../backend/model/dr_efficientnet_b0.pt")
    main(p.parse_args())
