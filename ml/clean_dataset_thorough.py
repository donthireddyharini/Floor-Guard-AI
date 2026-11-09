import os
import re
import glob
import shutil
from collections import defaultdict
from PIL import Image

BASE_DIR = r"c:\Users\donth_\Downloads\harry_client\floor-guard-ai"
dataset_dir = os.path.join(BASE_DIR, "dataset")

# 1. Identify all images across dataset/images/
all_images = glob.glob(os.path.join(dataset_dir, "images", "*", "*.*"))
print(f"Total current images: {len(all_images)}")

# Group images by base scene key
def get_base_key(fname):
    name = os.path.splitext(fname)[0].lower()
    # Normalize augmentation suffixes
    name = re.sub(r'(_aug\d+|_orig|_flip|_bright|_dim|_cool|_warm|_contrast|_hflip|_vflip)', '', name)
    name = re.sub(r'^(aug_)', '', name)
    # Sequence video frame collapses: e.g. hf_p41_water_spill_0040 -> hf_p41_water_spill
    name = re.sub(r'_\d{4}$', '', name)
    return name

groups = defaultdict(list)
for p in all_images:
    fname = os.path.basename(p)
    k = get_base_key(fname)
    groups[k].append(p)

print(f"Total unique base scene groups: {len(groups)}")

# Inspect specific problematic files
misannotated_fixes = {
    # aug_cables_sec01 is a yellow wet floor caution cone with water puddle
    "aug_cables_sec01_bright": 3, # Water Spill (was 7 cable)
    "aug_cables_sec01_flip": 3,
    # aug_mat_sec09 is a worker walking past caution cone on wet floor
    "aug_mat_sec09_bright": 3, # Water Spill (was 1 mat)
    "aug_mat_sec09_flip": 3,
    "aug_nat_sec09_flip": 3,
    "aug_nat_sec09_bright": 3,
}

print(f"Found {len(groups)} distinct scene keys across {len(all_images)} images.")
for k, flist in sorted(groups.items(), key=lambda x: len(x[1]), reverse=True)[:15]:
    print(f"Group '{k}': {len(flist)} images -> {[os.path.basename(x) for x in flist[:3]]}")
