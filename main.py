import sys
import Ui_backup
import paramiko
import os
import stat
import thread
import db
from PyQt5 import QtCore, QtGui, QtWidgets
class MainDialog(QtWidgets.QDialog, Ui_backup.Ui_Form, db.DB):
    def __init__(self, parent=None):
        super(MainDialog, self).__init__(parent)
        self.setupUi(self)
        self.DB()
        self.remotepath = "/backup"
        self.localpath = "/home/onuragtas/Workspace/backup/backup"
        self.ssh = paramiko.SSHClient()
        self.ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        self.connectButton.clicked.connect(self.connect)
        self.remoteList.itemClicked.connect(self.changeFolder)
        self.localList.itemClicked.connect(self.changeLocalFolder)
        self.servers.activated.connect(self.selectServer)
        self.backup.clicked.connect(self.backupF)
        self.stop.clicked.connect(self.stopf)

        self.backup.setEnabled(False)
        self.log.setText("disconnected")

        self.serverList = self.getServers()
        self.servers.clear()
        for item in self.serverList:
            self.servers.addItem(item[2]+"@"+item[1])

    def selectServer(self):
        self.server.setText(self.serverList[self.servers.currentIndex()][1])
        self.username.setText(self.serverList[self.servers.currentIndex()][2])
        self.password.setText(self.serverList[self.servers.currentIndex()][3])

        self.connect()

    def stopf(self):
        self.log.setText("disconnected")
        self.sftp2.close()
        self.backup.setEnabled(True)
        self.stop.setEnabled(False)

    def back(self):
        self.sftp2 = self.ssh.open_sftp()
        self.stop.setEnabled(True)
        self.sftp2.chdir(self.remotepath)
        dirs = self.sftp2.listdir()
        self.log.setText("listed...")
        for item in dirs:				
            remotesize = self.sftp.stat(item).st_size
            try:
                localsize = os.stat(self.localpath+"/"+item).st_size
            except OSError:
                localsize = 0
                
            if localsize != remotesize:
                self.log.setText(item+" downloading...")
                try:
                    self.sftp2.get(item,self.localpath+"/"+item)
                    self.log.setText(item+" finish")
                except:
                    self.log.setText(item+" disconnected")
            else:
                self.log.setText(item+" already downloaded.")

    def backupF(self):
        thread.start_new_thread(self.back,())

    def connect(self):
        try:
            self.ssh.connect(self.server.text(), username=self.username.text(), password=self.password.text(),allow_agent=False,look_for_keys=False)

            self.sftp = self.ssh.open_sftp()

            dirs = self.sftp.listdir()

            self.lpath.setText(self.localpath)
            self.rpath.setText(self.remotepath)

            self.remoteList.clear()
            self.localList.clear()

            self.remoteList.addItems(self.listDir(self.remotepath))
            self.localList.addItems(self.listLocalDir(self.localpath))

            self.log.setText("connected")
            self.backup.setEnabled(True)

            if self.checkServer(self.server.text(), self.username.text(), self.password.text()) == False:
                
                self.insertServer(self.server.text(), self.username.text(), self.password.text())

                self.serverList = self.getServers()
                self.servers.clear()
                for item in self.serverList:
                    self.servers.addItem(item[2]+"@"+item[1])

            selectedindex = 0
            i = 0
            for item in self.serverList:
                if self.server.text() == item[1]:
                    selectedindex = i
                i += 1
                
            self.servers.setCurrentIndex(selectedindex)

        except paramiko.ssh_exception.AuthenticationException:
            self.log.setText("not connect")
        

    def changeFolder(self):
        nowdir = self.remoteList.currentItem().text()
        try:
            fileattr = self.sftp.lstat(self.remotepath+"/"+nowdir)
            if stat.S_ISDIR(fileattr.st_mode):
                if nowdir != "..":
                    self.remotepath+="/"+nowdir
                else:
                    exp = self.remotepath.split("/")
                    end = exp[len(exp)-1]
                    self.remotepath = self.remotepath.replace("/"+end,"")

                items = []
                try:
                    items = self.listDir(self.remotepath)
                except:
                    print "error"

                if len(items) != 0:
                    self.remoteList.clear()
                    self.remoteList.addItems(items)
                    self.rpath.setText(self.remotepath)
        except:
            print "IOError"
        
    def changeLocalFolder(self):
        nowdir = self.localList.currentItem().text()
        if os.path.isdir(self.localpath+"/"+nowdir):
            if nowdir != "..":
                self.localpath+="/"+nowdir
            else:
                exp = self.localpath.split("/")
                end = exp[len(exp)-1]
                self.localpath = self.localpath.replace("/"+end,"")

            self.localList.clear()
            self.localList.addItems(self.listLocalDir(self.localpath))
            self.lpath.setText(self.localpath)
        

    def listDir(self, dir):
        array = []
        array.append("..")
        if dir == "":
            dir = "/"
        self.sftp.chdir(dir)
        dirs = self.sftp.listdir()
        dirs = sorted(dirs)
        for item in dirs:
            array.append(item)
        return array
    
    def listLocalDir(self, dir):
        array = []
        array.append("..")
        if dir == "":
            dir = "/"
        dirs = os.listdir(dir)
        dirs = sorted(dirs)
        for item in dirs:
            array.append(item)
        return array


app = QtWidgets.QApplication(sys.argv)
form = MainDialog()
form.show()
app.exec_()