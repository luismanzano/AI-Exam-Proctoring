import cv2

class ObjectDetector():

    def __init__(self):
        self.classFile = 'coco.names'

        with open(self.classFile, 'rt') as f:
            self.classNames = [line.rstrip() for line in f]

            self.configPath = 'ssd_mobilenet_v3_large_coco_2020_01_14.pbtxt'
            self.weightsPath = 'frozen_inference_graph.pb'

            self.net = cv2.dnn_DetectionModel(self.configPath, self.weightsPath)
            self.net.setInputSize(320, 320)
            self.net.setInputScale(1.0/127.5)
            self.net.setInputMean(127.5)
            self.net.setInputSwapRB(True)

    def DetectObjects(self, img):
        classIds, confs, bbox = self.net.detect(img, confThreshold=0.5)
        # print(bbox)
        numberPeople = 0
        phoneDetected = False
        laptopDetected = False
        img = cv2.resize(img, (0, 0), fx=0.25, fy=0.25)
        img.flags.writeable = False
        imgHeight, imgWidth = img.shape[:2]

        if len(classIds) != 0 and len(self.classNames) > 0:

            numberPeople = (classIds == 1).sum()

            #cv2.putText(img, f'No. Personas  {numberPeople}', (40, imgHeight - 70), cv2.FONT_HERSHEY_PLAIN,1.35, (255, 0, 0), 2)
            print("NUMBER OF PEOPLE", numberPeople)
            for classId, confidence, box in zip(classIds.flatten(), confs.flatten(), bbox):
                # DETECTANDO TELEFONOS
                if classId == 77:
                    phoneDetected = True
                    #cv2.putText(img, "DETECTADO", (160, imgHeight-110), cv2.FONT_HERSHEY_PLAIN, 1.35, (0, 0, 255), 2)
                # DETECTANDO LAPTOPS Y COLOCANDOLAS EN EL CUADRO
                elif classId == 73:
                    laptopDetected = True
                    #cv2.putText(img, "DETECTADA", (160, imgHeight - 90), cv2.FONT_HERSHEY_PLAIN, 1.35, (0, 0, 255), 2)
                # cv2.rectangle(img, box, (255, 0, 255), 3)
                # print(classId, str(self.classNames[classId - 1].upper()))
                # cv2.putText(img, self.classNames[classId - 1].upper(), (box[0] + 10, box[1] + 28),
                #             cv2.FONT_HERSHEY_SIMPLEX, 0.8,
                #             (0, 255, 0), 2)
                # cv2.putText(img, f'{str(int(confidence * 100))}%', (box[0] + 130, box[1] + 28),
                #             cv2.FONT_HERSHEY_SIMPLEX, 0.6,
                #             (0, 255, 0), 2)

        return numberPeople, phoneDetected, laptopDetected