import os
import subprocess
from dataclasses import dataclass
from pathlib import Path


@dataclass
class MarkingConfig:
    name: str
    compile: str
    execute: str
    timeout: int
    solution_dir: Path
    submission_dir: Path


@dataclass
class TestCase:
    id: int
    name: str
    input: str = None
    solution: str = None


@dataclass
class Attempt:
    sm_ID: str
    tc_ID: int
    code: int   # 0: PASS, 1: COMPILE_ERROR, 2: RUNTIME_ERROR, 3: TIMEOUT, 4: INCORRECT_OUTPUT
    output: str


class AutoMarking:
    def __init__(
            self,
            compile_command: str,
            execute_command: str,
            timeout: int,
            tests: [TestCase],
            solution_dir: str,
            submission_dir: str,
    ):
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
        try:
            if int(timeout) <= 0:
                return "Timeout should be greater than 0."
        except ValueError:
            return "Timeout should be an integer."

        solution_dir = Path(solution_dir)
        submission_dir = Path(submission_dir)
        if not solution_dir.is_dir():
            return f"No such directory {solution_dir}."
        if not submission_dir.is_dir():
            return f"No such directory {submission_dir}."

        try:
            subprocess.run(compile_command, shell=True, cwd=solution_dir)
        except subprocess.CalledProcessError:
            return "Failed to compile solution."

        submissions = [d for d in os.listdir(submission_dir) if os.path.isdir(submission_dir / d)]
        if not submissions or len(submissions) == 0:
            return "No submission found."

        return None

    def get_solutions(self) -> str | None:
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

    def compile_submission(self, submission: str) -> Attempt:
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
            sm_ID=submission,
            tc_ID=0,
            code=0 if error is None else 1,
            output="Compile success." if error is None else "Compile failed.\n" + error
        )

    def execute_submission(self, submission: str, test: TestCase) -> Attempt:
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
            sm_ID=submission,
            tc_ID=test.id,
            code=code,
            output=output
        )

    def run(self) -> [Attempt]:
        attempts = []
        for submission in self.submissions:
            print(f"Marking student submission: [{submission}].")
            compile_attempt = self.compile_submission(submission)
            attempts.append(compile_attempt)
            if compile_attempt.code == 0:
                for test in self.tests:
                    attempts.append(self.execute_submission(submission, test))

        return attempts


# Test the marking process is working
def main():
    with open(Path(os.getcwd()) / "../tests/marking/test_case/1.in") as f1:
        test1 = TestCase(
            id=1,
            name="test1",
            input=f1.read()
        )
    with open(Path(os.getcwd()) / "../tests/marking/test_case/2.in") as f2:
        test2 = TestCase(
            id=2,
            name="test2",
            input=f2.read()
        )
    marking = AutoMarking(
        compile_command="javac -encoding UTF-8 -sourcepath . IdSum.java",
        execute_command="java -Dfile.encoding=UTF-8 -XX:+UseSerialGC -Xss64m -Xms1920m -Xmx1920m IdSum",
        timeout=1,
        tests=[test1, test2],
        solution_dir=os.path.join(os.getcwd(), "../tests/marking/solution"),
        submission_dir=os.path.join(os.getcwd(), "../tests/marking/submission")
    )
    marking.get_solutions()
    attempts = marking.run()

    print("\nDetailed attempts are listed as follows:")
    for attempt in attempts:
        print(f"sm_ID: {attempt.sm_ID}, tc_ID: {attempt.tc_ID}, code: {attempt.code}, output: {attempt.output}")


if __name__ == '__main__':
    main()
