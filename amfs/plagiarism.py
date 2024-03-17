import os
from datetime import date, timedelta
from urllib.error import HTTPError
from urllib.request import urlopen

import mosspy
from bs4 import BeautifulSoup

# MOSS registered user id
# https://theory.stanford.edu/~aiken/moss/
userid = 569350584


class PlagDetection:
    def __init__(
            self,
            language: str,
            submission_dir: str,
            ignore_limit: int
    ):
        self.language = language
        self.submission_dir = submission_dir
        self.ignore_limit = ignore_limit

        # Set up MOSS config
        self.moss = mosspy.Moss(userid, self.language)
        self.moss.setIgnoreLimit(self.ignore_limit)
        self.moss.setDirectoryMode(1)
        self.moss.addFilesByWildcard(os.path.join(self.submission_dir,
                                                  self.wildcard_ext(self.language)))

    @staticmethod
    def wildcard_ext(language: str) -> str:
        match language:
            case "java":
                return "*/*.java"

    @staticmethod
    def extract_plag(row) -> dict[str, str]:
        file_1, file_2, line_match = None, None, None

        for index, cell in enumerate(row.find_all('td')):
            if index == 0:
                file_1 = cell.a.get_text()
            elif index == 1:
                file_2 = cell.a.get_text()
            elif index == 2:
                line_match = cell.get_text()

        return {
            'sm_1': file_1.split(' ')[0].split('/')[-2],
            'sm_2': file_2.split(' ')[0].split('/')[-2],
            'percentage': file_2.split(' ')[1].split('(')[1].split(')')[0],
            'line_match': line_match.rstrip('\n')
        }

    def run(self) -> dict:
        print(f"Detecting plagiarism over directory {self.submission_dir}")
        url = None

        # Send files and get report url
        while url is None:
            print("> ", end='')
            url = self.moss.send(lambda file_path, display_name: print('#', end='', flush=True))
            print("\n> MOSS Report Url: " + url)

        plagiarism: dict = {
            'extract': None,
            'url': url,
            'date': (date.today() + timedelta(days=13)).strftime("%b %d, %Y"),
            'pg_list': []
        }

        # Load contents from the url
        try:
            response = urlopen(url)
            charset = response.headers.get_content_charset()
            content = response.read().decode(charset)
            print("> Contents loaded from url, extracting plag details.")
            plagiarism['extract'] = True

            # Extract plagiarism rows
            soup = BeautifulSoup(content, 'lxml')
            for tr in soup.table.find_all('tr')[1:]:
                plagiarism['pg_list'].append(PlagDetection.extract_plag(tr))

        except HTTPError:
            print("> Failed to load contents from url.")

        return plagiarism


def main():
    pd = PlagDetection(
        language="java",
        submission_dir="/Users/zhangyuhan/Desktop/GRP/AMFS/tests/plagiarism",
        ignore_limit=100
    )

    plagiarism = pd.run()
    print(plagiarism['extract'])
    print(plagiarism['url'])
    print(plagiarism['date'])

    for row in plagiarism['pg_list']:
        print(row)


if __name__ == '__main__':
    main()
