import tflearn
import tensorflow as tf
from tflearn.layers.conv import conv_2d, max_pool_2d
from tflearn.layers.core import input_data, dropout, fully_connected
from tflearn.layers.estimator import regression
from create_image_data_set import create_feature_sets_and_labels
import numpy as np
import sys
import os
from constparimg import constantParametersImage, constantParametersNetwork
# with open( "image_dataset.pickle", "rb" ) as f: # b for binary
    # train_x, train_y, test_x, test_y = pickle.load(f)

tf.logging.set_verbosity(tf.logging.ERROR)

constantsImg = constantParametersImage()
constantsNet = constantParametersNetwork()


train_x, train_y, test_x, test_y = create_feature_sets_and_labels('posBat','negBat')

print(len(train_y[0]))
n_classes = len(train_y[0])
n_epochs = constantsNet.n_epochs
b_size = constantsNet.batch_size
l_rate = constantsNet.learning_rate

shape = train_x[0].shape
print("shape")
print(shape)

print(train_y[0])
train_x = np.array(train_x)
train_y = np.array(train_y)
test_x = np.array(test_x)
test_y = np.array(test_y)

train_y = train_y.reshape([-1, 2])
train_x = train_x.reshape([-1, shape[0], shape[1], shape[2]])
test_x = test_x.reshape([-1, shape[0], shape[1], shape[2]])

##def create_conv_net(network_parameters):
##    shape = network_parameters.shape
##    n_classes = network_parameters.n
convnet = input_data(shape=[None, shape[0], shape[1], shape[2]], name='input')

convnet = conv_2d(convnet, 32, 8, strides=4, activation='relu')
#convnet = max_pool_2d(convnet, 2)

convnet = conv_2d(convnet, 64, 4, strides=2, activation='relu')
#convnet = max_pool_2d(convnet, 2)

convnet = conv_2d(convnet, 64, 3, strides=1, activation='relu')
#convnet = max_pool_2d(convnet, 2)

convnet= fully_connected(convnet, 512, activation='relu')
convnet = dropout(convnet, .8)

convnet = fully_connected(convnet, n_classes, activation='softmax')

convnet = regression(convnet, optimizer='adam', batch_size=b_size, learning_rate=l_rate, loss='categorical_crossentropy', name='targets')

model = tflearn.DNN(convnet)



if(len(sys.argv) > 1):
	model.load(sys.argv[1])

for target in test_y:
    print(target)

predictions = model.predict(test_x)
i=0
for pred in predictions:
	print("pair")
	print(pred)
	print(test_y[i])
	i +=1
#writer = tflearn.train.SummaryWriter(logs_path, graph=tf.get_default_graph())
model.fit({'input': train_x}, {'targets': train_y}, n_epoch=n_epochs, snapshot_epoch=1, show_metric=True, run_id='image_test')

model.save('tflearncnnBattery.model')
predictions = model.predict(test_x)
i=0
for pred in predictions:
	print("pair")
	print(pred)
	print(test_y[i])
	i +=1
