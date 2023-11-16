# --*-- coding:utf-8 --*--
from PyQt5.QtCore import *
from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
from PyQt5.QtWebEngineWidgets import *
import sys, os, datetime

class Bookmark:
    def __init__(self, url, title, date):
        self.url = url
        self.title = title
        self.date = date


class BookmarkManager:
    def __init__(self):
        self.bookmarks = []

    def add_bookmark(self, bookmark):
        self.bookmarks.append(bookmark)

    def delete_bookmark(self, bookmark):
        self.bookmarks.remove(bookmark)

    def edit_bookmark(self, bookmark, new_url, new_title):
        bookmark.url = new_url
        bookmark.title = new_title

    def get_bookmarks(self):
        return self.bookmarks

class MainWindow(QMainWindow):
    def __init__(self, *args, **kwargs):
        super(MainWindow, self).__init__()
        self.setWindowTitle('Chrome fake :D')
        self.setWindowIcon(QIcon('icons/icons/penguin.png'))
        self.setMinimumSize(QSize(800, 640))
        self.showMaximized()
        self.show()


        self.urlbar = QLineEdit()

        self.urlbar.returnPressed.connect(self.navigate_to_url)

        self.tabs = QTabWidget()
        self.tabs.setDocumentMode(True)
        self.tabs.tabBarDoubleClicked.connect(self.tab_open_doubleclick)
        self.tabs.currentChanged.connect(self.current_tab_changed)
        self.tabs.setTabsClosable(True)
        self.tabs.tabCloseRequested.connect(self.close_current_tab)

        self.add_new_tab(QUrl('http://google.com'), 'Google')
        self.setCentralWidget(self.tabs)

        new_tab_action = QAction(QIcon('icons/icons/add_page.png'), 'New Page', self)
        new_tab_action.triggered.connect(self.add_new_tab)


        navigation_bar = QToolBar('Navigation')
        navigation_bar.setIconSize(QSize(16, 16))
        self.addToolBar(navigation_bar)


        back_button = QAction(QIcon('icons/icons/back.png'), 'Back', self)
        next_button = QAction(QIcon('icons/icons/next.png'), 'Forward', self)
        stop_button = QAction(QIcon('icons/icons/cross.png'), 'Stop', self)
        fresh_button = QAction(QIcon('icons/icons/renew.png'), 'reload', self)

        back_button.triggered.connect(self.tabs.currentWidget().back)
        next_button.triggered.connect(self.tabs.currentWidget().forward)
        stop_button.triggered.connect(self.tabs.currentWidget().stop)
        fresh_button.triggered.connect(self.tabs.currentWidget().reload)
 
        navigation_bar.addAction(back_button)
        navigation_bar.addAction(next_button)
        navigation_bar.addAction(stop_button)
        navigation_bar.addAction(fresh_button)

        navigation_bar.addSeparator()
        navigation_bar.addWidget(self.urlbar)

        bookmark_button =QAction(QIcon('icons/icons/penguin.png'), 'bookmark', self)
        bookmark_button.triggered.connect(self.bookmarks_list)
        navigation_bar.addSeparator()
        navigation_bar.addAction(bookmark_button)
        
        self.bookmarks_list_widget = QListWidget()
        self.bookmark_manager = BookmarkManager()

    def bookmarks_list(self):
        pass

    def renew_urlbar(self, t, browser=None):
        if browser != self.tabs.currentWidget():
            return
        self.urlbar.setText(t.toString())
        self.urlbar.setCursorPosition(0)


    def navigate_to_url(self):
        q = QUrl(self.urlbar.text())
        if q.scheme() == '':
            q.setScheme('http')
        self.tabs.currentWidget().setUrl(q)


    def add_new_tab(self, qurl=QUrl('http://google.com'), label='Google'):
        browser = WebEngineView(self)
        browser.setUrl(qurl)
        self.create_new_tab(browser, label)

    def create_new_tab(self, browser, label='Blank'):
        i = self.tabs.addTab(browser, label)
        self.tabs.setCurrentIndex(i)
        browser.urlChanged.connect(lambda qurl, browser=browser: self.renew_urlbar(qurl, browser))
        browser.loadFinished.connect(lambda _, i=i, browser=browser:
                                     self.tabs.setTabText(i, browser.page().title()[:20]))

    def tab_open_doubleclick(self, i):
        if i == -1:
            self.add_new_tab()

    def current_tab_changed(self, i):
        qurl = self.tabs.currentWidget().url()
        self.renew_urlbar(qurl, self.tabs.currentWidget())

    def close_current_tab(self, i):
        if self.tabs.count() > 1:
            self.tabs.removeTab(i)
        else:
            self.close()
    def bookmarks_list(self):
        bookmarks = self.bookmark_manager.get_bookmarks()
        self.bookmarks_list_widget.clear()
        for bookmark in bookmarks:
            item = QListWidgetItem(bookmark.title)
            item.setToolTip(bookmark.url)
            self.bookmarks_list_widget.addItem(item)

    def add_bookmark(self):
        url = self.urlbar.text()
        title = self.tabs.currentWidget().page().title()
        bookmark = Bookmark(url, title, datetime.datetime.now())
        self.bookmark_manager.add_bookmark(bookmark)
        self.bookmarks_list()

    def delete_bookmark(self):
        index = self.bookmarks_list_widget.currentRow()
        if index < 0:
            return
        bookmark = self.bookmarks_list_widget.takeItem(index)
        self.bookmark_manager.delete_bookmark(bookmark)
        self.bookmarks_list()

    def edit_bookmark(self):
        index = self.bookmarks_list_widget.currentRow()
        if index < 0:
            return
        bookmark = self.bookmarks_list_widget.item(index)
        title = QInputDialog.getText(self, 'Chỉnh sửa bookmark', 'Tiêu đề mới: ', text=bookmark.title)
        if title == '':
            return
        self.bookmark_manager.edit_bookmark(bookmark, title[0], title[1])
        self.bookmarks_list()
