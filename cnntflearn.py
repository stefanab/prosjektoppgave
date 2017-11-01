import tflearn
import tensorflow as tf
from tflearn.layers.conv import conv_2d, max_pool_2d
from tflearn.layers.core import input_data, dropout, fully_connected
from tflearn.layers.estimator import regression
from create_image_data_set import create_feature_sets_and_labels
import numpy as np
import sys
import os
# with open( "image_dataset.pickle", "rb" ) as f: # b for binary
    # train_x, train_y, test_x, test_y = pickle.load(f)

tf.logging.set_verbosity(tf.logging.ERROR)
	
train_x, train_y, test_x, test_y = create_feature_sets_and_labels('posbat','neg')
n_classes = 2
n_epochs = 1000
batch_size = 200
l_rate = 0.01


train_x = np.array(train_x)
train_y = np.array(train_y)
test_x = np.array(test_x)
test_y = np.array(test_y)
print(len(train_x[0]))

train_x = train_x.reshape([-1, 128, 96, 3])
test_x = test_x.reshape([-1, 128, 96, 3])


convnet = input_data(shape=[None, 128, 96, 3], name='input')

convnet = conv_2d(convnet, 32, 8, stride=4, activation='relu')
#convnet = max_pool_2d(convnet, 2)

convnet = conv_2d(convnet, 64, 4, stride=2, activation='relu')
#convnet = max_pool_2d(convnet, 2)

convnet = conv_2d(convnet, 64, 3, stride=1 activation='relu')
#convnet = max_pool_2d(convnet, 2)

convnet= fully_connected(convnet, 512, activation='relu')
convnet = dropout(convnet, .8)

convnet = fully_connected(convnet, n_classes, activation='softmax')

convnet = regression(convnet, optimizer='adam', learning_rate=l_rate, loss='categorical_crossentropy', name='targets')

model = tflearn.DNN(convnet)

if(len(sys.argv) > 1):
	model.load(sys.argv[1])
#writer = tflearn.train.SummaryWriter(logs_path, graph=tf.get_default_graph())
model.fit({'input': train_x}, {'targets': train_y}, n_epoch=n_epochs, validation_set=({'input': test_x}, {'targets': test_y}), snapshot_epoch=100, snapshot_step=100, show_metric=True, run_id='image_test')

model.save('tflearncnn.model')