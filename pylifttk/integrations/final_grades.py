


def _merge_grades(new_grades, grades=None, maxima=None, truncate_emails=True):
    grades = grades or dict()
    maxima = maxima or dict()

    if new_grades is None or not new_grades:
        new_grades = []

    for student, record in new_grades.items():
        # 'joestudent@princeton.edu': {'Sierpinski': 3.9,
        #   'Hello': 3.9,
        #   'Loops': 3.6,
        #   'Hamming': 4.0,
        #   'NBody': 3.6,
        #   'LFSR': 4.9,
        #   'Programming Exam 1': 7.0}

        # FIXME: Better way of doing username conversion
        netid = student
        if truncate_emails:
            netid = student.split("@")[0]

        for assignment, grade in record.items():
            # Add grade to student
            grades[netid] = grades.get(netid, dict())
            grades[netid][assignment] = grade

            # Compute maximum
            maxima[assignment] = max(grade, maxima.get(assignment, 0.0))

    return grades, maxima


def _import_codepost_grades(course_name, course_term):
    try:
        import pylifttk.codepost
        import pylifttk.codepost.macros

        codepost_course_id = pylifttk.codepost.macros.get_course_id(
            course_name=course_name,
            course_term=course_term)

        codepost_grades = pylifttk.codepost.macros.get_course_grades(
            course_id=codepost_course_id)

        return codepost_grades

    except ModuleNotFoundError:
        # This is `codepost` module likely improperly installed
        raise

    except Exception as exc:
        return None


def _import_gradescope_grades(course_name, course_term):
    try:
        import pylifttk.gradescope
        import pylifttk.gradescope.macros

        gradescope_course_id = pylifttk.gradescope.macros.get_course_id(
            course_name=course_name,
            course_term=course_term)

        gradescope_grades = pylifttk.gradescope.macros.get_course_grades(
            course_id=gradescope_course_id)

        return gradescope_grades

    except ModuleNotFoundError:
        # This is `codepost` module likely improperly installed
        raise

    except Exception as exc:
        return None


def get_all_course_grades(course_name, course_term):

    grades = {}  # student grades
    maxima = {}  # maximal grade for a given assignment

    # codePost assignments

    codepost_grades = _import_codepost_grades(
        course_name=course_name,
        course_term=course_term)

    grades, maxima = _merge_grades(codepost_grades, grades=grades, maxima=maxima)

    # Gradescope assignments

    gradescope_grades = _import_gradescope_grades(
        course_name=course_name,
        course_term=course_term)

    grades, maxima = _merge_grades(gradescope_grades, grades=grades, maxima=maxima)

    return grades, maxima