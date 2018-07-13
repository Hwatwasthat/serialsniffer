from PyQt5.QtWidgets import (QLabel, QVBoxLayout, QHBoxLayout, QApplication,
                             QComboBox, QMainWindow, QWidget, QTextEdit,
                             QPushButton, QAction, QLineEdit, QShortcut)
from PyQt5.QtCore import Qt, QThread, QObject, pyqtSignal, pyqtSlot
from PyQt5.QtGui import QKeySequence
from src import single, setup, file_data
from serial import Serial, SerialException
from time import ctime, time, localtime
import sys
import random


class Communicator(QObject):
    finished = pyqtSignal()  # give worker class a finished signal
    out_signal = pyqtSignal(str)  # Need to overload with type of data to be passed

    def __init__(self, parent=None):
        QObject.__init__(self, parent=parent)
        self.continue_run = True  # provide a bool run condition for the class
        self.out_signal[str].connect(main_window.main_widget.update_textbox)  # Need details of variable to be sent

    def do_work(self, ser, loop):
        count = 0
        while self.continue_run:
            if loop:
                cmd_in, cmd_out = ser.communication()
                if cmd_in:
                    count += 1
                    self.out_signal[str].emit(f"{count}.Device at {ctime()}:\n{cmd_in}")
                if cmd_out:
                    count += 1
                    self.out_signal[str].emit(f"{count}.Computer at {ctime()}:\n{cmd_out}")
            else:
                cmd_in = ser.read_command()
                if cmd_in:
                    count += 1
                    self.out_signal[str].emit(f"{count}.Device at {ctime()}:\n{cmd_in}")

        self.finished.emit()  # emit the finished signal when the loop is done

    def stop(self):
        self.continue_run = False


class Autosave(QObject):
    finished = pyqtSignal()
    out_signal = pyqtSignal()

    def __init__(self, cycle, parent=None):
        QObject.__init__(self, parent=parent)
        self.out_signal.connect(main_window.main_widget.autosave)
        self.cycle = cycle

    def do_work(self):
        timer = time()
        while True:
            QThread.sleep(30)
            if time() - timer >= self.cycle:
                self.out_signal.emit()
                timer = time()

    def stop(self):
        self.continue_run = False


class PreferencesWindow(QMainWindow):
    def __init__(self, parent=None):
        super(PreferencesWindow, self).__init__(parent)
        self.setWindowTitle('Preferences')


class MainWindow(QMainWindow):
    def __init__(self, parent=None):
        super().__init__(parent)
        # creating roman widget and setting it as central
        self.main_widget = Window(parent=self)
        self.setCentralWidget(self.main_widget)
        self.dialog = PreferencesWindow(self)
        self.setup_menu_bar()
        self.setWindowTitle("Serial Monitor")


    def setup_menu_bar(self):
        # filling up a menu bar
        bar = self.menuBar()

        # adding actions for file menu
        open_action = QAction('Open', self)

        # File menu
        file_menu = bar.addMenu('File')
        file_menu.addAction(open_action)
        file_menu.addAction('Preferences', self.dialog.show, 'ctrl+o')
        file_menu.addAction('Close', self.close, 'ctrl+q')

        help_action = QAction('Help', self)

        help_menu = bar.addMenu("Help")
        help_menu.addAction(help_action)


