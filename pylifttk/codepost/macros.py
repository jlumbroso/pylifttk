

import codepost as _codepost


def get_course_id(course_name, course_period):
    courses = _codepost.course.list_available()
    for course in courses:
        if course.name == course_name and course.period == course_period:
            return course.id


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
