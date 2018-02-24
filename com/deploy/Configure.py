import configparser
from com.deploy.User import User


class Configure:
    __hosts = []
    __users = []
    __configurePath = None
    __passwords = {}
    __tomcatHome = None
    __warHome = None

    def __init__(self, configurePath):
        self.__configurePath = configurePath
        if self.__configurePath == '' or self.__configurePath is None:
            self.__configurePath = "./configure.conf"
        self.read()

    def reload(self):
        self.__hosts.clear()
        self.__users.clear()
        self.__passwords.clear()
        self.read()

    def setConfigureFilePath(self, configurePath):
        self.__configurePath = configurePath
        if self.__configurePath == '' or self.__configurePath is None:
            self.__configurePath = "./configure.conf"

    def read(self):
        cf = configparser.ConfigParser()
        cf.read(self.__configurePath,encoding="utf-8")
        temp_host = cf.get("hosts", "hosts")
        temp_host = temp_host.split(",")
        for server in temp_host:
            self.__hosts.append(server)
        temp_password = cf.get("user", "password")

        temp_user = temp_host
        temp_password = temp_password.split(",")

        length = len(temp_user)

        for i in range(length):
            if len(temp_password) == 1:
                user = User(temp_user[i], temp_password[0])
                self.__users.append(user)
            else:
                user = User(temp_user[i], temp_password[i])
                self.__users.append(user)

        tomcatHome = cf.get("tomcat", "tomcatHome")
        warHome = cf.get("tomcat", "warHome")
        self.__tomcatHome = tomcatHome
        self.__warHome = warHome

    def getHosts(self):
        return self.__hosts[:]

    def getUsers(self):
        return self.__users[:]

    def getTomcatHome(self):
        return self.__tomcatHome

    def getWarHome(self):
        return self.__warHome

    def getPasswords(self):
        if len(self.__passwords) > 0:
            return self.__passwords
        for u in self.__users:
            self.__passwords[u.getUser()] = u.getPassword()
        return self.__passwords
