import sys
import os
import time
from fabric.api import *

sys.path.insert(0, '../../')
from com.deploy.Configure import Configure


class Deploy:
    tomcatHome = None
    warHome = None

    def __init__(self):
        self.conf = Configure(None)
        self.setHost(self.conf.getHosts(), self.conf.getPasswords())
        self.tomcatHome = self.conf.getTomcatHome()
        self.warHome = self.conf.getWarHome()

    def reloadConfigure(self):
        self.conf.reload()
        self.setHost(self.conf.getHosts(), self.conf.getPasswords())
        self.tomcatHome = self.conf.getTomcatHome()
        self.warHome = self.conf.getWarHome()

    def setHost(self, hosts, passwords):
        if hosts is None or passwords is None:
            env.hosts = self.conf.getHosts()
            env.passwords = self.conf.getPasswords()
            return
        env.hosts = hosts
        env.passwords = passwords

    def ls(self):
        try:
            for server in env.hosts:
                with settings(host_string=server):
                    run("ls", pty=False, timeout=5)
        except Exception as e:
            print("执行失败:", e)

    def start(self):
        for server in env.hosts:
            with settings(host_string=server):
                try:
                    result = self.getTomcatStatus(server)
                    if result:
                        print("(%s)的tomcat已经启动" % server)
                        continue
                    print("启动(%s)上的tomcat" % server)
                    run(self.tomcatHome + "/bin/startup.sh", pty=False)
                    time.sleep(5)
                except Exception as e:
                    print("执行失败:", e)

    def restart(self):
        self.stop()
        self.start()

    def stop(self):
        for server in env.hosts:
            with settings(host_string=server):
                try:
                    result = self.getTomcatStatus(server)
                    if not result:
                        print("(%s)上的tomcat已经关闭" % server)
                        continue
                    print("关闭(%s)上的tomcat..." % server)
                    run(self.tomcatHome + "/bin/shutdown.sh", pty=False)
                    time.sleep(10)
                except Exception as e:
                    print("执行失败:", e)

    # 列出所有可部署的项目
    def getAllProjectList(self):
        projectList = []
        fileList = os.listdir(self.warHome)
        for f in fileList:
            newFile = os.path.join(self.warHome, f)
            if os.path.isfile(newFile):
                file = os.path.splitext(f)
                if file[1] == '.war':
                    projectList.append(file[0])
        return projectList

    def deployProject(self, projectName):

        for server in env.hosts:
            print("正在部署服务器：" + server + " 项目名：" + projectName)
            with settings(host_string=server):
                self.deploy_one_server(projectName)
                print("部署服务器 " + server + " 项目" + projectName + " 完成!")

    def deploy_one_server(self, projectName):
        warfilename = projectName + ".war"
        print("上传文件到tomcat根目录...")
        with lcd(self.warHome):
            with cd(self.tomcatHome):
                put(warfilename, warfilename)
        # 停止tomcat
        # self.stop()

        print("删除原有的部署文件...")
        with cd(self.tomcatHome + "/webapps/"):
            run("rm -rf " + "'" + projectName + "'")
            run("rm -rfv " + "'" + warfilename + "'")

        print("正在将已上传的文件放到tomcat项目目录")
        with cd(self.tomcatHome):
            run("mv " + "'" + warfilename + "'" + " ./webapps/")
        print("项目上传完成")
        print("(%s)项目部署完成..." % projectName)

    def removeProject(self, projectName):
        warfilename = projectName + ".war"
        for server in env.hosts:
            with settings(host_string=server):
                with cd(self.tomcatHome + "/webapps/"):
                    try:
                        run("rm -rf " + "'" + projectName + "'")
                        run("rm -rfv " + "'" + warfilename + "'")
                        print("删除(%s)上部署的(%s)项目" % (server, projectName))
                    except Exception as e:
                        print("执行失败:", e)

    def tomcatStatus(self):
        command = "ps -ef | grep tomcat | grep -v grep | awk '{print $2}'"
        resultDict = {}
        for server in env.hosts:
            with settings(host_string=server):
                try:
                    result = run(command, pty=False, timeout=5)
                    resultDict[server] = result
                except Exception as e:
                    print("执行失败:", e)
        return resultDict

    def getTomcatStatus(self, server):
        command = "ps -ef | grep tomcat | grep -v grep | awk '{print $2}'"
        with settings(host_string=server):
            try:
                result = run(command, pty=False, timeout=5)
                if result == '':
                    return False
            except Exception as e:
                print("执行失败:", e)
                return False
        return True

    def showServer(self):

        servers = self.conf.getHosts()
        serverIndex = 0
        for server in servers:
            print(str(serverIndex) + "." + server)
            serverIndex += 1
        print(str(serverIndex) + ".all")
        return serverIndex

    def showWebApp(self):
        try:
            for server in env.hosts:
                with settings(host_string=server):
                    result = run("ls " + self.tomcatHome + "/webapps/", pty=False, timeout=5)
        except Exception as e:
            print("执行失败:", e)

    @staticmethod
    def goOn():
        input("Press enter key to continue...")

    @staticmethod
    def showFunction():
        message = '''
        1.选择服务器              2.开启tomcat
        3.关闭tomcat              4.重启tomcat
        5.查看tomcat状态          6.部署项目
        7.重新加载配置文件        8.查看已部署的项目
        9.退出                   10.删除部署的项目
                 '''
        print(message)

    def function(self):
        while (True):
            Deploy.showFunction()
            index = None
            while True:
                try:
                    index = int(input("请输入序号:"))
                    break
                except ValueError:
                    continue

            # 选择服务器
            if index == 1:
                self.showServer()
                serverInput = None
                while True:
                    try:
                        serverInput = input("请输入服务器序号:")
                        serverInput = serverInput.split(",")
                        for i, value in enumerate(serverInput):
                            serverInput[i] = int(value)
                            if serverInput[i] > len(self.conf.getHosts()):
                                raise ValueError("输入有误")
                        break
                    except ValueError:
                        continue

                if len(serverInput) == 1 and serverInput[0] == len(self.conf.getHosts()):

                    # 所有
                    self.setHost(None, None)

                else:
                    server = []
                    temp_passwords = {}
                    for i in serverInput:
                        if i < len(self.conf.getHosts()):
                            temp_server = self.conf.getHosts()[i]
                            server.append(temp_server)
                            temp_password = self.conf.getPasswords()[temp_server]
                            temp_passwords[temp_server] = temp_password
                    self.setHost(server, temp_passwords)

            elif index == 2:
                # 开启tomcat
                self.start()
                Deploy.goOn()
            elif index == 3:
                # 关闭tomcat
                self.stop()
                Deploy.goOn()
            elif index == 4:
                # 重启tomcat
                self.restart()
                Deploy.goOn()
            elif index == 5:
                # 查看tomcat状态
                resultDict = self.tomcatStatus()
                for key in resultDict:
                    if resultDict[key] == '':
                        print("(%s)上的tomcat已经关闭" % key)
                    else:
                        print("(%s)上的tomcat已经开启" % key)
                Deploy.goOn()
            elif index == 6:
                # 部署项目
                projectList = self.getAllProjectList()
                if len(projectList) == 0:
                    print("没有项目可供部署,请检查设置路径")
                    Deploy.goOn()
                    continue

                print("项目列表:")
                for i, name in enumerate(projectList):
                    print(str(i) + "." + name)
                print(str(len(projectList)) + ".all")
                print(str(len(projectList) + 1) + ".返回")
                projectIndex = None
                while True:
                    try:
                        projectIndex = input("请输入项目序号:")
                        projectIndex = projectIndex.split(",")
                        for i, value in enumerate(projectIndex):
                            projectIndex[i] = int(value)
                            if projectIndex[i] > len(projectList) + 1:
                                raise ValueError("输入有误")
                        break
                    except ValueError:
                        continue
                if len(projectIndex) == 1 and projectIndex[0] >= len(projectList):
                    if projectIndex[0] == len(projectList):
                        # 所有
                        for name in projectList:
                            self.deployProject(name)
                    else:
                        continue

                else:
                    # 单个或多个
                    for i in projectIndex:
                        self.deployProject(projectList[i])

                Deploy.goOn()

            elif index == 7:
                # 重新加载配置文件
                self.reloadConfigure()
            elif index == 8:
                # 查看已部署的项目
                self.showWebApp()
                Deploy.goOn()
            elif index == 9:
                # 退出
                break
            elif index == 10:

                projectName = input("请输入需要删除的项目名称:")
                confire = input("确认删除项目(%s)y/n?" % projectName)
                if confire == 'y' or confire == 'Y':
                    self.removeProject(projectName)
                    Deploy.goOn()
                else:
                    pass

            elif index == 100:
                # 测试
                self.ls()


if __name__ == "__main__":
    d = Deploy()
    d.function()
