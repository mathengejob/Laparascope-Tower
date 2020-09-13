# USB camera display using PyQt and OpenCV, from iosoft.blog
# Copyright (c) Jeremy P Bentham 2019
# Please credit iosoft.blog if you use the information or software in it

VERSION = "Laparoscope v0.10"

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

IMG_SIZE    = 1280,720          # 640,480 or 1280,720 or 1920,1080
IMG_FORMAT  = QImage.Format_RGB888
DISP_SCALE  = 1
# Scaling factor for display image
DISP_MSEC   = 1                # Delay between display cycles
CAP_API     = cv2.CAP_ANY       # API: CAP_ANY or CAP_DSHOW etc...
EXPOSURE    = 0                 # Zero for automatic exposure
TEXT_FONT   = QFont("Courier", 10)

camera_num  = 1                 # Default camera (first in list)
image_queue = Queue.Queue()     # Queue to hold images
capturing   = True              # Flag to indicate capturing

# Grab images from the camera (separate thread)
def grab_images(cam_num, queue):
    cap = cv2.VideoCapture(cam_num-1 + CAP_API)
    cap.set(cv2.CAP_PROP_FRAME_WIDTH, IMG_SIZE[0])
    cap.set(cv2.CAP_PROP_FRAME_HEIGHT, IMG_SIZE[1])
    if EXPOSURE:
        cap.set(cv2.CAP_PROP_AUTO_EXPOSURE, 0)
        cap.set(cv2.CAP_PROP_EXPOSURE, EXPOSURE)
    else:
        cap.set(cv2.CAP_PROP_AUTO_EXPOSURE, 1)
    while capturing:
        if cap.grab():
            retval, image = cap.retrieve(0)
            if image is not None and queue.qsize() < 2:
                queue.put(image)
            else:
                time.sleep(DISP_MSEC / 1000.0)
        else:
            print("Error: can't grab camera image")
            break
    cap.release()

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

# Main window
class MyWindow(QMainWindow):
    text_update = pyqtSignal(str)

    # Create main window
    def __init__(self, parent=None):
        QMainWindow.__init__(self, parent)

        self.central = QWidget(self)
        self.control_side=QVBoxLayout()
        self.textbox = QTextEdit(self.central)
        self.textbox.setFont(TEXT_FONT)
        self.textbox.setMinimumSize(50, 50)
        self.text_update.connect(self.append_text)
        sys.stdout = self
        print("Camera number %u" % camera_num)
        print("Image size %u x %u" % IMG_SIZE)
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
        QPushButton
        {
        border-radius : 50;  
        border : 2px solid black
        }
               
        """
        
        app = QApplication(sys.argv)
        app.setStyleSheet(style)
        win = MyWindow()
        win.showFullScreen()
        win.setWindowTitle(VERSION)
        win.start()
        sys.exit(app.exec_())

#EOF