import subprocess

#Create DcoekrImage class for instantiation of docker image object with defined attributes
class DockerImage:
    # Initiation function requires docker image ID, name and tag to create uniquely identified image existing on the host
    def __init__(self, id, name, tag):
        self.id = id #image id defined by docker system
        self.name = name #image name defined on docker system
        self.tag = tag #image tag assigned on docker system

    #getId() method retrieves image id attribute
    def getId(self):
        return self.id

    #getName method retrieves image name attribute
    def getName(self):
        return self.name

    #getTag() method retrieves image tag attribute
    def getTag(self):
        return self.tag
