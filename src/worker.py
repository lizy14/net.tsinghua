from PyQt5.QtCore import QObject, QTimer

from tsinghua import Account
from config import load_config

class Worker(QObject):
    """Worker"""
    def __init__(self, parent=None):
        super().__init__(parent)

        self.config = load_config()
        self.account = Account(config['username'])

        # Timers.
        self.status_timer = QTimer(self)
        self.info_timer = QTimer(self)
        self.auto_manage_timer = Qtimer(self)
        self.status_timer.setInterval(self.config['status_update_interval_msec'])
        self.info_timer.setInterval(self.config['info_update_interval_msec'])
        self.auto_manage_timer.setInterval(self.config['auto_manage_interval_msec'])

    def setup(self):
        """Things to set the worker up"""
        self.status_timer.timeout.connect(self.account.update_status)
        self.info_timer.timeout.connect(self.account.update_infos)
        self.auto_manage_timer.timeout.connect(self.auto_manage)

        self.status_timer.start()
        self.info_timer.start()
        self.auto_manage_timer.start()

        # Double check whether we need to do something when status changed.
        self.account.status_changed.connect(self.auto_manage)

        self.account.setup()

    def auto_manage(self):
        if not self.config['auto_manage']:
            return

        # Auto login.
        if self.account.status == 'OFFLINE':
            self.account.login()

        # TODO: Auto logout, etc.
