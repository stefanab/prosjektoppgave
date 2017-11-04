import os



class ModelSaver():

    def __init__(self, modelfile="modelFile.txt"):
        self.modelfile = modelfile


    def save(self, name, model, overwrite=False):
        if(overwrite):
            ## Sjekk om en fil allerede finnes
            ## Dersom navnet finnes bruk modelfile til å hente neste nummer som garantert ikke er brukt
            ## Lagre netverksmodellen som med model.save
        else:
            ## Lagre modellen med model.save
