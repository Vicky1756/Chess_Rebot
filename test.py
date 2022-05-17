import cv2
import base64
import io
import os
import math
import numpy as np
from Detection.perspective import *
from Detection.sideDetection_HSV import *
from itertools import count
import matplotlib.pyplot as plt
import DetectionFunctions as df
from DetectAllPoints import *
import PIL
import time

import tensorflow as tf
from tensorflow import keras
from tensorflow.keras import layers

from keras.preprocessing.image import ImageDataGenerator
import numpy as np
import chess
import warnings

os.environ["CUDA_DEVICE_ORDER"] = "PCI_BUS_ID"
os.environ["CUDA_VISIBLE_DEVICES"] = '1'
warnings.filterwarnings('ignore')
from keras.models import load_model
from keras.applications.imagenet_utils import decode_predictions
import mediapipe as mp
from board import evaluate_board

class BoardCamera:

    moving=[]
    chess_based_index=[]
    check_based_index=[]
    position_index=[]

    def __init__(self, side):
        self.ai_side = side
    
    def convert_image_to_bgr_numpy_array(self,image_path, size=(224, 224)):
        image = PIL.Image.open(image_path).resize(size)
        img_data = np.array(image.getdata(), np.float32).reshape(*size, -1)
        # swap R and B channels
        img_data = np.flip(img_data, axis=2)
        return img_data

    def prepare_image(self,image_path):
        im = self.convert_image_to_bgr_numpy_array(image_path)
        im = np.expand_dims(im, axis=0)
        return im
        
    def classify_cells(self,model, img_filename_list):
        category_reference = {0: 'chess', 1: 'empty'}
        self.pred_list = []
        self.fen=""
        try:
            for filename in img_filename_list:
                img = self.prepare_image("Output/"+str(filename))
                out = model.predict(img)
                top_pred = np.argmax(out)
                pred = category_reference[top_pred]
                # print(pred,filename)
                self.pred_list.append(pred)
                fen="0" if pred=="chess" else "1" if  pred=="empty" else None
        except:
            pass
        return fen

    def classify_cells2(self,model, img_filename_list):
        category_reference = {0: 'bishop', 1: 'king', 2: 'knight', 3: 'pawn', 4: 'queen', 5: 'rook'}
        self.pred_list = []
        self.fen=""
        try:
            for filename in img_filename_list:
                img = self.prepare_image("Output/"+str(filename))
                out = model.predict(img)
                top_pred = np.argmax(out)
                pred = category_reference[top_pred]
                # print(pred,filename)
                self.pred_list.append(pred)
                fen="b" if pred=="bishop"  else "k" if pred=="king" else "n" if pred=="knight" else "p" if pred=="pawn" else "q" if pred=="queen" else "r" if pred=="rook" else None
        except:
            pass
        return fen
        
    def classify_cells3(self,model, img_filename_list):
                category_reference = {0: 'bishop', 1:'empty',2: 'king', 3: 'knight', 4: 'pawn', 5: 'queen', 6: 'rook'}
                self.pred_list = []
                self.fen=""
                # print( img_filename_list)
                try:
                    for filename in img_filename_list:
                        img = self.prepare_image("Output/"+str(filename))
                        out = model.predict(img)
                        top_pred = np.argmax(out)
                        pred = category_reference[top_pred]
                        print(pred,filename)
                        self.pred_list.append(pred)
                        print(pred)
                        fen="b" if pred=="bishop" else "1" if pred=="empty" else "k" if pred=="king" else "n" if pred=="knight" else "p" if pred=="pawn" else "q" if pred=="queen" else "r" if pred=="rook" else None
                except:
                    pass
                return fen
    
    def main(self):
        State_check_chess=0
        self.pTime = 0
        self.cTime = 0
        direction = Borad_Direction()
        detection = SidePiece_Detection(colors='green')
        detection.colors_name='green'
        detection.load_jsonfile()
        detection.change_HSVBound_withDist_gain()
        vid = cv2.VideoCapture(0+cv2.CAP_DSHOW)
        vid.set(cv2.CAP_PROP_FPS, 30.0)
        vid.set(cv2.CAP_PROP_FOURCC, cv2.VideoWriter.fourcc('M', 'J', 'P', 'G'))
        vid.set(cv2.CAP_PROP_AUTOFOCUS, 0)
        vid.set(cv2.CAP_PROP_AUTO_WB, 0)
        vid.set(cv2.CAP_PROP_FOCUS, 2)
        vid.set(3,1920)
        vid.set(4,1080)
        self.count = 0
        self.export_size = 224
        mpHands = mp.solutions.hands
        hands = mpHands.Hands(static_image_mode=False,
                            max_num_hands=2,
                            min_detection_confidence=0.5,
                            min_tracking_confidence=0.5)
        mpDraw = mp.solutions.drawing_utils

        while(1):
            if State_check_chess==0:
                while True:
                    success, img = vid.read()
                    key=cv2.waitKey(1)
                    imgRGB = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
                    results = hands.process(imgRGB)
                    #print(results.multi_hand_landmarks)
                    if results.multi_hand_landmarks:
                        for handLms in results.multi_hand_landmarks:
                            for id, lm in enumerate(handLms.landmark):
                                #print(id,lm)
                                h, w, c = img.shape
                                cx, cy = int(lm.x *w), int(lm.y*h)
                                #if id ==0:
                                cv2.circle(img, (cx,cy), 3, (255,0,255), cv2.FILLED)
                            mpDraw.draw_landmarks(img, handLms, mpHands.HAND_CONNECTIONS)

                    cv2.imshow("Image", img)
                    cv2.waitKey(1)
                    if key ==ord(' '):
                        cv2.destroyAllWindows()
                        break
            # Destroy all the windows
                cv2.destroyAllWindows()
                State_check_chess=1     

            elif State_check_chess==1:
                direction = Borad_Direction()
                img = img
                clear_image, encoded_image, matrix = getMatrixFromImage(img)
                img,points,all_point=show_point_on_image(img, matrix)
                W,m=expandPerspective_IMG_Matrix (img,(np.array(points,dtype='float32')),offset = 35)
                rect = direction.convert_coord(m,points)
                new_img = direction.rotate_borad(img=W,points=rect,show=False)
                Crop_labels(new_img)
                output=""
                columns=["a","b","c","d","e","f","g","h"]
                colors=[]
                model = load_model("lnwpure_model_god.h5")
                result_fen=''
                for number in range(0,8):
                    for alphabet in columns:
                        fen = self.classify_cells3(model,[(alphabet+str(8-number)+".jpg")])
                        result_fen+=fen
                    result_fen+='/'
     
                result_fen=result_fen.replace('11','2').replace('111','3').replace('11111','5').replace('111111','6').replace('1111111','7')
                result_fen=result_fen.replace('22','4')
                result_fen=result_fen.replace('44','8')
                result_fen=result_fen.replace('41','5')
                result_fen=result_fen.replace('21','3')
                result_fen=result_fen.replace('43','7')
                result_fen=result_fen.replace('42','6')
                board=chess.Board(result_fen[:-1])
                new_fen = board.fen()
                print('board')
                print(board)
                State_check_chess=0
                return new_fen
    
    