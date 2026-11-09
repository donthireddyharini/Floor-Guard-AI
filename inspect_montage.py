import cv2
from PIL import Image

p = "floor-guard-ai/uploads/originals/1793962681682_5rwdf2.png"
im = Image.open(p)
print("Montage image size:", im.size)
