import sys
import requests
from bs4 import BeautifulSoup
from datetime import date

from PyQt5 import QtCore
from PyQt5.QtCore import Qt, QPropertyAnimation
from PyQt5.QtWidgets import QApplication, QMainWindow, QDialog, QFrame, QSizeGrip
from PyQt5.QtGui import QColor
from PyQt5.uic import loadUi


from my_db import *
from ui_functions import *


class LoginDialog(QDialog):
    def __init__(self, db):
        super(LoginDialog, self).__init__()
        loadUi("UI/finished_login.ui", self)
        self.db = db

        self.setWindowFlags(QtCore.Qt.FramelessWindowHint)
        self.setAttribute(QtCore.Qt.WA_TranslucentBackground)

        self.login_btn.clicked.connect(self.login)
        self.no_acc_btn.clicked.connect(lambda: self.redirect(self.signup_page))
        self.signup_btn.clicked.connect(self.register)
        self.login_close_btn.clicked.connect(self.close)
        self.signup_close_btn.clicked.connect(self.close)

    @staticmethod
    def set_txt(text, *args):
        [widget.setText(text) for widget in args]

    def login(self):
        widgets = [
            self.login_username,
            self.login_password,
            self.login_username_alert,
            self.login_password_alert
        ]

        msg = " Invalid username or password"

        username = widgets[0].text()
        password = widgets[1].text()

        if not username or not password:
            self.set_txt("", widgets[0], widgets[1])
            self.set_txt(msg, widgets[2], widgets[3])
        else:
            if self.db.check_user(username, password):
                self.set_txt("", widgets[0], widgets[1])
                self.set_txt("", widgets[2], widgets[3])

                # Show main window
                self.hide()
                main_window = AppWindow(self.db)
                main_window.show()
            else:
                self.set_txt("", widgets[0], widgets[1])
                self.set_txt(msg, widgets[2], widgets[3])

    def register(self):
        widgets = [
            self.signup_username,
            self.signup_password,
            self.signup_confirm,
            self.signup_username_alert,
            self.signup_password_alert,
            self.signup_confirm_alert
        ]

        msgs = [
            " Invalid input",
            " Passwords don't match",
            " Username is already used",
            " Invalid username (must be between 2 and 20 chars)",
            " Invalid password (must be between 4 and 16 chars)"
        ]

        self.set_txt("", widgets[3], widgets[4], widgets[5])

        username = self.signup_username.text()
        password = self.signup_password.text()
        confirm = self.signup_confirm.text()

        if not username or not password or not confirm:
            self.set_txt("", widgets[0], widgets[1], widgets[2])
            self.set_txt(msgs[0], widgets[3], widgets[4], widgets[5])
        elif password != confirm:
            self.set_txt("", widgets[1], widgets[2])
            self.set_txt(msgs[1], widgets[4], widgets[5])
        else:
            try:
                self.db.register_user(username, password)
                self.set_txt("", self.login_username, self.login_password)
                self.set_txt("", self.login_username_alert, self.login_password_alert)
                self.set_txt("", widgets[0], widgets[1], widgets[2])
                self.redirect(self.login_page)
            except UsernameAlreadyUsed:
                self.set_txt("", widgets[0])
                self.set_txt(msgs[2], widgets[3])
            except InvalidUsername:
                self.set_txt("", widgets[0])
                self.set_txt(msgs[3], widgets[3])
            except InvalidPassword:
                self.set_txt("", widgets[1], widgets[2])
                self.set_txt(msgs[4], widgets[4], widgets[5])

    def redirect(self, widget):
        self.stackedWidget.setCurrentWidget(widget)


class BoardFrame(QFrame):
    def __init__(self, parent, db, section, info):
        super(QFrame, self).__init__()
        loadUi("UI/BoardFrame.ui", self)
        self.app_window = parent
        self.db = db
        self.section = section
        self.info = info

        self.title.setText(self.info["Title"])
        self.date.setText(self.info["Deadline"])

        self.read_more_btn.clicked.connect(self.show_description)
        self.delete_btn.clicked.connect(self.delete_frame)

        if info["Attached"] or section == "Done":
            self.add_to_calendar_btn.deleteLater()
        else:
            self.add_to_calendar_btn.clicked.connect(self.add_to_calendar)

    def delete_frame(self):
        self.db.delete_frame(self.section, self.info["Title"])
        self.deleteLater()

    def show_description(self):
        description_dialog = DescriptionDialog(self.app_window, self.db, self.section, self.info)
        if not description_dialog.isVisible():
            description_dialog.show()

    def add_to_calendar(self):
        pass


class DescriptionDialog(QDialog):
    def __init__(self, parent, db, section, info):
        super(DescriptionDialog, self).__init__(parent)
        loadUi("UI/Description.ui", self)
        self.app_window = parent
        self.db = db
        self.section = section
        self.info = info

        self.title.setText(info["Title"])
        self.description.setText(info["Description"])
        self.date.setText(info["Deadline"])
        self.attached.setText("True" if info["Attached"] else "False")

        if section == "Done":
            self.mark_as_done_btn.deleteLater()
        else:
            self.mark_as_done_btn.clicked.connect(self.mark_as_done)

    def mark_as_done(self):
        self.db.delete_frame(self.section, self.info["Title"])
        self.db.add_frame("Done", self.info)
        self.app_window.update_board("Done", self.info)
        self.close()


