#!/usr/bin/env python
from time import sleep
import signal
import sys
import random as rdm
from filehandle.modelHandler import ModelHandler
import neuralnets
import tflearn
import tensorflow as tf
import constparimg as cpi
import numpy as np
from trainer import Trainer
from experiencehandle.experiencehandler import ExperienceHandler


def __main__():
    print("start")
    discount_factor = 0.8
    n_actions = 3
    constant            = cpi.constantParametersImage()
    constantNet            = cpi.constantParametersNetwork()

    print("setting up model")

    q_net, name         = neuralnets.ref2(n_actions=n_actions)

    print("creating trainer")

    trainer = Trainer(q_net, constant, constantNet, n_actions=n_actions)

    modelh = ModelHandler()
    exph   = ExperienceHandler()


    if(len(sys.argv) > 1):
        print("loading model")
        modelh.load(sys.argv[1], q_net)

    q_dash = q_net


    training = True

    experiences = exph.load_experiences()
    experi = np.array(experiences).shape
    print(experi)
    sleep(5)
    q_net = trainer.simulate_training(experiences, q_net)

    overwrite = False
    name += ".model"
    if(len(sys.argv) > 2):
        if(sys.argv[2] == 'o'):
            overwrite = True
        if(sys.argv[1] != name):
            print("input name does not match net name")
            name = sys.argv[1]

    modelh.save(name, q_net, overwrite = overwrite)

if __name__ == '__main__':
    __main__()
