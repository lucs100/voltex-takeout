#from PyQt6.QtWidgets import QMainWindow, QWidget, QVBoxLayout, QTabWidget, QGroupBox, QGridLayout, QLabel, QLineEdit, QPushButton, QFileDialog, QMessageBox, QCheckBox, QSizePolicy, QFrame, QApplication
from PyQt6.QtWidgets import *
from PyQt6.QtGui import QIcon
from PyQt6.QtCore import QObject, QThread, pyqtSignal, Qt
import asphyxia_db as engine
from subprocess import CalledProcessError

#to get cmd line args
import sys, os

#Based on https://github.com/lucs100/shtickerpack/blob/main/src/client.py
#TODO: there is a TON of hanging/unused code here thanks to this. it's fine though

#dummy syscall to get taskbar icon LOL
try:
    import ctypes
    myappid = 'lucs100.VoltexTakeout' # arbitrary string
    ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID(myappid)
except ImportError:
    pass

KONAMI_WEB_LINK = "https://p.eagate.573.jp/game/sdvx/vi/index.html"
DOWNLOAD_GUIDE_LINK = "https://github.com/lucs100/voltex-takeout/blob/master/csv_guide.md"

DB_LOAD_HELP_STR = ("We first need to load the database, so we can check which users exist.<br>"
                   "It's likely stored in <b>.../SOUND VOLTEX EXCEED GEAR/contents/savedata/</b>.")

CSV_LOAD_HELP_STR = ("Next we need to load your data file.<br>"
                    f"This should be the official data download from <a href='{KONAMI_WEB_LINK}'>Konami</a>.<br>"
                    "<b>Note:</b> you need the e-amusement Basic Course subscription to get this file. "
                    f"A guide is provided <a href='{DOWNLOAD_GUIDE_LINK}'>here</a>.")

DB_WRITE_HELP_STR = ("Finally we need to write to the database. We'll take a backup first.")

APP_NAME = "VoltexTakeout"
ORG_NAME = "lucs100"
APP_VER = "0.1"

#Globals
saveData: engine.SaveData|None = None #initialize to none, will be modified later
arcadeData: engine.pd.DataFrame|None = None #initialize to none, will be modified later

