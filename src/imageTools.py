import numpy as np
import cv2


def perspectiveUndistort(image, dots):
  height, width = image.shape[:2]

  src_pts = np.array(dots, dtype=np.float32)
  dst_pts = np.array([[0, 0], [width - 1, 0], [width - 1, height - 1], [0, height - 1]], dtype=np.float32)
  M = cv2.getPerspectiveTransform(src_pts, dst_pts)
  return cv2.warpPerspective(image, M, (width, height))

def radialUndistort(original_image, k_value=0, zoom_value=1):
  height, width = original_image.shape[:2]



  # Radial distortion correction
  center_x, center_y = width / 2, height / 2
  x, y = np.meshgrid(np.arange(width), np.arange(height))
  x = x.astype(np.float32) - center_x
  y = y.astype(np.float32) - center_y
  r = np.sqrt(x ** 2 + y ** 2)
  r_max = np.max(r)
  scale = float(zoom_value)
  x_distorted = x * (1 + k_value * (r / r_max)) * scale
  y_distorted = y * (1 + k_value * (r / r_max)) * scale
  map_x = (x_distorted + center_x).astype(np.float32)
  map_y = (y_distorted + center_y).astype(np.float32)
  return cv2.remap(original_image, map_x, map_y, cv2.INTER_LINEAR, borderMode=cv2.BORDER_CONSTANT)

def getFrameFromVideo(vidpath, framenum):
  cap = cv2.VideoCapture(vidpath)
  cap.set(1,framenum)
  ret, frame = cap.read()
  if ret:
    return frame
  return None