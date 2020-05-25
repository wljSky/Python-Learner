# -*- coding: utf-8 -*
# @fire 19.7.20
# update 19.12.15    @ change to class

import numpy as np
import cv2

import random
import os
import cv2
import numpy as np
from math import *
#import PIL
from PIL import ImageFont
from PIL import Image
from PIL import ImageDraw
from skimage import exposure


def getAllName(file_dir, tail_list = ['.jpg','.png']): 
    L=[] 
    for root, dirs, files in os.walk(file_dir):
        for file in files:
            if os.path.splitext(file)[1] in tail_list:
                L.append(os.path.join(root, file))
    return L

################# tool func
def randomVal(val):
    # np.random.random()：Return random floats in the half-open interval [0.0, 1.0).
    #返回0-val的随机值
    return int(np.random.random() * val)

def randomSmallerChance(n):
    #n-(0,1)  n的概率为真
    #>n:true <n:false
    t = random.random()
    if t<n:
        return True
    else:
        return False
##################################


class DataAugment(object):
    """docstring for ClassName"""
    def __init__(self, img):
        # img is opencv type
        self.img = img
        self.img_h = img.shape[0]
        self.img_w = img.shape[1]
        self.img_channel = img.shape[2]



    def imgPerspective(self):
        # 透视变换
        #### param zore ###
        factor = random.randint(int(self.img_h*0.12), int(self.img_h*0.16))
        ###################

        pts1 = np.float32([ [0, 0], 
                            [0, self.img_h], 
                            [self.img_w, 0], 
                            [self.img_w, self.img_h]])
        pts2 = np.float32([ [randomVal(factor) ,     randomVal(factor) ], 
                            [randomVal(factor) ,     self.img_h - randomVal(factor) ], 
                            [self.img_w - randomVal(factor) , randomVal(factor) ],
                            [self.img_w - randomVal(factor) , self.img_h - randomVal(factor) ]])
        M = cv2.getPerspectiveTransform(pts1, pts2)
        self.img = cv2.warpPerspective(self.img, M, (self.img_w, self.img_h))


    def imgChannel(self):
        # 通道变换(交换、复制)

        b, g, r = self.img[:,:,:1], self.img[:,:,1:2], self.img[:,:,2:3]

        if randomSmallerChance(0.1):
            b = b*random.random()
            b = b.astype('uint8')
        elif randomSmallerChance(0.2):
            g = g*random.random()
            g = g.astype('uint8')
        elif randomSmallerChance(0.3):
            r = r*random.random()
            r = r.astype('uint8')

        elif randomSmallerChance(0.4):
            b,g = g,b
        elif randomSmallerChance(0.6):
            r,g = g,r
        elif randomSmallerChance(0.8):
            b,r = r,b

        else:
            gray = r*0.299 + g*0.587 + b*0.114
            r,g,b = gray, gray, gray

        self.img = np.concatenate([b, g, r], axis=-1)


    def imgColor(self):
        # 色彩变换
        #### param zore ###

        ###################

        hsv = cv2.cvtColor(self.img,cv2.COLOR_BGR2HSV);
        hsv[:,:,0] = hsv[:,:,0]*(0.6+ np.random.random()*0.6);
        hsv[:,:,1] = hsv[:,:,1]*(0.6+ np.random.random()*0.8);
        hsv[:,:,2] = hsv[:,:,2]*(0.7+ np.random.random()*0.4);

        self.img = cv2.cvtColor(hsv,cv2.COLOR_HSV2BGR);


    def imgLight(self):         
        #图像亮度
        flag = random.uniform(1, 2)       
        self.img = exposure.adjust_gamma(self.img, flag) 


    def imgBlur(self):
        # 模糊
        #### param zore ###
        if self.img_h>100:
            
            blur_level = random.randint(2,3)
            ###################
            if random.random()<0.6:
                self.img = cv2.blur(self.img, (blur_level * 2 + 1, blur_level * 2 + 1))
            else:
                kernel_size = (5, 5)   
                sigma = 1.5   
                self.img = cv2.GaussianBlur(self.img, kernel_size, sigma)   


    def imgNoise(self):
        # 随机噪声

        def _addPepperandSalt(src):
            percetage=0.005+random.random()*0.03
            NoiseImg=src
            NoiseNum=int(percetage*src.shape[0]*src.shape[1])
            for i in range(NoiseNum):
                randX=random.randint(0,src.shape[0]-1)
                randY=random.randint(0,src.shape[1]-1)
                if random.randint(0,1)<=0.5:
                    NoiseImg[randX,randY]=0
                else:
                    NoiseImg[randX,randY]=255          
            return NoiseImg
  

        self.img = _addPepperandSalt(self.img)


    def imgShelter(self):
        # 随机遮挡区域
        #### param zore ###
        shelter_size = random.randint(int(self.img_h*0.14), int(self.img_h*0.2))
        shelter_num = int((int(self.img_h*0.22) - shelter_size)*0.1)
        color_random = False
        ###################

        if color_random:
            d = np.random.randint(0, 255, (shelter_size,shelter_size,self.img_channel))
        else:
            d = np.random.randint(0,255)*np.ones((shelter_size,shelter_size,self.img_channel))
        for i in range(shelter_num):
            x = random.randint(0, self.img_w - shelter_size - 1)
            y = random.randint(0, self.img_h - shelter_size - 1)
            self.img[y:y+shelter_size, x:x+shelter_size] = d


    ####### merge all ########
    def imgOutput(self):


        if randomSmallerChance(0.5):
            self.imgChannel()
        elif randomSmallerChance(0.9):
            self.imgColor()
        else:
            self.imgLight()

        if randomSmallerChance(0.8):
            self.imgPerspective()

        else:
            if randomSmallerChance(0.6):
                self.imgBlur()
            else:
                self.imgNoise()

        if randomSmallerChance(0.8):
            self.imgShelter()

        return self.img




def imgsAug(img_dir, target_num = 100):
    img_names = getAllName(img_dir)
    origin_num = len(img_names)
    print("origin_num: ",origin_num)
    if origin_num<target_num:
        aug_count = 0
        while aug_count < target_num-origin_num:
            if aug_count%500==0:
                print(aug_count)

            img_id = aug_count%origin_num
            img_name = img_names[img_id]

            img = cv2.imread(img_name)
            imgAug = DataAugment(img)
            img = imgAug.imgOutput()

            save_name = os.path.join(img_dir, "aug_"+str(aug_count)+"_"+os.path.basename(img_name))
            print(save_name)
            cv2.imwrite(save_name, img)

            aug_count+=1


if __name__ == '__main__':

    img_dir = "./t/2"
    imgsAug(img_dir)
