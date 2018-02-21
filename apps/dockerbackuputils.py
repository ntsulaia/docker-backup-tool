import subprocess
from DockerContainer import * #import all attributes and methods from DockerContainer class
from DockerImage import *     #import all attributes and methods from DockerImage class
import datetime
import os
import re

#getContainerIdList() function retrieves IDs of all containers and provides them in the list

def getContainerIdList():
    cmd = "/usr/bin/docker ps -aq"
    p = subprocess.Popen(cmd, stdout=subprocess.PIPE, shell=True)
    (output, err) = p.communicate()
    p_status = p.wait()
    output = str(output.decode('utf-8')).strip().split("\n")
    return output

#getContainerList() function takes previously obtained containers ID list and creates
# DockerContainer class objects for each ID

def getContainerList(containerIdList):
    containerList = []
    if containerIdList:
        for container in containerIdList:
            dockerContainer = DockerContainer(container) #DockerContainer class object instantiation with given ID
            dockerContainer.setName()                    #set name to DockerContainer class object
            dockerContainer.setState()                   #set DockerContainer class object state
            dockerContainer.setMounts(container)         #set DockerContainer class object mounts
            containerList.append(dockerContainer)        #add DockerContainer class object to containers list
    return containerList

#gerRunningContainerList() function takes previously obtained containers ID list and creates
# DockerContainer class objects for each ID with running state

def getRunningContainerList(containerIdList):
    runningContainerList = []
    for container in getContainerList(containerIdList):
        state = container.getState()                     #get container state attribute of DockerContainer class object
        if state["status"] == "running":                 #check if container state is "running"
            runningContainerList.append(container)       #if running state is true add DockerContainer class object to list
    return runningContainerList

#getContainerNamesFromCLI() function takes a string of container names provided by "--container-list" option from cli and
#transforms it into list

def getContainerNamesFromCLI(pattern):
    containerNameList = pattern.replace(" ", "").lstrip('"').rstrip('"').split(",")
    return containerNameList

#getContainerListFromNames() function takes previous container names list and transforms it into containers ID list
def getContainerListFromNames(containerNameList):
    cmd = "/usr/bin/docker ps -qa --filter=name=^/%s$"  #cli command to retrieve container IDs according to their names
    containerIdList = []
    if containerNameList:
        for name in containerNameList:
            p = subprocess.Popen(cmd % (name), stdout=subprocess.PIPE, shell=True) #execute cli command
            (output, err) = p.communicate()                                        #get result os cli command
            p_status = p.wait()
            if output:
                output = str(output.decode('utf-8')).strip()
                containerIdList.append(output)                                         #add container ID to list
    return containerIdList

#dockerContainerPause() function pauses containers with "running" status before starting volume backup process and sets
#container.paused flag to True

def dockerContainersPause(containerList):
    pause = "/usr/bin/docker container pause %s"
    for container in containerList:
        state = container.getState()
        if state["status"] == "running":
            p = subprocess.Popen(pause % (container.getId()), stdout=subprocess.PIPE, shell=True)
            (output, err) = p.communicate()
            p_status = p.wait()
            container.paused = True

#dockerContainerUnpause() function unpauses all previously paused containers after backup process is completed and sets
#container.paused flag to False

def dockerContainersUnpause(containerList):
    unpause = "/usr/bin/docker container unpause %s"
    for container in containerList:
        if container.paused:
            p = subprocess.Popen(unpause % (container.getId()), stdout=subprocess.PIPE, shell=True)
            (output, err) = p.communicate()
            p_status = p.wait()
            container.paused = False

#dockerVolumeBackup() is the main function which executes the process of containers volumes backup and stores backup files
#in predefined backup paths which is provided by "--backup-path" cli option
#Required parameters are the list of containers ID, backup path and number of copies to keep in backup path
#number of copies parameter prevents backup storage overfilling

