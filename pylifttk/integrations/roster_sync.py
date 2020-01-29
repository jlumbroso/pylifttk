

def csstaff_to_ed(src_names, dest_course_name, dest_course_term):
    import pylifttk.csstaff
    import pylifttk.ed

    if type(src_names) is str:
        src_names = list(src_names)

    students = {}
    for src_name in src_names:
        students.update(pylifttk.csstaff.course_enrollment(course_key=src_name, as_dict=True))

    # {'coursename': 'COS126_F2018',
    #  'lecture': 'L01',
    #  'precept': 'P08',
    #  'netid': 'aa99',
    #  'first': 'Anita',
    #  'last': 'Agarwal',
    #  'puid': '920299006',
    #  'acareer': 'UGRD',
    #  'year': '2023'}

    # {'coursename': 'COS231_F2018',
    #  'lecture': 'L01',
    #  'lab': 'B02',
    #  'class': 'C01',
    #  'netid': 'bagoran',
    #  'first': 'Bhuta',
    #  'last': 'Goran',
    #  'puid': '920177604',
    #  'acareer': 'UGRD',
    #  'year': '2023'}

    simplified_students = []
    for student in students.values():
        simplified_students.append({
          "name": "{} {}".format(student["first"], student["last"]),
          "email": "{}@princeton.edu".format(student["netid"]),
          "tutorial": student.get("precept", student.get("lab", None))
        })

    course_id = pylifttk.ed.get_course_id(
        course_name=dest_course_name,
        course_term=dest_course_term,
    )

    pylifttk.ed.invite_many(
        course_id=course_id,
        users=simplified_students
    )


def csstaff_to_codepost(src_names, dest_course_name, dest_course_term):
    import pylifttk.csstaff
    import pylifttk.codepost

    if type(src_names) is str:
        src_names = list(src_names)

    students = {}
    for src_name in src_names:
        students.update(pylifttk.csstaff.course_enrollment(course_key=src_name, as_dict=True))

    # {'coursename': 'COS126_F2018',
    #  'lecture': 'L01',
    #  'precept': 'P08',
    #  'netid': 'aa99',
    #  'first': 'Anita',
    #  'last': 'Agarwal',
    #  'puid': '920299006',
    #  'acareer': 'UGRD',
    #  'year': '2023'}

    # {'coursename': 'COS231_F2018',
    #  'lecture': 'L01',
    #  'lab': 'B02',
    #  'class': 'C01',
    #  'netid': 'bagoran',
    #  'first': 'Bhuta',
    #  'last': 'Goran',
    #  'puid': '920177604',
    #  'acareer': 'UGRD',
    #  'year': '2023'}

    simplified_students = []
    for student in students.values():
        simplified_students.append({
            "email": "{}@princeton.edu".format(student["netid"]),
            "section": student.get("precept", student.get("lab", None))
        })

    course_id = pylifttk.codepost.get_course_id(dest_course_name, dest_course_term)

    student_email_list = list(map(lambda obj: obj.get("email"), simplified_students))

    pylifttk.codepost.invite_many_students(
        course_id=course_id,
        students=student_email_list,
    )

    sections = {}
    for student in simplified_students:
        if student["section"] is None:
            continue

        sections[student["section"]] = sections.get(student["section"], list())
        sections[student["section"]].append(student["email"])

    pylifttk.codepost.set_course_sections(
        course_id=course_id,
        section_dict=sections,
    )

