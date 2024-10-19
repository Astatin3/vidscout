import os
import sys
import json

import requests
from pytubefix import YouTube
from pytubefix.cli import on_progress

TBAip = "https://www.thebluealliance.com/api/v3"
# Free TBA Key!
headers = {"User-Agent": "Mozilla/5.0", "X-TBA-Auth-Key": "fzQY0pv6qwfwuII5Xx2bmP57BBSuE0maxKailYlrI0e1EdfKCq6F3Th9FFDqpW7f"}
RES = '1080p'

if len(sys.argv) < 2:
  sys.exit("Usage: downloader.py <event code>")

evcode = sys.argv[1]

event_matches = requests.get(TBAip + "/event/" + evcode + "/matches", headers=headers).json()

video_urls = [None for _ in range(len(event_matches))]

for match in event_matches:
  if match["comp_level"] != "qm": continue
  match_urls = []
  for video_url in match["videos"]:
    if video_url["type"] != "youtube": continue
    match_urls.append(video_url["key"])
  if len(match_urls) != 0:
    video_urls[match["match_number"]] = match_urls

if not os.path.exists(evcode):
    os.makedirs(evcode)

for i, match in enumerate(video_urls):
  if match is None: continue
  # print(match)
  for url in match:
    if os.path.exists(os.path.join(evcode, str(i)+".mp4")):
      continue
    yt = YouTube("https://youtube.com/watch?v="+url,  on_progress_callback=on_progress)
    if yt.author != "FIRSTRoboticsCompetition": continue


    for idx, stream in enumerate(yt.streams):
      if stream.resolution == RES:
        break

    print(f"Downloading match {i}, {stream.resolution}")

    # print(yt.streams[idx])
    yt.streams[idx].download(output_path = evcode, filename = str(i)+".mp4")

    # ys = yt.streams.get_highest_resolution()
    # print(yt.title)
