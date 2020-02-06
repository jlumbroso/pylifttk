import re as _re


def parse_category_type(s):
    s = s.lower().strip()
    keywords = ["correctness", "memory", "timing"]
    for keyword in keywords:
        if keyword in s:
            return keyword


def parse_runscript_output(lines):
    """
    Testing correctness of Ordered
    *-----------------------------------------------------------
    Running 10 total tests.

    Test 0a: check formatting of inputs from assignment specification
      % java Ordered 10 17 49
      true

      % java Ordered 49 17 10
      true

      % java Ordered 10 49 17
      false

    ==> passed
    """

    current_category_type = None
    current_category_section = None
    current_test = None
    current_caption = None
    current_linestart = None
    current_log = None
    current_logging = False

    tests = []

    for linenumber, line in enumerate(lines, start=1):

        # detect new category
        m = _re.match(r"(Testing correctness of |Analyzing memory of |Timing )(.*)", line)
        if m is not None:
            # "Testing correctness of Ordered"
            current_category_type = parse_category_type(m.group(1))
            current_category_section = m.group(2)
            current_caption = None
            current_log = None
            current_logging = False
            continue

        # detect new test
        m = _re.match(r"Test (([0-9])*([^:]*)): (.*)", line)
        if m is not None:
            # "Test 0a: check formatting of inputs from assignment specification"
            # 1 -> 0a; 2 -> 0; 3 -> a; 4 -> check formatting of ...
            current_test = m.group(1)
            current_test_split = (m.group(2), m.group(3))
            current_caption = m.group(4)

            current_logging = True
            current_linestart = linenumber
            current_log = []
            continue

        # if not scanning for a test, then ignore lines
        if current_test is None:
            continue

        # detect the end of a test
        m = _re.match(r"^==> (passed|FAILED)$", line)
        if m is not None:
            test_outcome = (m.group(1) == "passed")
            tests.append({
                "category": current_category_type,
                "section": current_category_section,
                "reference": current_test,
                "caption": current_caption,
                "passed": test_outcome,
                "lines": {
                    "start": current_linestart,
                    "end": linenumber,
                },
                "log": current_log,
            })
            current_logging = False
            current_test = None
            continue

        m = _re.match(r"^==> ((\d+)/(\d+)) tests* passed$", line)
        if m is not None:
            test_count_passed = int(m.group(2))
            test_count_total = int(m.group(3))

            # NOTE: larger than eq to catch the edge case of bonus test cases passed
            test_outcome = (test_count_passed >= test_count_total)

            if test_outcome:
                current_log.append(line)

            tests.append({
                "category": current_category_type,
                "section": current_category_section,
                "reference": current_test,
                "caption": current_caption,
                "passed": test_outcome,
                "lines": {
                    "start": current_linestart,
                    "end": linenumber,
                },
                "log": current_log,
            })
            current_logging = False
            current_test = None
            continue

        if not current_logging:
            continue

        # skip whitelines at beginning of log
        if current_logging and len(current_log) == 0 and _re.match(r"^\s+$", line) is not None:
            continue

        # logging new line
        current_log.append(line)

    return tests
