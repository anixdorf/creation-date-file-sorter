from datetime import datetime
from unittest import TestCase, main

from lib.dateparser.dateparser import parse_date


class TestEnhancedDateParser(TestCase):
    def test_parse_date_iso_format_t_separator(self):
        self.assertEqual(
            parse_date("some_file_2022-01-15T14:30:00.jpg"),
            datetime(2022, 1, 15, 14, 30, 0),
        )

    def test_parse_date_iso_format_space_separator(self):
        self.assertEqual(
            parse_date("archive.2023-02-10 09:25:10.zip"),
            datetime(2023, 2, 10, 9, 25, 10),
        )

    def test_parse_date_yyyymmdd_hhmmss_format(self):
        self.assertEqual(
            parse_date("backup_20210320_120000.tar.gz"), datetime(2021, 3, 20, 12, 0, 0)
        )

    def test_parse_date_yyyymmdd_format(self):
        self.assertEqual(parse_date("IMG-20201105-WA0001.jpg"), datetime(2020, 11, 5))

    def test_parse_date_yyyy_mm_dd_format(self):
        self.assertEqual(parse_date("My-Vacation-2019-07-04.png"), datetime(2019, 7, 4))

    def test_parse_date_yyyy_mm_dd_underscore_format(self):
        self.assertEqual(
            parse_date("report_2018_05_21_final.docx"), datetime(2018, 5, 21)
        )

    def test_parse_date_yyyy_mm_dd_dot_format(self):
        self.assertEqual(parse_date("Scan.2017.12.31.pdf"), datetime(2017, 12, 31))

    def test_parse_date_dd_mm_yyyy_dot_format(self):
        self.assertEqual(parse_date("document_15.08.2016.txt"), datetime(2016, 8, 15))

    def test_parse_date_dd_mm_yyyy_hyphen_format(self):
        self.assertEqual(parse_date("receipt-01-02-2022.pdf"), datetime(2022, 2, 1))

    def test_parse_date_img_prefix_format(self):
        self.assertEqual(
            parse_date("IMG_20230312_123456.jpg"), datetime(2023, 3, 12, 12, 34, 56)
        )

    def test_parse_date_vid_prefix_format(self):
        self.assertEqual(parse_date("VID-20210901-WA0000.mp4"), datetime(2021, 9, 1))

    def test_parse_date_screenshot_prefix_format(self):
        self.assertEqual(
            parse_date("Screenshot_2022-04-30-11-22-33.png"), datetime(2022, 4, 30)
        )

    def test_parse_date_no_date(self):
        self.assertIsNone(parse_date("a_file_with_no_date.txt"))

    def test_parse_date_invalid_date(self):
        self.assertIsNone(parse_date("2021-13-40_invalid_date.jpg"))

    def test_parse_date_empty_string(self):
        self.assertIsNone(parse_date(""))

    def test_parse_date_none_input(self):
        self.assertIsNone(parse_date(None))


if __name__ == "__main__":
    main()
