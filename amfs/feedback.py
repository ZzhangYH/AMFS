"""
Copyright (C) 2024 Yuhan Zhang - All Rights Reserved

This file is part of AMFS, which is distributed under the terms of the GPLv3 License.
See the file LICENSE at the top level directory of this distribution for details.
"""

import os
from dataclasses import dataclass, field
from itertools import combinations
from pathlib import Path

from jinja2 import Template
from weasyprint import HTML, CSS

from amfs.marking import TestCase, Attempt


@dataclass
class Submission:
    """
    Record of a submission information.

    Attributes:
        id: ID of this submission
        mark: Actual mark of this submission
        attempts: A list of all marking attempts of this submission
        failed_tests: A set of test case IDs failed by this submission
        passed_tests: A set of test case IDs passed by this submission
    """
    id: str
    mark: float
    attempts: [Attempt]
    failed_tests: set[int] = None
    passed_tests: set[int] = None
    feedback: [str] = field(default_factory=list)


# noinspection GrazieInspection
class FeedbackReport:
    """
    Feedback generation module.

    Attributes:
        name: Nome of the marking job
        full_mark: Full mark of the marking job
        template_file: Path string to the html template file
        css_file: Path string to the css file for the template
        submission_dir: Directory containing subdirectories of student submissions
        submissions: A list of all submission objects
        tests: A list of all test case objects
        feedbacks: A list of all feedback strings
        feedback selection: A list of sets containing test case IDs corresponding to each feedback
    """
    def __init__(
            self,
            name: str,
            full_mark: float,
            template_file: str,
            css_file: str,
            submission_dir: str,
            submissions: [Submission],
            tests: [TestCase],
            feedbacks: [str],
            feedback_selection: [frozenset[int]]
    ):
        """
        Initiates a new feedback generation job.

        Args:
            name: Nome of the marking job
            full_mark: Full mark of the marking job
            template_file: Path string to the html template file
            css_file: Path string to the css file for the template
            submission_dir: Directory containing subdirectories of student submissions
            submissions: A list of all submission objects
            tests: A list of all test case objects
            feedbacks: A list of all feedback strings
            feedback selection: A list of sets containing test case IDs
             corresponding to each feedback
        """
        self.name = name
        self.full_mark = full_mark
        self.template_file = Path(template_file)
        self.css_file = Path(css_file)
        self.submission_dir = Path(submission_dir)
        self.submissions = submissions
        self.tests = tests
        self.feedbacks = feedbacks
        self.feedback_selection = feedback_selection

        # Setting up for result stats
        self.sm_mark_sum = 0.0
        self.tc_stats = [{
            'name': f"{tc.name}",
            'mark': tc.mark,
            'pass_count': 0
        } for tc in tests]

        for submission in self.submissions:
            self.sm_mark_sum += submission.mark
            submission.mark = round(submission.mark, 1)
            submission.failed_tests = set()
            submission.passed_tests = set()
            for attempt in submission.attempts:
                if attempt.code == 0:
                    self.tc_stats[attempt.tc_id]['pass_count'] += 1
                    submission.passed_tests.add(attempt.tc_id)
                else:
                    submission.failed_tests.add(attempt.tc_id)

            print(f"Submission {submission.id}: fail: {submission.failed_tests}, pass: {submission.passed_tests}")

    @staticmethod
    def overridden_tests(tests: frozenset[int]) -> set[frozenset[int]]:
        """
        Calculates all possible combinations of test case IDs in the given set.
        This is used for discarding certain feedbacks already covered by combinatorial ones.

        Args:
            tests: A set of test case IDs

        Returns:
            A set of calculated set combinations
        """
        result = set()
        for r in range(1, len(tests)):
            for combination in combinations(tests, r):
                result.add(frozenset(combination))

        return result

    @staticmethod
    def render_code(code: int) -> str:
        """
        Renders the marking result code to corresponding written indicators in feedback reports.

        Args:
            code: Integer code in the attempt object

        Returns:
            A written indicator for the attempt result
        """
        match code:
            case 0:
                return "PASS"
            case 1:
                return "COMPILE_ERROR"
            case 2:
                return "RUN_ERROR"
            case 3:
                return "TIME_LIMIT"
            case 4:
                return "WRONG_ANSWER"

    @staticmethod
    def html_tc(test: TestCase, fail: bool, tag: str) -> str:
        """
        Generates HTML code blocks for the specified test case.

        Args:
            test: Test case object
            fail: Whether it is failed or not
            tag: HTML tag (<h4> or <a>)

        Returns:
            HTML code blocks to be render in feedback reports
        """
        content = test.name + f" ({0.0 if fail else test.mark:.1f}/{test.mark:.1f})"
        state = "fail" if fail else "pass"

        if tag == "h4":
            return f'<h4 id="{content}" class="{state}">{content}</h4>'
        elif tag == "a":
            return f'<a href="#{content}" class="{state}">{content}</a>'

    def _generate_feedback(self) -> None:
        """
        Generates feedback for all submissions. The process include comparing failed test cases
        of a submission with feedback selections, resulting in a list of feedback messages
        written into the submission object.

        Returns:
            None
        """
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
                        discarded |= FeedbackReport.overridden_tests(combination)

            feedback = [self.feedback_selection.index(tests) for tests in temp - discarded]
            print(f"> temp: {temp}")
            print(f"> discarded: {discarded}")
            print(f"> final: {temp - discarded}")
            print(f"> feedback: {feedback}")
            submission.feedback = [self.feedbacks[i] for i in feedback]

    def _render_report(self) -> None:
        """
        Renders feedback reports for all submissions and saves them directly into each corresponding
        submission directories.

        Returns:
            None
        """
        report = {
            'name': self.name,
            'full_mark': f"{self.full_mark:.1f}"
        }

        for submission in self.submissions:
            print(f"Rendering report for submission {submission.id}")

            sm_dict = {
                'id': submission.id,
                'mark': f"{submission.mark:.1f}",
                'failed_tests': [FeedbackReport.html_tc(self.tests[i], True, "a")
                                 for i in submission.failed_tests],
                'passed_tests': [FeedbackReport.html_tc(self.tests[i], False, "a")
                                 for i in submission.passed_tests],
                'feedback': submission.feedback,
                'attempts': [{
                    'name': FeedbackReport.html_tc(self.tests[attempt.tc_id],
                                                   attempt.code != 0,
                                                   "h4"),
                    'code': FeedbackReport.render_code(attempt.code),
                    'output': attempt.output
                } for attempt in submission.attempts]
            }

            with open(self.template_file, 'r') as f:
                template = Template(f.read())
                content = template.render(report=report, submission=sm_dict)

            HTML(string=content).write_pdf(
                target=self.submission_dir / submission.id / "feedback.pdf",
                stylesheets=[CSS(filename=self.css_file)]
            )

    def _statistics(self) -> dict:
        """
        Summarizes the marking results, providing statistics for the users.

        Returns:
            A dictionary of the results data.
        """
        sm_count = len(self.submissions)
        full_mark = f"{self.full_mark:.2f}"
        avg_mark = f"{self.sm_mark_sum / sm_count:.2f}"
        for tc in self.tc_stats:
            tc['full_mark'] = f"{tc['mark']:.2f}"
            tc['avg_mark'] = f"{tc['mark'] * tc['pass_count'] / sm_count:.2f}"
            tc['pass_rate'] = f"{tc['pass_count'] / sm_count:.0%}"

        print("Result statistics:")
        print("> sm_count:", sm_count)
        print("> full_mark:", full_mark)
        print("> avg_mark:", avg_mark)
        print("> tc_stats:", self.tc_stats)

        return {
            'sm_count': sm_count,
            'avg_mark': avg_mark,
            'full_mark': full_mark,
            'tc_stats': self.tc_stats
        }

    def run(self) -> dict:
        """
        Generates feedback, render and writes feedback reports.

        Returns:
            The marking result statistics
        """
        self._generate_feedback()
        self._render_report()
        return self._statistics()


