import math
from time import time

import cv2
import sys

import numpy as np
from cv2.typing import Point, Scalar

from src.videoCrop import contains_start, contains_end
import src.imageTools as imageTools

redColor = (120, 70, 238)
colorRange = 60

if len(sys.argv) < 3:
  print("Usage: playVideo.py <event code> <match> <undistortion config>")
  sys.exit(1)

class distorton_config:
  def __init__(self):
    self.k_value = 0
    self.zoom_value = 1
    self.dots = [
      [0.,0.],
      [0.,0.],
      [0.,0.],
      [0.,0.]
    ]

dconf = distorton_config()
conf_split = sys.argv[3].split(',')
dconf.k_value = float(conf_split[0])
dconf.zoom_value = float(conf_split[1])
dconf.dots[0][0] = float(conf_split[2])
dconf.dots[0][1] = float(conf_split[3])
dconf.dots[1][0] = float(conf_split[4])
dconf.dots[1][1] = float(conf_split[5])
dconf.dots[2][0] = float(conf_split[6])
dconf.dots[2][1] = float(conf_split[7])
dconf.dots[3][0] = float(conf_split[8])
dconf.dots[3][1] = float(conf_split[9])

filename = sys.argv[1] + "/" + sys.argv[2] + ".mp4"

blueColor = (280, 30, 125)
blueColorUnselected = (int(blueColor[0]/3), int(blueColor[1]/3), int(blueColor[2]/3))
redColor = (125, 30, 280)
redColorUnselected = (int(redColor[0]/3), int(redColor[1]/3), int(redColor[2]/3))

cap = cv2.VideoCapture(filename)
totalFrames = cap.get(cv2.CAP_PROP_FRAME_COUNT)
FPS = cap.get(cv2.CAP_PROP_FPS)
width = cap.get(cv2.CAP_PROP_FRAME_WIDTH)


selAlliance = "blue"
selAllianceIndex = 1
allianceIndex = [
  "blue-1",
  "blue-2",
  "blue-3",
  "red-1",
  "red-2",
  "red-3"
]

boxes = {
  "blue-1": np.zeros((int(totalFrames), 4)),
  "blue-2": np.zeros((int(totalFrames), 4)),
  "blue-3": np.zeros((int(totalFrames), 4)),
  "red-1": np.zeros((int(totalFrames), 4)),
  "red-2": np.zeros((int(totalFrames), 4)),
  "red-3": np.zeros((int(totalFrames), 4))
}

def undistort(frame):
  display_frame = imageTools.radialUndistort(frame, dconf.k_value, dconf.zoom_value)
  return imageTools.perspectiveUndistort(display_frame, dconf.dots)

def dispColorCircle(frame, text, location, color):
  cv2.circle(frame, location, 20, color, -1)
  cv2.putText(frame, text, (location[0]-7, location[1]+8), cv2.FONT_HERSHEY_SIMPLEX, 0.75, (255, 255, 255), 2)

def distance(p1, p2):
  return math.sqrt((p1[0]-p2[0])**2 + (p1[1]-p2[1])**2)

clicked = False
def click_event(event, x, y, flags, param):
  global selAllianceIndex
  global selAlliance

  global clicked
  global clickStart
  global mousePos

  if not isPaused: return
  if event == cv2.EVENT_LBUTTONDOWN:
    clicked = True
    for i in range(1,4):
      if distance((x, y), (int(width/2)+50*i,50)) < 20:
        print("Click event detected")
        selAllianceIndex = i
        selAlliance = "red"
        clicked = False
        rerender()
      elif distance((x, y), (int(width/2)+50*i-200,50)) < 20:
        selAllianceIndex = i
        selAlliance = "blue"
        clicked = False
        rerender()
    if clicked:
      clickStart = (x, y)
  if clicked and event == cv2.EVENT_LBUTTONUP:
    clicked = False
    boxes[selAlliance+"-"+str(selAllianceIndex)][int(curFrame)] = np.array([
      clickStart[0], clickStart[1],
      x-clickStart[0], y-clickStart[1]
    ])
    restartTracking()
    rerender()
  if clicked and event == cv2.EVENT_MOUSEMOVE:
    mousePos = (x,y)
    rerender()


cv2.imshow('frame', np.zeros((1,1)))
cv2.setMouseCallback('frame', click_event)