def dockerVolumeBackup(containerList, backup_path, numberOfCopies):
    cmd = "/usr/bin/docker run --rm --volumes-from {0} -v {1}:/backup alpine tar cvf backup/{2}_{3}.tar {2}" #cli command which stores container volumes
    time = str(datetime.datetime.now().strftime("%Y-%m-%d_%H%M%S")) #timestamp to be added to backup file name
    dockerContainersPause(containerList)
    for container in containerList:
        if container.getMounts():
            containerBackupFolder = "{0}/{1}".format(backup_path, container.getName())
            if not os.path.isdir(containerBackupFolder):  # if provided backup path does not exist, it is created
                os.makedirs(containerBackupFolder)
            for mount in container.getMounts():
                backupFolder = "{0}/{1}".format(containerBackupFolder, mount.lstrip("/"))
                if not os.path.isdir(
                        backupFolder):  # if backup folder of container volume does not exist, it is created
                    os.makedirs(backupFolder)
                p = subprocess.Popen(cmd.format(container.getName(), backupFolder, mount.lstrip("/"), time),
                                     stdout=subprocess.PIPE, shell=True, cwd=containerBackupFolder)
                (output, err) = p.communicate()
                p_status = p.wait()
                dockerBackupsRotate(backupFolder, numberOfCopies)  # call the function to remove all old backup files
    dockerContainersUnpause(containerList)


# getImageList() function retrieves image ID, name and tag information for all existing images, creates DockerImage class
# object for each image and assigns its attributes

def getImageList():
    cmd = "/usr/bin/docker images --filter 'dangling=false' --format '{{ .ID }}->{{ .Repository }}->{{ .Tag }}'"
    imageList = []
    p = subprocess.Popen(cmd, stdout=subprocess.PIPE, shell=True)
    (output, err) = p.communicate()
    p_status = p.wait()
    output = str(output.decode('utf-8')).strip()
    if output != "":
        output = output.split("\n")
        if output:
            for item in output:
                item = item.split("->")
                dockerImage = DockerImage(item[0], item[1], item[2])
                imageList.append(dockerImage)
    return imageList


# getImageNamesFromCLI() function takes the string of images provided by "--image-list" cli option and transforms it into list
def getImageNamesFromCLI(pattern):
    imageNameList = pattern.replace(" ", "").lstrip('"').rstrip('"').split(",")
    return imageNameList


# getImageListFromNames() function takes image names list, retrieves ID, name and tag information for each of them, creates
# DockerImage class objct for each image and stores them in the list

def getImageListFromNames(imageNameList):
    cmd = "/usr/bin/docker images --format '{{ .ID }}_____{{ .Repository }}_____{{ .Tag }}' | grep '_____%s_____'"
    imageList = []
    if imageNameList:
        for imageName in imageNameList:
            p = subprocess.Popen(cmd % (imageName), stdout=subprocess.PIPE, shell=True)
            (output, err) = p.communicate()
            p_status = p.wait()
            output = str(output.decode('utf-8')).strip()
            if output != "":
                output = output.split("\n")
            if output:
                for item in output:
                    item = item.strip().split("_____")
                    dockerImage = DockerImage(item[0], item[1], item[2])
                    imageList.append(dockerImage)
    return imageList

# dockerImageBAckup(0 function is main function for image backup, which takes list of DockerImage class objects, backup path
# and number of backup copies to be kept in backup path.

def dockerImageBackup(imageList, backup_path, numberOfCopies):
    cmd = "/usr/bin/docker image save -o {0}/{1}.tar {2}:{3}"
    time = str(datetime.datetime.now().strftime("%Y-%m-%d_%H%M%S"))  # timestamp to be added to backup file name
    for image in imageList:
        backupFolder = "{0}/{1}_{2}".format(backup_path, image.getName().replace("/", "_"), image.getTag().replace("/", "_"))
        if not os.path.isdir(backupFolder):
            os.makedirs(backupFolder)  # if backup folder does not exist, it is created

        # backup file of the image contains image name. tag and timestamp. Image name can contain "/" character but image
        # filename can not, that's why all "/" characters are replaced by "_" character.

        backupFile = "{0}_{1}_{2}".format(image.getName().replace("/", "_"), image.getTag().replace("/", "_"), time)
        p = subprocess.Popen(cmd.format(backupFolder, backupFile, image.getName(), image.getTag()), stdout=subprocess.PIPE, shell=True)
        (output, err) = p.communicate()
        p_status = p.wait()
        dockerBackupsRotate(backupFolder, numberOfCopies)  # calls the function, which removes all old backup files

# dockerBackupRotate() function removes all old backup files and keeps only last n files provided by number of copies parameter
def dockerBackupsRotate(backup_path, numberOfCopies):
    files = os.listdir(backup_path)
    backupFiles = [f for f in files if f.endswith(".tar")]
    preserve = sorted(backupFiles)[-numberOfCopies:]
    for file in backupFiles:
        if file not in preserve:
            os.remove(os.path.join(backup_path, file))
