import re
import sys
import datetime
from hashlib import (
    sha256,
)

from PyQt5 import (
    QtCore,
    QtGui,
    QtWidgets,
)
from PyQt5.QtCore import (
    pyqtSignal,
)

from PyQt5.QtWidgets import (
    QApplication,
    QWidget,
    QMessageBox,
    QLineEdit,
)
from sqlalchemy import (
    exc,
)

from .data.models import (
    UserProfile,
    Session, Users,
)
from .list_phones import (
    ListPhonesWindow, ColorsEnum,
)
from .login import (
    RegDialog,
    ResetPasswordWin,
)
from .reminders import ReminderBirthDialog


class TextEnum:

    DEFAULT_LOGIN_TEXT = 'Имя пользователя'
    DEFAULT_PASSWORD_TEXT = 'Пароль'
    DEFAULT_PASSWORD_REPEAT_TEXT = 'Повторите пароль'
    DEFAULT_DATE_BIRTH_TEXT = 'Дата рождения'
    DEFAULT_EMAIL_TEXT = 'Адрес электронной почты'


class ClickableLineEdit(QLineEdit):
    """
    С событием клика мыши
    """
    clicked = pyqtSignal()

    def mousePressEvent(self, event):
        self.clicked.emit()
        QLineEdit.mousePressEvent(self, event)


