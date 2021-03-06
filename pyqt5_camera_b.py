# USB camera display using PyQt and OpenCV, from iosoft.blog
# Copyright (c) Jeremy P Bentham 2019
# Please credit iosoft.blog if you use the information or software in it

VERSION = "Laparoscope v0.10"
from datetime import datetime
import numpy as np
import os
import sys, time, threading, cv2
try:
    from PyQt5.QtCore import Qt
    pyqt5 = True
except:
    pyqt5 = False
if pyqt5:
    from PyQt5.QtCore import* #QTimer, QPoint, pyqtSignal,pyqtSlot
    from PyQt5.QtWidgets import* #QApplication, QMainWindow, QTextEdit, QLabel, QTabWidget,QPushButton
    from PyQt5.QtWidgets import * #QWidget, QAction, QVBoxLayout, QHBoxLayout,QGridLayout,QSizePolicy,QSpacerItem
    from PyQt5.QtGui import* # QFont, QPainter, QImage, QTextCursor,QIcon
else:
    from PyQt4.QtCore import Qt, pyqtSignal, QTimer, QPoint
    from PyQt4.QtGui import QApplication, QMainWindow, QTextEdit, QLabel
    from PyQt4.QtGui import QWidget, QAction, QVBoxLayout, QHBoxLayout
    from PyQt4.QtGui import QFont, QPainter, QImage, QTextCursor
try:
    import Queue as Queue
except:
    import queue as Queue

from PyQt5 import QtCore, QtGui, QtWidgets
IMG_SIZE    = 1280,720  # 640,480 or 1280,720 or 1920,1080
IMG_FORMAT  = QImage.Format_RGB888
DISP_SCALE  = 1
# Scaling factor for display image
DISP_MSEC   = 1                # Delay between display cycles
CAP_API     = cv2.CAP_ANY       # API: CAP_ANY or CAP_DSHOW etc...
EXPOSURE    = 0                 # Zero for automatic exposure
TEXT_FONT   = QFont("Courier", 10)
#logic = 1
camera_num  = 1                 # Default camera (first in list)
image_queue = Queue.Queue()     # Queue to hold images
capturing   = True              # Flag to indicate capturing
#video >>>>>>>>>>>>>>>
FileName='_.avi'
VIDEO_TYPE = {
'avi': cv2.VideoWriter_fourcc(*'XVID'),
#'mp4': cv2.VideoWriter_fourcc(*'H264'),
'mp4': cv2.VideoWriter_fourcc(*'XVID'),
}
STD_DIMENSIONS =  {
"480p": (640, 480),
"720p": (1280, 720),
"1080p": (1920, 1080),
"4k": (3840, 2160),
 }
res = '720p'
PickName =1
# Grab images from the camera (separate thread)
def grab_images(cam_num, queue):
    global cap
    global out
    cap = cv2.VideoCapture(cam_num-1 + CAP_API)
    cap.set(cv2.CAP_PROP_FRAME_WIDTH, IMG_SIZE[0])
    cap.set(cv2.CAP_PROP_FRAME_HEIGHT, IMG_SIZE[1])
    out = cv2.VideoWriter(FileName, MyWindow.get_video_type(FileName), 25, MyWindow.get_dims(cap, res))
    if EXPOSURE:
        cap.set(cv2.CAP_PROP_AUTO_EXPOSURE, 0)
        cap.set(cv2.CAP_PROP_EXPOSURE, EXPOSURE)
    else:
        cap.set(cv2.CAP_PROP_AUTO_EXPOSURE, 1)
    while capturing:
        if cap.grab():
            retval, image = cap.retrieve(0)
            #MyWindow.btnc.clicked.connect(cv2.imwrite(filename='ioi.jpg', img=cap))
            if image is not None and queue.qsize() < 2:
                queue.put(image)

            else:
                time.sleep(DISP_MSEC / 1000.0)
               
        
        else:
            print("Error: can't grab camera image")
            break
     
    cap.release()

#take photo

    
# Image widget
class ImageWidget(QWidget):
    def __init__(self, parent=None):
        super(ImageWidget, self).__init__(parent)
        self.image = None

    def setImage(self, image):
        self.image = image
        self.setMinimumSize(image.size())
        self.update()

    def paintEvent(self, event):
        qp = QPainter()
        qp.begin(self)
        if self.image:
            qp.drawImage(QPoint(0, 0), self.image)
        qp.end()
        
        
        #Login form
