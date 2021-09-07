from datetime import (
    datetime,
)

from PyQt5 import (
    QtCore,
    QtWidgets,
)
from PyQt5.QtCore import (
    Qt,
)
from PyQt5.QtGui import QPixmap
from PyQt5.QtWidgets import (
    QMainWindow,
    QTableWidgetItem,
    QTableWidget,
    QMessageBox,
    QHeaderView,
    QDialog,
)
from sqlalchemy import (
    or_,
    select,
)
from sqlalchemy.exc import (
    NoResultFound,
)

from app.data.models import (
    Users,
    Session,
    Phone,
    UserProfile,
)


class ColorsEnum:
    BACKGROUND_COLOR = "background-color: rgb(255, 255, 255);"
    TEXT_COLOR = "color: rgb(57, 57, 57);"
    COLOR_LINE_EDIT = "color: rgb(135, 135, 135);"


class TabBar(QtWidgets.QTabBar):
    def tabSizeHint(self, index):
        size = QtWidgets.QTabBar.tabSizeHint(self, index)
        size.transpose()
        return size

    def paintEvent(self, event):
        painter = QtWidgets.QStylePainter(self)
        opt = QtWidgets.QStyleOptionTab()

        for index in range(self.count()):
            self.initStyleOption(opt, index)
            painter.drawControl(QtWidgets.QStyle.CE_TabBarTabShape, opt)
            painter.save()

            size = opt.rect.size()
            size.transpose()
            rect = QtCore.QRect(QtCore.QPoint(), size)
            rect.moveCenter(opt.rect.center())
            opt.rect = rect

            center = self.tabRect(index).center()
            painter.translate(center)
            painter.rotate(90)
            painter.translate(-center)
            painter.drawControl(QtWidgets.QStyle.CE_TabBarTabLabel, opt)
            painter.restore()

class UserInfoDialog(QDialog):
    """
    Окно с информацией о юзере
    """
    def __init__(self, session, parent, user_login):
        super().__init__()
        self.parent = parent
        self.session = session

        self.user = self.find_user(
            user_login=user_login,
        )

        self.resize(590, 212)
        self.setStyleSheet(
            ColorsEnum.BACKGROUND_COLOR,
        )
        self.label_login = QtWidgets.QLabel(self)
        self.label_login.setGeometry(
            QtCore.QRect(
                60, 40, 141, 17
            ),
        )
        self.label_login.setStyleSheet(
            ColorsEnum.TEXT_COLOR,
        )

        self.label_date_birth = QtWidgets.QLabel(self)
        self.label_date_birth.setGeometry(
            QtCore.QRect(
                60, 90, 111, 17
            )
        )
        self.label_date_birth.setStyleSheet(
            ColorsEnum.TEXT_COLOR,
        )

        self.label_login_data = QtWidgets.QLabel(self)
        self.label_login_data.setGeometry(
            QtCore.QRect(
                210, 40, 321, 17
            )
        )
        self.label_login_data.setStyleSheet(
            ColorsEnum.TEXT_COLOR,
        )

        self.label_date_birth_data = QtWidgets.QLabel(self)
        self.label_date_birth_data.setGeometry(
            QtCore.QRect(
                210, 90, 161, 17
            )
        )
        self.label_date_birth_data.setStyleSheet(
            ColorsEnum.TEXT_COLOR,
        )

        self.pushButton = QtWidgets.QPushButton(self)
        self.pushButton.setGeometry(
            QtCore.QRect(
                190, 140, 181, 41)
        )
        self.pushButton.setStyleSheet("background-color: rgb(255, 0, 0);\n"
                                      "font: 75 14pt \"Ubuntu\";\n"
                                      "color: rgb(255, 255, 255);")

        self.retranslateUi()
        QtCore.QMetaObject.connectSlotsByName(self)

        # сигналы
        self.pushButton.clicked.connect(self.log_out)

    def find_user(self, user_login):
        """
        Находит юзера по логину
        """
        return self.session.query(
            UserProfile
        ).filter_by(
            login=user_login
        ).one()

    def log_out(self):
        """
        Разлогиниваем пользователя
        """
        from .main import LoginWindow
        self.user.state_auth = False
        self.session.commit()
        self.parent.close()
        self.close()
        win_reg = LoginWindow()
        win_reg.show()


    def retranslateUi(self):
        from .main import TextEnum
        _translate = QtCore.QCoreApplication.translate
        self.label_login.setText(_translate("Dialog", TextEnum.DEFAULT_LOGIN_TEXT))
        self.label_date_birth.setText(_translate("Dialog", TextEnum.DEFAULT_DATE_BIRTH_TEXT))
        self.label_login_data.setText(_translate("Dialog", f'{self.user.login}'))
        self.label_date_birth_data.setText(_translate("Dialog", f'{self.user.date_birth}'))
        self.pushButton.setText(_translate("Dialog", "Выйти"))


