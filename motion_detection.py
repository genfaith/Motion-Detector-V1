import cv2 as cv
import numpy as np
import os

VIDEO_ROOT = 'Motion Detector/videos/'

FOURCC = cv.VideoWriter_fourcc(*'mp4v')
OUTPUT_FILE = 'saved_surveillance_footage.mp4'
FRAME_WIDTH = 640
FRAME_HEIGHT = 360
FRAME_RATE = 30


class FOOTAGE_WRITER():
  def __init__(self, output_file, fourcc=FOURCC, frame_rate=FRAME_RATE, frame_width=FRAME_WIDTH, frame_height=FRAME_HEIGHT):
    self.filename = VIDEO_ROOT + output_file
    self.fourcc = fourcc
    self.fps = frame_rate
    self.frame_size = (frame_width, frame_height)

    # Cannot inherit cv.VideoWriter
    self.writer = cv.VideoWriter(
          self.filename, self.fourcc, self.fps, self.frame_size
      )
    
  def write(self, frame):
    self.writer.write(frame)


class MotionDetector:
  def __init__(self, cam_path, save_footage_dir):
    self.cam_path = cam_path
    self.save_footage_dir = save_footage_dir

  def detect_motion(self):
    # print(self.cam_path)
    cap = cv.VideoCapture(self.cam_path)
    # cap = cv.VideoCapture(0)

    surveillance_tracker = 1

    save_footage_file = os.path.join(self.save_footage_dir, f'/surveillance_footage_{surveillance_tracker}.mp4')

    footage_writer = FOOTAGE_WRITER(save_footage_file)

    initial_gray_frame = None

    motion_detected = False

    motion_detection_threshold = 5
    motion_detection_count = 0

    while True:
      ret, frame = cap.read()

      # getting video properties
      # frame_width = int(cap.get(cv.CAP_PROP_FRAME_WIDTH))
      # frame_height = int(cap.get(cv.CAP_PROP_FRAME_HEIGHT))
      frame_fps = int(cap.get(cv.CAP_PROP_FPS)) or 30
      # frame_fourcc = cv.VideoWriter_fourcc(*'mp4v')
      # frame_fourcc = cv.VideoWriter_fourcc(*'XVID')

      # print(frame_fourcc)

      # print(frame_width, frame_height)

      frame_wait_period = int(1 * 1000/ frame_fps)

      if ret and cv.waitKey(frame_wait_period) != 27: # About 30 fps 
        # gray_frame = cv.GaussianBlur(cv.cvtColor(frame, cv.COLOR_BGR2GRAY), (15, 15), 0)
        gray_frame = cv.cvtColor(frame, cv.COLOR_BGR2GRAY)
        # CANNY
        canny_frame = cv.Canny(gray_frame, 125, 150)

        # print(initial_gray_frame)
        # check the absolute difference between frames
        try:
          diff_frame = cv.absdiff(initial_gray_frame, gray_frame)
          ret_val, thresh_frame = cv.threshold(diff_frame, thresh=127, maxval=255, type=cv.THRESH_BINARY)
          # thresh_frame = cv.adaptiveThreshold(diff_frame, 255, cv.ADAPTIVE_THRESH_MEAN_C, cv.THRESH_BINARY_INV, 11, 7)

          # corners = cv.goodFeaturesToTrack(
          #   diff_frame,
          #   **TRACKING_PARAMS
          # )

          # if corners is not None:
          #   print('*'*20)
          #   for x, y, in np.float32(corners).reshape(-1, 2):
          #     print(x > 640)
          #     cv.circle(thresh_frame, (np.int64(x), np.int64(y)), 10, (255,), -2)
          #   print('*'*20)

          contours, bb_frame = self.white_region_detector(thresh_frame, frame)

          if contours != ():
            motion_detected = True
            motion_detection_count += 1
          else:
            motion_detected = False
            motion_detection_count = 0
            

          if motion_detected:
            # print('MOTION DETECTED')
            pass
          else:
            # print('NO MOTION')
            pass

          print(motion_detection_count)

          if motion_detection_count >= motion_detection_threshold:
            try:
              self.write_surveillance_frame(footage_writer, self.resize(frame))
              print("FRAME WRITTEN")
            except Exception as e:
              print(e)
              # print('UNABLE TO WRITE VIDEO FRAME')
              # continue
            surveillance_tracker_incremented=False
          elif not surveillance_tracker_incremented:
            print('SURVEILLANCE TRACKER INCREMENTED')
            surveillance_tracker+=1
            save_footage_file = os.path.join(self.save_footage_dir, f'surveillance_footage_{surveillance_tracker}.mp4')
            footage_writer = FOOTAGE_WRITER(save_footage_file)
            surveillance_tracker_incremented=True


          cv.imshow('window1', self.resize(bb_frame))
          cv.imshow('window2', self.resize(gray_frame))
          cv.imshow('window3', self.resize(canny_frame))
          cv.imshow('window4', self.resize(diff_frame))
          cv.imshow('window5', self.resize(thresh_frame))
          # print(diff_frame.max())
        except Exception as e:
          # print(e)

          pass

        initial_gray_frame = gray_frame.copy()
      else:
        break

    cap.release()
    cv.destroyAllWindows()

  # White region detector
  def white_region_detector(self, frame, original_image):
    contours, _ = cv.findContours(frame, cv.RETR_EXTERNAL, cv.CHAIN_APPROX_SIMPLE)

    for contour in contours:
      x, y, w, h = cv.boundingRect(contour)
      # print(x, y, w, h)
      cv.rectangle(original_image, (x, y), (x+w, y+h), (0, 0, 255), -1)

    return contours, original_image

  def write_surveillance_frame(self, footage_writer, frame):
    footage_writer.write(frame)

  def resize(self, frame):
    resized_frame = cv.resize(frame, (640, 360))
    return resized_frame
  

if __name__ == '__main__':
  # print(os.curdir)
  motion_detector = MotionDetector(
    cam_path=VIDEO_ROOT + 'surveillance_video.mp4',
    save_footage_dir=VIDEO_ROOT
  )

  motion_detector.detect_motion()