#create a custom subclassed window
class VoltexTakeoutMainWindow(QMainWindow):
    def __init__(self):
        #call the init method of QMainWindow
        super().__init__()

        self.setWindowTitle(f"{APP_NAME} v{APP_VER}")
        if getattr(sys, 'frozen', False):
            iconPath = os.path.join(sys._MEIPASS, "./src/assets/VoltexTakeout.png")
        else: iconPath = "./assets/VoltexTakeout.png"
        print(iconPath)
        self.setWindowIcon(QIcon(iconPath))
        self.setFixedSize(500, 350)

        self.mainContainer = QWidget()
        self.layout = QVBoxLayout()

        self.tabs = QTabWidget()
        self.tabs.resize(500, 600)

        self.tab1 = QWidget()
        self.tab2 = QWidget()
        self.tab3 = QWidget()

        INFO_GROUP_HEIGHT = 120

        # define our entire tabs
        self.dbLoadPanel = VoltexTakeoutInfoTray(DB_LOAD_HELP_STR)
        self.dbLoadInfoGroup = VoltexTakeoutTitledPanel(self.dbLoadPanel, "Database load instructions")
        self.dbLoadInfoGroup.setFixedHeight(INFO_GROUP_HEIGHT)
        self.dbLoadPanel = VoltexTakeoutDBLoadTray(self)
        self.dbLoadGroup = VoltexTakeoutTitledPanel(self.dbLoadPanel, "Load database file")
        self.tab1.layout = QVBoxLayout()
        self.tab1.layout.addWidget(self.dbLoadInfoGroup)
        self.tab1.layout.addWidget(self.dbLoadGroup)
        self.tab1.setLayout(self.tab1.layout)
        self.tabs.addTab(self.tab1, "Step 1 [Load database]")

        self.csvLoadPanel = VoltexTakeoutInfoTray(CSV_LOAD_HELP_STR)
        self.csvLoadInfoGroup = VoltexTakeoutTitledPanel(self.csvLoadPanel, "Arcade data load instructions")
        self.csvLoadInfoGroup.setFixedHeight(INFO_GROUP_HEIGHT)
        self.csvLoadPanel = VoltexTakeoutCSVLoadTray(self)
        self.csvLoadGroup = VoltexTakeoutTitledPanel(self.csvLoadPanel, "Load arcade data")
        self.tab2.layout = QVBoxLayout()
        self.tab2.layout.addWidget(self.csvLoadInfoGroup)
        self.tab2.layout.addWidget(self.csvLoadGroup)
        self.tab2.setLayout(self.tab2.layout)
        self.tabs.addTab(self.tab2, "Step 2 [Load arcade data]")
        
        self.dbWritePanel = VoltexTakeoutInfoTray(DB_WRITE_HELP_STR)
        self.dbWriteInfoGroup = VoltexTakeoutTitledPanel(self.dbWritePanel, "Database write instructions")
        self.dbWriteInfoGroup.setFixedHeight(INFO_GROUP_HEIGHT)
        self.dbWritePanel = VoltexTakeoutDBWriteTray(self)
        self.dbWriteGroup = VoltexTakeoutTitledPanel(self.dbWritePanel, "Write to DB")
        self.tab3.layout = QVBoxLayout()
        self.tab3.layout.addWidget(self.dbWriteInfoGroup)
        self.tab3.layout.addWidget(self.dbWriteGroup)
        self.tab3.setLayout(self.tab3.layout)
        self.tabs.addTab(self.tab3, "Step 3 [Write to database]")

        # self.tabs.setTabEnabled(1, False)
        # self.tabs.setTabEnabled(2, False)

        self.layout.addWidget(self.tabs)
        self.mainContainer.setLayout(self.layout)
        self.setCentralWidget(self.mainContainer)

        self.show()

class VoltexTakeoutTitledPanel(QGroupBox):
    def __init__(self, layout: QGridLayout, title: str):
        super().__init__(title) #sets title to identifier
        self.setLayout(layout)

class VoltexTakeoutInfoTray(QGridLayout):
    def __init__(self, helpLabel: str, identifier: str = "InfoTray"):
        super().__init__()

        self.identifier = identifier
        self.helpLabel = QLabel(helpLabel, wordWrap=True)
        self.helpLabel.setOpenExternalLinks(True)
        self.addWidget(self.helpLabel, 0, 0)

