import os
import cv2
import face_recognition
import time

cap = cv2.VideoCapture(0)

class FaceRecognizer:
    def __init__(self, carnet):
        # SAMPLE PICTURE OF THE PERSON WE WANT TO DETECT
        self.target_individual_img = face_recognition.load_image_file(f'Faces/{carnet}.jpg')
        self.target_individual_encoding = face_recognition.face_encodings(self.target_individual_img)[0]
        #print("TARGET INDIVIDUAL ENCODING ", self.target_individual_encoding)
        self.known_face_encodings = [
            self.target_individual_encoding
        ]

        self.known_face_names = [
            "Cara Validada"
        ]

        # INTIALIZE THE VARIABLES WE NEED TO GET THE MODEL UP AND RUNNING

        self.face_locations = []
        self.face_encodings = []
        self.face_names = []
        self.process_this_frame = True


    def RecognizeFaces(self, img):
        # RESIZE THE IMAGE TO IMPROVE PERFORMANCE
        small_frame = cv2.resize(img, (0, 0), fx=0.25, fy=0.25)
        # BECAUSE THE FACE DETECTOR USES RGB INSTEAD OF BGR WHICH IS THE FORMAT OF THE SOURCE
        rgb_small_frame = cv2.cvtColor(small_frame, cv2.COLOR_BGR2RGB)

        if self.process_this_frame:
            # FIND ALL THE FACES AND FACE ENCODINGS IN THE CURRENT FRAME
            face_locations = face_recognition.face_locations(rgb_small_frame)
            face_encodings = face_recognition.face_encodings(rgb_small_frame, face_locations)

            face_names = []

            for face_encoding in face_encodings:
                # SEE IF THE FACE DETECTED IS A MATCH FOR ANY SAMPLE THAT WE HAVE
                matches = face_recognition.compare_faces(self.known_face_encodings, face_encoding)
                name = "CARA DESCONOCIDA"

                if True in matches:
                    first_match_index = matches.index(True)
                    name = self.known_face_names[first_match_index]

                face_names.append(name)


        process_this_frame = not self.process_this_frame

        # DISPLAY THE RESULTS

        # for (top, right, bottom, left), name in zip(face_locations, face_names):
        #     # Scale back up face locations since the frame we detected in was scaled to 1/4 size
        #     top *= 4
        #     right *= 4
        #     bottom *= 4
        #     left *= 4
        #
        #     # Draw a box around the face
        #     cv2.rectangle(img, (left, top), (right, bottom), (0, 0, 255), 2)
        #
        #     # Draw a label with a name below the face
        #     cv2.rectangle(img, (left, bottom - 35), (right, bottom), (0, 0, 255), cv2.FILLED)
        #     font = cv2.FONT_HERSHEY_DUPLEX
        #     cv2.putText(img, name, (left + 6, bottom - 6), font, 1.0, (255, 255, 255), 1)

        return face_locations, face_names



