import os
from pathlib import Path

import mosspy

# MOSS registered user id
# https://theory.stanford.edu/~aiken/moss/
userid = 569350584


class PlagiarismDetection:
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
        self.moss.addFilesByWildcard(os.path.join(self.submission_dir, wildcard_ext(self.language)))

    def run(self):
        print(f"Detecting plagiarism over directory {self.submission_dir}")
        url = None

        # Send files and download report
        while url is None:
            print("> ", end='')
            url = self.moss.send(lambda file_path, display_name: print('#', end='', flush=True))
            print("\n> MOSS Report Url: " + url)

        self.moss.saveWebPage(url, self.submission_dir + "/plagiarism.html")
        print("> Report downloaded successfully")


def wildcard_ext(language: str) -> str:
    match language:
        case "java":
            return "*/*.java"


def main():
    pd = PlagiarismDetection(
        language="java",
        submission_dir="/Users/zhangyuhan/Desktop/GRP/AMFS/tests/plagiarism",
        ignore_limit=100
    )
    pd.run()


if __name__ == '__main__':
    main()