# each tab contains a webview
class WebEngineView(QWebEngineView):
    def __init__(self, mainwindow, parent=None):
        super(WebEngineView, self).__init__(parent)
        self.settings().setAttribute(QWebEngineSettings.PluginsEnabled, True)
        self.page().windowCloseRequested.connect(self.on_windowCloseRequested)
        self.page().profile().downloadRequested.connect(self.on_downloadRequested)
        self.mainwindow = mainwindow

    def on_windowCloseRequested(self):
        the_index = self.mainwindow.tabs.currentIndex()
        self.mainwindow.tabs.removeTab(the_index)

    def on_downloadRequested(self, downloadItem):
        if  downloadItem.isFinished()==False and downloadItem.state()==0:
     
            the_filename = downloadItem.url().fileName()
            if len(the_filename) == 0 or "." not in the_filename:
                cur_time = datetime.datetime.now().strftime('%Y%m%d%H%M%S')
                the_filename = "下载文件" + cur_time + ".xls"
            the_sourceFile = os.path.join(os.getcwd(), the_filename)

    
            # downloadItem.setSavePageFormat(QWebEngineDownloadItem.CompleteHtmlSaveFormat)
            downloadItem.setPath(the_sourceFile)
            downloadItem.accept()
            downloadItem.finished.connect(self.on_downloadfinished)

    def on_downloadfinished(self):
        js_string = '''
                alert("Đã lưu trang thành công");
                '''
        self.page().runJavaScript(js_string)

        # 重写createwindow()
    def createWindow(self, QWebEnginePage_WebWindowType):
        new_webview = WebEngineView(self.mainwindow)
        self.mainwindow.create_new_tab(new_webview)
        return new_webview

if __name__=='__main__':
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec_())