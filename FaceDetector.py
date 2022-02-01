import cv2
import mediapipe as mp

class FaceDetector():
    def __init__(self, minDetectionCon = 0.5):

        self.minDetectionCon = minDetectionCon
        self.mpFaceDetection = mp.solutions.face_detection
        self.mpDraw = mp.solutions.drawing_utils
        self.faceDetection = self.mpFaceDetection.FaceDetection(minDetectionCon)

    def findFaces(self, img, draw = True):
        imgRGB = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
        small_img = cv2.resize(imgRGB, (0, 0), fx=0.25, fy=0.25)
        small_img.flags.writeable = False
        imgHeight, imgWidth = img.shape[:2]
        numberFaces = 0
        self.results = self.faceDetection.process(small_img)
        # print(self.results)
        bboxs = []
        if self.results.detections:
            numberFaces = len(self.results.detections)
            # cv2.putText(img, f'Personas c/ Estudiante  {numberFaces - 1}', (40, imgHeight - 50), cv2.FONT_HERSHEY_PLAIN,
            #             1.35, (255, 0, 0), 2)
            for id, detection in enumerate(self.results.detections):
                bboxC = detection.location_data.relative_bounding_box

                #lets first get the dimensions of the img
                ih, iw, ic = img.shape
                bbox = int(bboxC.xmin * iw), int(bboxC.ymin * ih), \
                       int(bboxC.width * iw), int(bboxC.height * ih)

                bboxs.append([id, bbox, detection.score])
                img = self.fancyDraw(img, bbox, )

                cv2.putText(img, f'{int(detection.score[0] * 100)}%', (bbox[0], bbox[1]-20), cv2.FONT_HERSHEY_PLAIN,
                            3, (0, 255, 0), 2)

                self.mpDraw.draw_detection(img, detection)

        return bboxs, numberFaces

    def fancyDraw(self, img, bbox, l = 30, t=4):
        x,y,w,h = bbox
        x1, y1 = x*w, y+h

        cv2.rectangle(img, bbox, (255, 0, 255), 2)
        cv2.line(img, (x,y), (x+l, y), (255, 0, 255), t)
        return img
