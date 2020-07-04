import sys
from PyQt5.QtWidgets import (QApplication, QWidget, QPushButton,
                             QTextEdit, QLineEdit, QVBoxLayout,
                             QHBoxLayout, QFrame, QSpacerItem,
                             QSizePolicy, QProgressBar, QLabel)
from PyQt5.QtCore import pyqtSlot, QProcess
import subprocess
from mutagen.mp3 import MP3
import os

def colonTime(seconds):
    """Convert seconds to readable time"""
    sec = seconds % 60
    seconds = int(seconds / 60)
    mins = seconds % 60
    seconds = int(seconds / 60)
    final = ''
    if seconds:
        final += '{:02d}:'.format(seconds)
    if mins or seconds:
        final += '{:02d}:'.format(mins)
    final += '{:02d}'.format(sec)
    return final

class App(QWidget):
    def __init__(self):
        super().__init__()
        self.title = 'audiosplitter'
        self.initUI()
        self.scan_mp3()        
        self.process = QProcess(self)
    
    def initUI(self):
        self.setWindowTitle(self.title)

        ### UI
        self.vbox = QVBoxLayout(self)

        ## Left screen
        self.hbox = QHBoxLayout()        

        self.textBox = QTextEdit()
        
        self.hbox.addWidget(self.textBox)

        ## Right screen
        self.vbox2 = QVBoxLayout()

        fileHbox = QHBoxLayout()
        fpathLabel = QLabel()
        fpathLabel.setText("File:")
        self.filePath = QLineEdit("input.mp3", self)
        fileHbox.addWidget(fpathLabel)
        fileHbox.addWidget(self.filePath)

        line = QFrame()
        line.setFrameShape(QFrame.HLine)
        line.setFrameShadow(QFrame.Sunken)

        artistHbox = QHBoxLayout()
        artistLabel = QLabel()
        artistLabel.setText("Artist:")
        self.artist = QLineEdit("", self)
        artistHbox.addWidget(artistLabel)
        artistHbox.addWidget(self.artist)

        albumHbox = QHBoxLayout()
        albumLabel = QLabel()
        albumLabel.setText("Album:")
        self.album = QLineEdit("", self)
        albumHbox.addWidget(albumLabel)
        albumHbox.addWidget(self.album)
        
        button = QPushButton('Start', self)
        button.clicked.connect(self.start)

        button2 = QPushButton('Rescan for mp3', self)
        button2.clicked.connect(self.scan_mp3)

        self.logWindow = QTextEdit()
        self.logWindow.setReadOnly(True)

        self.vbox2.addLayout(fileHbox)
        self.vbox2.addWidget(line)
        self.vbox2.addLayout(artistHbox)
        self.vbox2.addLayout(albumHbox)
        self.vbox2.addWidget(button)
        self.vbox2.addWidget(button2)        
        self.vbox2.addWidget(self.logWindow)

        self.hbox.addLayout(self.vbox2)

        ## Bottom screen
        self.progress = QProgressBar()
        self.progress.setValue(0)

        
        self.vbox.addLayout(self.hbox)        
        self.vbox.addWidget(self.progress)
        self.show()


    @pyqtSlot()
    def start(self):
        """Start button handler"""
        times = self.textBox.toPlainText()
        f = self.filePath.text()
        artist = self.artist.text()
        album = self.album.text()

        audio = MP3(f)
        duration = colonTime(int(audio.info.length))

        times = [x.strip().split(' - ') for x in times.split('\n')]

        for x in range(len(times)):
            current = times[x]
            finish = duration if x == len(times) - 1 else times[x+1][1]
            self.logWindow.append(current[0])

            subprocess.run([
                'ffmpeg',
                '-i', f,
                '-ss', current[1],
                '-to', finish,

                '-metadata', 'artist={}'.format(artist),
                '-metadata', 'album={}'.format(album),
                '-metadata', 'title={}'.format(current[0]),
                '-metadata', 'track={}/{}'.format(x+1, len(times)),
                
                '-acodec', 'copy',
                '{:02d} {} - {}.mp3'.format(x+1, artist, current[0]),
                '-vsync', '2'
            ])


            self.progress.setValue(int(100 / len(times) * (x+1)))

    @pyqtSlot()
    def scan_mp3(self):
        """Scans current directory for mp3 files, returns first found"""
        l = list(filter(lambda x: x.endswith('.mp3'), os.listdir()))
        if l: self.filePath.setText(l[0])
        else: self.filePath.setText("")
            
        

                                  

if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = App()
    sys.exit(app.exec_())
