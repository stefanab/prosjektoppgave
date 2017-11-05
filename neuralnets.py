from tflearn.layers.conv import conv_2d, max_pool_2d
from tflearn.layers.core import input_data, dropout, fully_connected
from tflearn.layers.estimator import regression
import tflearn
from constparimg import constantParametersImage, constantParametersNetwork



def conv_neural_network_model1(shape=None, imconstpar=constantParametersImage(), netconstpar=constantParametersNetwork()):

    convnet = input_data(shape=[None, imconstpar.height, imconstpar.width, imconstpar.channels], name='input')

    convnet = conv_2d(convnet, 32, 8, strides=4, activation='relu')
    #convnet = max_pool_2d(convnet, 2)

    convnet = conv_2d(convnet, 64, 4, strides=2, activation='relu')
    #convnet = max_pool_2d(convnet, 2)

    convnet = conv_2d(convnet, 64, 3, strides=1, activation='relu')
    #convnet = max_pool_2d(convnet, 2)

    convnet= fully_connected(convnet, 512, activation='relu')
    convnet = dropout(convnet, .8)

    convnet = fully_connected(convnet, 2, activation='softmax')

    convnet = regression(convnet, optimizer='SGD', loss='categorical_crossentropy', name='targets')

    model = tflearn.DNN(convnet)

def reflectance_neural_network_model(shape=[None, 1, 6, 1]):
    ref = input_data(shape=shape, name='input')
    ref = fully_connected(ref, 64, activation='relu')
    convnet = dropout(convnet, .8)

    convnet = fully_connected(convnet, 8, activation='softmax')

    convnet = regression(convnet, optimizer='sgd', loss='categorical_crossentropy', name='targets')

    model = tflearn.DNN(convnet)
