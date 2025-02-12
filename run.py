from motion_detection import MotionDetector

VIDEO_ROOT = 'Motion Detector/videos/'   # path to video and save footage files

motion_detector = MotionDetector(
    cam_path=VIDEO_ROOT + 'surveillance_video.mp4',
    save_footage_dir=VIDEO_ROOT
  )

motion_detector.detect_motion()