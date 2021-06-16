from main import *

GLOBAL_STATE = 0


class UIFunctions(AppWindow):
    def maximize_restore(self):
        global GLOBAL_STATE
        status = GLOBAL_STATE

        if status == 0:
            self.showMaximized()
            GLOBAL_STATE = 1
            # more
            # change icon
        else:
            GLOBAL_STATE = 0
            self.showNormal()
            self.resize(self.width()+1, self.height()+1)
            # more
            # change icon

    def ui_definitions(self):
        self.setWindowFlag(QtCore.Qt.FramelessWindowHint)
        self.setAttribute(QtCore.Qt.WA_TranslucentBackground)

        self.maximize_btn.clicked.connect(lambda: UIFunctions.maximize_restore(self))
        self.minimize_btn.clicked.connect(lambda: self.showMinimized())
        self.close_btn.clicked.connect(lambda: self.close())

        self.sizegrip = QSizeGrip(self.frame_grip)

    @staticmethod
    def return_status():
        return GLOBAL_STATE

    def toggle_menu(self, max_width, enable):
        if enable:
            width = self.left_menu.width()
            max_extend = max_width
            standard = 60

            if width == 60:
                width_extended = max_extend
            else:
                width_extended = standard

            self.animation = QPropertyAnimation(self.left_menu, b"minimumWidth")
            self.animation.setDuration(500)
            self.animation.setStartValue(width)
            self.animation.setEndValue(width_extended)
            self.animation.setEasingCurve(QtCore.QEasingCurve.InOutQuart)
            self.animation.start()
