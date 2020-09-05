import datetime

import yaml

import pylifttk
import pylifttk.codepost
import pylifttk.integrations.grading_tests
import pylifttk.runscript.parser

# CURRENT_COURSE_NAME = "COS126"
# CURRENT_COURSE_TERM = "F2020"

# PREVIOUS_COURSE_NAME = "COS126"
# PREVIOUS_COURSE_TERM = "S2020"

TESTS_FILE = "TESTS.txt"

TEST_CAPTION_FORMATTING = {
    "Hello": ("{section}", "Test {reference}"),
    "Loops": ("{section}", "Test {reference}"),
    "NBody": ("{category.capitalized}", "Test {reference}"),
    "Sierpinski": ("{section}", "Test {reference} ({category})"),
    "Hamming": ("{section.capitalized}", "Test {reference}"),
    "LFSR": ("{section.capitalized}: {category.capitalized}", "Test {reference}"),
    "Guitar": ("{section.capitalized}", "{category.capitalized}: Test {reference}"),
    "Markov": ("{section.capitalized}", "{category.capitalized}: Test {reference}"),
    "TSPP": ("{category.capitalized}", "Test {reference}"),
}

ASSIGNMENTS = list(TEST_CAPTION_FORMATTING.keys())

_cp = pylifttk.codepost._codepost


class strWithCapitalization(str):
    @property
    def capitalized(self):
        return self.capitalize()


def create_environment(assignment_id):
    response = _cp.api_requestor.STATIC_REQUESTOR._request(
        method="POST",
        endpoint="/autograder/environments/",
        data={
            "id": -1,
            "language": "python-3.7",
            "dockerRunInstructions": ["pip install --force --upgrade pylifttk"],
            "dockerfile": "",
            "assignment": assignment_id,
            "dumpMode": False,
            "testParsing": True,
            "compileText": "",
            "buildType": "default",
            "allowNetworkAccess": False,
            "maxStudentTestRuns": None,
            "exposeDumpLogs": False,
            "maxExposedFailedTests": None,
        }
    )
    if response.status_code < 300:
        return response.json.get("id")


def retrieve_environment(environment_id):
    try:
        int(environment_id)
    except ValueError:
        raise
    response = _cp.api_requestor.STATIC_REQUESTOR._request(
        method="GET",
        endpoint="/autograder/environments/{}/".format(environment_id),
    )
    if response.status_code < 300:
        return response.json


def build_environment(environment_id):

    environment_obj = retrieve_environment(environment_id=environment_id)
    if environment_obj is None:
        return

    response = _cp.api_requestor.STATIC_REQUESTOR._request(
        method="PATCH",
        endpoint="/autograder/environments/{}/build/".format(environment_id),
        data=environment_obj
    )
    return response.status_code < 300


def delete_environment(environment_id):
    try:
        int(environment_id)
    except ValueError:
        raise
    response = _cp.api_requestor.STATIC_REQUESTOR._request(
        method="DELETE",
        endpoint="/autograder/environments/{}/".format(environment_id),
    )
    return response.status_code < 300


def create_helper_file(environment_id, filename, contents):
    response = _cp.api_requestor.STATIC_REQUESTOR._request(
        method="POST",
        endpoint="/autograder/helperFiles/",
        data={
            "id":-1,
            "name": filename,
            "environment": environment_id,
            "code": contents,
            "path": None,
        }
    )
    return response.status_code < 300


def create_autograder_file(environment_id, file_name, contents, file_type="helper"):
    response = _cp.api_requestor.STATIC_REQUESTOR._request(
        method="POST",
        endpoint="/autograder/{filetype}Files/".format(filetype=file_type),
        data={
            "id":-1,
            "name": file_name,
            "environment": environment_id,
            "code": contents,
            "path": None,
        }
    )
    if response.status_code < 300:
        return response.json.get("id")


def retrieve_autograder_file(file_id, file_type="helper"):
    response = _cp.api_requestor.STATIC_REQUESTOR._request(
        method="GET",
        endpoint="/autograder/{file_type}Files/{file_id}".format(
            file_type=file_type,
            file_id=file_id,
        ),
    )
    if response.status_code < 300:
        return response.json