# noinspection PyArgumentList,PyArgumentList
class Window(QWidget):
    stop_signal = pyqtSignal()
    stop_autosave_signal = pyqtSignal()

    # noinspection PyArgumentList
    def __init__(self, parent):
        super(Window, self).__init__(parent=parent)
        self.setup_ui()
        self.started = False
        self.started_autosave = False

    def setup_ui(self):
        self.first_label = QLabel('Device COM port')
        self.combo_first = QComboBox()

        self.second_label = QLabel('Computer COM port')
        self.combo_second = QComboBox()

        self.header_label = QLabel('Header end byte')
        self.header_entry = QLineEdit()

        self.body_label = QLabel('Body end byte')
        self.body_entry = QLineEdit()

        self.set_serial = QPushButton('Set serial settings')
        self.start_stop_button = QPushButton("Start Communication")
        self.save_button = QPushButton("Save commands")
        self.clear_button = QPushButton("Clear")

        self.start_stop_button.setDisabled(True) # Disabled till settings are locked in
        self.save_button.setDisabled(True)  # Disabled until communication starts
        self.clear_button.setDisabled(True)  # Also disabled until communication starts)


        # Creates a scrollable, selectable text field that cannot be edited by the user
        self.output_box = QTextEdit()
        self.output_box.setReadOnly(True)
        self.output_box.setTextInteractionFlags(Qt.TextSelectableByKeyboard | Qt.TextSelectableByMouse)

        # Get list of available ports
        ports = setup.find_ports()
        ports.insert(0, " ")
        self.combo_first.addItems(ports)
        self.combo_second.addItems(ports)

        # Initialise Vertical layout box for Combo boxes labels
        v_box_label = QVBoxLayout()
        v_box_label.addWidget(self.first_label)
        v_box_label.addWidget(self.second_label)

        # Initialise Vertical layout box for Combo boxes controlling ports
        v_box_combo = QVBoxLayout()
        v_box_combo.addWidget(self.combo_first)
        v_box_combo.addWidget(self.combo_second)

        v_box_label_second = QVBoxLayout()
        v_box_label_second.addWidget(self.header_label)
        v_box_label_second.addWidget(self.body_label)

        v_box_header_body = QVBoxLayout()
        v_box_header_body.addWidget(self.header_entry)
        v_box_header_body.addWidget(self.body_entry)

        # Initialise Horizontal layout box for Combo boxes and labels
        h_box_options = QHBoxLayout()
        h_box_options.addLayout(v_box_label)
        h_box_options.addLayout(v_box_combo)
        h_box_options.addLayout(v_box_label_second)
        h_box_options.addLayout(v_box_header_body)
        h_box_options.addStretch()

        # Initialise a Horizontal box for command buttons
        h_box_buttons = QHBoxLayout()
        h_box_buttons.addWidget(self.set_serial)
        h_box_buttons.addWidget(self.start_stop_button)
        h_box_buttons.addWidget(self.save_button)
        h_box_buttons.addWidget(self.clear_button)
        h_box_buttons.addStretch()

        v_box_upper_left = QVBoxLayout()
        v_box_upper_left.addLayout(h_box_options)
        v_box_upper_left.addLayout(h_box_buttons)


        # Initialise Vertical layout box for window
        v_box_master = QVBoxLayout()
        v_box_master.addLayout(v_box_upper_left)
        v_box_master.addWidget(self.output_box)

        # Start/stop button action
        self.start_stop_button.clicked.connect(self.start_stop)

        # Save Button action
        self.save_button.clicked.connect(self.save_textbox)

        # Clear button action
        self.clear_button.clicked.connect(self.output_box.clear)

        self.setLayout(v_box_master)
        self.show()

    def start_stop(self):
        """
        Controls interactions off the start/stop button. Changes appearance
        of button and initiates a new thread for operation and clears the output.
        :return:
        """
        if not self.started:
            self.output_box.clear()  # Clears the textbox so its easier to read
            self.start_communication_thread()
            self.started = True
            self.start_stop_button.setText("Stop Communication")
            self.save_button.setDisabled(False)  # Disabled until communication starts
            self.clear_button.setDisabled(False)
        else:
            self.stop_communication_thread()
            self.started = False
            self.start_stop_button.setText("Start Communication")
            self.start_stop_button.setDisabled(True)
            self.save_button.setDisabled(True)
            self.clear_button.setDisabled(True)

    def setup_serial(self):
        ser, loop = setup.full_setup((self.combo_first, self.combo_second))
        self.setup_communication_thread(ser, loop)

    def setup_communication_thread(self):
        # Create the instances of thread and worker
        self.thread_communication = QThread()
        self.worker_communication = Communicator()
        self.stop_signal.connect(self.worker_communication.stop)
        self.setup_thread(self.worker_communication, self.thread_communication)
        self.thread_communication.started.connect(ser, loop)

    def setup_autosave_thread(self):
        """
        Sets up the autosave thread. Must be initialised after main_window
        otherwise the poor darling gets confused (due to referencing in the
        __init__ for autosave).
        """
        # Create the instance of thread and worker
        self.thread_autosave = QThread()
        self.worker_autosave = Autosave(120)
        self.setup_thread(self.worker_autosave, self.thread_autosave)
        self.thread_autosave.start()

    @staticmethod
    def setup_thread(worker, thread):
        # Connect the stop_signal signal to the stop method of worker
        worker.moveToThread(thread)
        worker.finished.connect(thread.quit)  # connect the workers finished signal to stop thread
        worker.finished.connect(worker.deleteLater)  # connect the workers finished signal to clean up worker
        thread.finished.connect(thread.deleteLater)  # connect threads finished signal to clean up thread
        # Make it so when the thread receives the start command the worker starts
        thread.started.connect(worker.do_work)
        thread.finished.connect(worker.stop)

    def start_communication_thread(self):
        self.thread_communication.start()

    def stop_communication_thread(self):
        self.stop_signal.emit()

    def start_autosave_thread(self):
        self.thread_autosave.start()

    @pyqtSlot(str)  # Needed to let it know where the data is being passed is a slot to accept it
    def update_textbox(self, data):
        self.output_box.append(data)

    def save_textbox(self):
        """
        Saves the contents of the textbox to a timestamped file. Will not overwrite another, unless you save
        in the same minute.
        :return:
        """
        date = ctime()
        date = date[11:16] + date[7:11] + date[4:8]+ date[-4:]  # Just changes the format to one I prefer
        dated_title = f"Results-{date}.txt".replace(" ", "-").replace(":", ".") # Fixes format for filesystem
        with open(dated_title, "w") as file:
            file.write(self.output_box.toPlainText())
        self.output_box.append("Saved")

    def autosave(self):
        with open("autosave.txt", "w") as file:
            file.write(self.output_box.toPlainText())
        print(f"Autosaved data at {ctime()}")

if __name__ == '__main__':
    app = QApplication(sys.argv)
    main_window = MainWindow()
    main_window.main_widget.setup_autosave_thread()
    main_window.show()
    sys.exit(app.exec_())