class VoltexTakeoutDBLoadTray(QGridLayout):
    def __init__(self, parentWindow: QMainWindow, identifier: str = "DBLoadTray"):
        super().__init__()

        self.parentWindow = parentWindow
        self.identifier = identifier

        # self.dbInputDirHint = QLabel("SDVX savedata location:")
        # self.dbInputDirHint.setFixedWidth(150)
        # self.dbInputDirPath = QLabel("(None)")

        self.dbInputBrowseButton = QPushButton("Select file...")
        # self.dbInputBrowseButton.setFixedWidth(150)
        self.dbInputBrowseButton.clicked.connect(lambda:self.openLoadDB(self.dbInputBrowseButton))

        self.dbLoadStatusLabel = QLabel("Database status:", alignment=Qt.AlignmentFlag.AlignRight|Qt.AlignmentFlag.AlignVCenter)
        # self.dbLoadStatusLabel.setFixedWidth(200)
        self.dbLoadStatusValue = QLabel("Not yet loaded")

        self.statsKeysLabel = QLabel("Keys:", alignment=Qt.AlignmentFlag.AlignRight|Qt.AlignmentFlag.AlignVCenter)
        self.statsUsersLabel = QLabel("Users:", alignment=Qt.AlignmentFlag.AlignRight|Qt.AlignmentFlag.AlignVCenter)
        self.statsPlaysLabel = QLabel("Plays:", alignment=Qt.AlignmentFlag.AlignRight|Qt.AlignmentFlag.AlignVCenter)
        # self.dbLoadStatusLabel.setFixedWidth(200)
        self.statsKeysValue = QLabel("--")
        self.statsUsersValue = QLabel("--")
        self.statsPlaysValue = QLabel("--")
        

        # self.addWidget(self.dbInputDirHint, 0, 0)
        # self.addWidget(self.dbInputDirPath, 0, 1)
        self.addWidget(self.dbInputBrowseButton, 0, 0, 1, 2)

        self.addWidget(self.dbLoadStatusLabel, 1, 0, 2, 1)
        self.addWidget(self.dbLoadStatusValue, 1, 1, 2, 1)

        self.addWidget(self.statsKeysLabel, 0, 2)
        self.addWidget(self.statsKeysValue, 0, 3)
        self.addWidget(self.statsUsersLabel, 1, 2)
        self.addWidget(self.statsUsersValue, 1, 3)
        self.addWidget(self.statsPlaysLabel, 2, 2)
        self.addWidget(self.statsPlaysValue, 2, 3)

        self.setContentsMargins(8, 16, 8, 16)
    
    def openLoadDB(self, button: QPushButton):
        fp, fileFilter = QFileDialog.getOpenFileName(
            None,
            caption = "Select savedata file...",
            directory = "C:",
            filter = "Asphyxia CORE Database (*.db);;All Files (*)"
        )
        print(f"File: {fp}")
        if fp == '':
            return

        # Checks ok, we can proceed
        # oldText = button.text()
        # button.setText("Loading... just a sec!")
        print("Beginning load...")
        # button.setEnabled(False)
        
        try:
            global saveData
            saveData = engine.SaveData(fp)
        except Exception as e:
            msg = QMessageBox.critical(None, "Error!", 
                                      f"<b>Data load failed:</b><br>{e}")
            return False
        assert saveData is not None, "No save data was returned."
        print(saveData)

        # Set button and text states on success (wow this sucks)
        self.dbLoadStatusValue.setText("Loaded!")
        self.dbLoadStatusValue.setStyleSheet("color: green")
        self.statsKeysValue.setText(str(len(saveData.keys)))
        self.statsUsersValue.setText(str(len(saveData.getProfiles())))
        self.statsPlaysValue.setText(str(len(saveData.getPlayData())))

        self.parent().parent().parent().parent().setTabEnabled(1, True)
        # self.dbInputDirPath.setText(fp)
        # button.setEnabled(True)
        # button.setText(oldText)
    
    def getSaveData(self, button: QPushButton):
        return

        # Old thread-based code, probably not neccesary

        # self.thread = QThread()
        # self.worker = UnpackWorker(sourceDir=sourceDir, destinationDir=destinationDir)
        # self.worker.moveToThread(self.thread)
        # self.thread.started.connect(self.worker.run)
        # self.worker.success.connect(self.thread.quit)
        # self.thread.finished.connect(self.worker.deleteLater)
        # self.worker.result.connect(self.handleUnpackResult)
        # self.thread.start()
        
        # #setup triggers for when thread is done
        # self.thread.finished.connect(
        #     lambda: button.setEnabled(True)
        # )
        # self.thread.finished.connect(
        #     lambda: button.setText("Go!")
        # )
        
