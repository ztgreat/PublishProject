class User:
    __user = ''
    __password = ''

    def __init__(self, user, password):
        self.__user = user
        self.__password = password

    def setUser(self, user):
        self.__user = user

    def setPassword(self, password):
        self.__password = password

    def getUser(self):
        return self.__user

    def getPassword(self):
        return self.__password
