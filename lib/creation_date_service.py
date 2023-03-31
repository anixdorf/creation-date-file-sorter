import logging


class CreationDateService(object):
    def __init__(self, shell_application):
        self.shell_application = shell_application
        self.logger = logging.getLogger("CreationDateService")

    def get_creation_datetime(self, file_path):
        return self.shell_application.get_creation_datetime(file_path)