def main():
    submissions = [
        Submission(id="Submission_00",
                   mark=3,
                   attempts=[
                       Attempt(sm_id="Submission_00", tc_id=0, code=0, mark=0, output="Compile success."),
                       Attempt(sm_id="Submission_00", tc_id=1, code=0, mark=1, output="10\n"),
                       Attempt(sm_id="Submission_00", tc_id=2, code=0, mark=2, output="8\n")
                   ]),
        Submission(id="Submission_01",
                   mark=0,
                   attempts=[
                       Attempt(sm_id="Submission_01", tc_id=0, code=1, mark=0, output="Compile failed.\nerror: file not found: IdSum.java\nUsage: javac <options> <source files>\nuse --help for a list of possible options")
                   ]),
        Submission(id="Submission_02",
                   mark=0,
                   attempts=[
                       Attempt(sm_id="Submission_02", tc_id=0, code=0, mark=0, output="Compile success."),
                       Attempt(sm_id="Submission_02", tc_id=1, code=2, mark=0, output="10\n\nRuntime error.\nException in thread \"main\" java.lang.IndexOutOfBoundsException\n\tat IdSum.main(IdSum.java:58)"),
                       Attempt(sm_id="Submission_02", tc_id=2, code=0, mark=2, output="8\n")
                   ]),
        Submission(id="Submission_03",
                   mark=0,
                   attempts=[
                       Attempt(sm_id="Submission_03", tc_id=0, code=0, mark=0, output="Compile success."),
                       Attempt(sm_id="Submission_03", tc_id=1, code=0, mark=1, output="10\n"),
                       Attempt(sm_id="Submission_03", tc_id=2, code=3, mark=0, output="8\n\nTimeout expired.")
                   ]),
        Submission(id="Submission_04",
                   mark=0,
                   attempts=[
                       Attempt(sm_id="Submission_04", tc_id=0, code=0, mark=0, output="Compile success."),
                       Attempt(sm_id="Submission_04", tc_id=1, code=4, mark=0, output="20\n"),
                       Attempt(sm_id="Submission_04", tc_id=2, code=4, mark=0, output="16\n")
                   ]),
    ]

    tests = [
        TestCase(id=0, name="Compilation", mark=0),
        TestCase(id=1, name="Test 1", mark=1),
        TestCase(id=2, name="Test 2", mark=2),
    ]

    feedbacks = [
        "Test cases not run due to failure of compilation.",
        "This is feedback 1",
        "This is feedback 2",
        "This is combinatorial feedback 1, 2"
    ]

    feedback_selection = [
        frozenset({0}),
        frozenset({1}),
        frozenset({2}),
        frozenset({1, 2})
    ]

    fr = FeedbackReport(
        name="Sample",
        full_mark=3,
        template_file="templates/feedback.html",
        css_file="static/feedback.css",
        submission_dir=os.path.join(os.getcwd(), "../tests/Module/marking-feedback/submission"),
        submissions=submissions,
        tests=tests,
        feedbacks=feedbacks,
        feedback_selection=feedback_selection
    )
    fr.run()


if __name__ == '__main__':
    main()
