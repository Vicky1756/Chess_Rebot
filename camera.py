import cv2

class VideoCamera(object):
    def __init__(self):
       #capturing video

        # self.video = cv2.VideoCapture( 0 )

        self.video = cv2.VideoCapture( cv2.CAP_DSHOW )
    
    def __del__(self):
        print('turning off')
        #releasing camera
        self.video.release()

    def get_frame(self):

        ret, frame = self.video.read()
        status = False

        # if not frame:
        if frame is None and ret is None:
            frame = cv2.imread('./static/img/background/no_signal.jpg')
            status = False
        else:
            # """ cam open """"
            # frame = frame
            # status = True
            # """ cam close """
            frame = cv2.imread('./static/img/background/no_signal.jpg')
            status = False
        
        frame = cv2.resize(frame,(472, 354)) # ,fx=0,fy=0,interpolation = cv2.INTER_CUBIC

        # encode OpenCV raw frame to jpg and displaying it
        ret, jpeg = cv2.imencode('.jpg', frame)
        return (jpeg.tobytes(), status)


       

