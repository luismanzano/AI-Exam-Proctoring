import cv2
import mediapipe as mp

import numpy as np

class EyesAndMouth():
    def __init__(self):

        self.mpDraw = mp.solutions.drawing_utils
        self.mpFaceMesh = mp.solutions.face_mesh
        self.faceMesh = self.mpFaceMesh.FaceMesh(max_num_faces=2)
        self.drawSpec = self.mpDraw.DrawingSpec(thickness= 1, circle_radius=1)
        self.x1Mouth, self.y1Mouth, self.x2Mouth, self.y2Mouth = 0, 0, 0, 0

    def findAttributes(self, img):
        small_img = cv2.resize(img, (0, 0), fx=0.25, fy=0.25)
        img = small_img
        img.flags.writeable = False
        grayImg = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        imgRGB = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
        results = self.faceMesh.process(imgRGB)
        imgHeight, imgWidth = img.shape[:2]

        openMouthRatio = 0
        gazeRatioRight = 0
        gazeRatioLeft = 0
        gazeRatio = 0
        gazeRatioAVG = 1

        # NOW TO THE ACTUAL WORK
        if results.multi_face_landmarks:
            gazeRatioRight = 0
            for id, faceLms in enumerate(results.multi_face_landmarks):
                ih, iw, ic = img.shape

                mouthPositionTop = (int(faceLms.landmark[306].x * iw), int(faceLms.landmark[306].y * ih))
                mouthPositionBottom = (int(faceLms.landmark[61].x * iw), int(faceLms.landmark[61].y * ih))

                # cv2.circle(img, (int(faceLms.landmark[306].x * iw), int(faceLms.landmark[306].y * ih)), 2, (0, 0, 255),
                #            2)
                # cv2.circle(img, (int(faceLms.landmark[61].x * iw), int(faceLms.landmark[61].y * ih)), 2, (0, 0, 255), 2)

                mouthWidth = faceLms.landmark[306].x - faceLms.landmark[61].x
                mouthHeight = faceLms.landmark[13].y - faceLms.landmark[14].y
                openMouthRatio = abs(mouthHeight / mouthWidth)
                # if openMouthRatio > 0.1:
                #     cv2.putText(img, 'Boca Abierta', (160, imgHeight-140), cv2.FONT_HERSHEY_PLAIN, 1.5, 255, 2)

                rightEyeRegion = np.array([
                    (faceLms.landmark[33].x * iw, faceLms.landmark[33].y * ih),
                    (faceLms.landmark[246].x * iw, faceLms.landmark[246].y * ih),
                    (faceLms.landmark[161].x * iw, faceLms.landmark[161].y * ih),
                    (faceLms.landmark[160].x * iw, faceLms.landmark[160].y * ih),
                    (faceLms.landmark[159].x * iw, faceLms.landmark[159].y * ih),
                    (faceLms.landmark[158].x * iw, faceLms.landmark[158].y * ih),
                    (faceLms.landmark[157].x * iw, faceLms.landmark[157].y * ih),
                    (faceLms.landmark[173].x * iw, faceLms.landmark[173].y * ih),
                    (faceLms.landmark[133].x * iw, faceLms.landmark[133].y * ih),
                    (faceLms.landmark[155].x * iw, faceLms.landmark[155].y * ih),
                    (faceLms.landmark[154].x * iw, faceLms.landmark[154].y * ih),
                    (faceLms.landmark[153].x * iw, faceLms.landmark[153].y * ih),
                    (faceLms.landmark[145].x * iw, faceLms.landmark[145].y * ih),
                    (faceLms.landmark[144].x * iw, faceLms.landmark[144].y * ih),
                    (faceLms.landmark[163].x * iw, faceLms.landmark[163].y * ih),
                    (faceLms.landmark[7].x * iw, faceLms.landmark[7].y * ih)], np.int32)

                leftEyeRegion = np.array([
                    (int(faceLms.landmark[398].x * iw), int(faceLms.landmark[398].y * ih)),
                    (int(faceLms.landmark[384].x * iw), int(faceLms.landmark[384].y * ih)),
                    (int(faceLms.landmark[385].x * iw), int(faceLms.landmark[385].y * ih)),
                    (int(faceLms.landmark[386].x * iw), int(faceLms.landmark[386].y * ih)),
                    (int(faceLms.landmark[387].x * iw), int(faceLms.landmark[387].y * ih)),
                    (int(faceLms.landmark[388].x * iw), int(faceLms.landmark[388].y * ih)),
                    (int(faceLms.landmark[466].x * iw), int(faceLms.landmark[466].y * ih)),
                    (int(faceLms.landmark[263].x * iw), int(faceLms.landmark[263].y * ih)),
                    (int(faceLms.landmark[249].x * iw), int(faceLms.landmark[249].y * ih)),
                    (int(faceLms.landmark[390].x * iw), int(faceLms.landmark[390].y * ih)),
                    (int(faceLms.landmark[373].x * iw), int(faceLms.landmark[373].y * ih)),
                    (int(faceLms.landmark[374].x * iw), int(faceLms.landmark[374].y * ih)),
                    (int(faceLms.landmark[380].x * iw), int(faceLms.landmark[380].y * ih)),
                    (int(faceLms.landmark[381].x * iw), int(faceLms.landmark[381].y * ih)),
                    (int(faceLms.landmark[382].x * iw), int(faceLms.landmark[382].y * ih)),
                    (int(faceLms.landmark[362].x * iw), int(faceLms.landmark[362].y * ih))
                ], np.int32)

                # cv2.polylines(img, [leftEyeRegion], True, (0, 0, 255), 1)
                # cv2.polylines(img, [rightEyeRegion], True, (0, 0, 255), 1)

                # RECTANGLE WHERE THE LEFT EYE IS AT
                leftEyeMinX = np.min(leftEyeRegion[:, 0])
                leftEyeMaxX = np.max(leftEyeRegion[:, 0])
                leftEyeMinY = np.min(leftEyeRegion[:, 1])
                leftEyeMaxY = np.max(leftEyeRegion[:, 1])

                leftEyeFrame = img[leftEyeMinY: leftEyeMaxY, leftEyeMinX: leftEyeMaxX]
                leftEyeFrame = cv2.resize(leftEyeFrame, None, fx=5, fy=5)

                #   MASK TO REMOVE EVERYTHING BUT THE EYE (LEFT)
                width, height, channel = img.shape
                mask = np.zeros(img.shape[:2], np.uint8)
                cv2.polylines(mask, [leftEyeRegion], True, (255, 255, 255), 2)
                cv2.fillPoly(mask, [leftEyeRegion], 255)
                leftEyeMasked = cv2.bitwise_and(grayImg, grayImg, mask=mask)
                leftEyeGray = leftEyeMasked[leftEyeMinY: leftEyeMaxY, leftEyeMinX: leftEyeMaxX]

                #   DETECTING THE POSITION OF THE IRIS (LEFT)
                _, thresholdEye = cv2.threshold(leftEyeGray, 70, 255, cv2.THRESH_BINARY)
                height, width = thresholdEye.shape
                leftSideThreshold = thresholdEye[0:height, 0:int(width / 2)]
                leftSideWhite = cv2.countNonZero(leftSideThreshold)
                rightSideThreshold = thresholdEye[0:height, int(width / 2):]
                rightSideWhite = cv2.countNonZero(rightSideThreshold)

                # print("RATIO1", leftSideWhite, rightSideWhite)
                if rightSideWhite != 0:
                    gazeRatio = leftSideWhite / rightSideWhite
                else:
                    gazeRatio = gazeRatioRight

                #   RECTANGLE WHERE THE RIGHT EYE IS AT
                rightEyeMinX = np.min(rightEyeRegion[:, 0])
                rightEyeMaxX = np.max(rightEyeRegion[:, 0])
                rightEyeMinY = np.min(rightEyeRegion[:, 1])
                rightEyeMaxY = np.max(rightEyeRegion[:, 1])

                # MASK TO REMOVE EVERYTHING BUT THE EYE (RIGHT)
                cv2.polylines(mask, [rightEyeRegion], True, (255, 255, 255), 2)
                cv2.fillPoly(mask, [rightEyeRegion], 255)
                rightEyeMasked = cv2.bitwise_and(grayImg, grayImg, mask=mask)
                rightEyeGray = rightEyeMasked[rightEyeMinY: rightEyeMaxY, rightEyeMinX: rightEyeMaxX]

                # DETECTING THE POSITION OF THE IRIS (RIGHT)
                _, thresholdEyeRight = cv2.threshold(rightEyeGray, 70, 255, cv2.THRESH_BINARY)
                heightRight, widthRight = thresholdEyeRight.shape
                leftSideThresholdRight = thresholdEyeRight[0:heightRight, 0:int(widthRight / 2)]
                leftSideWhiteRight = cv2.countNonZero(leftSideThresholdRight)
                rightSideThresholdRight = thresholdEyeRight[0:heightRight, int(widthRight / 2):]
                rightSideWhiteRight = cv2.countNonZero(rightSideThresholdRight)

                # print("RATIO2", leftSideWhiteRight, rightSideWhiteRight)
                if rightSideWhiteRight != 0:
                    gazeRatioRight = leftSideWhiteRight / rightSideWhiteRight
                else:
                    gazeRatioRight = gazeRatio

                # CALCULATING THE AVERAGE BETWEEN BOTH RATIOS TO KNOW WHERE THE PERSON IS LOOKINGX`
                gazeRatioAVG = (gazeRatio + gazeRatioRight) / 2

                # if gazeRatioAVG > 1.5:
                #     cv2.putText(img, "Izquierda", (160, imgHeight-175), cv2.FONT_HERSHEY_PLAIN, 1.5, 255, 2)
                # elif gazeRatioAVG < 0.5:
                #     cv2.putText(img, "Derecha", (160, imgHeight-175), cv2.FONT_HERSHEY_PLAIN, 1.5, 255, 2)
                # else:
                #     cv2.putText(img, "En Pantalla", (160, imgHeight-175), cv2.FONT_HERSHEY_PLAIN, 1.5, 255, 2)

                # cv2.putText(img, str(gazeRatioAVG), (50, 100), cv2.FONT_HERSHEY_PLAIN, 2, 255, 2)

                rightEyeFrame = img[rightEyeMinY: rightEyeMaxY, rightEyeMinX: rightEyeMaxX]
                # rightEyeFrame = cv2.resize(rightEyeFrame, None, fx=5, fy=5)
                # cv2.imshow("BN_LEFT_THRESHOLD_EYE", thresholdEye)
                # cv2.imshow("BN_RIGHT_THRESHOLD_EYE", thresholdEyeRight)
                # cv2.imshow('Mask', leftEyeMasked)

                # print("OPEN MOUTH RATIO", openMouthRatio)
                # print("MOUTH POSITION TOP", mouthPositionTop)
                # print("MOUTH POSITION BOTTOM", mouthPositionBottom)

        return openMouthRatio, gazeRatioAVG


