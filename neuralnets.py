from tflearn.layers.conv import conv_2d, max_pool_2d
from tflearn.layers.core import input_data, dropout, fully_connected
from tflearn.layers.estimator import regression
from tflearn.layers.merge_ops import merge
import tflearn
from constparimg import constantParametersImage, constantParametersNetwork


def conv_neural_network_model(name="conv_neural_network_model", imconstpar=constantParametersImage(), netconstpar=constantParametersNetwork()):

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

    convnet = regression(convnet, optimizer='adam', loss='categorical_crossentropy', name='targets')

    model = tflearn.DNN(convnet)

    return model

def conv_neural_network_model1(name="conv_neural_network_model1", shape=None, imconstpar=constantParametersImage(), netconstpar=constantParametersNetwork()):

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

    return model

def conv_reflectance_neural_network_model1(n_actions=3, name="conv_neural_network_model1", shape=None, imconstpar=constantParametersImage(), netconstpar=constantParametersNetwork()):

    convnet = input_data(shape=[None, imconstpar.height, imconstpar.width, imconstpar.channels], name='image_input')
    reflectance = tflearn.input_data(shape=[None, 1, 6, 1], name="reflectance_input")

    convnet = conv_2d(convnet, 32, 8, strides=4, activation='relu', name='conv1')
    #convnet = max_pool_2d(convnet, 2)

    convnet = conv_2d(convnet, 64, 4, strides=2, activation='relu', name='conv2')
    #convnet = max_pool_2d(convnet, 2)

    convnet = conv_2d(convnet, 64, 3, strides=1, activation='relu', name='conv3')
    #convnet = max_pool_2d(convnet, 2)


    convnet= fully_connected(convnet, 256, activation='relu', name='fc1')
    convnet = dropout(convnet, .8)

    convnet = fully_connected(convnet, 8, activation='softmax', name='fc2')

    merged_net = merge([convnet, reflectance], mode='concat', axis=0)
    #convnet = regression(convnet, optimizer='SGD', loss='categorical_crossentropy', name='targets')
    merged_net = fully_connected(merged_net, 128, activation='sigmoid', name='m_fc1')
    merged_net = fully_connected(merged_net, n_actions, activation='linear', name='m_fc2')
    merged_net = regression(merged_net, optimizer='adam', loss='categorical_crossentropy', name='targets')
    model = tflearn.DNN(merged_net)

    return model, name

def reflectance_neural_network_model(name="reflectance_neural_network_model", n_actions=5, shape=[None, 1, 6, 1]):
    ref = input_data(shape=shape, name='input')
    ref = fully_connected(ref, 64, activation='relu')
    ref = dropout(ref, .8)

    ref = fully_connected(ref, n_actions, activation='softmax')

    ref = regression(ref, optimizer='sgd', loss='categorical_crossentropy', name='targets')

    model = tflearn.DNN(ref)

    return model

def reflectance_neural_network_model3(n_actions=5, name="reflectance_neural_network_model3", shape=[None, 1, 18, 1]):
    ref = input_data(shape=shape, name='input')
    ref = fully_connected(ref, 32, activation='relu')
    ref = dropout(ref, .8)

    ref = fully_connected(ref, n_actions, activation='softmax')

    ref = regression(ref, optimizer='adam', loss='categorical_crossentropy', name='targets')

    model = tflearn.DNN(ref)

    return model

def reflectance_neural_network_model2(n_actions=5, name="reflectance_neural_network_model2", shape=[None, 1, 6, 1]):
    ref = input_data(shape=shape, name='input')

    ref = fully_connected(ref, n_actions, activation='tanh')

    ref = regression(ref, optimizer='sgd', loss='categorical_crossentropy', name='targets')

    model = tflearn.DNN(ref)

    return model
