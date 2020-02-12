
import json as _json

import codepost as _codepost
import yaml as _yaml

import pylifttk.runscript.parser


# FIXME: clean-up this mess!


def reset_tests(a):
    if isinstance(a, int):
        a = _codepost.assignment.retrieve(id=a)
    if isinstance(a, _codepost.models.abstract.api_resource.AbstractAPIResource):
        a.refresh()

    deleted_testcategories = []
    deleted_testcases = []

    for cat in a.testCategories:
        cat_id = cat.id
        for test in cat.testCases:
            test_id = test.id
            try:
                if test.delete():
                    deleted_testcases.append(test_id)
            except:
                continue

        try:
            if cat.delete():
                deleted_testcategories.append(cat_id)
        except:
            continue

    return deleted_testcategories, deleted_testcases


def add_tests(a, tests):
    # {'category': 'correctness',
    #  'section': 'LFSR',
    #  'reference': '1',
    #  'caption': 'check length() with no intervening calls to step() or generate()',
    #  'passed': True,
    #  'lines': {'start': 116, 'end': 121},
    #  'log': ['  * seed = "01101000010", tap = 9',
    #   '  * seed = "01101000010", tap = 4',
    #   '  * seed = "01101000010100010000", tap = 17',
    #   '  * seed = "011101110101101011110100101010010111011110111011101100001011", tap = 59']}

    a_id = a.id

    category_name_format = "{section}: {category}"
    test_description_format = "Test {reference}"

    category_name_format = "{category}"
    test_description_format = "{section}: Test {reference}"

    category_name_format = "{section}"
    test_description_format = "Test {reference}"

    cat_names = {
        category_name_format.format(
            category=test["category"].capitalize(),
            section=test["section"])
        for test in tests
    }

    cat_lookup = dict()
    test_mapping = dict()

    # Create the test categories
    for cat_name in cat_names:
        cat_obj = _codepost.test_category.create(
            assignment=a_id,
            name=cat_name)
        cat_lookup[cat_name] = cat_obj.id

    # Create the test cases
    for test in tests:
        cat_name = category_name_format.format(
            category=test["category"].capitalize(),
            section=test["section"])
        cat_id = cat_lookup.get(cat_name)

        test_description = test_description_format.format(**test)[0:47]

        test_obj = _codepost.test_case.create(
            testCategory=cat_id,
            type="external",
            description=test_description,
            explanation=test["caption"].capitalize())
        test_obj.save()

        # save the mapping
        key = None
        if "shortname" in test:
            key = test["shortname"]
        else:
            key = "{category}-{section}-{reference}".format(**test)

        test_mapping[key] = test_obj.id

    return test_mapping


def trigger_tests(autograder_output=None, autograder_output_filename=None, mapping_filename=None, mapping_data=None, prefix=None):

    if autograder_output is None and autograder_output_filename is not None:
        autograder_output = open(autograder_output_filename).read()

    if mapping_data is None and mapping_filename is not None:
        mapping_data = _yaml.load(open(mapping_filename).read(), Loader=_yaml.FullLoader)

    autograder_lines = None
    try:
        autograder_lines = autograder_output.splitlines()
    except:
        return False

    parsed_tests = pylifttk.runscript.parser.parse_runscript_output(autograder_lines)

    def trigger_codePost_submission_test(testCase_id, passed=False, log="", prefix=None):
        if prefix is None:
            prefix = ""
        path = "{}/outputs/{}.json".format(prefix, testCase_id)
        with open(path, "w") as file:
            json_data = _json.dump({
                "id": testCase_id,
                "passed": passed,
                "log": "\n".join(log),
            }, file)

    missing_tests = 0

    for test in parsed_tests:

        # get shortname or recompute it
        key = None
        if "shortname" in test:
            key = test["shortname"]
        else:
            key = "{category}-{section}-{reference}".format(**test)

        # lookup mapping
        if key not in mapping_data:
            missing_tests += 1
            continue

        trigger_codePost_submission_test(
            testCase_id=mapping_data.get(key),
            passed=test.get("passed"),
            log=test.get("log"),
            prefix=prefix
        )

    return missing_tests


