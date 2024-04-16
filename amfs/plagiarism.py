"""
Copyright (C) 2024 Yuhan Zhang - All Rights Reserved

This file is part of AMFS, which is distributed under the terms of the GPLv3 License.
See the file LICENSE at the top level directory of this distribution for details.
"""

import os
from datetime import date, timedelta
from urllib.error import HTTPError, URLError
from urllib.request import urlopen

import mosspy
from bs4 import BeautifulSoup

# MOSS registered user id
# https://theory.stanford.edu/~aiken/moss/
USER_ID = 569350584


class PlagDetection:
    """
    Plagiarism detection module.

    Attributes:
        language: Programming language for detection
        submission_dir: Directory containing subdirectories of student submissions
        ignore_limit: Maximum number of times a given passage may appear before it is ignored
    """

    def __init__(
            self,
            language: str,
            submission_dir: str,
            ignore_limit: int
    ):
        """
        Initiates a new plagiarism detection job.

        Args:
            language: Programming language for detection
            submission_dir: Directory containing subdirectories of student submissions
            ignore_limit: Maximum number of times a given passage may appear before it is ignored
        """
        self.language = language
        self.submission_dir = submission_dir
        self.ignore_limit = ignore_limit

        # Set up MOSS config
        self.moss = mosspy.Moss(USER_ID, self.language)
        self.moss.setIgnoreLimit(self.ignore_limit)
        self.moss.setDirectoryMode(1)
        self.moss.addFilesByWildcard(os.path.join(self.submission_dir,
                                                  self.wildcard_ext(self.language)))

    @staticmethod
    def wildcard_ext(language: str) -> str:
        """
        Generates a wildcard file extensions of the specified programming language.
        For example: java -> "\*/\*.java"

        Args:
            language: Programming language for detection

        Returns:
            A matching pattern for wildcard file extensions
        """
        match language:
            case "java":
                return "*/*.java"

    @staticmethod
    def extract_plag(row) -> dict[str, str]:
        """
        Extracts detailed plagiarism information from the specified HTML tr row.

        Args:
            row: HTML tr row from MOSS report url

        Returns:
            A dictionary containing the extracted plagiarism information
        """
        file_1, file_2, line_match = None, None, None

        for index, cell in enumerate(row.find_all('td')):
            if index == 0:
                file_1 = cell.a.get_text()
            elif index == 1:
                file_2 = cell.a.get_text()
            elif index == 2:
                line_match = cell.get_text()

        return {
            'sm_1': file_1.split(' ')[0].split('/')[-2] + ' ' + file_1.split(' ')[1],
            'sm_2': file_2.split(' ')[0].split('/')[-2] + ' ' + file_2.split(' ')[1],
            'line_match': line_match.rstrip('\n')
        }

    def run(self) -> dict:
        """
        Sends all detecting files to MOSS server, retrieves the report url, and extracts the
        information within.

        Returns:
            A dictionary containing the extracted plagiarism information
        """
        return {
            'response': True,
            'extract': True,
            'url': "http://moss.stanford.edu/results/5/6439746637801",
            'date': "Apr 29, 2024",
            'pg_list': [
                {'sm_1': 'Submission_02 (97%)', 'sm_2': 'Submission_03 (97%)', 'line_match': '58'},
                {'sm_1': 'Submission_00 (99%)', 'sm_2': 'Submission_03 (97%)', 'line_match': '57'},
                {'sm_1': 'Submission_00 (99%)', 'sm_2': 'Submission_02 (96%)', 'line_match': '57'},
                {'sm_1': 'Submission_04 (97%)', 'sm_2': 'Submission_03 (95%)', 'line_match': '57'},
                {'sm_1': 'Submission_02 (95%)', 'sm_2': 'Submission_04 (97%)', 'line_match': '57'},
                {'sm_1': 'Submission_00 (97%)', 'sm_2': 'Submission_04 (97%)', 'line_match': '57'}
            ]
        }


def main():
    pd = PlagDetection(
        language="java",
        submission_dir="/Users/zhangyuhan/Desktop/GRP/AMFS/test/submission",
        ignore_limit=100
    )

    plagiarism = pd.run()
    print("Response:", plagiarism['response'])
    print("Extract:", plagiarism['extract'])
    print("Url:", plagiarism['url'])
    print("Date:", plagiarism['date'])

    for row in plagiarism['pg_list']:
        print(row)


if __name__ == '__main__':
    main()