class VoltexTakeoutCSVLoadTray(QGridLayout):
    def __init__(self, parentWindow: QMainWindow, identifier: str = "CSVLoadTray"):
        super().__init__()

        self.parentWindow = parentWindow
        self.identifier = identifier
       
        # self.csvInputDirHint = QLabel("Arcade data location:")
        # self.csvInputDirHint.setFixedWidth(150)
        # self.csvInputDirPath = QLabel("(None)")
        self.csvInputBrowseButton = QPushButton("Select e-amuse export...")
        # self.csvInputBrowseButton.setFixedWidth(150)
        self.csvInputBrowseButton.clicked.connect(lambda: self.openLoadCSV(self.csvInputBrowseButton))
        
        self.csvLoadStatusLabel = QLabel("Arcade CSV status:", alignment=Qt.AlignmentFlag.AlignRight|Qt.AlignmentFlag.AlignVCenter)
        # self.csvLoadStatusLabel.setFixedWidth(150)
        self.csvLoadStatusValue = QLabel("Not yet loaded")

        self.statsSongsLabel = QLabel("Songs:", alignment=Qt.AlignmentFlag.AlignRight|Qt.AlignmentFlag.AlignVCenter)
        self.statsSongsValue = QLabel("--")

        # self.addWidget(self.csvInputDirHint, 0, 0)
        # self.addWidget(self.csvInputDirPath, 0, 1, 1, 2)
        self.addWidget(self.csvInputBrowseButton, 0, 0, 1, 2)
        
        self.addWidget(self.csvLoadStatusLabel, 1, 0, 2, 1)
        self.addWidget(self.csvLoadStatusValue, 1, 1, 2, 1)

        self.addWidget(self.statsSongsLabel, 1, 2)
        self.addWidget(self.statsSongsValue, 1, 3)
        
        self.setContentsMargins(8, 16, 8, 16) 

    def openLoadCSV(self, button: QPushButton):
        fp, fileFilter = QFileDialog.getOpenFileName(
            None,
            caption = "Select arcade data file...",
            directory = "C:",
            filter = "e-amuse Data Export (*.csv);;All Files (*)"
        )
        print(f"File: {fp}")
        if fp == '':
            return

        # Checks ok, we can proceed
        # oldText = button.text()
        # button.setText("Loading... just a sec!")
        print("Beginning load...")
        # button.setEnabled(False)
        
        try:
            global arcadeData
            arcadeData = engine.loadScores(fp)
            
        except Exception as e:
            msg = QMessageBox.critical(None, "Error!", 
                                      f"<b>Data load failed:</b><br>{e}")
            return False
        assert arcadeData is not None, "No save data was returned."
        print(arcadeData)

        # Set button and text states on success (wow this sucks)
        self.csvLoadStatusValue.setText("Loaded!")
        self.csvLoadStatusValue.setStyleSheet("color: green")
        self.statsSongsValue.setText(str(len(arcadeData)))

        # self.parent().parent().parent().parent().setTabEnabled(2, True) #ugh..
        # self.csvInputDirPath.setText(fp)
        # self.csvInputDirPath.setText(str(fp))
        # button.setEnabled(True)
        # button.setText(oldText)

