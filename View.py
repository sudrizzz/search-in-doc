import os.path
import subprocess

from PyQt5 import QtWidgets
from PyQt5.QtCore import QAbstractTableModel, Qt, QPoint
from PyQt5.QtGui import QFont, QIcon
from PyQt5.QtWidgets import QApplication, QWidget, QLineEdit, \
    QGridLayout, QPushButton, QLabel, QFileDialog, QTableView, QHeaderView, QMenu, QSizePolicy

from Search import Search


class App(QWidget):
    def __init__(self, data):
        super().__init__()
        self.title = '文档内容搜索'
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
        label3.setMaximumHeight(40)
        self.bt1 = QPushButton('选择目录')
        self.bt2 = QPushButton('搜索')
        self.bt3 = QPushButton('清空缓存')
        self.line1 = QLineEdit("")
        self.line2 = QLineEdit("")

        layout.addWidget(label1, 0, 0)
        layout.addWidget(self.line1, 0, 1)
        layout.addWidget(self.bt1, 0, 2)
        layout.addWidget(label2, 1, 0)
        layout.addWidget(self.line2, 1, 1)
        layout.addWidget(self.bt2, 1, 2)
        layout.addWidget(label3, 2, 0)
        layout.addWidget(self.bt3, 2, 2)
        self.bt2.setToolTip('初次搜索会创建缓存，请稍等')
        self.bt3.setToolTip('若未搜索到文档内新增内容，请点击清空缓存按钮，再尝试搜索')
        self.line1.setToolTip('若未选择目录，则默认为程序所在目录')
        self.line2.setToolTip('支持多个关键词，请使用空格隔开，按 Enter 搜索')

        self.table_model = MyTableModel(self, self.data)
        self.table_view = QTableView()
        self.table_view.horizontalHeader().setDefaultAlignment(Qt.AlignLeft | Qt.AlignVCenter)
        self.table_view.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeToContents)
        self.table_view.setModel(self.table_model)
        self.table_view.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        self.table_view.setContextMenuPolicy(Qt.CustomContextMenu)
        layout.addWidget(self.table_view, 3, 0, 3, 3)
        self.setLayout(layout)

        self.bt1.clicked.connect(self.set_browser_path)
        self.bt2.clicked.connect(self.search_content)
        self.bt3.clicked.connect(self.clear_cache)
        self.line1.returnPressed.connect(self.enter_to_search)
        self.line2.returnPressed.connect(self.enter_to_search)
        self.table_view.doubleClicked.connect(self.on_double_click)
        self.table_view.customContextMenuRequested.connect(self.on_right_click)

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
        keyword = self.line2.text().strip().split(' ')
        search = Search()
        data = search.find_in_dir(root_dir, keyword, cache_path)
        if len(data) == 0:
            data = [['', '', '']]
        self.table_model.set_data(data)
        self.table_view.repaint()
        self.table_view.update()

    def clear_cache(self):
        cache_path = os.path.abspath('.cache')
        files = os.listdir(cache_path)
        for file in files:
            file_path = os.path.join(cache_path, file)
            os.remove(file_path)

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

    def enter_to_search(self):
        self.search_content()


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
