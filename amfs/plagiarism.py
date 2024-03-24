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
        print(f"Detecting plagiarism over directory {self.submission_dir}")
        url = None

        # Send files and get report url
        while url is None:
            print("> ", end='')
            url = self.moss.send(lambda file_path, display_name: print('#', end='', flush=True))
            print("\n> MOSS Report Url: " + url)

        plagiarism: dict = {
            'response': None,
            'extract': None,
            'url': url,
            'date': (date.today() + timedelta(days=13)).strftime("%b %d, %Y"),
            'pg_list': []
        }

        # Load contents from the url
        try:
            response = urlopen(url)
            plagiarism['response'] = True
            plagiarism['extract'] = True
            charset = response.headers.get_content_charset()
            content = response.read().decode(charset)
            print("> Contents loaded from url, extracting plag details.")

            # Extract plagiarism rows
            soup = BeautifulSoup(content, 'lxml')
            for tr in soup.table.find_all('tr')[1:]:
                plagiarism['pg_list'].append(PlagDetection.extract_plag(tr))

        except HTTPError:
            plagiarism['response'] = True
            print("> Failed to load contents from url.")

        except (URLError, ValueError):
            print("> Url error.")

        return plagiarism


def main():
    pd = PlagDetection(
        language="java",
        submission_dir="/Users/zhangyuhan/Desktop/GRP/AMFS/tests/plagiarism",
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