class VoltexTakeoutDBWriteTray(QGridLayout):
    def __init__(self, parentWindow: QMainWindow, identifier: str = "DBWriteTray"):
        super().__init__()

        self.parentWindow = parentWindow
        self.identifier = identifier
        # self.DEFAULT_INPUT_DIR = f"C:\\Users\\{os.getlogin()}\\AppData\\Local\\Corporate Clash\\resources\\default"
        # self.DEFAULT_OUTPUT_DIR = f"C:\\Users\\{os.getlogin()}\\AppData\\Local\\Corporate Clash\\resources\\vanilla"

        self.inputDirHint = QLabel("SDVX savedata location:")
        self.inputDirHint.setFixedWidth(150)
        self.inputDirPath = QLineEdit()
        self.inputBrowseButton = QPushButton("Select input folder...")
        self.inputBrowseButton.clicked.connect(self.openInputFileDialog)
        # self.defaultInputButton = QPushButton("Use default input folder")
        # self.defaultInputButton.clicked.connect(self.setDefaultInputDir)

        self.outputDirHint = QLabel("Place output folders in:")
        self.outputDirHint.setFixedWidth(150)
        self.outputDirPath = QLineEdit()
        self.outputBrowseButton = QPushButton("Select output folder...")
        self.outputBrowseButton.clicked.connect(self.openOutputFileDialog)
        # self.defaultOutputButton = QPushButton("Use vanilla output folder")
        # self.defaultOutputButton.clicked.connect(self.setDefaultOutputDir)

        self.defaultHybridButton = QPushButton("Autoset output")
        self.defaultHybridButton.clicked.connect(self.setDefaultInputDir)
        self.defaultHybridButton.clicked.connect(self.setDefaultOutputDir)
        
        self.unpackButton = QPushButton("Go!")
        self.unpackButton.setFixedSize(189, 121)
        self.unpackButton.clicked.connect(lambda:self.unpackTargetDir(self.unpackButton))
        #print(f"Unpack - H: {self.unpackButton.height()}, W: {self.unpackButton.width()}")

        self.addWidget(self.inputDirHint, 0, 0)
        self.addWidget(self.outputDirHint, 1, 0)
        self.addWidget(self.inputDirPath, 0, 1, 1, 2)
        self.addWidget(self.outputDirPath, 1, 1, 1, 2)

        self.addWidget(self.defaultHybridButton, 2, 0, 1, 4)
        # self.addWidget(self.defaultInputButton, 3, 0, 1, 2)
        # self.addWidget(self.defaultOutputButton, 3, 2, 1, 2)
        
        self.addWidget(self.inputBrowseButton, 0, 3)
        self.addWidget(self.outputBrowseButton, 1, 3)

        self.addWidget(self.unpackButton, 0, 4, 3, 1)
        self.unpackButton.setMaximumHeight(999)

        self.setContentsMargins(8, 16, 8, 16)
    
    def openInputFileDialog(self):
        dir = QFileDialog.getExistingDirectory(
            None,
            caption = "Select input phase file folder...",
            directory = f"C:\\Users\\{os.getlogin()}\\AppData\\Local\\Corporate Clash\\resources\\default"
        )
        if dir:
            path = pathlib.Path(dir)
            self.inputDirPath.setText(str(path))
            print(f"Selected {path} in tray {self.identifier}")

    def openOutputFileDialog(self):
        dir = QFileDialog.getExistingDirectory(
            None,
            caption = "Select output phase file folder...",
            directory = f"C:\\Users\\{os.getlogin()}\\AppData\\Local\\Corporate Clash\\resources"
        )
        if dir:
            path = pathlib.Path(dir)
            self.outputDirPath.setText(str(path))
            print(f"Selected {path} in tray {self.identifier}")

    def setDefaultInputDir(self):
        self.inputDirPath.setText(self.DEFAULT_INPUT_DIR)

    def setDefaultOutputDir(self):
        self.outputDirPath.setText(self.DEFAULT_OUTPUT_DIR)
    
    def handlePathErrors(self, inputPath: str, outputPath: str) -> bool:
        if inputPath == "":
            msg = QMessageBox.warning(None, "No input!", "Select an input folder first.")
            return False
        if outputPath == "":
            msg = QMessageBox.warning(None, "No outut!", "Select an output folder first.")
            return False
        if inputPath == outputPath:
            msg = QMessageBox.warning(None, "Warning!", "The input and output folders can't be the same.")
            return False
        return True
    
    def handleUnpackResult(self, result: "ThreadResult"):
        msg = result.messageType(None, result.title, result.text)
    
    def unpackTargetDir(self, button: QPushButton):
        sourceDir = self.inputDirPath.text()
        destinationDir = self.outputDirPath.text()

        if not self.handlePathErrors(sourceDir, destinationDir):
            return False
        
        if not os.path.exists(destinationDir):
            os.mkdir(destinationDir)

        if not engine.checkOutputDirectoryValid(destinationDir):
            msg = QMessageBox.warning(None, "Alert!", 
                "The output folder doesn't exist or already has phase folders inside!")
            return
        
        #checks ok, we can proceed
        button.setText("Unpacking... just a sec!")
        print("Beginning unpack...")
        button.setEnabled(False)

        self.thread = QThread()
        self.worker = UnpackWorker(sourceDir=sourceDir, destinationDir=destinationDir)
        self.worker.moveToThread(self.thread)
        self.thread.started.connect(self.worker.run)
        self.worker.success.connect(self.thread.quit)
        self.thread.finished.connect(self.worker.deleteLater)
        self.worker.result.connect(self.handleUnpackResult)
        self.thread.start()
        
        #setup triggers for when thread is done
        self.thread.finished.connect(
            lambda: button.setEnabled(True)
        )
        self.thread.finished.connect(
            lambda: button.setText("Go!")
        )
        


