import cv2
import numpy as np

image_size = (640, 360)

start_img = cv2.imread("./images/start.png")
end_img = cv2.imread("./images/end.png")

def containsImage(frame, image):
  if frame is None: return False
  frame = cv2.resize(frame, image_size, interpolation=cv2.INTER_AREA)
  frame = frame[323:345, 305:335]
  res = cv2.matchTemplate(frame, image, cv2.TM_CCOEFF_NORMED)
  found = False
  for _ in zip(*(np.where(res >= .98))[::-1]):
    found = True
    break
  return found

def contains_start(frame):
  return containsImage(frame, start_img)

def contains_end(frame):
  return containsImage(frame, end_img)

def search_video(video_path, search_img, start_index = 0):
  cap = cv2.VideoCapture(video_path)

  if not cap.isOpened():
    print("Cannot open camera")
    exit()

  i = -1
  while True:
    # Capture frame-by-frame
    ret, frame = cap.read()
    if not ret:
      print("Can't receive frame (stream end?). Exiting ...")
      break
    i += 1

    if i < start_index: continue

    frame = cv2.resize(frame, image_size, interpolation = cv2.INTER_AREA)
    crop_img = frame[323:345, 305:335]

    res = cv2.matchTemplate(crop_img, search_img, cv2.TM_CCOEFF_NORMED)
    found = False
    for _ in zip(*(np.where(res >= .98))[::-1]):
      found = True
      break
    if found:
      # cv2.waitKey(0)
      break

  cap.release()
  return i


def videoCrop(video_path):
  start = search_video(video_path, start_img)
  end = search_video(video_path, end_img, start)
  return start, end