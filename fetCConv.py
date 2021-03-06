# -*- coding: utf-8 -*-
"""
Created on Thu Aug 17 09:33:26 2017
@author: 浩浩
"""
#fetCConv.py
#fetC指的是visualFetC，它引用了基于脸部的模型（归一化和框平滑之后）。
#This is the CNN trained over fetC.
from keras.models import Sequential
from keras.layers import Dense, Dropout, Activation, Flatten
from keras.layers import Convolution2D, MaxPooling2D, AveragePooling2D
from keras.optimizers import SGD
from keras.utils import np_utils, generic_utils
import keras.layers.normalization
import numpy as np
from readVideo import *
import random
from sklearn import preprocessing
from sklearn.externals import joblib
videoPath = r'E:/Video_for_test/'
videoPathTest= r'E:/Video_as_test/'
vidNames = os.listdir(videoPath)
vidNames = [x for x in vidNames if x.endswith(".mp4")]
vidNamesTest=os.listdir(videoPathTest)
vidNamesTest=[x for x in vidNamesTest if x.endswith('.mp4')]
fileName = r'E:/Video_for_test/training_gt.csv'
trueVal = getTruthVal(fileName)
for i in range(len(vidNames)):
	vidNames[i] = vidNames[i].strip('.mp4')
for i in range(len(vidNamesTest)):
	vidNamesTest[i] = vidNamesTest[i].strip('.mp4')
row,col=50,50
#splitVal = 0.9
#vidNamesTest = vidNames[int(splitVal*len(vidNames))+1:]
#vidNames = vidNames[:int(splitVal*len(vidNames))]
#X代表特征矩阵，Y代表标签
#每一个视频中，X的特征矩阵数量和Y的标签都是一样的
X_train, Y_train = readData(vidNames, trueVal, feature = 'C')
# X_test = X_test.reshape(X_test.shape[0], 3, row, col)

X_test, Y_test = readData(vidNamesTest, trueVal, feature = 'CT')

X_test = X_test.reshape(X_test.shape[0], 50, 50, 1)
X_test = X_test.astype('float32')
X_test /= 255
##转换下X_train格式，如果用batch可以注释掉
X_train = X_train.reshape(X_train.shape[0], 50, 50, 1)
X_train = X_train.astype('float32')
X_train /= 255
###可以读出X,Y,test,train了
numPerBatch = 1
numBatch = (len(vidNames)/numPerBatch)
#每隔多久存一次模型的权重，训练多的时候可以用
model_save_interval = 1
num_epochs = 100

model_file_name = 'E:/Video_for_test/models/fetC/32_64_256/visualFetC_Conv_Augmented_32_64_256'
##以后可能用到 visualFetC_Conv_Augmented_32_64_256&&visualFetC_Conv_48_96_256
model = Sequential()
# input: 100x100 images with 3 channels -> (3, 100, 100) tensors.
# this applies 64 convolution filters of size 3x3 each.

model.add(Convolution2D(32, 3, 3, border_mode='valid', input_shape=(row, col,1)))
model.add(Activation('relu'))
model.add(Convolution2D(32, 3, 3))
model.add(Activation('relu'))
model.add(MaxPooling2D(pool_size=(2, 2)))
# model.add(keras.layers.normalization.LRN2D())
model.add(Dropout(0.5))

model.add(Convolution2D(64, 3, 3, border_mode='valid'))
model.add(Activation('relu'))
model.add(Convolution2D(64, 3, 3))
model.add(Activation('relu'))
model.add(AveragePooling2D(pool_size=(2, 2)))
# model.add(keras.layers.normalization.LRN2D())
model.add(Dropout(0.5))
model.add(Flatten())
# Note: Keras does automatic shape inference.
model.add(Dense(256))
model.add(Activation('relu'))
model.add(Dropout(0.5))

model.add(Dense(5))
model.add(Activation('sigmoid'))

model.compile(loss='mean_absolute_error', optimizer='rmsprop')
# Prefer mean_absolute_error, since that is the one used for the challenge

# Saving model
jsonString = model.to_json()
open(model_file_name + '.json', 'w').write(jsonString)

minScore = 1.0

# raw_input('WAIT')

print ('Training started...')
for k in range(int(num_epochs)):
	#shuffle the data points before going through them
	random.shuffle(vidNames)
	progbar = generic_utils.Progbar(len(vidNames))

	for i in range(int(numBatch)):
		# Read numPerBatch files, get the images and answers

		# print 'Starting reading the batch'

		X_batch, Y_batch = readData(vidNames[(i*numPerBatch):((i+1)*numPerBatch)], trueVal, 'C')
		# print X_batch.shape
		X_batch = X_batch.reshape(X_batch.shape[0], 50, 50, 1)
		# print X_batch.shape
		# print 'Finished reading the batch'
		X_batch = X_batch.astype('float32')
		X_batch /= 255
		# Augment the data (Currently 15000 images per batch, try for 60000)

		# print 'Training on Batch'
		try:
			loss = model.train_on_batch(X_batch, Y_batch)
		# Train the model
		# print 'Finished training on Batch'

			progbar.add(numPerBatch, values=[("train loss", loss)])
		except:
			continue

	#print type(loss)
	if k%model_save_interval == 0:
		model.save_weights(model_file_name + '_epoch_{:02d}.hdf5'.format(k))

	score = model.evaluate(X_test, Y_test, verbose=0)
	print ("For epoch", k, ",Testing loss is", score)
	if minScore > score:
		model.save_weights(model_file_name + '.hdf5', overwrite = True)
		minScore = score