class QHorizontalSpacer(QFrame):
    def __init__(self):
        super(QHorizontalSpacer, self).__init__()
        self.setFrameShape(QFrame.Shape.HLine)
        self.setFrameShadow(QFrame.Shadow.Sunken)

class ThreadResult():
    def __init__(self, ok: bool, style: QMessageBox = None, title: str = None, text: str = None):
        self.ok = ok
        self.messageType = style
        self.title = title
        self.text = text

class RepackWorker(QObject):
    # result = pyqtSignal(engine.phasePackOverallResult) 
    result = None
    finished = pyqtSignal(ThreadResult)
    #progress = pyqtSignal(int)

    def __init__(self, dir, outputDir, modName, deleteFiles, deleteFolders):
        super(RepackWorker, self).__init__()
        self.dir = dir
        self.outputDir = outputDir
        self.modName = modName
        self.deleteFiles = deleteFiles
        self.deleteFolders = deleteFolders

    def run(self):
        """Launch the unpacking process."""
        #debugpy.debug_this_thread() #must be done to enable debugging!!!
        try:
            data: engine.phasePackOverallResult = engine.repackAllLooseFiles(
                cwd=self.dir, 
                output_dir=self.outputDir, 
                output_name=self.modName, 
                delete_file_mode=self.deleteFiles, 
                delete_folder_mode=self.deleteFolders)    
        except CalledProcessError as e:
            self.finished.emit(ThreadResult(False, QMessageBox.critical, "Warning!",
                f"Multify error! Please let me know ASAP on GitHub.\nError text:\n{e}"))
        except FileNotFoundError as e:
            self.finished.emit(ThreadResult(False, QMessageBox.critical, "Warning!",
                f"Lookup table error! Please let me know ASAP on Github.\nError text:\n{e}\nCWD:\n{os.getcwd()}"))
        except Exception as e:
            self.finished.emit(ThreadResult(False, QMessageBox.critical, "Warning!",
                f"Unknown error! Please let me know ASAP on GitHub.\nError text:\n{e}"))
        else:
            if len(data.files) == 0:
                self.finished.emit(ThreadResult(True, QMessageBox.warning, "Note!",
                    f"There weren't any valid files in that folder!"))
            else:
                self.finished.emit(ThreadResult(True, QMessageBox.information, "Success!",
                    f"{len(data.files)} files successfully packed!"))
            self.result.emit(data)

class UnpackWorker(QObject):
    success = pyqtSignal() #this is so awful.... enum>?????
    result = pyqtSignal(ThreadResult)

    def __init__(self, sourceDir, destinationDir):
        super(UnpackWorker, self).__init__()
        self.dir = dir
        self.sourceDir = sourceDir
        self.destinationDir = destinationDir

    def run(self):
        #debugpy.debug_this_thread() #must be added/removed manually to debug in thread
        try:
            engine.unpackDirectory(self.sourceDir, self.destinationDir)
        except CalledProcessError as e:
            self.result.emit(ThreadResult(False, QMessageBox.critical, "Warning!",
                f"Multify error! Please let me know ASAP on GitHub.\nError text:\n{e.__dict__}"))
        except Exception as e:
            self.result.emit(ThreadResult(False, QMessageBox.critical, "Warning!",
                f"Unknown error! Please let me know ASAP on GitHub.\nError text:\n{e.__dict__}"))
        else:
            self.result.emit(ThreadResult(True, QMessageBox.information, "Success!",
                "Folder unpacked!"))
        finally:
            self.success.emit()


if __name__ == "__main__":
    #QApplication object is the app, sys.argv are the cmd line args
    app = QApplication(sys.argv)

    app.setApplicationName(APP_NAME)
    app.setOrganizationName(ORG_NAME)
    app.setApplicationVersion(APP_VER)

    #create a widget (the window)
    window = VoltexTakeoutMainWindow()
    window.show() #need to explicitly show it, windows (w/o a visible parent) are hidden by default

    #start the event loop
    app.exec()

    #reaches here once app exits and event loop stops