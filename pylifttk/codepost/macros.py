

import codepost as _codepost


def get_course_id(course_name, course_term):
    courses = _codepost.course.list_available()
    for course in courses:
        if course.name == course_name and course.period == course_term:
            return course.id


def invite_many_students(course_id, students, append=True):

    roster = students[:]

    if append:
        existing_students = _codepost.roster.retrieve(id=course_id).students
        for student in existing_students:
            if student not in roster:
                roster.append(student)

    _codepost.roster.update(
        id=1,
        students=roster
    )


def set_course_sections(course_id, section_dict):

    sections_name_to_id = {}
    for section in _codepost.course.retrieve(id=course_id).sections:
        sections_name_to_id[section.name] = section.id

    for section_name, roster in section_dict.items():
        if section_name not in sections_name_to_id:
            continue

        section_id = sections_name_to_id[section_name]

        _codepost.section.update(
            id=section_id,
            students=roster,
        )


def get_course_grades(course_id, only_finalized=True, api_key=None):
    """
    Returns a dictionary mapping every student in the specified course
    to a dictionary, which itself maps assignment names to grades. By
    default, only finalized submission grades are return, but this can
    be changed with the `only_finalized` boolean parameter.
    """
    # Course is an object with these properties:
    # {u'assignments': [92, 93, 94, 95, 96, 97, 98, 99, 100, 101, 102, 103],
    #  u'emailNewUsers': True,
    #  u'id': 11,
    #  u'name': u'COS126',
    #  u'organization': 1,
    #  u'period': u'S2019',
    #  u'sections': [64, 65, 66, 67, 68, 69, 70, 71, 89, 90, 91, 92, 93, 94, 95],
    #  u'sendReleasedSubmissionsToBack': True,
    #  u'showStudentsStatistics': True,
    #  u'timezone': u'US/Eastern'}

    course = _codepost.course.retrieve(id=course_id)

    # Mapping:  student -> (assignment -> grade)
    # This data structure is optimizing storing for output
    grades = {}

    for assignment in course.assignments:

        # Assignment object:
        # {u'course': 11,
        #  u'id': 92,
        #  u'isReleased': True,
        #  u'mean': 19.49,
        #  u'median': 20.0,
        #  u'name': u'Loops',
        #  u'points': 20,
        #  u'rubricCategories': [519, 640, 641, 642, 643, 644, 645],
        #  u'sortKey': 1}

        assignment_name = assignment.name

        # Submission object:
        # {u'assignment': 92,
        #  u'dateEdited': u'2019-02-20T22:55:55.335293-05:00',
        #  u'files': [40514, 40515, 40516, 40517, 40518, 40519, 40520],
        #  u'grade': 20.0,
        #  u'grader': u'jgrader@princeton.edu',
        #  u'id': 9351,
        #  u'isFinalized': True,
        #  u'queueOrderKey': 1,
        #  u'students': [u'jstudent@princeton.edu']}
        submissions = assignment.list_submissions()  # codepost.assignment.list_submissions(id=aid)

        for submission in submissions:

            # Ungraded
            if submission.grade is None:
                continue

            # Unclaimed
            if submission.grader is None:
                continue

            # Unfinalized
            if not submission.isFinalized:
                if only_finalized:
                    continue

            # Insert the grade in our data structure
            for student in submission.students:
                student_grades = grades.get(student, dict())
                student_grades[assignment_name] = submission.grade
                grades[student] = student_grades

    # At this point, grades contains all the grades of the assignments
    # of the course

    return grades


def get_ungraded_students(assignment_id, course_id=None, students=None):
    """
    Returns a dictionary containing the students whose submissions are either
    unclaimed, unfinalized or not uploaded.

    :param assignment_id:
    :param course_id:
    :param students:
    :return:
    """
    if students is None:
        students = _codepost.roster.retrieve(id=course_id).students
    submissions = _codepost.assignment.retrieve(id=assignment_id).list_submissions()

    count_total = 0
    count_finalized = 0
    count_not_finalized = 0
    students_missing = {student: True for student in students}
    students_not_claimed = set()
    students_not_finalized = set()

    for submission in submissions:
        count_total += 1

        for s in submission.students:
            students_missing[s] = False

        if submission.isFinalized:
            count_finalized += 1
        else:
            count_not_finalized += 1
            if submission.grader is None:
                students_not_claimed = students_not_claimed.union(
                    set(submission.students))
            else:
                students_not_finalized = students_not_finalized.union(
                    set(submission.students))

    students_not_claimed = list(students_not_claimed.intersection(set(students)))
    students_not_finalized = list(students_not_finalized.intersection(set(students)))
    students_missing = [
        student
        for student, is_missing in students_missing.items()
        if is_missing
    ]

    # FIXME: Not hard-code these keywords
    return {
        "not-claimed": students_not_claimed,
        "not-finalized": students_not_finalized,
        "not-uploaded": students_missing,
    }