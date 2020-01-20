
import itertools

import codepost as _codepost

import pylifttk.codepost
import pylifttk.codepost.macros
import pylifttk.tigerfile


def find_assignment_ids(course_name, course_term, lookups=None, codepost_course_id=None, tigerfile_dropbox_id=None):
    if codepost_course_id is None:
        codepost_course_id = pylifttk.codepost.macros.get_course_id(
            course_name=course_name,
            course_term=course_term)

    if tigerfile_dropbox_id is None:
        tigerfile_dropbox_id = pylifttk.tigerfile.get_dropboxes(
            course_name=course_name,
            course_term=course_term,
            fetch_id=True)

    # Find codePost assignment ids
    codepost_assignments = dict()

    course = _codepost.course.retrieve(id=codepost_course_id)
    for assignment in course.assignments:
        codepost_assignments[assignment.name] = assignment.id

    # Find tigerfile assignment ids
    tigerfile_assignments = dict()

    assignments = pylifttk.tigerfile.get_assignments(dropbox_id=28)
    for assignment in assignments:
        if "name" in assignment and "id" in assignment:
            tigerfile_assignments[assignment["name"]] = assignment["id"]

    # Create match-up
    result = {}
    for (name, cp_id) in codepost_assignments.items():
        if name in tigerfile_assignments:
            result[name] = (cp_id, tigerfile_assignments[name])

        if lookups and name in lookups and lookups[name] in tigerfile_assignments:
            result[lookups[name]] = (cp_id, tigerfile_assignments[lookups[name]])

    return result


def get_ungraded_assignment(cp_course_id, cp_assignment_id, tf_assignment_id):
    ungraded = pylifttk.codepost.macros.get_ungraded_students(
        course_id=cp_course_id,
        assignment_id=cp_assignment_id
    )

    memberships = pylifttk.tigerfile.get_memberships(
        assignment_id=tf_assignment_id,
        simplified=True)

    def convert_emails_to_memberships(email):
        # jstudent@princeton.edu -> jstudent -> adffe93428934dafed193032
        username = email.split("@")[0]
        return (username, memberships.get(username))

    def has_not_submitted(email):
        username = email.split("@")[0]
        return memberships.get(username) is None

    non_submitting_students = list(filter(has_not_submitted, itertools.chain.from_iterable(ungraded.values())))

    for subcategory in ungraded.keys():
        ungraded[subcategory] = list(
            set(ungraded[subcategory]).difference(set(non_submitting_students))
        )
    ungraded["not-submitted"] = non_submitting_students

    ungraded_with_memberships = {
        key: list(map(convert_emails_to_memberships, ungraded[key]))
        for key in ungraded
    }

    return ungraded_with_memberships


def get_ungraded_assignments(course_name, course_term, lookups=None, codepost_course_id=None,
                             tigerfile_dropbox_id=None):
    if codepost_course_id is None:
        codepost_course_id = pylifttk.codepost.macros.get_course_id(
            course_name=course_name,
            course_term=course_term)

    if tigerfile_dropbox_id is None:
        tigerfile_dropbox_id = pylifttk.tigerfile.get_dropboxes(
            course_name=course_name,
            course_term=course_term,
            fetch_id=True)

    assignments = find_assignment_ids(
        course_name=course_name,
        course_term=course_term,
        codepost_course_id=codepost_course_id,
        tigerfile_dropbox_id=tigerfile_dropbox_id,
        lookups=lookups
    )

    info = {}
    for assignment_name, (cp_assignment_id, tf_assignment_id) in assignments.items():
        assignment_ungraded_info = get_ungraded_assignment(
            cp_course_id=codepost_course_id,
            cp_assignment_id=cp_assignment_id,
            tf_assignment_id=tf_assignment_id)

        record = {
            "name": assignment_name,
            "codePost-course-id": codepost_course_id,
            "codePost-assignment-id": cp_assignment_id,
            "tigerfile-dropbox-id": tigerfile_dropbox_id,
            "tigerfile-assignmnent-id": tf_assignment_id,
            "ungraded": assignment_ungraded_info
        }
        info[assignment_name] = record

    return info


def generate_tigerfile_to_codepost_script(course_name, course_term, lookups=None):
    TEMPLATE = "/n/fs/tigerfile/Files/{course_name}_{course_term}/{assignment_name}/submissions/{submission_id}/"

    assignment_ungraded_infos = get_ungraded_assignments(
        course_name=course_name,
        course_term=course_term,
        lookups=lookups
    )
    script = []
    for assignment_info in assignment_ungraded_infos.values():
        assignment_name = assignment_info["name"]
        ungraded_not_uploaded = assignment_info["ungraded"]["not-uploaded"]
        submission_ids = []
        for (netid, submission_id) in ungraded_not_uploaded:
            submission_path = TEMPLATE.format(
                course_name=course_name,
                course_term=course_term,
                assignment_name=assignment_name,
                submission_id=submission_id
            )
            script.append("cp -pr {submission_path} ./{submission_id}".format(
                submission_path=submission_path,
                submission_id=submission_id))
            submission_ids.append(submission_id)

        if len(submission_ids) > 0:
            script.append(
                "~/assignments/{assignment_name}/run-script {submissions} | tee runscript-{assignment_name}.log".format(
                    assignment_name=assignment_name.lower(),
                    submissions=" ".join(submission_ids)
            ))
            script.append(
                "push-to-codePost --verbose -a'{assignment_name}' -s {submissions} | tee codepost-{assignment_name}.log".format(
                    assignment_name=assignment_name,
                    submissions=" ".join(submission_ids),
            ))
    return "\n".join(script)