class LoginWindow(QWidget):
    """
    Окно ввода логина и пароля
    """

    def __init__(self):
        super().__init__()
        self.setEnabled(True)
        self.resize(538, 337)
        self.session = Session()

        # стиль текста
        font = QtGui.QFont()
        font.setFamily(
            "Ubuntu"
        )
        font.setPointSize(18)
        font.setWeight(9)
        text_color = "color: rgb(0, 0, 0);"

        # бэкграунд окна
        self.setStyleSheet(
            ColorsEnum.BACKGROUND_COLOR
        )

        self.centralwidget = QtWidgets.QWidget(
            self,
        )

        # кнопка входа
        self.apply_btn = QtWidgets.QPushButton(
            self.centralwidget,
        )
        self.apply_btn.setGeometry(
            QtCore.QRect(
                20, 160, 161, 51
            )
        )

        self.apply_btn.setFont(font)
        self.apply_btn.setStyleSheet(
            f"{text_color}\n background-color: rgb(0, 255, 0);\n",
        )

        # кнопка регистрации
        self.reg_btn = QtWidgets.QPushButton(
            self.centralwidget,
        )
        self.reg_btn.setGeometry(
            QtCore.QRect(
                190, 160, 161, 51
            )
        )
        self.reg_btn.setFont(font)
        self.reg_btn.setStyleSheet(
            f"{text_color}\n f'{ColorsEnum.BACKGROUND_COLOR}'\n"
        )

        # кнопка отмены
        self.exit_btn = QtWidgets.QPushButton(self.centralwidget)
        self.exit_btn.setGeometry(
            QtCore.QRect(
                360, 160, 161, 51
            )
        )
        self.exit_btn.setFont(font)
        self.exit_btn.setStyleSheet(
            f"{text_color}\n background-color: rgb(255, 0, 0);\n"
        )

        # чекбокс "запомнить меня"
        self.remember_checkbox = QtWidgets.QCheckBox(
            self.centralwidget,
        )
        self.remember_checkbox.setGeometry(
            QtCore.QRect(
                210, 240, 141, 22
            )
        )
        self.remember_checkbox.setStyleSheet(
            text_color,
        )

        # чекбокс "показать пароль"
        self.show_pass_checkbox = QtWidgets.QCheckBox(
            self.centralwidget
        )
        self.show_pass_checkbox.setGeometry(
            QtCore.QRect(
                210, 270, 141, 22
            )
        )
        self.show_pass_checkbox.setStyleSheet(
            text_color
        )

        self.main_label = QtWidgets.QLabel(
            self.centralwidget
        )
        self.main_label.setGeometry(
            QtCore.QRect(
                140, 16, 281, 51
            )
        )
        self.main_label.setStyleSheet(
            f"{text_color}\n {ColorsEnum.BACKGROUND_COLOR}\n"
            "font: 75 24pt \"Ubuntu\";"
        )

        # строки ввода логина и пароля
        self.input_login = ClickableLineEdit(
            self.centralwidget
        )
        self.input_login.setGeometry(
            QtCore.QRect(
                60, 80, 421, 29
            )
        )
        self.input_login.setStyleSheet(
            "background-color: rgb(255, 255, 255);\n"
            "color: rgb(99, 99, 99);"
        )

        self.input_pass = ClickableLineEdit(self.centralwidget)
        self.input_pass.setGeometry(
            QtCore.QRect(
                60, 110, 421, 29)
        )
        self.input_pass.setStyleSheet(
            "background-color: rgb(255, 255, 255);\n"
            "color: rgb(99, 99, 99);"
        )

        self.label_forgot_pass = QtWidgets.QLabel(
            self.centralwidget,
        )
        self.label_forgot_pass.setGeometry(
            QtCore.QRect(
                230, 300, 111, 17
            )
        )
        self.label_forgot_pass.setStyleSheet(
            "color: rgb(0, 0, 255);\n"
            "font: 75 11pt \"Ubuntu\";\n"
            "text-decoration: underline;"
        )

        self.label_forgot_pass.setOpenExternalLinks(False)
        self.label_forgot_pass.setText('<a href="#">Забыли пароль?/</a>')

        self.retranslateUi()
        QtCore.QMetaObject.connectSlotsByName(self)

        # сигналы
        self.show_pass_checkbox.stateChanged.connect(
            self.state_changed
        )

        self.apply_btn.clicked.connect(
            self.show_list_phones_window
        )
        self.reg_btn.clicked.connect(
            self.show_win_reg_main
        )
        self.exit_btn.clicked.connect(
            self.close_window
        )

        self.label_forgot_pass.linkActivated.connect(
            self.show_reset_password
        )

        self.input_login.clicked.connect(
            lambda: self.clear_data(
                line=self.input_login
            )
        )
        self.input_pass.clicked.connect(
            lambda: self.clear_data(
                line=self.input_pass,
                need_echo_mode=True
            )
        )

    def clear_data(self, line, need_echo_mode=False):
        """
        Очищает QLineEdit
        """
        if (line.text() == TextEnum.DEFAULT_LOGIN_TEXT) or (line.text() == TextEnum.DEFAULT_PASSWORD_TEXT):
            line.setText('')
            if need_echo_mode:
                line.setEchoMode(QtWidgets.QLineEdit.Password)



    def show_list_phones_window(self):
        """
        Открывает окно со списком телефонов
        """
        input_login = str(self.input_login.text())
        input_pass = str(self.input_pass.text())
        if not (input_login or input_pass):
            QMessageBox.warning(
                self, '', 'Не все обязательные поля заполнены!'
            )
        else:
            # FIXME поставить органичение, чтобы использовали только латиницу
            if bool(re.search('[а-яА-Я]', f'{input_login}{input_pass}')):
                QMessageBox.warning(
                    self, '', 'Логин и пароль должны содержать только латиницу, спец.символы или цифры!'
                )
            else:
                try:
                    user = self.session.query(
                        UserProfile
                    ).filter_by(
                        login=input_login,
                        password=sha256(input_pass.encode('utf-8')).hexdigest(),
                    ).one()
                except exc.NoResultFound:
                    QMessageBox.warning(
                        self, '', 'Неверный логин или пароль!'
                    )
                else:
                    if self.remember_checkbox.isChecked():
                        user.state_auth = True
                        self.session.commit()
                    self.close()
                    self.win_list_phones = ListPhonesWindow(
                        login=user.login,
                    )
                    self.win_list_phones.show()
                    reminder_birth(session=self.session)

    def close_window(self):
        """
        Закрытие окна
        """
        self.close()

    def state_changed(self, int):
        """
        Срабатывает при изменении состояния чекбокса "Показать пароль"
        """
        if self.show_pass_checkbox.isChecked():
            self.input_pass.setEchoMode(
                QtWidgets.QLineEdit.Normal
            )
        else:
            self.input_pass.setEchoMode(
                QtWidgets.QLineEdit.PasswordEchoOnEdit
            )

    def show_win_reg_main(self):
        """
        Открывает окно регистрации
        """
        win_reg = RegDialog()
        win_reg.exec_()

    def show_reset_password(self):
        """
        Открывает окно восстановления пароля
        """
        win_reset_password = ResetPasswordWin()
        win_reset_password.exec_()

    def retranslateUi(self):
        _translate = QtCore.QCoreApplication.translate
        self.main_label.setText(_translate("LoginWindow", "Окно авторизации"))

        self.apply_btn.setText(_translate("LoginWindow", "Войти"))
        self.reg_btn.setText(_translate("LoginWindow", "Регистрация"))
        self.exit_btn.setText(_translate("LoginWindow", "Отмена"))

        self.remember_checkbox.setText(_translate("LoginWindow", "Запомнить меня"))
        self.show_pass_checkbox.setText(_translate("LoginWindow", "Показать пароль"))

        self.input_login.setText(_translate("LoginWindow", TextEnum.DEFAULT_LOGIN_TEXT))
        self.input_pass.setText(_translate("LoginWindow", TextEnum.DEFAULT_PASSWORD_TEXT))


def reminder_birth(session):
    """
    Показывает окно с именниниками
    """
    date_now = datetime.datetime.now().date()
    date_next = date_now + datetime.timedelta(days=7)
    users = session.query(Users).filter(
        Users.date_birth.between(date_now, date_next)).all()
    if users:
        win_reminder = ReminderBirthDialog(users=users)
        win_reminder.exec_()


def run():
    app = QApplication(sys.argv)
    session = Session()
    try:
        user = session.query(
            UserProfile
        ).filter_by(
            state_auth=True
        ).one()
    except exc.NoResultFound:
        login_window = LoginWindow()
        login_window.show()
    else:
        win_list_phones = ListPhonesWindow(
            login=user.login,
        )
        win_list_phones.show()
        reminder_birth(session=session)

    sys.exit(app.exec_())
