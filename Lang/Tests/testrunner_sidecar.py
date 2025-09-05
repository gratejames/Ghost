# import os
from pathlib import Path
import subprocess

results = {}
longestTestName = 0
longestCategoryName = 0


class Test:
    _type = "No Test Detected"
    _pass = "None"

    def __init__(self, name: str):
        self.name = name

    def __repr__(self):
        return f"t:{self.name}"


def doTest(path: Path):
    global results, longestTestName, longestCategoryName
    if path == "testrunner.py":
        return None
    # print(path)
    if path.suffix != ".g":
        return None
    category = str(path.parent)
    if not any(match in category for match in desired_tests):
        return None
    longestCategoryName = max(longestCategoryName, len(category))
    testName = path.name.removesuffix(".g")
    longestTestName = max(longestTestName, len(testName))
    test = Test(testName)
    assemblerOutputTest = list(path.parent.glob(testName + ".ghasm.expected"))
    assemblerErrorTest = list(path.parent.glob(testName + ".assemblererror.expected"))
    assemblerPassTest = list(path.parent.glob(testName + ".assemblerpass.expected"))

    pre_run_out_files = list(path.parent.glob(testName + ".ghasm"))
    if len(pre_run_out_files) != 0:
        pre_run_out_files[0].unlink()

    if len(assemblerOutputTest) != 0:
        test._type = "Assembly Validation"
        with open(assemblerOutputTest[0], "r") as f:
            expected_asm_output = f.read()

        actual_term_output = subprocess.run(
            ["/home/flicker/Desktop/Ghost/Lang/main.py", path],
            stdout=subprocess.PIPE,
        ).stdout.decode("utf-8")
        asm_output_files = list(path.parent.glob(testName + ".ghasm"))
        if len(asm_output_files) == 0:
            test._pass = "Fail: No Output"
        else:
            with open(asm_output_files[0], "r") as f:
                actual_asm_output = f.read()
            if actual_asm_output == expected_asm_output:
                test._pass = "Pass"
            else:
                test._pass = "Fail: Mismatch"
            asm_output_files[0].unlink()

    if len(assemblerPassTest) != 0:
        test._type = "Confirm Assembler Pass"
        with open(assemblerPassTest[0], "r") as f:
            expected_term_output = f.read()

        actual_term_output = subprocess.run(
            ["/home/flicker/Desktop/Ghost/Lang/main.py", path],
            stdout=subprocess.PIPE,
        ).stdout.decode("utf-8")
        asm_output_files = list(path.parent.glob(testName + ".ghasm"))
        if len(asm_output_files) == 0:
            test._pass = "Fail: No Output"
        else:
            if (
                len(expected_term_output) == 0
                or expected_term_output == actual_term_output
            ):
                test._pass = "Pass"
            else:
                test._pass = "Fail: Mismatch"
            asm_output_files[0].unlink()

    if len(assemblerErrorTest) != 0:
        test._type = "Confirm Assembler Error"
        with open(assemblerErrorTest[0], "r") as f:
            expected_term_output = f.read()

        actual_term_output = subprocess.run(
            ["/home/flicker/Desktop/Ghost/Lang/main.py", path],
            stdout=subprocess.PIPE,
        ).stdout.decode("utf-8")
        asm_output_files = list(path.parent.glob(testName + ".ghasm"))
        if len(asm_output_files) == 0:
            if (
                len(expected_term_output) == 0
                or expected_term_output == actual_term_output
            ):
                test._pass = "Pass"
            else:
                test._pass = "Fail: Mismatch"
        else:
            test._pass = "Fail: Output Generated"
            asm_output_files[0].unlink()

    if category not in results:
        results[category] = []
    results[category].append(test)


def findTests(list_files):
    for path in list_files:
        if path.is_dir():
            findTests(path.iterdir())
        else:
            doTest(path)


desired_tests = [
    # "Mine",
    # "Book/chapter_1/",
    # "Book/chapter_2/",
    # "Book/chapter_3/",
    # "Book/chapter_4/",
    # "Book/chapter_5/",  # HAS FAILS: Incrementing parenthesized expressions, and `int a = a = 5;` (80/82)
    # "Book/chapter_6/",  # HAS FAILS: Goto not implemented (Also why is declaration_as_statement invalid?) (56/68)
    # "Book/chapter_7/",  # HAS FAILS: Still no goto (23/27)
    # "Book/chapter_8/",  # HAS FAILS: many, switch not implemented, but also still don't know why decl_as_loop_body is invalid (66/97)
    # "Book/chapter_9/",  # HAS FAILS 39/78
]

findTests(Path(".").iterdir())
# print(results)

if False:  # Color Switch
    failColor = "\033[91m"
    passColor = "\033[92m"
    clearColor = "\033[00m"
else:
    failColor = ""
    passColor = ""
    clearColor = ""

allTestCount = 0
allPassCount = 0

for category, tests in results.items():
    testsOutput = ""
    passes = 0
    testNumber = 0
    for t in tests:
        padding = " " * (longestTestName - len(t.name))
        passText = (
            (passColor if t._pass == "Pass" else failColor) + t._pass + clearColor
        )
        testsOutput += f"    {t.name}{padding}    {passText} ({t._type})" + "\n"
        if t._pass == "Pass":
            passes += 1
        if t._pass != "None":
            testNumber += 1
    padding = " " * (longestCategoryName - len(category))
    print(f"{category}:{padding}  ({passes}/{len(tests)})")
    print(testsOutput)
    # allTestCount += testNumber
    allTestCount += len(tests)
    allPassCount += passes

print(
    f"Total: {allPassCount} of {allTestCount} tests passed, {(allPassCount/allTestCount*100):.2f}%"
)
