import os
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

    def run(self) -> [dict[str, str]]:
        print(f"Detecting plagiarism over directory {self.submission_dir}")
        url = None

        # Send files and get report url
        while url is None:
            print("> ", end='')
            url = self.moss.send(lambda file_path, display_name: print('#', end='', flush=True))
            print("\n> MOSS Report Url: " + url)

        # Load contents from the url
        response = urlopen(url)
        charset = response.headers.get_content_charset()
        content = response.read().decode(charset)
        print("\n> Contents loaded from url, soap doing the work...")

        # Extract plagiarism rows
        soup = BeautifulSoup(content, 'lxml')
        plag_list: [dict[str, str]] = []
        for tr in soup.table.find_all('tr')[1:]:
            plag_list.append(PlagDetection.extract_plag(tr))

        return plag_list


def main():
    pd = PlagDetection(
        language="java",
        submission_dir="/Users/zhangyuhan/Desktop/GRP/AMFS/tests/plagiarism",
        ignore_limit=100
    )

    for row in pd.run():
        print(row)


if __name__ == '__main__':
    main()