class ListPhonesTable(QTableWidget):
    """
    Таблица со списком номеров телефона
    """

    def __init__(self, parent, session):
        super(ListPhonesTable, self).__init__()
        self.parent = parent
        self.session = session
        self.setGeometry(QtCore.QRect(15, 11, 891, 631))
        self.setColumnCount(3)
        self.setRowCount(20)  # добавляем "лишнюю" строку для редактирования
        self.setHorizontalHeaderLabels(
            ('Имя', 'Телефон', 'Дата рождения')
        )
        self.verticalHeader().setVisible(False)
        self.horizontalHeader().setSectionResizeMode(0, QHeaderView.Stretch)
        self.horizontalHeader().setSectionResizeMode(1, QHeaderView.Stretch)
        self.horizontalHeader().setSectionResizeMode(2, QHeaderView.Stretch)

    def keyPressEvent(self, event):
        """
        При нажатии на Enter коммитим данные
        """
        # FIXME почему то не равное количество строк появляется при инициилизации таблицы
        # TODO добавить сообщение о том, что запись перемещена
        self.need_clear = False
        msg = []
        if event.key() == Qt.Key_Return:
            count_row = self.rowCount()  # количество строк
            for row in range(count_row):
                # получаем данные из строки
                fullname = self.item(row, 0)
                phone_number = self.item(row, 1)
                date_birth = self.item(row, 2)

                index = self.parent.tabWidget.currentIndex()
                text = self.parent.tabWidget.tabText(index)

                if fullname:
                    fullname = fullname.text()
                    if fullname:
                        fullname = fullname.title()
                if phone_number:
                    phone_number = phone_number.text()
                    if phone_number:
                        if not phone_number.startswith('+'):
                            # просим пользователя вводить номер в определенном формате
                            msg.append(f'Неверный формат номера телефона: {phone_number}!')
                            continue
                if date_birth:
                    date_birth = date_birth.text()
                    if date_birth:
                        try:
                            datetime.strptime(date_birth, '%Y-%m-%d')
                        except (TypeError, ValueError):
                            msg.append(f'Неверный формат даты: {date_birth} !')
                            continue

                check_any_fields = (
                        ((fullname is None) or (fullname is ''))
                        or ((phone_number is None) or (phone_number is ''))
                        or (date_birth is None)
                )
                check_all_fields = (
                        ((fullname is None) or (fullname is ''))
                        and ((phone_number is None) or (phone_number is ''))
                        and ((date_birth is None) or (date_birth is ''))
                )

                try:

                    # пытаемся найти строку
                    current_row = getattr(self, f'row_{row}')
                    current_split_fullname = current_row[0].split(' ')
                    if check_all_fields:
                        user = self.find_user(
                            fullname_split=current_split_fullname,
                            date_birth=current_row[2],
                            phone_num=current_row[1]
                        )
                        if user:
                            user = tuple(user)[0]
                            self.session.delete(user)
                            self.session.commit()
                        continue
                    if check_any_fields:
                        msg.append(f'Не все обязательные поля заполнены {fullname}, {date_birth}, {phone_number} !')
                        continue

                    сheck_changes = not (
                            (fullname in current_row)
                            and (phone_number in current_row)
                            and (date_birth in current_row)
                    )

                    if сheck_changes:
                        fullname_split = fullname.split(' ')
                        if len(fullname_split) < 2:
                            msg.append(f'Не все обязательные поля заполнены {fullname}, {date_birth}, {phone_number} !')
                            continue
                        check_dupl = self.find_user(
                            fullname_split=fullname_split,
                            date_birth=date_birth,
                            phone_num=phone_number
                        )
                        if check_dupl:
                            msg.append(f'Присутствуют дубликаты: {fullname}, {phone_number}, {date_birth} !')
                            continue
                        user = self.find_user(
                            fullname_split=current_split_fullname,
                            date_birth=current_row[2],
                            phone_num=current_row[1]
                        )
                        if user:
                            user = tuple(user)[0]  # ожидаем только 1 юзера
                        user.surname = fullname_split[0]
                        user.name = fullname_split[1]
                        user.date_birth = date_birth
                        self.check_phone(
                            user=user,
                            phone_number=phone_number,
                        )
                        self.session.commit()
                        if fullname[0] not in text:
                            msg.append(f'Запись {fullname} будет перенесена в соответствующую вкладку!')
                        self.need_clear = True


                except AttributeError:
                    # новая строка, создаем новый контакт
                    if check_all_fields:
                        # если строки нет, и она пустая, значит это незаполненные строки
                        continue
                    if check_any_fields:
                        # если не все строки заполнены
                        msg.append(f'Не все обязательные поля заполнены: {fullname}, {phone_number}, {date_birth} !')
                        continue

                    new_split_fullname = fullname.split((' '))
                    if len(new_split_fullname) < 2:
                        msg.append(f'Не все обязательные поля заполнены: {fullname}, {phone_number}, {date_birth} !')
                        continue
                    new_user = Users()
                    new_user.surname = new_split_fullname[0]
                    new_user.name = new_split_fullname[1]
                    new_user.date_birth = date_birth

                    self.check_phone(
                        user=new_user,
                        phone_number=phone_number,
                    )
                    check_dupl = self.find_user(
                        fullname_split=new_split_fullname,  # новые значения
                        date_birth=date_birth,
                        phone_num=phone_number
                    )
                    if check_dupl:
                        msg.append(f'Присутствуют дубликаты: {fullname}, {phone_number}, {date_birth} !')
                        continue
                    self.session.add(new_user)
                    setattr(self, f'row_{row}', (fullname, phone_number, str(date_birth)))
                    self.session.commit()
                    if fullname[0] not in text:
                        msg.append(f'Запись {fullname} будет перенесена в соответствующую вкладку!')
                    self.need_clear = True

            if msg:
                msg = '\n'.join(msg)
                QMessageBox.warning(
                    self, '', msg
                )

            if self.need_clear:
                self.clearContents()
                for r in range(self.rowCount()+1):
                    self.removeRow(r)

                self.setRowCount(20)
                count_attr = self.__dict__.keys()
                list_attr_row = [item for item in count_attr if item.startswith('row')]
                for attr_row in list_attr_row:
                    delattr(self, f'{attr_row}')

                filter_list = [Users.surname.like(f'{symbol}%') for symbol in text]
                rows = self.session.query(
                    Users
                ).filter(
                    or_(*filter_list)
                ).all()
                if rows:
                    for index_row, data in enumerate(rows):
                        self.insert_row(
                            tab=self,
                            index_row=index_row,
                            fullname=data.fullname,
                            phone_number=data.phone.number,
                            date_birth=data.date_birth,
                            need_setattr=True
                        )
                self.need_clear = False


    @staticmethod
    def insert_row(tab, index_row, fullname, phone_number, date_birth, need_setattr=False):
        """
        Вставляет новую строку в таблицу
        """
        tab.insertRow(index_row)
        tab.setItem(index_row, 0, QTableWidgetItem(fullname))
        tab.setItem(index_row, 1, QTableWidgetItem(phone_number))
        tab.setItem(index_row, 2, QTableWidgetItem(str(date_birth)))
        if need_setattr:
            setattr(
                tab,
                f'row_{index_row}',
                (fullname, phone_number, str(date_birth))
            )

    def find_user(self, fullname_split, date_birth, phone_num):
        """
        Проверяет дубликаты юзеров
        """
        stmt = select(Users).where(
            Users.surname == fullname_split[0],
            Users.name == fullname_split[1],
            Users.date_birth == datetime.strptime(date_birth, '%Y-%m-%d') if date_birth else None
        ).join(Users.phone).where(Phone.number == phone_num)

        return self.session.execute(stmt).first()

    def check_phone(self, user, phone_number):
        """
        Проверяет, есть ли такой номер в базе
        """
        phone_qs = self.session.query(
            Phone
        )
        try:
            phone = phone_qs.filter_by(
                number=phone_number
            ).one()
        except NoResultFound:
            self.added_new_phone(user=user, phone_number=phone_number)
        else:
            user.phone_id = phone.phone_id

    def added_new_phone(self, user, phone_number):
        """
        Добавляет новый номер телефона и привязывает его к юзеру
        """
        new_phone = Phone()
        new_phone.number = phone_number
        user.phone = new_phone


