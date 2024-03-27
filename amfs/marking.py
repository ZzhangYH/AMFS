import os
import subprocess
from dataclasses import dataclass
from pathlib import Path


@dataclass
class TestCase:
    """
    Test case configurations.

    Attributes:
        id: ID of this test case
        name: Name of this test case
        mark: Full mark of this test case
        input: stdin for this test case
        solution: Sample stdout for this test case
    """
    id: int
    name: str
    mark: float
    input: str = None
    solution: str = None


@dataclass
class Attempt:
    """
    Record of an attempt running a submission against a test case.

    Attributes:
        sm_id: Submission ID in this attempt
        tc_id: Test case ID in this attempt
        code: Indicates the result for this attempt:
              0 (PASS), 1 (COMPILE_ERROR), 2 (RUN_ERROR), 3 (TIME_LIMIT), 4 (WRONG_ANSWER)
        mark: Actual mark in this attempt
        output: stdout captured in this attempt, with stderr if applicable
    """
    sm_id: str
    tc_id: int
    code: int   # 0: PASS, 1: COMPILE_ERROR, 2: RUN_ERROR, 3: TIME_LIMIT, 4: WRONG_ANSWER
    mark: float
    output: str


class AutoMarking:
    """
    Automated marking module.

    Attributes:
        compile_command: Compilation command for marking
        execute_command: Execution command for marking
        timeout: Timeout limit
        tests: List of all test cases
        solution_dir: Directory containing the sample solution
        submission_dir: Directory containing subdirectories of student submissions
    """
    def __init__(
            self,
            compile_command: str,
            execute_command: str,
            timeout: int,
            tests: [TestCase],
            solution_dir: str,
            submission_dir: str,
    ):
        """
        Initiates a new automated marking job.

        Args:
            compile_command: Compilation command for marking
            execute_command: Execution command for marking
            timeout: Timeout limit
            tests: List of all test cases
            solution_dir: Directory containing the sample solution
            submission_dir: Directory containing subdirectories of student submissions
        """
        self.compile_command = compile_command
        self.execute_command = execute_command
        self.timeout = timeout
        self.tests = tests
        self.solution_dir = Path(solution_dir)
        self.submission_dir = Path(submission_dir)
        self.submissions = [d for d in os.listdir(self.submission_dir)
                            if os.path.isdir(self.submission_dir / d)]

    @staticmethod
    def check_configs(
            compile_command: str,
            timeout: str,
            solution_dir: str,
            submission_dir: str
    ) -> str | None:
        """
        Checks if the configurations submitted is valid for marking.

        Args:
            compile_command: Compilation command for marking
            timeout: Timeout limit
            solution_dir: Directory containing the sample solution
            submission_dir: Directory containing subdirectories of student submissions

        Returns:
            An error message explaining invalid config, otherwise None
        """
        error: [str] = []

        try:
            if int(timeout) <= 0:
                error.append("Timeout should be greater than 0.")
        except ValueError:
            error.append("Timeout should be an integer.")

        solution_dir = Path(solution_dir)
        submission_dir = Path(submission_dir)
        if not solution_dir.is_dir():
            error.append(f"No such directory {solution_dir}.")
        if not submission_dir.is_dir():
            error.append(f"No such directory {submission_dir}.")

        if solution_dir.is_dir():
            try:
                result = subprocess.run(compile_command,
                                        stdout=subprocess.PIPE,
                                        stderr=subprocess.STDOUT,
                                        shell=True,
                                        cwd=solution_dir)
                if result.stdout:
                    if "error" in result.stdout.decode() or "error" in result.stdout.decode():
                        error.append("Failed to compile solution.")

            except subprocess.CalledProcessError:
                error.append("Failed to compile solution.")

        if submission_dir.is_dir():
            submissions = [d for d in os.listdir(submission_dir) if os.path.isdir(submission_dir / d)]
            if not submissions or len(submissions) == 0:
                error.append("No submission found.")

        return error if len(error) > 0 else None

    def _get_solutions(self) -> str | None:
        """
        Generating sample solutions for all test cases.

        Returns:
            An error message, otherwise None
        """
        try:
            subprocess.run(self.compile_command, shell=True, cwd=self.solution_dir)
        except subprocess.CalledProcessError:
            return "Failed to compile solution."

        for test in self.tests:
            try:
                p = subprocess.run(
                    self.execute_command,
                    shell=True,
                    cwd=self.solution_dir,
                    capture_output=True,
                    check=True,
                    input=test.input,
                    text=True
                )
                test.solution = p.stdout
            except subprocess.CalledProcessError:
                return f"Error occurred when generating solution for test case: {test.name}."

        print("Sample solutions generated.")
        return None

    def _compile_submission(self, submission: str) -> Attempt:
        """
        Compiling a specific submission.

        Args:
            submission: Submission ID

        Returns:
            An Attempt object as the result of the compilation
        """
        try:
            subprocess.run(
                self.compile_command,
                shell=True,
                cwd=self.submission_dir / submission,
                capture_output=True,
                check=True,
                text=True
            )
            print("> Compile success.")
            error = None
        except subprocess.CalledProcessError as e:
            print("> Compile failed.")
            error = e.stderr

        return Attempt(
            sm_id=submission,
            tc_id=0,
            code=0 if error is None else 1,
            mark=0,
            output="Compile success." if error is None else "Compile failed.\n" + error
        )

    def _execute_submission(self, submission: str, test: TestCase) -> Attempt:
        """
        Executing a specific submission against a specific test case.

        Args:
            submission: Submission ID
            test: Test case object

        Returns:
            An Attempt object as the result of the execution
        """
        print(f"> Running test case {test.id}.")
        try:
            result = subprocess.run(
                self.execute_command,
                shell=True,
                cwd=self.submission_dir / submission,
                capture_output=True,
                check=True,
                input=test.input,
                text=True,
                timeout=self.timeout
            )
            code = 0 if result.stdout == test.solution else 4
            output = result.stdout
        except subprocess.CalledProcessError as e:
            code = 2
            output = e.output + "\nRuntime error.\n" + e.stderr
        except subprocess.TimeoutExpired as e:
            code = 3
            output = e.output.decode('utf-8') + "\nTimeout expired."

        return Attempt(
            sm_id=submission,
            tc_id=test.id,
            code=code,
            mark=test.mark if code == 0 else 0,
            output=output
        )

    def run(self) -> [Attempt]:
        """
        Runs the automated marking module:
        1. Getting sample solutions;
        2. Running all submissions against compilation and test cases;
        The submission will not be executed if compilation fails.

        Returns:
            A list of attempts while marking
        """
        self._get_solutions()
        attempts = []
        for submission in self.submissions:
            print(f"Marking student submission: [{submission}].")
            compile_attempt = self._compile_submission(submission)
            attempts.append(compile_attempt)
            if compile_attempt.code == 0:
                for test in self.tests:
                    attempts.append(self._execute_submission(submission, test))

        return attempts


