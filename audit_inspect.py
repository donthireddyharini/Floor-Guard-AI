import os
import glob
from PIL import Image
import numpy as np

BASE_DIR = r"c:\Users\donth_\Downloads\harry_client\floor-guard-ai"
dataset_dir = os.path.join(BASE_DIR, "dataset")

images = sorted(glob.glob(os.path.join(dataset_dir, "images", "*", "*.*")))
print(f"Total images in dataset: {len(images)}")

splits = {"train": 0, "val": 0, "test": 0}
class_counts = {}
suspicious_annotations = []

for img_p in images:
    split = os.path.basename(os.path.dirname(img_p))
    splits[split] = splits.get(split, 0) + 1
    
    fname = os.path.basename(img_p)
    base = os.path.splitext(fname)[0]
    lbl_p = os.path.join(dataset_dir, "labels", split, base + ".txt")
    
    classes_in_file = []
    if os.path.exists(lbl_p):
        with open(lbl_p, 'r') as f:
            for line in f:
                parts = line.strip().split()
                if parts:
                    cid = int(parts[0])
                    classes_in_file.append(cid)
                    class_counts[cid] = class_counts.get(cid, 0) + 1
    else:
        classes_in_file = [0] # clean floor
        class_counts[0] = class_counts.get(0, 0) + 1
        
    # Check suspicious combinations
    # aug_cables_sec01 -> was water spill
    if "cables_sec01" in fname or "nat_sec09" in fname or "mat_sec09" in fname:
        suspicious_annotations.append((fname, classes_in_file, "Likely water spill misnamed/mislabeled"))
        
    if "boxes" in fname and 7 in classes_in_file:
        suspicious_annotations.append((fname, classes_in_file, "Box labeled as cable"))
        
    if "bottle" in fname and 3 in classes_in_file:
        suspicious_annotations.append((fname, classes_in_file, "Bottle labeled as water spill"))

print("\nSplit Counts:", splits)
print("\nClass ID Counts:", sorted(class_counts.items()))
print("\nSuspicious identified so far:", len(suspicious_annotations))
for s in suspicious_annotations:
    print(" - ", s)
