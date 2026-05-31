import sys
import serial

from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtGui import *


class ParkingDashboard(QMainWindow):

    def __init__(self):
        super().__init__()

        # ---------------- WINDOW ---------------- #
        self.setWindowTitle("SMART CAR PARKING SYSTEM")
        self.setGeometry(200, 100, 1000, 650)

        # ---------------- VARIABLES ---------------- #
        self.car_count = 0

        # Edge Detection Variable
        self.previous_state = "EMPTY"

        # ---------------- MAIN WIDGET ---------------- #
        main_widget = QWidget()
        self.setCentralWidget(main_widget)

        main_layout = QVBoxLayout()
        main_widget.setLayout(main_layout)

        # ---------------- TITLE ---------------- #
        title = QLabel("SMART CAR PARKING SENSOR")
        title.setAlignment(Qt.AlignCenter)

        title.setStyleSheet("""
            QLabel{
                color: white;
                font-size: 34px;
                font-weight: bold;
                padding: 20px;
            }
        """)

        # ---------------- PARKING CARD ---------------- #
        self.slot_card = QFrame()
        self.slot_card.setFixedHeight(300)

        self.slot_card.setStyleSheet("""
            QFrame{
                background-color: #1f2937;
                border-radius: 25px;
            }
        """)

        card_layout = QVBoxLayout()
        self.slot_card.setLayout(card_layout)

        # ---------------- STATUS LABEL ---------------- #
        self.status = QLabel("WAITING FOR SENSOR...")
        self.status.setAlignment(Qt.AlignCenter)

        self.status.setStyleSheet("""
            QLabel{
                color: white;
                font-size: 28px;
                font-weight: bold;
            }
        """)

        # ---------------- INDICATOR ---------------- #
        self.indicator = QLabel()
        self.indicator.setFixedSize(180, 180)

        self.indicator.setStyleSheet("""
            background-color: gray;
            border-radius: 90px;
        """)

        glow = QGraphicsDropShadowEffect()
        glow.setBlurRadius(80)
        glow.setOffset(0)
        glow.setColor(QColor("gray"))

        self.indicator.setGraphicsEffect(glow)

        card_layout.addStretch()
        card_layout.addWidget(self.indicator, alignment=Qt.AlignCenter)
        card_layout.addWidget(self.status)
        card_layout.addStretch()

        # ---------------- CAR COUNTER ---------------- #
        self.counter = QLabel("Cars Parked : 0")
        self.counter.setAlignment(Qt.AlignCenter)

        self.counter.setStyleSheet("""
            QLabel{
                color: #00ffaa;
                font-size: 26px;
                font-weight: bold;
                padding: 15px;
            }
        """)

        # ---------------- LOG BOX ---------------- #
        self.logs = QTextEdit()
        self.logs.setReadOnly(True)

        self.logs.setStyleSheet("""
            QTextEdit{
                background-color: #111827;
                color: #00ffcc;
                font-size: 16px;
                border-radius: 20px;
                padding: 15px;
            }
        """)

        # ---------------- RESET BUTTON ---------------- #
        self.reset_btn = QPushButton("RESET COUNTER")

        self.reset_btn.setStyleSheet("""
            QPushButton{
                background-color: #2563eb;
                color: white;
                font-size: 18px;
                font-weight: bold;
                border-radius: 15px;
                padding: 15px;
            }

            QPushButton:hover{
                background-color: #1d4ed8;
            }
        """)

        self.reset_btn.clicked.connect(self.reset_counter)

        # ---------------- FOOTER ---------------- #
        footer = QLabel("STM32F103C8T6 + IR SENSOR + PYQT5")
        footer.setAlignment(Qt.AlignCenter)

        footer.setStyleSheet("""
            QLabel{
                color: gray;
                font-size: 14px;
                padding: 10px;
            }
        """)

        # ---------------- ADD WIDGETS ---------------- #
        main_layout.addWidget(title)
        main_layout.addWidget(self.slot_card)
        main_layout.addWidget(self.counter)
        main_layout.addWidget(self.logs)
        main_layout.addWidget(self.reset_btn)
        main_layout.addWidget(footer)

        # ---------------- WINDOW STYLE ---------------- #
        self.setStyleSheet("""
            QMainWindow{
                background-color: #0b1020;
            }
        """)

        # ---------------- SERIAL ---------------- #
        self.serial = serial.Serial(
            port='COM6',          # CHANGE YOUR COM PORT
            baudrate=115200,
            timeout=1
        )

        # ---------------- TIMER ---------------- #
        self.timer = QTimer()
        self.timer.timeout.connect(self.read_sensor)
        self.timer.start(100)

    # ==========================================================
    # SENSOR READING FUNCTION
    # ==========================================================
    def read_sensor(self):

        if self.serial.in_waiting:

            data = self.serial.readline().decode().strip()

            print(data)

            current_time = QDateTime.currentDateTime().toString(
                "hh:mm:ss"
            )

            # ======================================================
            # OBJECT DETECTED
            # ======================================================
            if data == "Near":

                self.status.setText("SLOT OCCUPIED")

                self.indicator.setStyleSheet("""
                    background-color: red;
                    border-radius: 90px;
                """)

                glow = QGraphicsDropShadowEffect()
                glow.setBlurRadius(100)
                glow.setOffset(0)
                glow.setColor(QColor("red"))

                self.indicator.setGraphicsEffect(glow)

                self.slot_card.setStyleSheet("""
                    QFrame{
                        background-color: #2d1117;
                        border-radius: 25px;
                        border: 3px solid red;
                    }
                """)

                # ==================================================
                # EDGE DETECTION
                # Increment ONLY when state changes
                # EMPTY ---> OCCUPIED
                # ==================================================
                if self.previous_state == "EMPTY":

                    self.car_count += 1

                    self.counter.setText(
                        f"Cars Parked : {self.car_count}"
                    )

                    self.logs.append(
                        f"[{current_time}] CAR ENTERED"
                    )

                self.previous_state = "OCCUPIED"

            # ======================================================
            # SLOT EMPTY
            # ======================================================
            else:

                self.status.setText("SLOT AVAILABLE")

                self.indicator.setStyleSheet("""
                    background-color: #00ff99;
                    border-radius: 90px;
                """)

                glow = QGraphicsDropShadowEffect()
                glow.setBlurRadius(100)
                glow.setOffset(0)
                glow.setColor(QColor("#00ff99"))

                self.indicator.setGraphicsEffect(glow)

                self.slot_card.setStyleSheet("""
                    QFrame{
                        background-color: #0f2b1d;
                        border-radius: 25px;
                        border: 3px solid #00ff99;
                    }
                """)

                self.previous_state = "EMPTY"

                self.logs.append(
                    f"[{current_time}] SLOT EMPTY"
                )

    # ==========================================================
    # RESET FUNCTION
    # ==========================================================
    def reset_counter(self):

        self.car_count = 0

        self.counter.setText(
            "Cars Parked : 0"
        )

        self.logs.append(
            "Counter Reset"
        )


# ==============================================================
# MAIN APPLICATION
# ==============================================================
if __name__ == "__main__":

    app = QApplication(sys.argv)

    window = ParkingDashboard()
    window.show()

    sys.exit(app.exec_())