# Test the marking process is working
def main():
    with open(Path(os.getcwd()) / "../tests/Module/marking-feedback/test_case/test_case_1.in") as f1:
        test1 = TestCase(
            id=1,
            name="test1",
            mark=1,
            input=f1.read()
        )
    with open(Path(os.getcwd()) / "../tests/Module/marking-feedback/test_case/test_case_2.in") as f2:
        test2 = TestCase(
            id=2,
            name="test2",
            mark=2,
            input=f2.read()
        )
    marking = AutoMarking(
        compile_command="javac -encoding UTF-8 -sourcepath . IdSum.java",
        execute_command="java -Dfile.encoding=UTF-8 -XX:+UseSerialGC -Xss64m -Xms1920m -Xmx1920m IdSum",
        timeout=1,
        tests=[test1, test2],
        solution_dir=os.path.join(os.getcwd(), "../tests/Module/marking-feedback/solution"),
        submission_dir=os.path.join(os.getcwd(), "../tests/Module/marking-feedback/submission")
    )
    attempts = marking.run()

    print("\nDetailed attempts are listed as follows:")
    for attempt in attempts:
        print(f"sm_ID: {attempt.sm_id}, tc_ID: {attempt.tc_id}, code: {attempt.code}, output: {attempt.output}")


if __name__ == '__main__':
    main()
