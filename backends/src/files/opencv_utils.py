import cv2

# generator yielding a video frame and a frame timestamp (seconds) each time
def video_frames(path):
  video = cv2.VideoCapture(path)
  fps = video.get(cv2.CAP_PROP_FPS)
  ret, frame = video.read()
  count = 0
  while ret:
    count = count + 1
    # Was using 'cv2.COLOR_BGR2RGB', but images were blue (https://stackoverflow.com/questions/52494592/wrong-colours-with-cv2-imdecode-python-opencv)
    frame = cv2.cvtColor(frame, cv2.IMREAD_COLOR)
    yield frame, count / fps
    ret, frame = video.read()
