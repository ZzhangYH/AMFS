import os
from dataclasses import dataclass, field
from itertools import combinations
from pathlib import Path

from jinja2 import Template

from amfs.marking import TestCase, Attempt


@dataclass
class Submission:
    id: str
    mark: float
    attempts: [Attempt]
    failed_tests: set[int] = None
    passed_tests: set[int] = None
    feedback: [str] = field(default_factory=list)


class FeedbackReport:
    def __init__(
            self,
            name: str,
            full_mark: float,
            template_dir: str,
            submission_dir: str,
            submissions: [Submission],
            tests: [TestCase],
            feedbacks: [str],
            feedback_selection: [frozenset[int]]
    ):
        self.name = name
        self.full_mark = full_mark
        self.template_dir = Path(template_dir)
        self.submission_dir = Path(submission_dir)
        self.submissions = submissions
        self.tests = tests
        self.feedbacks = feedbacks
        self.feedback_selection = feedback_selection

        for submission in self.submissions:
            submission.mark = round(submission.mark, 1)
            submission.failed_tests = set()
            submission.passed_tests = set()
            for attempt in submission.attempts:
                if attempt.code != 0:
                    submission.failed_tests.add(attempt.tc_id)
                else:
                    submission.passed_tests.add(attempt.tc_id)

            print(f"Submission {submission.id}: fail: {submission.failed_tests}, pass: {submission.passed_tests}")

    def generate_feedback(self) -> None:
        for submission in self.submissions:
            print(f"Generating feedback for submission {submission.id}")

            # Skip submissions that pass all tests
            if submission.failed_tests == set():
                print("> Pass")
                continue

            temp: set[frozenset[int]] = set()
            discarded: set[frozenset[int]] = set()
            for combination in self.feedback_selection:
                if combination <= submission.failed_tests:
                    temp.add(combination)
                    if len(combination) > 1:
                        discarded |= overridden_tests(combination)

            feedback = [self.feedback_selection.index(tests) for tests in temp - discarded]
            print(f"> temp: {temp}")
            print(f"> discarded: {discarded}")
            print(f"> final: {temp - discarded}")
            print(f"> feedback: {feedback}")
            submission.feedback = [self.feedbacks[i] for i in feedback]

    def render_report(self) -> None:
        report = {
            'name': self.name,
            'full_mark': f"{self.full_mark:.1f}"
        }

        for submission in self.submissions:
            print(f"Rendering report for submission {submission.id}")

            sm_dict = {
                'id': submission.id,
                'mark': f"{submission.mark:.1f}",
                'failed_tests': [md_link(self.tests[i], True) for i in submission.failed_tests],
                'passed_tests': [md_link(self.tests[i], False) for i in submission.passed_tests],
                'feedback': submission.feedback,
                'attempts': [{
                    'name': md_heading(self.tests[attempt.tc_id], attempt.code != 0),
                    'code': render_code(attempt.code),
                    'output': attempt.output
                } for attempt in submission.attempts]
            }

            with open(self.template_dir / "feedback.md", 'r') as f:
                template = Template(f.read(), trim_blocks=True)
                content = template.render(report=report, submission=sm_dict)

            with open(self.submission_dir / submission.id / "feedback.md", 'w') as f:
                f.write(content)

    def run(self):
        self.generate_feedback()
        self.render_report()


def overridden_tests(tests: frozenset[int]) -> set[frozenset[int]]:
    result = set()
    for r in range(1, len(tests)):
        for combination in combinations(tests, r):
            result.add(frozenset(combination))

    return result


def md_heading(test: TestCase, fail: bool) -> str:
    return test.name + f" ({0.0 if fail else test.mark:.1f}/{test.mark:.1f})"


def md_link(test: TestCase, fail: bool) -> str:
    result = "[" + md_heading(test, fail) + "](#"
    for c in md_heading(test, fail):
        if c.isalnum():
            result += c.lower()
        elif c == "-" or c == "_":
            result += c
        elif c == " ":
            result += "-"

    result += ")"
    return result


def render_code(code: int) -> str:
    match code:
        case 0:
            return "PASS"
        case 1:
            return "COMPILE_ERROR"
        case 2:
            return "RUNTIME_ERROR"
        case 3:
            return "TIMEOUT"
        case 4:
            return "INCORRECT_OUTPUT"


def main():
    submissions = [
        Submission(id="00",
                   mark=3,
                   attempts=[
                       Attempt(sm_id="00", tc_id=0, code=0, mark=0, output="Compile success."),
                       Attempt(sm_id="00", tc_id=1, code=0, mark=1, output="10\n"),
                       Attempt(sm_id="00", tc_id=2, code=0, mark=2, output="8\n")
                   ]),
        Submission(id="01",
                   mark=0,
                   attempts=[
                       Attempt(sm_id="01", tc_id=0, code=1, mark=0, output="Compile failed.\nerror: file not found: IdSum.java\nUsage: javac <options> <source files>\nuse --help for a list of possible options")
                   ]),
        Submission(id="02",
                   mark=0,
                   attempts=[
                       Attempt(sm_id="00", tc_id=0, code=2, mark=0, output="Compile success."),
                       Attempt(sm_id="00", tc_id=1, code=2, mark=0, output="10\n\nRuntime error.\nException in thread \"main\" java.lang.IndexOutOfBoundsException\n\tat IdSum.main(IdSum.java:58)"),
                       Attempt(sm_id="00", tc_id=2, code=2, mark=0, output="8\n\nRuntime error.\nException in thread \"main\" java.lang.IndexOutOfBoundsException\n\tat IdSum.main(IdSum.java:58)")
                   ]),
        Submission(id="03",
                   mark=0,
                   attempts=[
                       Attempt(sm_id="00", tc_id=0, code=0, mark=0, output="Compile success."),
                       Attempt(sm_id="00", tc_id=1, code=0, mark=0, output="10\n\nTimeout expired."),
                       Attempt(sm_id="00", tc_id=2, code=0, mark=0, output="8\n\nTimeout expired.")
                   ]),
        Submission(id="04",
                   mark=0,
                   attempts=[
                       Attempt(sm_id="00", tc_id=0, code=0, mark=0, output="Compile success."),
                       Attempt(sm_id="00", tc_id=1, code=0, mark=0, output="20\n"),
                       Attempt(sm_id="00", tc_id=2, code=0, mark=0, output="16\n")
                   ]),
    ]

    tests = [
        TestCase(id=0, name="Compilation", mark=0),
        TestCase(id=1, name="Test 1", mark=1),
        TestCase(id=2, name="Test 2", mark=2),
    ]

    feedbacks = [
        "This is feedback 1",
        "This is feedback 2",
        "This is combinatorial feedback 1, 2"
    ]

    feedback_selection = [
        frozenset({1}),
        frozenset({2}),
        frozenset({1, 2})
    ]

    fr = FeedbackReport(
        name="Sample",
        full_mark=3,
        template_dir="templates",
        submission_dir=os.path.join(os.getcwd(), "../tests/marking/submission"),
        submissions=submissions,
        tests=tests,
        feedbacks=feedbacks,
        feedback_selection=feedback_selection
    )
    fr.run()


if __name__ == '__main__':
    main()
