import logging
import os

import win32com.client

from lib.parse_datetime import parse_datetime


class ShellApplication(object):
    def __init__(self):
        self.logger = logging.getLogger("ShellApplication")
        self.shell = win32com.client.Dispatch("Shell.Application")

    def get_file_properties(self, file_path):
        folder, filename = os.path.split(file_path)
        folder = self.shell.NameSpace(folder)
        file = folder.ParseName(filename)
        properties = {}
        for i, name in self._get_property_names(folder):
            properties[self._filter_string(name)] = self._filter_string(folder.GetDetailsOf(file, i))
        try:
            self.logger.debug("properties of '%s': %s", file_path, properties)
        except Exception as e:
            print("can't log: " + str(e))
        return properties

    def get_creation_datetime(self, file_path, fields):
        properties = self.get_file_properties(file_path)
        values = []
        for index, field in enumerate(fields):
            if field in properties:
                value = properties[field]
                if value:
                    values.append((fields[index], parse_datetime(value)))
        values = [value for value in values if value[0] and value[1]]
        if len(values) > 0:
            values.sort(key=lambda x: x[1])
            return values[0]
        return None, None

    @staticmethod
    def _get_property_names(folder):
        result = []
        for i in range(384):
            details_result = folder.GetDetailsOf(None, i)
            if details_result:
                result.append((i, details_result))
        return result

    @staticmethod
    def _filter_string(input_str: str) -> str:
        return input_str \
            .replace("\u200e", "") \
            .replace("\u200f", "") \
            .replace("\u202a", "") \
            .replace("\u202c", "")
