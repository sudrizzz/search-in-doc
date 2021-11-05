import os.path
import subprocess

from PyQt5 import QtWidgets
from PyQt5.QtCore import QAbstractTableModel, Qt, QPoint
from PyQt5.QtGui import QFont, QIcon
from PyQt5.QtWidgets import QApplication, QWidget, QLineEdit, \
    QGridLayout, QPushButton, QLabel, QFileDialog, QTableView, QHeaderView, QMenu

from Search import Search


class App(QWidget):
    def __init__(self, data):
        super().__init__()
        self.title = '文档搜索'
        self.left = 400
        self.top = 50
        self.width = 800
        self.height = 600
        self.data = data
        self.initUI()
        QApplication.setFont(QFont('Microsoft YaHei', pointSize=10))

    def initUI(self):
        self.setWindowTitle(self.title)
        self.setGeometry(self.left, self.top, self.width, self.height)
        layout = QGridLayout()

        label1 = QLabel('根目录')
        label2 = QLabel('关键词')
        label3 = QLabel('搜索结果')
        label4 = QLabel('若未搜索到文档内新增内容，请点击右侧清空缓存按钮，再尝试搜索')
        bt1 = QPushButton('选择目录')
        bt2 = QPushButton('搜索')
        bt3 = QPushButton('清空缓存')
        line1 = QLineEdit("")
        line2 = QLineEdit("")
        label3.setMaximumHeight(40)
        label4.setMaximumHeight(40)

        layout.addWidget(label1, 0, 0)
        layout.addWidget(line1, 0, 1)
        layout.addWidget(bt1, 0, 2)
        layout.addWidget(label2, 1, 0)
        layout.addWidget(line2, 1, 1)
        layout.addWidget(bt2, 1, 2)
        layout.addWidget(label3, 2, 0)

        table_model = MyTableModel(self, self.data)
        table_view = QTableView()
        table_view.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeToContents)
        table_view.setModel(table_model)

        layout.addWidget(table_view, 3, 0, 3, 3)

        layout.addWidget(label4, 4, 0, 4, 2, alignment=Qt.AlignLeft | Qt.AlignBottom)
        layout.addWidget(bt3, 4, 2, 4, 3, alignment=Qt.AlignRight | Qt.AlignBottom)

        self.setLayout(layout)
        bt1.clicked.connect(self.set_browser_path)
        bt2.clicked.connect(self.search_content)

        table_view.doubleClicked.connect(self.on_double_click)
        table_view.setContextMenuPolicy(Qt.CustomContextMenu)
        table_view.customContextMenuRequested.connect(self.on_right_click)

        # Show widget
        self.center()
        self.show()

    def center(self):
        frameGm = self.frameGeometry()
        screen = QtWidgets.QApplication.desktop().screenNumber(
            QtWidgets.QApplication.desktop().cursor().pos())
        centerPoint = QtWidgets.QApplication.desktop().screenGeometry(screen).center()
        frameGm.moveCenter(centerPoint)
        self.move(frameGm.topLeft())

    def set_browser_path(self):
        path = str(QFileDialog.getExistingDirectory(self, "选择根目录"))
        self.line1.setText(path)

    def search_content(self):
        cache_path = os.path.abspath('.cache')
        if not os.path.exists(cache_path):
            os.mkdir(cache_path)
        root_dir = self.line1.text()
        self.line1.setText(os.path.abspath(root_dir))
        keyword = self.line2.text()
        search = Search()
        data = search.find_in_dir(root_dir, keyword, cache_path)
        if len(data) == 0:
            data = [['', '', '']]
        self.table_model.set_data(data)
        self.table_view.repaint()
        self.table_view.update()

    def on_double_click(self, index):
        row = index.row()
        data = self.table_model.data[row][1]
        os.startfile(data)

    def on_right_click(self, QPos=None):
        self.table_view.rcMenu = QMenu()
        open_action = self.table_view.rcMenu.addAction('打开')
        copy_action = self.table_view.rcMenu.addAction('复制路径')
        open_dir_action = self.table_view.rcMenu.addAction('打开所在文件夹')
        parent = self.sender()
        mPos = parent.mapToGlobal(QPoint(5, 20)) + QPos
        self.table_view.rcMenu.move(mPos)
        self.table_view.rcMenu.show()

        index = self.table_view.indexAt(QPos)
        data = self.table_model.data[index.row()][1]
        action = self.table_view.rcMenu.exec_(self.table_view.viewport().mapToGlobal(QPos))
        if action == open_action:
            os.startfile(data)
        elif action == copy_action:
            QApplication.clipboard().setText(data)
        elif action == open_dir_action:
            subprocess.Popen(r'explorer /select, %s' % data)


class MyTableModel(QAbstractTableModel):
    def __init__(self, parent, data, *args):
        QAbstractTableModel.__init__(self, parent, *args)
        self.data = data
        self.header = ['序号', '文件', '行内容']

    def rowCount(self, parent):
        return len(self.data)

    def columnCount(self, parent):
        return len(self.data[0])

    def data(self, index, role):
        if not index.isValid():
            return None
        elif role != Qt.DisplayRole:
            return None
        return self.data[index.row()][index.column()]

    def headerData(self, col, orientation, role):
        if orientation == Qt.Horizontal and role == Qt.DisplayRole:
            return self.header[col]
        return None

    def set_data(self, data):
        self.data = data
        self.layoutAboutToBeChanged.emit()
        self.dataChanged.emit(self.createIndex(0, 0), self.createIndex(self.rowCount(0), self.columnCount(0)))
        self.layoutChanged.emit()
