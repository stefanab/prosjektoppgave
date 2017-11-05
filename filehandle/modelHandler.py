import os
import glob
import tempfile
import sys
import tflearn


class ModelHandler():

    def __init__(self, modelfile="modelFile.txt", default_model_name="defaultModel"):
        self.modelfile        = modelfile
        self.default_model_name = default_model_name

    def modify_file(self, filename):

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

    def load(self, name, model):
        dir_path = os.path.dirname(os.path.realpath(__file__))
        os.chdir(dir_path)
        return model.load(name)

    def save(self, name, model, overwrite=False):
        if(not overwrite):
            # Find courrent directory and check if there already exists a file
            # with the specified name
            print("checking directory for model...")
            dir_path = os.path.dirname(os.path.realpath(__file__))
            os.chdir(dir_path)
            print(dir_path)
            match = glob.glob(dir_path + "/" + name + ".index")

            if(len(match) != 0):
                print("file name already exsists...")
                print("saving model with another name...")
                count = self.modify_file(self.modelfile)

                if(count == -1):
                    print("count was not set. You should rename your model file")

                model.save(self.default_model_name + str(count) + ".model")

            else:
                print("model name not taken")

                model.save(name)

            ## Sjekk om en fil allerede finnes
            ## Dersom navnet finnes bruk modelfile til å hente neste nummer
            ## som garantert ikke er brukt og lag en ny fil med inkrementert verdi
            ## Lagre netverksmodellen som med model.save
        else:
            model.save(name)
            ## Lagre modellen med model.save
