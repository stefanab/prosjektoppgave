import tflearn
import tensorflow as tf
from tflearn.layers.conv import conv_2d, max_pool_2d
from tflearn.layers.core import input_data, dropout, fully_connected
from tensorflow.examples.tutorials.mnist import input_data as id
from tflearn.layers.estimator import regression
from create_image_data_set import create_feature_sets_and_labels
import numpy as np
import sys
import mnist
import os
# with open( "image_dataset.pickle", "rb" ) as f: # b for binary
    # train_x, train_y, test_x, test_y = pickle.load(f)


mnist = id.read_data_sets("/tmp/data/", one_hot=True)
train_x, train_y, test_x, test_y = create_feature_sets_and_labels('posMugsmall','negMugsmall')
n_classes = 10
n_epochs = 10
b_size = 128
l_rate = 0.01


train_x = mnist.train.images
train_y = mnist.train.labels
test_x = mnist.test.images
test_y = mnist.test.labels
# for i in range(1):
	# print("pair")
	# print(train_x[i])
	# print(train_y[i])
	# print("pair")
	# print(test_x[i])
	# print(test_y[i])

train_x = train_x.reshape([-1, 28, 28, 1])
test_x = test_x.reshape([-1, 28, 28, 1])
print(train_y[0])
train_y = train_y.reshape([-1, 10])
test_y = test_y.reshape([-1, 10])

convnet = tf.placeholder('float', [None, 784])
y = tf.placeholder('float')
convnet = tf.reshape(convnet, shape=[-1, 28, 28, 1])
convnet = input_data(shape=[None, 28, 28, 1], name='input')

convnet = conv_2d(convnet, 32, 2, strides=1, activation='relu')
#convnet = max_pool_2d(convnet, 2)

convnet = conv_2d(convnet, 64, 2, strides=1, activation='relu')
#convnet = max_pool_2d(convnet, 2)

convnet = conv_2d(convnet, 64, 2, strides=1, activation='relu')
#convnet = max_pool_2d(convnet, 2)

convnet= fully_connected(convnet, 512, activation='relu')
convnet = dropout(convnet, .8)

convnet = fully_connected(convnet, n_classes, activation='softmax')

convnet = regression(convnet, optimizer='adam', batch_size=b_size, learning_rate=l_rate, loss='categorical_crossentropy', name='targets')

model = tflearn.DNN(convnet)

if(len(sys.argv) > 1):
	model.load(sys.argv[1])
#writer = tflearn.train.SummaryWriter(logs_path, graph=tf.get_default_graph())

model.fit({'input': train_x}, {'targets': train_y}, n_epoch=n_epochs, 
#validation_set=({'input': test_x}, {'targets': test_y}), \
snapshot_epoch=1, show_metric=True, run_id='image_test')
model.save('tflearncnnmnist.model')
predictions = model.predict(test_x)
for pred in predictions:
	print(pred)

 