class LoginForm(QWidget):
    def __init__(self,parent=None):
        super().__init__()
        self.setWindowTitle('Patient Form')
        self.resize(400, 250)
        self.center()

        layout = QVBoxLayout()
             
 
        self.lineEdit_username = QLineEdit()
        self.lineEdit_username.setPlaceholderText('Please enter Patient name')
        self.lineEdit_username.setGeometry(QtCore.QRect(50, 150, 300, 30))
        layout.addWidget(self.lineEdit_username)



        self.button_login = QPushButton("Accept")
        self.button_login.clicked.connect(self.check_password)
        self.button_login.clicked.connect(MyWindow.DisplayPatient)
        self.button_login.clicked.connect(lambda:self.close())
        layout.addWidget(self.button_login)
        self.button_login.setGeometry(QtCore.QRect(160, 250, 75, 30))

        self.setLayout(layout)
       
        

    def check_password(self):
  
             #
        global PatientName
        PatientName= self.lineEdit_username.text()
        

                
          #app.quit()
    def center(self):
        qr = self.frameGeometry()
        cp = QDesktopWidget().availableGeometry().center()
        qr.moveCenter(cp)
        self.move(qr.topLeft())

    
# Main window
class MyWindow(QMainWindow):
    text_update = pyqtSignal(str)
    
   
    # Create main window
    def __init__(self, parent=None):
        QMainWindow.__init__(self, parent)
       # self.
        self.central = QWidget(self)
        self.control_side=QVBoxLayout()
        self.textbox = QTextEdit(self.central)
        self.textbox.setFont(TEXT_FONT)
        self.textbox.setMinimumSize(50, 50)
        self.text_update.connect(self.append_text)
        sys.stdout = self
        print("Camera number %u" % camera_num)
        self.logic = 0
        self.value = 1
        self.V_Logic=0
        self.ImageName=""
        
       
        
        #LoginForm.center(self)
        
        #PickName.valueChanged.connect(print(PickName))
            #print(PickName)



        if DISP_SCALE > 1:
            print("Display scale %u:1" % DISP_SCALE)

        self.vlayout = QVBoxLayout()        # Window layout
        self.displays = QHBoxLayout()
        self.control = QVBoxLayout()
        self.textboxs= QHBoxLayout()
        self.co2= QVBoxLayout()
        self.buttons =QVBoxLayout()
        self.disp = ImageWidget(self)
        self.controls= QTabWidget()
      

        self.vlayout.addLayout(self.displays)
        self.displays.addWidget(self.disp)
        self.label = QLabel(self)
       # self.displays.addLayout(self.control)
        self.displays.addLayout(self.textboxs)
        self.vlayout.addWidget(self.label)
        self.vlayout.addWidget(self.textbox)
        self.central.setLayout(self.vlayout)
        self.setCentralWidget(self.central)
        self.central.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.MinimumExpanding)
        self.displays.addLayout(self.control_side)
        self.control_side.addWidget(self.controls)
        self.control_side.addLayout(self.control)

 
 
        #widget

        self.Pictures=QWidget()
        self.Pictures.layout=QVBoxLayout()
        self.Pictures.setLayout(self.Pictures.layout)
        
        self.Videos=QWidget()
        self.Videos.layout=QVBoxLayout()
        self.Videos.setLayout(self.Videos.layout)
  
        
        self.controls.addTab(self.Pictures,"Pictures")
        self.controls.addTab(self.Videos,"Videos")

        #carbon
        self.control.addLayout(self.co2)      
                # C02(+)
        self.btnco2p= QPushButton('CO2+')
        self.btnco2p.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        self.co2.addWidget(self.btnco2p)
                #Labels
        self.setco2=QLabel("mmHg")
        self.co2.addWidget(self.setco2)
        self.setco2.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.MinimumExpanding)
        self.setco2.setAlignment(Qt.AlignCenter)
   
                # CO2(-)
        self.btnco2m= QPushButton('CO2-')
        self.co2.addWidget(self.btnco2m)
        self.btnco2m.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        

       
        self.mainMenu = self.menuBar()      # Menu bar
        exitAction = QAction('&Exit', self)
        exitAction.setShortcut('Ctrl+Q')
        exitAction.triggered.connect(self.close)
        self.fileMenu = self.mainMenu.addMenu('&File')
        self.fileMenu.addAction(exitAction)
        
        #spacers
        self.verticalSpacer = QSpacerItem(150, 100,QSizePolicy.Expanding)
        self.verticalSpacerb = QSpacerItem(70, 50,QSizePolicy.Expanding)
        #sizes
        size = QSize(60, 60)
        # Camera
        self.btnc= QPushButton('Capture')
        self.btnc.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.MinimumExpanding)
        self.Pictures.layout.addLayout(self.buttons)
        self.buttons.addWidget(self.btnc)
        self.buttons.addSpacerItem(self.verticalSpacer)
        self.btnc.setIcon(QIcon('camera.png'))
        #self.btnc.setStyleSheet("border-radius : 50;")
        self.btnc.setIconSize(size)


        #Video
        self.btnr= QPushButton('Record')
        self.btnr.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.MinimumExpanding)
        self.Videos.layout.addWidget(self.btnr)
        self.Videos.layout.addSpacerItem(self.verticalSpacerb)
        self.btnr.setIcon(QIcon('video.png'))
        self.btnr.setIconSize(size)
        
        self.btns= QPushButton('Stop')
        self.btns.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.MinimumExpanding)
        self.Videos.layout.addWidget(self.btns)
        self.btns.setIcon(QIcon('stop.png'))
        self.btns.setIconSize(size)
        self.Videos.layout.addSpacerItem(self.verticalSpacerb)
        
        self.btnc.clicked.connect(self.CaptureClicked)# Capture Photo trigger
        self.btnr.clicked.connect(self.RecordingClicked) # Recording Video trigger
        self.btns.clicked.connect(self.StopClicked)#Stop recording Trigger
        
    # capturing image
    def CaptureClicked(self):
        
        self.now = datetime.now()
        self.dt_string = self.now.strftime("%d_%m-%H_%M_%S")
        self.ImageName=PatientName+"-"+self.dt_string
        self.logic=2
        #print(self.ImageName)
        
        ##recording video
    def RecordingClicked(self):
        self.V_Logic=3
        self.FileName=self.ImageName+".avi"
    def StopClicked(self):
        self.V_Logic=4
        
    def change_res(cap, width, height):
        cap.set(3, width)
        cap.set(4, height)
    
    # grab resolution dimensions and set video capture to it.
    def get_dims(cap, res='720p'):
        width, height = STD_DIMENSIONS["480p"]
        if res in STD_DIMENSIONS:
            width,height = STD_DIMENSIONS[res]
        ## change the current caputre device
        ## to the resulting resolution
        MyWindow.change_res(cap, width, height)
        return width, height
    

    def get_video_type(FileName):
        FileName, ext = os.path.splitext(FileName)
        if ext in VIDEO_TYPE:
          return  VIDEO_TYPE[ext]
        return VIDEO_TYPE['avi']
    
    

        
    #>>>>>>>>>>>>>>>>>>>>>>>>
        
   
    # Start image capture & display
    def start(self):
        self.timer = QTimer(self)           # Timer to trigger display
        self.timer.timeout.connect(lambda: 
                    self.show_image(image_queue, self.disp, DISP_SCALE))
        self.timer.start(DISP_MSEC)         
        self.capture_thread = threading.Thread(target=grab_images, 
                    args=(camera_num, image_queue))
        self.capture_thread.start()         # Thread to grab images

    # Fetch camera image from queue, and display it
    def show_image(self, imageq, display, scale):
        if not imageq.empty():
            image = imageq.get()
            if image is not None and len(image) > 0:
                img = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
                self.display_image(img, display, scale)
                
                #capturing
                if (self.logic==2):
                   self.value=self.value+1
                   cv2.imwrite('%s.jpg'%self.ImageName,image)
                   print('your Image have been Saved')
                   self.logic=1
                #else:
                   #print("error printing")
                #video recording
                if (self.V_Logic==3):
                   out.write(image)
                   print("Recording...")
                
                if (self.V_Logic==4):
                   out.release()
                   print("Recording Stopped.")
                   self.V_Logic=0
                    
                
    def DisplayPatient(self):
       # self.setco2.setText(B.PatientName)
        print("Patient Name:", PatientName)
 
  

    # Display an image, reduce size if required
    
    def display_image(self, img, display, scale=1):
        disp_size = img.shape[1]//scale, img.shape[0]//scale
        disp_bpl = disp_size[0] * 3
        if scale > 1:
            img = cv2.resize(img, disp_size, 
                             interpolation=cv2.INTER_CUBIC)
        qimg = QImage(img.data, disp_size[0], disp_size[1], 
                      disp_bpl, IMG_FORMAT)
        display.setImage(qimg)

    # Handle sys.stdout.write: update text display
    def write(self, text):
        self.text_update.emit(str(text))
    def flush(self):
        pass

    # Append to text display
    def append_text(self, text):
        cur = self.textbox.textCursor()     # Move cursor to end of text
        cur.movePosition(QTextCursor.End) 
        s = str(text)
        while s:
            head,sep,s = s.partition("\n")  # Split line at LF
            cur.insertText(head)            # Insert text at cursor
            if sep:                         # New line if LF
                cur.insertBlock()
        self.textbox.setTextCursor(cur)     # Update visible cursor

    # Window is closing: stop video capture
    def closeEvent(self, event):
        global capturing
        capturing = False
        self.capture_thread.join()

