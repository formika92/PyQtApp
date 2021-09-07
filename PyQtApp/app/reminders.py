from PyQt5 import (
    QtCore,
    QtWidgets,
)
from PyQt5.QtWidgets import (
    QDialog, QFrame,
    QAbstractItemView,
    QHeaderView,
)


class ReminderBirthDialog(QDialog):
    """
    Напоминание о днях рождениях
    """

    def __init__(self, users):
        super().__init__()
        self.users = users
        self.resize(480, 712)
        self.setStyleSheet(
            "background-color: rgb(255, 255, 255);"
        )

        self.cancel_btn = QtWidgets.QPushButton(self)
        self.cancel_btn.setGeometry(
            QtCore.QRect(
                147, 610, 181, 41
            )
        )
        self.cancel_btn.setStyleSheet(
            "background-color: rgb(255, 0, 0);\n"
            "color: rgb(0, 0, 0);\n"
            "font: 75 18pt \"Ubuntu\";"
        )

        self.label_title = QtWidgets.QLabel(self)
        self.label_title.setGeometry(
            QtCore.QRect(
                80, 40, 331, 41
            )
        )
        self.label_title.setStyleSheet(
            "color: rgb(135, 135, 135);\n"
            "font: 75 22pt \"Ubuntu\";"
        )
        self.label_title.setObjectName("label")

        self.retranslateUi()
        QtCore.QMetaObject.connectSlotsByName(self)

        # сигналы
        self.cancel_btn.clicked.connect(
            self.close_window
        )
        self.tableWidget = QtWidgets.QTableWidget(self)
        self.tableWidget.setGeometry(
            QtCore.QRect(
                90, 140, 331, 191
            )
        )
        self.tableWidget.setColumnCount(1)
        self.tableWidget.setHorizontalHeaderLabels(
            ('',)
        )
        self.tableWidget.setStyleSheet(
            "color: rgb(58, 58, 58);\n"
            "font: 75 22pt \"Ubuntu\";"
        )
        self.tableWidget.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)

        self.tableWidget.verticalHeader().setVisible(False)
        self.tableWidget.resizeColumnsToContents()
        self.tableWidget.setFrameStyle(QFrame.NoFrame)
        self.tableWidget.setHorizontalScrollMode(QAbstractItemView.ScrollPerPixel)
        self.tableWidget.setVerticalScrollMode(QAbstractItemView.ScrollPerPixel)

        self.retranslateUi()
        QtCore.QMetaObject.connectSlotsByName(self)

        self.add_list_users()

    def close_window(self):
        """
        Закрытие окна
        """
        self.close()

    def add_list_users(self):
        """
        Добавляет список имен
        """
        if self.users:
            for row, user in enumerate(self.users):
                self.tableWidget.insertRow(row)
                self.tableWidget.setRowHeight(row, 50)
                self.tableWidget.setItem(row, 0, QtWidgets.QTableWidgetItem(user.fullname))

    def retranslateUi(self):
        _translate = QtCore.QCoreApplication.translate
        self.cancel_btn.setText(_translate("Dialog", "Закрыть"))
        self.label_title.setText(_translate("Dialog", "Именниники на ближайшую неделю"))
