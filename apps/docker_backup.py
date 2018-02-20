import argparse
import re
import dockerbackuputils
from dockerbackuputils import *

#get version of the package
def getVersion():
    with open("__init__.py") as file:
        return re.search(r"""__version__\s+=\s+(['"])(?P<ver>.+?)\1""",
                         file.read()).group("ver")

#volumeBackup() function takes arguments and options parsed from cli and executes appropriate volume backup
#(i.e. full, only-running or only for provided list)

def volumeBackup(args):
    if args.full:
        cList = getContainerList(getContainerIdList())
        if cList:
            dockerVolumeBackup(cList, args.backup_path, args.number_of_copies)
            print("\n **** Backup process of volumes successfully executed! **** \n")
        else:
            print("\n **** There is no container to backup! **** \n")
    elif args.only_running:
        cList = getRunningContainerList(getContainerIdList())
        if cList:
            dockerVolumeBackup(cList, args.backup_path, args.number_of_copies)
            print("\n **** Backup process of volumes successfully executed! **** \n")
        else:
            print("\n **** There is no running container to backup! **** \n")
    else:
        cList = getContainerList(getContainerListFromNames(getContainerNamesFromCLI(args.container_list)))
        if cList:
            dockerVolumeBackup(cList, args.backup_path, args.number_of_copies)
            print("\n **** Backup process of volumes successfully executed! **** \n")
        else:
            print("\n **** There is no container to backup! **** \n")


#imageBackup() function takes arguments and options parsed from cli and executes appropriate image backup
#(i.e. full or only for provided list)

def imageBackup(args):
    if args.full:
        iList = getImageList()
        if iList:
            dockerImageBackup(iList, args.backup_path, args.number_of_copies)
            print("\n **** Backup process of images successfully executed! **** \n")
        else:
            print("\n **** There is no image to backup! **** \n")
    else:
        iList = getImageListFromNames(getImageNamesFromCLI(args.image_list))
        if iList:
            dockerImageBackup(iList, args.backup_path, args.number_of_copies)
            print("\n **** Backup process of images successfully executed! **** \n")
        else:
            print("\n **** There is no image to backup! **** \n")


#create cli argument parser using python argparse framework

parser = argparse.ArgumentParser()
parser.add_argument("-v", "--version", action="version", version=getVersion()) #add "--version" option
subparsers = parser.add_subparsers()

volumeParser = subparsers.add_parser("volume")  #add subcommand "volume" for container volume backup
volumeParser.add_argument("-b", "--backup_path", help="absolute path to backup folder", required=True) #add --backup-path option
volumeParser.add_argument("-n", "--number_of_copies", help="number of backup copies to keep", type=int, required=True) #add --number-of-copies option
volumeParserGroup = volumeParser.add_mutually_exclusive_group(required=True) #add mutually exclusive arguments group
volumeParserGroup.add_argument("-a", "--full", action="store_true", help="backup all existing containers volumes") #add --full option to the group for full volume backup
volumeParserGroup.add_argument("-r", "--only_running", action="store_true", help="backup volumes only for running containers") #add --only_running option to the group for running containers volume backup
volumeParserGroup.add_argument("-l", "--container_list", help="comma separated list of container names enclosed in double quotes") #add --container_list option to the group
volumeParser.set_defaults(func=volumeBackup) #set default function for volume backup

imageParser = subparsers.add_parser("image") #add subcommand "image" for image backup
imageParser.add_argument("-b", "--backup_path", help="absolute path to backup folder", required=True) #add --backup-path option
imageParser.add_argument("-n", "--number_of_copies", help="number of backup copies to keep", type=int, required=True) #add --number-of-copies option
imageParserGroup = imageParser.add_mutually_exclusive_group(required=True) #add mutually exclusive arguments group
imageParserGroup.add_argument("-a", "--full", action="store_true", help="backup all existing images, excluding dangling") #add --full option to the group for full image backup
imageParserGroup.add_argument("-l", "--image_list", help="comma separated list of image names enclosed in double quotes") #add --image_list option to the group
imageParser.set_defaults(func=imageBackup) #set default function for image backup

#main function for docker-backup entry point
def mainfunc():
    args = parser.parse_args()
    args.func(args)

if __name__ == "__main__":
    mainfunc()