if __name__ == '__main__':
    if len(sys.argv) > 1:
        try:
            camera_num = int(sys.argv[1])
        except:
            camera_num = 0
    if camera_num < 1:
        print("Invalid camera number '%s'" % sys.argv[1])
    else:
        style = """

            QPushButton {
            color: #333;
            border: 2px solid #555;
            border-radius: 40px;
            border-style: outset;
            background: qradialgradient(
            cx: 0.3, cy: -0.4, fx: 0.3, fy: -0.4,
            radius: 1.35, stop: 0 #fff, stop: 1 #888
            );
            padding: 5px;
            }

            QPushButton:hover {
            background: qradialgradient(
            cx: 0.3, cy: -0.4, fx: 0.3, fy: -0.4,
            radius: 1.35, stop: 0 #fff, stop: 1 #bbb
            );
            }

            QPushButton:pressed {
            border-style: inset;
            background: qradialgradient(
            cx: 0.4, cy: -0.1, fx: 0.4, fy: -0.1,
            radius: 1.35, stop: 0 #fff, stop: 1 #ddd
            );
            }


        QWidget
         {
         background:#0e3360;
         
         color:white;
         font: bold large "FreeMono";
         font-size:30px;
         }
        QLabel::setCo2
        {
           text-align: centre;
        }
        QLabel
        {
        color:white;
        border: 1px solid white;
        
        border: radius:4px;
        }
        QPushButton::
        {
        border-radius : 50;  
        border : 2px solid black
        }
               
        """
        import sys
        app = QApplication(sys.argv)
        app.setStyleSheet(style)
        Form2 = LoginForm()
        Form2.setStyleSheet("#Qwidget{\n"
"background-color:white\n"
"\n"
"}\n"
"\n"
"QLineEdit{\n"
"border:none;\n"
"border-bottom:1px solid rgba(0,0,0,.2);\n"
"background-color:transparent;\n"

"         font-size:22px;"
"}\n"
"\n"
"QLineEdit:hover{\n"
"border:none;\n"
"border-bottom:1px solid black;\n"
"background-color:transparent;\n"
"}\n"
"\n"
"QFrame{\n"
"background-color:transparent;\n"
"}\n"
"\n"
"\n"
"\n"
""
"QPushButton{\n"
"border-radius:10px;\n"
"background-color:cadetblue;\n"
"color:white;\n"
"font-size:25px;"
"}\n"
"\n"
"QPushButton:hover{\n"
"border-radius:10px;\n"
"background-color:grey;\n"
"color:black;\n"
"border:1px solid black;\n"
"\n"
"}"                        
)
        
         #.start()
        #Form2.show()
        layout = QStackedLayout()
        win = MyWindow()
        win.show()
        win.setWindowTitle(VERSION)
        win.start()
        Form2.show()
        sys.exit(app.exec_())

#EOF