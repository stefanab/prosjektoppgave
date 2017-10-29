import numpy as np
import random
import pickle
import sys
from collections import Counter
from PIL import Image
import glob

def load_images(folder, classification):
    image_feature_list = []
    for image in glob.glob(folder +'/*'):
        
        im = np.array(Image.open(image), dtype=np.uint8)
        
        image_feature_list.append([im, classification])
        
    return image_feature_list
    


def create_feature_sets_and_labels(pos, neg, test_size=0.1):
    features = []
    features += load_images(pos, [0,1])
    features += load_images(neg, [1,0])
    random.shuffle(features)
    
    features = np.array(features)
    print("length is")
    print(len(features))
    testing_size = int(test_size*len(features))
    
    train_x = list(features[:,0][:-testing_size])
    train_y = list(features[:,1][:-testing_size])
    
    test_x  = list(features[:,0][-testing_size:])
    test_y  = list(features[:,1][-testing_size:])
    return train_x, train_y, test_x, test_y

if __name__ == '__main__':
    pos = sys.argv[1]
    neg = sys.argv[2]
    train_x, train_y, test_x, test_y = create_feature_sets_and_labels(pos, neg)
    with open('image_dataset.pickle', 'wb') as f:
        pickle.dump([train_x, train_y, test_x, test_y], f)
    