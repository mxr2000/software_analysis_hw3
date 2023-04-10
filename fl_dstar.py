import typing
import sys
import os

Options = typing.Dict[str, str]


class LineInfo():
    lineNo: int
    failedCnt: int
    passedCnt: int
    stmt: str

    def __init__(self, lineNo: int, stmt: str, failedCnt: int, passedCnt: int) -> None:
        self.lineNo = lineNo
        self.stmt = stmt
        self.failedCnt = failedCnt
        self.passedCnt = passedCnt

    def __compute_suspiciousness(self, total: int) -> float:
        return self.failedCnt * self.failedCnt / (self.passedCnt + total - self.failedCnt)

    def format(self, total: int) -> str:
        suspiciousness = self.__compute_suspiciousness(total)
        return "{lineNo: ^10}|{stmt: ^80}|{failedCnt: ^15}|{passedCnt: ^15}|{total: ^15}|{suspiciousness:^15.2f}".format(
            lineNo=self.lineNo,
            stmt=self.stmt[0:80],
            failedCnt=self.failedCnt,
            passedCnt=self.passedCnt,
            total=total,
            suspiciousness=suspiciousness
        )


class Context():
    total: int
    lineInfos: typing.List[LineInfo]

    def __init__(self, lineInfos: typing.List[LineInfo], total: int) -> None:
        self.total = total
        self.lineInfos = lineInfos

    def header(self) -> str:
        return "{:^10}|{:^80}|{:^15}|{:^15}|{:^15}|{:^15}".format(
            "Line #", "Statement", "#failedTests(s)", "#passedTests(s)", "totla_failed", "Suspiciousness")

    def output(self):
        header = self.header()
        print(header)
        print("-" * len(header))
        for line in self.lineInfos:
            print(line.format(self.total))


def add(a: int, b: int) -> int:
    return a + b


def print_options(options: Options):
    for pair in options.items():
        print(pair[0])
        print(pair[1])


def parse_command_line() -> typing.Tuple[str, str]:
    if len(sys.argv) != 5:
        raise Exception("Not enough arguments")
    options = {"--passing_dir": "", "--failing_dir": ""}
    if sys.argv[1] not in options.keys() or sys.argv[3] not in options.keys():
        raise Exception("Arguments error")
    options[sys.argv[1]] = sys.argv[2]
    options[sys.argv[3]] = sys.argv[4]
    return options["--passing_dir"], options["--failing_dir"]


def parse_gcov_file(filename: set) -> typing.Dict[int, typing.Tuple[bool, str]]:
    result: typing.Dict[int, typing.Optional[int]] = {}
    with open(filename) as file:
        for line in file:
            parts = [s.strip() for s in line.split(":")]
            if len(parts) < 2 or parts[0] == "-" or parts[1] == "0":
                continue
            lineNo = int(parts[1])
            result[lineNo] = (parts[0] != "#####", parts[2])
    return result


def process_gcov_data(passing_dir: str, failed_dir: str) -> Context:
    result: typing.Dict[int, typing.Tuple[int, int]] = {}
    total_failed = len(os.listdir(passing_dir))
    print(len(os.listdir(failed_dir)))
    for filename in os.listdir(passing_dir):
        executed = parse_gcov_file(os.path.join(passing_dir, filename))
        for (lineNo, (is_executed, stmt)) in executed.items():
            if lineNo not in result:
                result[lineNo] = (0, 0, stmt)
            if is_executed:
                result[lineNo] = (result[lineNo][0] + 1, result[lineNo][1], stmt)
    for filename in os.listdir(failed_dir):
        executed = parse_gcov_file(os.path.join(failed_dir, filename))
        for (lineNo, (is_executed, stmt)) in executed.items():
            if lineNo not in result:
                result[lineNo] = (0, 0, stmt)
            if is_executed:
                result[lineNo] = (result[lineNo][0], result[lineNo][1] + 1, stmt)
    lines: typing.List[LineInfo] = []
    for (lineNo, (passed, failed, stmt)) in result.items():
        lines.append(LineInfo(lineNo, stmt, failed, passed))
    return Context(lines, total_failed)


if __name__ == "__main__":
    passing_dir, failing_dir = parse_command_line()
    ctx = process_gcov_data(passing_dir, failing_dir)
    ctx.output()