isPaused = True
def rerender():
  global frame

  global clicked
  global clickStart
  global mousePos

  framecopy = frame.copy()
  cv2.rectangle(framecopy, (0,0),(500,100), (0,0,0), -1)
  cv2.putText(framecopy, "Paused" if isPaused else "Unpaused", (0,20), cv2.FONT_HERSHEY_SIMPLEX, 0.75, (255, 255, 255), 2)
  cv2.putText(framecopy, "Frame: "+str(curFrame)+"/"+str(totalFrames), (0,40), cv2.FONT_HERSHEY_SIMPLEX, 0.75, (255, 255, 255), 2)
  cv2.putText(framecopy, "FPS: "+str(round(1.0 / (time() - start_time)))+"/"+str(round(FPS)), (0,60), cv2.FONT_HERSHEY_SIMPLEX, 0.75, (255, 255, 255), 2)

  for i in range(1,4):
    dispColorCircle(framecopy, str(i), (int(width/2)+50*i,50), redColor if selAlliance == "red" and selAllianceIndex == i else redColorUnselected)
    dispColorCircle(framecopy, str(i), (int(width/2)+50*i-200,50), blueColor if selAlliance == "blue" and selAllianceIndex == i else blueColorUnselected)

  for alliance in allianceIndex:
    if alliance.startswith("red"):
      color = redColor
    else:
      color = blueColor

    box = boxes[alliance][int(curFrame)]
    if box is None: continue
    if np.sum(box) == 0: continue

    cv2.rectangle(framecopy, (int(box[0]), int(box[1])), (int(box[0]+box[2]), int(box[1]+box[3])), color, 3)
    dispColorCircle(framecopy, alliance.split("-")[1], (int(box[0]+box[2]/2), int(box[1]+box[3]/2)), color)


    # cv2.rectangle(framecopy, ())

  if clicked:
    if selAlliance.startswith("red"):
      color = redColor
    else:
      color = blueColor
    cv2.rectangle(framecopy, (clickStart[0], clickStart[1]), (mousePos[0], mousePos[1]), color, 3)


  cv2.imshow('frame', framecopy)


multiTracker = None
trackingEnabled = [False, False, False, False, False, False]

def restartTracking():
  global multiTracker
  global trackingEnabled
  multiTracker = cv2.legacy.MultiTracker_create()
  # Initialize MultiTracker
  for i, alliance in enumerate(allianceIndex):
    box = boxes[alliance][int(curFrame)]
    if np.sum(box) == 0:
      trackingEnabled[i] = False
      continue
    multiTracker.add(cv2.legacy.TrackerCSRT_create(), frame, box)
    trackingEnabled[i] = True

def track(frame):
  global multiTracker
  global trackingEnabled

  if multiTracker is None:
    restartTracking()


  success, trackedBoxes = multiTracker.update(frame)
  if not success: return
  for i, box in enumerate(trackedBoxes):
    boxes[allianceIndex[i]][int(curFrame)] = np.array(box)


isInMatch = False
while cap.isOpened():
  global frame
  global start_time
  start_time = time()
  ret, frame = cap.read()
  if not ret:
    break

  if not isInMatch and contains_start(frame):
    isInMatch = True
  elif isInMatch and contains_end(frame):
    break

  # print(f"{i}, {isInMatch}")
  curFrame = cap.get(cv2.CAP_PROP_POS_FRAMES)
  if not isInMatch: continue
  if curFrame % 5 != 0: continue

  if not isPaused:
    if cv2.waitKey(1) & 0xff == 32:
      isPaused = not isPaused

  frame = undistort(frame)
  track(frame)
  rerender()

  while isPaused:
    k = cv2.waitKey(0) & 0xff
    if k == 81: # Left arrow
      cap.set(cv2.CAP_PROP_POS_FRAMES, cap.get(cv2.CAP_PROP_POS_FRAMES) - 1 - 15)
      curFrame = cap.get(cv2.CAP_PROP_POS_FRAMES)
      restartTracking()
      break
    # if k == 83: # right arrow
    #   cap.set(cv2.CAP_PROP_POS_FRAMES, cap.get(cv2.CAP_PROP_POS_FRAMES) - 1 + 15)
    #   break
    if k == 27:
      cap.release()
      break
    if k == 32:
      isPaused = not isPaused
      break


cap.release()