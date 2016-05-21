# !/usr/bin/env python3
# -*- coding: utf-8 -*-

from app.ui.ui_files_list_dialog import Ui_FilesListDialog
from app import mlog, mconfig
from app.util.download_thread import DownloadThread
import app.custom_you_get.status as status
from PyQt5.QtGui import *
from PyQt5.QtCore import *
from PyQt5.QtWidgets import *

__author__ = 'InG_byr'


class FilesListDialog(Ui_FilesListDialog):
    def __init__(self):
        super().__init__()
        self.files_list_dialog = QDialog()
        self.setupUi(self.files_list_dialog)
        self.files_list_dialog.show()
        self.msg = QMessageBox()
        self.set_slot()
        self.set_combo_box()

    def set_slot(self):
        self.push_button_confirm.clicked.connect(self.start_download_files)
        self.push_button_cancel.clicked.connect(self.files_list_dialog.close)

    def set_combo_box(self):
        options = mconfig.get_streams()
        if options:
            self.combo_box_options.addItems(options)
        else:
            self.combo_box_options.addItem('default')

    def update_files_list(self, files_list):
        self.text_files_list.setHtml(files_list)
        # self.text_files_list.insertHtml(files_list)

    def start_download_files(self):
        option = self.combo_box_options.currentText()
        mconfig.set_file_itag(option)
        mlog.debug('option is ' + option)

        self.download_thread = DownloadThread(mconfig.get_urls(), **mconfig.kwargs)
        self.download_thread.finish_signal.connect(self.finish_download)
        self.download_thread.start()

        self.result_info = self.show_progress_bar()

    def show_msg(self, icon, title, text):
        self.msg.setWindowTitle(title)
        self.msg.setIcon(icon)
        self.msg.setText(text)
        self.msg.setStandardButtons(QMessageBox.Ok)
        self.msg.show()

    def finish_download(self, is_succeed):
        if is_succeed:
            if self.result_info:
                self.show_msg(QMessageBox.Information, 'Tip',
                              self.result_info + '\n\nFiles path: ' + mconfig.get_file_path())
            else:
                self.show_msg(QMessageBox.Information, 'Completed',
                              'Download completed (ง •̀_•́)ง\n\nFiles path:' + mconfig.get_file_path())
        else:
            self.show_msg(QMessageBox.Critical, 'Failed', 'Download failed (╯°Д°)╯︵ ┻━┻')

    def show_progress_bar(self):
        percent = 0
        is_exits = False
        result = None
        progressDialog = QProgressDialog(self.files_list_dialog)
        progressDialog.setAutoReset(True)
        progressDialog.setWindowModality(Qt.WindowModal)
        progressDialog.setMinimumDuration(5)
        progressDialog.setWindowTitle('Downloading')
        progressDialog.setLabelText('Current speed: ')
        progressDialog.setCancelButtonText('Cancel')
        progressDialog.setRange(0, 100)

        while percent < 100 and not is_exits:
            percent = status.get_percent()
            is_exits = status.get_exist()
            if is_exits:
                result = 'Files already exists (..•˘_˘•..)'
                percent = 100
            progressDialog.setValue(percent)
            progressDialog.setLabelText('Current speed: ' + str(status.get_speed()))
            QThread.msleep(100)
            if progressDialog.wasCanceled():
                pass
                # todo: can not cancel
                status.set_stop_thread(True)
                self.download_thread.wait()
                mlog.debug('stop the download thread')
                mlog.debug('download_thread.isRunning ' + str(self.download_thread.isRunning()))
                percent = 100
                result = 'Paused Σ(っ °Д °;)っ'

        return result