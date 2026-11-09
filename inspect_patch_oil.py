import cv2, numpy as np

im = cv2.imread("floor-guard-ai/uploads/originals/1793954604867_yoogny.jpeg")
patch = im[607:607+206, 53:53+440]
gray = cv2.cvtColor(patch, cv2.COLOR_BGR2GRAY)
edges = cv2.Canny(gray, 40, 140)
edge_pct = np.count_nonzero(edges) / (patch.shape[0] * patch.shape[1])
hsv = cv2.cvtColor(patch, cv2.COLOR_BGR2HSV)
print("Patch shape:", patch.shape)
print("Mean brightness:", np.mean(gray))
print("Std brightness:", np.std(gray))
print("Edge pct:", edge_pct)
print("Mean saturation:", np.mean(hsv[:,:,1]))