class AddFrameDialog(QDialog):
    def __init__(self, parent):
        super(AddFrameDialog, self).__init__(parent)
        loadUi("UI/PopUp.ui", self)
        self.section = None
        self.app_window = parent
        self.db = parent.db
        self.deadline.setDate(date.today())

        self.add_btn.clicked.connect(self.process_data)
        self.cancel_btn.clicked.connect(self.close)

    def process_data(self):
        title = self.title.text()
        description = self.description.toPlainText()
        deadline = self.deadline.date().toPyDate().strftime("%d/%m/%Y")
        attach = 1 if self.attach.isChecked() else 0

        if not (title and description and deadline):
            print("Fill all fields!\n")
        else:
            info = {
                "Title": title,
                "Description": description,
                "Deadline": deadline,
                "Attached": attach
            }
            self.db.add_frame(self.section, info)
            self.app_window.update_board(self.section, info)
            self.close()

    def clean_widgets(self):
        # Clean Text
        pass


class AppWindow(QMainWindow):
    def __init__(self, db):
        super(AppWindow, self).__init__()
        loadUi("UI/APP.ui", self)
        self.db = db

        self.generate_board()
        self.add_frame_dialog = AddFrameDialog(self)

        self.toggle_btn.clicked.connect(lambda: UIFunctions.toggle_menu(self, 170, True))
        self.home_btn.clicked.connect(lambda: self.redirect(self.home_page))
        self.board_btn.clicked.connect(lambda: self.redirect(self.board_page))
        self.school_btn.clicked.connect(lambda: self.redirect(self.school_page))

        self.add_event_btn.clicked.connect(lambda: self.show_popup("Events"))
        self.add_todo_btn.clicked.connect(lambda: self.show_popup("ToDo"))

        self.scrap_tues_blog()
        self.scrap_tues_news()

        def move_window(event):
            if UIFunctions.return_status() == 1:
                UIFunctions.maximize_restore(self)

            if event.buttons() == Qt.LeftButton:
                self.move(self.pos() + event.globalPos() - self.dragPos)
                self.dragPos = event.globalPos()
                event.accept()

        self.content_top.mouseMoveEvent = move_window
        UIFunctions.ui_definitions(self)

    def mousePressEvent(self, event):
        self.dragPos = event.globalPos()

    def scrap_tues_blog(self):
        url = "https://www.elsys-bg.org/blog"
        src = requests.get(url).text
        soup = BeautifulSoup(src, "lxml")

        tues_posts = {}

        for idx, post in enumerate(soup.find_all(class_="text")[1:]):
            tues_posts[f"Post {idx+1}"] = {
                "Title": post.h3.text,
                "Date": post.time.text,
                "Text": post.p.text.strip(),
                "Link": f"https://www.elsys-bg.org/{post.a['href']}",
            }

        self.post1_title.setText(tues_posts["Post 1"]["Title"])
        self.post2_title.setText(tues_posts["Post 2"]["Title"])
        self.post3_title.setText(tues_posts["Post 3"]["Title"])

        self.post1_text.setText(tues_posts["Post 1"]["Text"])
        self.post2_text.setText(tues_posts["Post 2"]["Text"])
        self.post3_text.setText(tues_posts["Post 3"]["Text"])

        self.post1_date.setText(tues_posts["Post 1"]["Date"])
        self.post2_date.setText(tues_posts["Post 2"]["Date"])
        self.post3_date.setText(tues_posts["Post 3"]["Date"])

    def scrap_tues_news(self):
        url = "https://www.elsys-bg.org/novini-i-sybitija/novini"
        src = requests.get(url).text
        soup = BeautifulSoup(src, "lxml")

        tues_news = {}

        for idx, news in enumerate(soup.find_all(class_="text")[1:]):
            tues_news[f"News {idx + 1}"] = {
                "Title": news.h3.text,
                "Date": news.time.text,
                "Link": f"https://www.elsys-bg.org/{news.a['href']}",
            }

        self.news1_title.setText(tues_news["News 1"]["Title"])
        self.news2_title.setText(tues_news["News 2"]["Title"])
        self.news3_title.setText(tues_news["News 3"]["Title"])

        self.news1_date.setText(tues_news["News 1"]["Date"])
        self.news2_date.setText(tues_news["News 2"]["Date"])
        self.news3_date.setText(tues_news["News 3"]["Date"])

    def show_popup(self, section):
        if not self.add_frame_dialog.isVisible():
            self.add_frame_dialog.section = section
            self.add_frame_dialog.show()

    def generate_board(self):
        board = self.db.get_user_board()
        for section in board:
            for frame_info in board[section]:
                frame = BoardFrame(self, self.db, section, frame_info)
                if section == "Events":
                    self.events_box_layout.addWidget(frame)
                elif section == "ToDo":
                    self.todo_box_layout.addWidget(frame)
                elif section == "Done":
                    self.done_box_layout.addWidget(frame)

    def update_board(self, section, info):
        frame = BoardFrame(self, self.db, section, info)
        if section == "Events":
            self.events_box_layout.addWidget(frame)
        elif section == "ToDo":
            self.todo_box_layout.addWidget(frame)
        elif section == "Done":
            self.done_box_layout.addWidget(frame)

    def redirect(self, widget):
        self.pages_stack.setCurrentWidget(widget)


def main():
    app = QApplication(sys.argv)
    db = JsonDb()
    welcome_window = LoginDialog(db)
    welcome_window.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
