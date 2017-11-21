import os
from PIL import Image
import numpy as np
import glob
import sys
import tempfile

# Class to handle experience saving. The class should take as input the total experiences
# in a run and save them to the correct "bucket". That is, the correct folder which is
# completely defined by the number of inputs given by sensors (ref, cam), and timesteps in MDP
# (number of previous states curent state is dependant on) and number of outputs given by
# the number of actions.
#
#These experiences can then be loaded and trained on.

class ExperienceHandler():

    def __init__(self, n_actions=3, ref=True, cam=True, timesteps=1, experiencefile="experienceFile.txt", default_experience_name="experience"):
        self.experience_file         = experiencefile
        self.experience_name         = default_experience_name

        self.timesteps = timesteps
        self.ref = ref
        self.cam = cam
        self.n_actions = n_actions

        if(cam):
            self.current_cam_state = []
            self.updated_cam_state = []
        if(ref):
            self.current_ref_state = []
            self.updated_ref_state = []
        self.action            = []
        self.reward            = []
        self.is_final_state    = []
        #self.file_number = self.modify_file(experiencefile)


    def modify_file(self, filename):
      dir_path = os.path.dirname(os.path.realpath(__file__))
      os.chdir(dir_path)
      #Create temporary file read/write
      t = tempfile.NamedTemporaryFile(mode="r+")

      #Open input file read-only
      i = open(filename, 'r')
      count = -1
      #Copy input file to temporary file, modifying as we go
      for line in i:
          count = int(line)
          count += 1
          t.write(str(count)+"\n")

      i.close()
      t.seek(0) #Rewind temporary file to beginning
      o = open(filename, "w")  #Reopen input file writable

      #Overwriting original file with temporary file contents
      for line in t:
           o.write(line)

      t.close()
      print(count)
      return count

    #experiences are build up of 5 or 7 columns (if cam = true)
    # index nunmber:
    # 0 action
    # 1 reward
    # 2 current_ref_state
    # 3 updated_ref_state
    # 4 is_final_state
    # 5 current_cam_state
    # 6 updated_cam_state
    def process_experiences(self, experiences):
        for experience in experiences:

            if(self.cam):
                self.current_cam_state.append(experience[5])
                self.updated_cam_state.append(experience[6])

            if(self.ref): #should always be true
                self.current_ref_state.append(experience[2])
                self.updated_ref_state.append(experience[3])

            self.is_final_state.append(experience[4])
            self.action.append(experience[0])
            self.reward.append(experience[1])


    def save_experiences_to_file(self, numpy_array):
        print("save from exphandl")
        dir_path = os.path.dirname(os.path.realpath(__file__))
        os.chdir(dir_path)
        count = self.modify_file(self.experience_file)
        print("saving array to:")
        print(dir_path)
        np.save(self.experience_name + str(count) + ".npy", numpy_array)
        pass


    def load_experiences(self):
        dir_path = os.path.dirname(os.path.realpath(__file__))
        os.chdir(dir_path)
        match = glob.glob(dir_path + "/*.npy")
        #print(match)
        if(len(match) != 0):
            flattened_array = []
            for array in match:
                print(array)
                numpy_array = np.load(array, encoding='bytes')
                print (numpy_array.shape)
                for exp in numpy_array:
                    flattened_array.append(exp)

            flattened_array = np.array(flattened_array)
            print(flattened_array.shape)
            return flattened_array

def __main__():
    expHandle = ExperienceHandler()
    # liste = [1,2,3]
    # liste = np.array(liste)
    # array = [[0,0,0,0,0,0], True, 2, [24.2], liste, "two"]
    # array.append(np.array([1, 0]))
    # array = np.array(array)
    # print(array.dtype)
    # expHandle.save_experiences_to_file(array)
    # dir_path = os.path.dirname(os.path.realpath(__file__))
    # os.chdir(dir_path)
    same_array = expHandle.load_experiences()
    print("array")
    print(same_array)

    pass

if __name__ == "__main__":
    __main__()