def transfer_tests_from_prev_to_current_course(
        assignment_name,
        current_course_name, current_course_term,
        prev_course_name, prev_course_term
):

    CURRENT_COURSE_NAME = current_course_name
    CURRENT_COURSE_TERM = current_course_term

    PREVIOUS_COURSE_NAME = prev_course_name
    PREVIOUS_COURSE_TERM = prev_course_term

    prev_assignment = _cp.course.list_available(
        name=PREVIOUS_COURSE_NAME, period=PREVIOUS_COURSE_TERM)[0].assignments.by_name(assignment_name)

    current_assignment = _cp.course.list_available(
        name=CURRENT_COURSE_NAME, period=CURRENT_COURSE_TERM)[0].assignments.by_name(assignment_name)

    # Compute the tests

    prev_submissions = sorted(prev_assignment.list_submissions(),
                              key=lambda record: record.grade,
                              reverse=True)

    best_prev_submission = prev_submissions[0]

    tests_file_contents = [
        file for file in best_prev_submission.files if file.name == TESTS_FILE
    ][0].code

    tests = pylifttk.runscript.parser.parse_runscript_output(tests_file_contents.split("\n"))

    # Add the capitalization hack

    tests = [
        {
            field: strWithCapitalization(value)
            for (field, value) in test.items()
        }
        for test in tests
    ]

    # Reset the environment

    if current_assignment.environment is not None:
        try:
            delete_environment(environment_id=current_assignment.environment)
        except:
            pass

    current_environment_id = create_environment(assignment_id=current_assignment.id)

    # Reset the tests + reconfigure them

    category_name_format, test_description_format = TEST_CAPTION_FORMATTING[assignment_name]

    pylifttk.integrations.grading_tests.reset_tests(current_assignment)

    current_mapping = pylifttk.integrations.grading_tests.add_tests(
        current_assignment,
        tests,
        category_name_format=category_name_format,
        test_description_format=test_description_format)

    current_mapping_yaml = yaml.dump({
        str(key): value
        for (key,value) in current_mapping.items()
    })

    ts = datetime.datetime.now().isoformat().split("T")[0]

    current_mapping_filename = "{course}_{term}_{assignment}_cP-{ts}.yaml".format(
        course=CURRENT_COURSE_NAME, term=CURRENT_COURSE_TERM, assignment=assignment_name, ts=ts)

    # Upload the right files

    file_id_yaml = create_autograder_file(
        file_type="helper",
        environment_id=current_environment_id,
        file_name=current_mapping_filename,
        contents=current_mapping_yaml,
    )

    file_id_parser_py = create_autograder_file(
        file_type="helper",
        environment_id=current_environment_id,
        file_name="parser.py",
        contents="\n".join([
            "# do parsing here",
            "",
            "import pylifttk",
            "",
            "print('STARTING autograder parsing...')",
            "print('RUNNING version {} of pylifttk'.format(pylifttk.__version__))",
            "",
            "import pylifttk.integrations.grading_tests",
            "",
            "pylifttk.integrations.grading_tests.trigger_tests(",
            "    autograder_output_filename='{tests_filename}',".format(
                tests_filename=TESTS_FILE),
            "    mapping_filename='{current_mapping_filename}')".format(
                current_mapping_filename=current_mapping_filename),
            "",
        ]),
    )

    file_id_tests_file = create_autograder_file(
        file_type="solution",
        environment_id=current_environment_id,
        file_name=TESTS_FILE,
        contents=tests_file_contents,
    )

    file_id_parser_sh = create_autograder_file(
        file_type="source",
        environment_id=current_environment_id,
        file_name="parser.sh",
        contents="python parser.py\n\n",
    )

    # Retrieve previous mapping

    prev_mapping = None

    if prev_assignment.environment is not None:
        prev_environment = retrieve_environment(environment_id=prev_assignment.environment)

        prev_helper_files = prev_environment.get("helperFiles", list())

        for prev_helper_file_id in prev_helper_files:
            prev_helper_file = retrieve_autograder_file(
                file_type="helper",
                file_id=prev_helper_file_id
            )
            if ".yaml" in prev_helper_file.get("name"):
                break
            prev_helper_file = None

        if prev_helper_file is not None:
            prev_mapping = {
                key: int(value)
                for (key, value) in
                yaml.load(prev_helper_file.get("code"), Loader=yaml.BaseLoader).items()
            }

    # If we have the two mappings, we can transfer tests

    for (test_internal_name, prev_test_case_id) in prev_mapping.items():

        if test_internal_name not in current_mapping:
            continue

        current_test_case_id = current_mapping[test_internal_name]

        prev_test_case_obj = _cp.test_case.retrieve(id=prev_test_case_id)
        current_test_case_obj = _cp.test_case.retrieve(id=current_test_case_id)

        if prev_test_case_obj.explanation is not None and (
                current_test_case_obj.explanation is None or
                len(current_test_case_obj.explanation) < len(prev_test_case_obj.explanation)
        ):
            _cp.test_case.update(
                id=current_test_case_id,
                explanation=prev_test_case_obj.explanation
            )

    # Build the environment
    build_environment(environment_id=current_environment_id)