class ListPhonesWindow(QMainWindow):
    """
    Окно со списком номеров телефона
    """

    def __init__(self, login):
        super().__init__()
        self.login = login
        self.session = Session()
        self.setEnabled(True)
        self.resize(1058, 753)
        self.setStyleSheet(
            "background-color: rgb(198, 198, 198);"
        )
        self.centralwidget = QtWidgets.QWidget(self)
        self.centralwidget.setObjectName("centralwidget")

        self.label = QtWidgets.QLabel(self.centralwidget)
        self.label.setGeometry(
            QtCore.QRect(
                650, 20, 81, 17
            )
        )
        self.label.setStyleSheet(
            "color: rgb(0, 0, 0);\n"
            "font: 75 12pt \"Ubuntu\";"
        )

        self.label_user_name = QtWidgets.QLabel(
            self.centralwidget
        )
        self.label_user_name.setOpenExternalLinks(False)
        self.label_user_name.setGeometry(
            QtCore.QRect(
                740, 20, 271, 20
            )
        )
        self.label_user_name.setStyleSheet(
            "color: rgb(0, 85, 255);\n"
            "font: 75 11pt \"Ubuntu\";\n"
            "text-decoration: underline;"
        )

        self.label_icon_user = QtWidgets.QLabel(self.centralwidget)
        self.label_icon_user.setGeometry(
            QtCore.QRect(
                585, 10, 40, 41
            )
        )

        self.label_icon_user.setPixmap(QPixmap("pics/logo.png").scaledToWidth(40))

        self.setCentralWidget(self.centralwidget)

        self.create_tab()
        self.retranslateUi()
        QtCore.QMetaObject.connectSlotsByName(self)

        # сигналы
        self.label_user_name.linkActivated.connect(
            self.show_user_info
        )
        self.tabWidget.tabBarClicked.connect(
            self.added_table_widget
        )

        self.added_table_widget(
            index=0,
        )

    def show_user_info(self):
        """
        Открывает окно с информацией о юзере
        """
        win_user_info = UserInfoDialog(
            parent=self,
            session=self.session,
            user_login=self.login
        )
        win_user_info.exec_()

    def create_tab(self):
        """
        Добавляет вкладки с таблицей
        """
        self.tabWidget = QtWidgets.QTabWidget(self.centralwidget)
        self.tabWidget.setGeometry(
            QtCore.QRect(
                60, 60, 951, 661
            )
        )
        self.tabWidget.setTabBar(TabBar(self.tabWidget))
        self.tabWidget.setLayoutDirection(
            QtCore.Qt.LeftToRight
        )
        self.tabWidget.setStyleSheet(
            "background-color: rgb(255, 255, 255);\n"
            "selection-background-color: rgb(135, 135, 135);\n"
            f'{ColorsEnum.COLOR_LINE_EDIT}'
        )
        self.tabWidget.setTabPosition(
            QtWidgets.QTabWidget.West
        )

        tuple_symbols = ("АБ", "ВГ", "ДЕ", "ЖЗИЙ", "КЛ", "МН", "ОП", "РС", "ТУ", "ФХ", "ЦЧШЩ", "ЪЫЬЭ", "ЮЯ")
        for index, symbols in enumerate(tuple_symbols):
            setattr(
                self, f'tab_{index + 1}',
                ListPhonesTable(
                    session=self.session,
                    parent=self,
                )
            )
            tab_obj = getattr(self, f'tab_{index + 1}')
            self.tabWidget.addTab(tab_obj, symbols)

    def added_table_widget(self, index):
        """
        Заполняет таблицу
        """
        text = self.tabWidget.tabText(index)
        if text:
            rows = self.get_qs_users(
                model=Users,
                filter_text=text
            )
            if rows:
                tab_obj = getattr(self, f'tab_{index+1}', None)
                tab_obj.clearContents()
                for r in range(tab_obj.rowCount()+1):
                    tab_obj.removeRow(r)
                tab_obj.setRowCount(20)
                for index_row, data in enumerate(rows):
                    tab_obj.insert_row(
                        tab=tab_obj,
                        index_row=index_row,
                        fullname=data.fullname,
                        phone_number=data.phone.number,
                        date_birth=data.date_birth,
                        need_setattr=True
                    )

    def get_qs_users(self, model, filter_text):
        """
        Получает список для заполнения таблицы
        """
        filter_list = [model.surname.like(f'{symbol}%') for symbol in filter_text]
        return self.session.query(
            model
        ).filter(
            or_(*filter_list)
        ).all()

    def retranslateUi(self):
        _translate = QtCore.QCoreApplication.translate
        self.tabWidget.setToolTip(_translate("ListPhonesWindow", "<html><head/><body><p><br/></p></body></html>"))
        self.label.setText(_translate("ListPhonesWindow", "Зашли как"))
        self.label_user_name.setText(_translate("ListPhonesWindow", f'<a href="#">{self.login}'))
