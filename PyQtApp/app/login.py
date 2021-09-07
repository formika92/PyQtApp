import datetime
import smtplib
import ssl
from email.message import (
    EmailMessage,
)
from hashlib import (
    sha256,
)

from PyQt5 import (
    QtCore,
    QtWidgets,
)
from PyQt5.QtWidgets import (
    QDialog,
    QMessageBox,
    QDateEdit,
)
from sqlalchemy import (
    exc,
)

from app.data.models import (
    UserProfile,
    Session,
)

SMTP_HOST = "smtp.gmail.com"
SMTP_PORT = 587


class CustomDateEdit(QDateEdit):
    """
    С отображением текста вместо даты до её выбора
    """
    date_changed = True

    def paintEvent(self, event):
        from .list_phones import ColorsEnum
        if self.date_changed:
            self.lineEdit().setText('Дата рождения')
            self.lineEdit().setStyleSheet(
                ColorsEnum.COLOR_LINE_EDIT
            )
        QDateEdit.paintEvent(self, event)
        self.calendarWidget().clicked.connect(self.change_data)

    def change_data(self):
        self.date_changed = False


class RegDialog(QDialog):
    """
    Окно формы регистрации
    """

    def __init__(self):
        from PyQtApp.app.main import ClickableLineEdit
        super().__init__()
        from .list_phones import ColorsEnum
        self.session = Session()
        self.resize(429, 298)
        self.setStyleSheet(ColorsEnum.BACKGROUND_COLOR)

        style_btn_ok = (
            "background-color: rgb(0, 255, 0);\n"
            "color: rgb(0, 0, 0);\n"
            "font: 75 18pt \"Ubuntu\";"
        )

        style_btn_cancel = (
            "background-color: rgb(255, 0, 0);\n"
            "color: rgb(0, 0, 0);\n"
            "font: 75 18pt \"Ubuntu\";"
        )

        self.btn_ok = QtWidgets.QPushButton(self)
        self.btn_ok.setGeometry(
            QtCore.QRect(
                50, 230, 151, 51
            )
        )
        self.btn_ok.setStyleSheet(style_btn_ok)

        self.btn_cancel = QtWidgets.QPushButton(self)
        self.btn_cancel.setGeometry(
            QtCore.QRect(
                230, 230, 151, 51
            )
        )
        self.btn_cancel.setStyleSheet(style_btn_cancel)

        self.field_password_repeat = ClickableLineEdit(self)
        self.field_password_repeat.setGeometry(
            QtCore.QRect(
                40, 140, 361, 29
            )
        )
        self.field_password_repeat.setStyleSheet(
            ColorsEnum.COLOR_LINE_EDIT
        )

        self.field_password = ClickableLineEdit(self)
        self.field_password.setGeometry(
            QtCore.QRect(
                40, 100, 361, 29
            )
        )
        self.field_password.setStyleSheet(
            ColorsEnum.COLOR_LINE_EDIT
        )

        self.field_login = ClickableLineEdit(self)
        self.field_login.setGeometry(
            QtCore.QRect(
                40, 60, 361, 29
            )
        )
        self.field_login.setStyleSheet(
            ColorsEnum.COLOR_LINE_EDIT
        )

        self.date_birth = CustomDateEdit(self)
        self.date_birth.setGeometry(
            QtCore.QRect(
                100, 180, 231, 29
            )
        )
        self.date_birth.setCalendarPopup(True)
        self.date_birth.setDisplayFormat("dd.MM.yyyy")
        self.date_birth.setDate(QtCore.QDate.currentDate())

        # сигналы
        self.btn_ok.clicked.connect(lambda: self.apply_form())
        self.btn_cancel.clicked.connect(lambda: self.close_window())

        self.field_login.clicked.connect(
            lambda: self.clear_data(
                line=self.field_login
            )
        )
        self.field_password.clicked.connect(
            lambda: self.clear_data(
                line=self.field_password
            )
        )
        self.field_password_repeat.clicked.connect(
            lambda: self.clear_data(
                line=self.field_password_repeat
            )
        )

        self.retranslateUi()
        QtCore.QMetaObject.connectSlotsByName(self)

    def clear_data(self, line):
        """
        Очищает QLineEdit
        """
        from PyQtApp.app.main import TextEnum
        if (
                (line.text() == TextEnum.DEFAULT_LOGIN_TEXT)
                or (line.text() == TextEnum.DEFAULT_PASSWORD_TEXT)
                or (line.text() == TextEnum.DEFAULT_PASSWORD_REPEAT_TEXT)

        ):
            line.setText('')

    def close_window(self):
        """
        Закрытие окна
        """
        self.close()

    def apply_form(self):
        """
        Регистрация пользователя
        """
        login = str(self.field_login.text())
        password = str(self.field_password.text())
        password_repeat = str(self.field_password_repeat.text())

        try:
            date_birth = datetime.datetime.strptime(
                self.date_birth.text(), '%d.%m.%Y'
            ).date()
        except (TypeError, ValueError):
            QMessageBox.warning(
                self, 'Предупреждение', 'Неверный формат даты!'
            )
            return

        if not all(
                (
                        login,
                        password_repeat,
                        password,
                        date_birth,
                )
        ):
            QMessageBox.warning(
                self, 'Предупреждение', 'Заполните все поля!'
            )
            return

        if password != password_repeat:
            QMessageBox.warning(
                self, 'Предупреждение', 'Пароли не совпадают!'
            )
            return

        # проверка на наличие логина в бд
        try:
            self.session.query(
                UserProfile
            ).filter_by(
                login=login
            ).one()
        except exc.NoResultFound:
            password = sha256(
                password.encode('utf-8')
            ).hexdigest()

            new_userprofile = UserProfile(
                login=login,
                date_birth=date_birth,
                password=password,
            )
            self.session.add(new_userprofile)
            self.session.commit()

            self.close()

            QMessageBox.warning(
                self, '', 'Пользователь зарегистрирован!!'
            )
            return

        else:
            QMessageBox.warning(
                self, 'Предупреждение', 'Пользователь с таким логином уже существует!'
            )

    def retranslateUi(self):
        from PyQtApp.app.main import TextEnum
        _translate = QtCore.QCoreApplication.translate
        self.btn_ok.setText(_translate("Dialog", "Ок"))
        self.btn_cancel.setText(_translate("Dialog", "Отмена"))
        self.field_password_repeat.setText(_translate("Dialog", TextEnum.DEFAULT_PASSWORD_REPEAT_TEXT))
        self.field_password.setText(_translate("Dialog", TextEnum.DEFAULT_PASSWORD_TEXT))
        self.field_login.setText(_translate("Dialog", TextEnum.DEFAULT_LOGIN_TEXT))


