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

class DownloadManager:
        def __init__(self):
            self.downloads = []

        def add_download(self, download):
            self.downloads.append(download)

        def remove_download(self, download):
            self.downloads.remove(download)

        def get_downloads(self):
            return self.downloads

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
        translate_button = QAction(QIcon('icons/icons/translate.png'), 'Dịch trang', self)


        back_button.triggered.connect(self.tabs.currentWidget().back)
        next_button.triggered.connect(self.tabs.currentWidget().forward)
        stop_button.triggered.connect(self.tabs.currentWidget().stop)
        fresh_button.triggered.connect(self.tabs.currentWidget().reload)
        translate_button.triggered.connect(self.translate_page)

        navigation_bar.addAction(back_button)
        navigation_bar.addAction(next_button)
        navigation_bar.addAction(stop_button)
        navigation_bar.addAction(fresh_button)
        navigation_bar.addAction(translate_button)

        navigation_bar.addSeparator()
        navigation_bar.addWidget(self.urlbar)

        bookmark_button =QAction(QIcon('icons/icons/penguin.png'), 'bookmark', self)
        bookmark_button.triggered.connect(self.bookmarks_list)
        navigation_bar.addSeparator()
        navigation_bar.addAction(bookmark_button)
        
        history_button = QAction(QIcon('icons/icons/history.png'), 'Lịch sử', self)
        history_button.triggered.connect(self.show_history)
        navigation_bar.addAction(history_button)
        
        downloads_button = QAction(QIcon('icons/icons/download.png'), 'Quản lý Tải về', self)
        downloads_button.triggered.connect(self.show_downloads)
        navigation_bar.addAction(downloads_button)
        
        incognito_button = QAction(QIcon('icons/icons/incognito.png'), 'New Incognito Tab', self)
        incognito_button.triggered.connect(self.add_incognito_tab)
        navigation_bar.addAction(incognito_button)

        self.bookmarks_list_widget = QListWidget()
        self.bookmark_manager = BookmarkManager()


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
        
    def show_history(self):
        history_dialog = QDialog(self)
        history_dialog.setWindowTitle('Lịch sử Web')

        history_list_widget = QListWidget(history_dialog)
        for entry in self.tabs.currentWidget().history:
            item = QListWidgetItem(f"{entry['title']} - {entry['url']}")
            history_list_widget.addItem(item)

        layout = QVBoxLayout()
        layout.addWidget(history_list_widget)
        history_dialog.setLayout(layout)

        history_dialog.exec_() 
        
    def show_downloads(self):  # Thêm phương thức show_downloads vào lớp MainWindow
        downloads_dialog = QDialog(self)
        downloads_dialog.setWindowTitle('Quản lý Tải về')

        downloads_list_widget = QListWidget(downloads_dialog)
        for download in self.tabs.currentWidget().download_manager.get_downloads():
            item = QListWidgetItem(download.url().toString())
            downloads_list_widget.addItem(item)

        layout = QVBoxLayout()
        layout.addWidget(downloads_list_widget)
        downloads_dialog.setLayout(layout)

        downloads_dialog.exec_()
        
    def add_incognito_tab(self):
        # Tạo một webview mới cho chế độ ẩn danh với một profile riêng biệt
        incognito_profile = QWebEngineProfile('incognito', self)
        incognito_webview = WebEngineView(self, profile=incognito_profile)
        incognito_webview.settings().setAttribute(QWebEngineSettings.PrivateBrowsingEnabled, True)   
         
    def translate_page(self):
        # Inject Google Translate script vào trang hiện tại
        js_code = """
        if (!window.__googleTranslateInjected) {
            var gt = document.createElement('script');
            gt.src = 'https://translate.google.com/translate_a/element.js?cb=googleTranslateElementInit';
            document.body.appendChild(gt);
            window.googleTranslateElementInit = function() {
                new window.google.translate.TranslateElement({pageLanguage: 'auto', includedLanguages: 'vi,en', layout: window.google.translate.TranslateElement.InlineLayout.SIMPLE}, 'google_translate_element');
            };
            var div = document.createElement('div');
            div.id = 'google_translate_element';
            div.style.position = 'fixed';
            div.style.top = '10px';
            div.style.right = '10px';
            div.style.zIndex = 9999;
            document.body.appendChild(div);
            window.__googleTranslateInjected = true;
        }
        """
        self.tabs.currentWidget().page().runJavaScript(js_code)
   
# each tab contains a webview
class WebEngineView(QWebEngineView):
    def __init__(self, mainwindow, parent=None):
        super(WebEngineView, self).__init__(parent)
        self.settings().setAttribute(QWebEngineSettings.PluginsEnabled, True)
        self.page().windowCloseRequested.connect(self.on_windowCloseRequested)
        self.page().profile().downloadRequested.connect(self.on_downloadRequested)
        self.mainwindow = mainwindow
        
        # Thêm lịch sử web
        self.history = []
        self.page().urlChanged.connect(self.update_history)

        self.download_manager = DownloadManager()
        # Kết nối sự kiện khi download được yêu cầu
        self.page().profile().downloadRequested.connect(self.on_downloadRequested)
        
    def on_windowCloseRequested(self):
        the_index = self.mainwindow.tabs.currentIndex()
        self.mainwindow.tabs.removeTab(the_index)

    def on_downloadRequested(self, downloadItem):
        if  downloadItem.isFinished()==False and downloadItem.state()==0:
     
            the_filename = downloadItem.url().fileName()
            if len(the_filename) == 0 or "." not in the_filename:
                cur_time = datetime.datetime.now().strftime('%Y%m%d%H%M%S')
                the_filename = "download" + cur_time + ".xls"
            the_sourceFile = os.path.join(os.getcwd(), 'Downloads', the_filename)

    
            # downloadItem.setSavePageFormat(QWebEngineDownloadItem.CompleteHtmlSaveFormat)
            downloadItem.setPath(the_sourceFile)
            downloadItem.accept()
            downloadItem.finished.connect(self.on_downloadfinished)
            
            self.download_manager.add_download(downloadItem)
            # downloadItem.finished.connect(self.on_downloadfinished)

    def on_downloadfinished(self):
        js_string = '''
                alert("Đã lưu ảnh thành công");
                '''
        self.page().runJavaScript(js_string)
        
    def show_downloads(self):
        downloads_dialog = QDialog(self)
        downloads_dialog.setWindowTitle('Quản lý Tải về')

        downloads_list_widget = QListWidget(downloads_dialog)
        for download in self.download_manager.get_downloads():
            item = QListWidgetItem(download.url().toString())
            downloads_list_widget.addItem(item)

        layout = QVBoxLayout()
        layout.addWidget(downloads_list_widget)
        downloads_dialog.setLayout(layout)

        downloads_dialog.exec_()


    def createWindow(self, QWebEnginePage_WebWindowType):
        new_webview = WebEngineView(self.mainwindow)
        self.mainwindow.create_new_tab(new_webview)
        return new_webview
    
    def update_history(self):
        current_url = self.url().toString()
        current_title = self.page().title()
        self.history.append({'url': current_url, 'title': current_title})
    
if __name__=='__main__':
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec_())
    
