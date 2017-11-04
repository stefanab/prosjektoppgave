import filehandle.modelSaver as ms
from tflearn.layers.conv import conv_2d, max_pool_2d
from tflearn.layers.core import input_data, dropout, fully_connected
from tflearn.layers.estimator import regression
import tflearn

modelS = ms.ModelSaver()

convnet = input_data(shape=[None, 1, 1, 1], name='input')

convnet = conv_2d(convnet, 32, 8, strides=4, activation='relu')
#convnet = max_pool_2d(convnet, 2)

convnet = conv_2d(convnet, 64, 4, strides=2, activation='relu')
#convnet = max_pool_2d(convnet, 2)

convnet = conv_2d(convnet, 64, 3, strides=1, activation='relu')
#convnet = max_pool_2d(convnet, 2)

convnet= fully_connected(convnet, 512, activation='relu')
convnet = dropout(convnet, .8)

convnet = fully_connected(convnet, 2, activation='softmax')

convnet = regression(convnet, optimizer='adam', loss='categorical_crossentropy', name='targets')

model = tflearn.DNN(convnet)


print("save")
modelS.save("tester.model", model)