class ResetPasswordWin(QDialog):

    def __init__(self):
        from PyQtApp.app.main import ClickableLineEdit
        super().__init__()
        self.resize(480, 312)
        self.setStyleSheet(
            "background-color: rgb(255, 255, 255);"
        )

        self.reset_btn = QtWidgets.QPushButton(self)
        self.reset_btn.setGeometry(
            QtCore.QRect(
                50, 210, 181, 41
            )
        )
        self.reset_btn.setStyleSheet(
            "background-color: rgb(135, 135, 135);\n"
            "color: rgb(0, 0, 0);\n"
            "font: 75 16pt \"Ubuntu\";"
        )

        self.cancel_btn = QtWidgets.QPushButton(self)
        self.cancel_btn.setGeometry(
            QtCore.QRect(
                240, 210, 181, 41
            )
        )
        self.cancel_btn.setStyleSheet(
            "background-color: rgb(255, 0, 0);\n"
            "color: rgb(0, 0, 0);\n"
            "font: 75 18pt \"Ubuntu\";"
        )

        self.field_email = ClickableLineEdit(self)
        self.field_email.setGeometry(
            QtCore.QRect(
                92, 110, 281, 29
            )
        )
        self.field_email.setStyleSheet(
            "color: rgb(135, 135, 135);\n"
            "background-color: rgb(255, 255, 255);"
        )

        self.reset_pass_link = QtWidgets.QLabel(self)
        self.reset_pass_link.setGeometry(
            QtCore.QRect(
                70, 40, 331, 41
            )
        )
        self.reset_pass_link.setStyleSheet(
            "color: rgb(135, 135, 135);\n"
            "font: 75 22pt \"Ubuntu\";"
        )
        self.reset_pass_link.setObjectName("label")

        self.retranslateUi()
        QtCore.QMetaObject.connectSlotsByName(self)

        # сигналы
        self.reset_btn.clicked.connect(
            lambda: self.send_email(
                to_addr=self.field_email.text()
            )
        )

        self.cancel_btn.clicked.connect(
            self.close_window
        )

        self.field_email.clicked.connect(
            lambda: self.clear_data(
                line=self.field_email
            )
        )

    def clear_data(self, line):
        """
        Очищает QLineEdit
        """
        from PyQtApp.app.main import TextEnum
        if line.text() == TextEnum.DEFAULT_EMAIL_TEXT:
            line.setText('')

    def close_window(self):
        """
        Закрытие окна
        """
        self.close()

    def send_email(
            self,
            to_addr,
    ):
        """
        Отправляет email на адрес юзера
        """

        # # для отправки сообщений нужно указать действительный адрес эл. почты,
        # # убедиться, что в аккаунте эл. почты включен доступ внешним приложениям
        # # если Gmail, то включить доступ по протоколу IMAP в настройках и доступ
        # # https://myaccount.google.com/lesssecureapps

        # from_addr = "pyqtapp@example.ru"
        # msg = EmailMessage()
        # msg.set_content("Some link")
        # msg["Subject"] = "Reset password"
        # msg["From"] = from_addr
        # msg["To"] = to_addr
        #
        # context = ssl.create_default_context()
        #
        # with smtplib.SMTP(SMTP_HOST, port=SMTP_PORT) as smtp:
        #     smtp.starttls(context=context)
        #     smtp.login(
        #         from_addr,
        #         "somepassword"
        #     )
        #     smtp.send_message(msg)
        self.close()

    def retranslateUi(self):
        from PyQtApp.app.main import TextEnum
        _translate = QtCore.QCoreApplication.translate
        self.reset_btn.setText(_translate("Dialog", "Сменить пароль"))
        self.cancel_btn.setText(_translate("Dialog", "Отмена"))
        self.field_email.setText(_translate("Dialog", TextEnum.DEFAULT_EMAIL_TEXT))
        self.reset_pass_link.setText(_translate("Dialog", "Восстановление пароля"))
