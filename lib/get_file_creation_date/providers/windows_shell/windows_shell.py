import os
import logging
from typing import Optional

import win32com.client

from lib.dateparser.dateparser import parse_date
from lib.get_file_creation_date.domain.create_date_result import GetFileCreationDateResult
from lib.get_file_creation_date.providers.file_creation_date_provider import FileCreationDateProvider


class WindowsShellFileCreationDateProvider(FileCreationDateProvider):
    FIELDS = ["Aufnahmedatum", "Medium erstellt", "Erstelldatum", "Änderungsdatum"]

    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.shell = win32com.client.Dispatch("Shell.Application")

    def get_file_creation_date(self, file_path: str) -> Optional[GetFileCreationDateResult]:
        properties = self._get_file_properties(file_path)
        values = []
        for index, field in enumerate(self.FIELDS):
            if field in properties:
                value = properties[field]
                if value:
                    values.append((self.FIELDS[index], parse_date(value)))
        values = [value for value in values if value[0] and value[1]]
        if len(values) > 0:
            values.sort(key=lambda x: x[1])
            return GetFileCreationDateResult(method=values[0][0], creation_date=values[0][1])
        return None

    def _get_file_properties(self, file_path):
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
