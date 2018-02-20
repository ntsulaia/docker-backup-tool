import subprocess

#Create DcoekrContainer class for instantiation of docker container object with defined attributes
class DockerContainer:
    #Initiation function requires docker container ID to create uniquely identified container existing on the host
    def __init__(self, id):
        self.id = id          #container ID defined by docker system
        self.name = ""        #container name defined on docker system
        self.state = {}       #container state with two key:value pairs (container status (f.e. running, paused, exited), container running state (True/False))
        self.mounts = []      #container all mounts (volumes, binds)
        self.paused = False   #flag which indicates if running container was paused during backup process

    #setName() method assigns name attribute to DockerContainer class object based on container's name
    def setName(self):
        cmd = "/usr/bin/docker inspect --format '{{ .Name }}' %s"  #cli command to be used for retrieving container's name based on given ID
        p = subprocess.Popen(cmd % (self.id), stdout=subprocess.PIPE, shell=True) #executing cli command for given container ID
        (output, err) = p.communicate()  #getting output from cli command
        p_status = p.wait()
        self.name = str(output.decode('utf-8')).lstrip("/").strip() #assign retrieved container name to name attribute

    #setState() method assigns state attribute to DockerContainer class object based on container status
    def setState(self):
        cmd = ["/usr/bin/docker inspect --format '{{ .State.Status }}' %s", #cli command to retrieve container status
               "/usr/bin/docker inspect --format '{{ .State.Running }}' %s"] #cli command to retrieve container running status policy (true/false)
        p = subprocess.Popen(cmd[0] % (self.id), stdout=subprocess.PIPE, shell=True) #executing first cli command
        (output, err) = p.communicate() #getting output from cli command
        p_status = p.wait()
        self.state["status"] = str(output.decode('utf-8')).strip() #assign retrieved container state to state:status attribute
        p = subprocess.Popen(cmd[1] % (self.id), stdout=subprocess.PIPE, shell=True) #executing second cli command
        (output, err) = p.communicate() #getting output from cli command
        p_status = p.wait()
        self.state["running"] = str(output.decode('utf-8')).strip() #assign retrieved container running state policy (true/false) to state:running attribute

    #setMounts() method assigns mounts attribute to DockerContainer class object based on container mount points
    def setMounts(self, id):
        cmd = "/usr/bin/docker inspect --format '{{ range.Mounts }}{{ .Destination }} {{ end }}' %s" #cli command to retrieve mount points
        p = subprocess.Popen(cmd % (self.id), stdout=subprocess.PIPE, shell=True) #execute cli command
        (output, err) = p.communicate() #getting output from cli command
        p_status = p.wait()
        output = str(output.decode('utf-8')).strip().split(" ")
        for mount in output:
            if  mount != '':
                self.mounts.append(mount) #assign retrieved container mount points to mounts list attribute

    #getId() method retrieves DocketContainer class object id attribute value
    def getId(self):
        return self.id

    #getName() method retrieves DocketContainer class object name attribute value
    def getName(self):
        return self.name

    #getState() method retrieves DocketContainer class object state attribute values
    def getState(self):
        return self.state

    #getMounts() method retrieves DocketContainer class object mounts attribute values
    def getMounts(self):
        return self.mounts