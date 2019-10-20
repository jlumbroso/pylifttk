
import bs4 as _bs4

import pylifttk.gradescope.api
import pylifttk.gradescope.util


def get_assignment_grades(course_id, assignment_id, simplified=False, **kwargs):

    # Fetch the grades
    response = pylifttk.gradescope.api.request(
        endpoint="courses/{}/assignments/{}/scores.csv".format(course_id, assignment_id)
    )

    # Parse the CSV format
    grades = pylifttk.gradescope.util.parse_csv(response.content)

    # Summarize it if necessary by removing question-level data
    if simplified:
        shortened_grades = list(map(pylifttk.gradescope.util.shortened_grade_record, grades))
        return shortened_grades

    return grades


def get_courses(by_name=False):
    response = pylifttk.gradescope.api.request(endpoint="account")
    soup = _bs4.BeautifulSoup(response.content)
    hrefs = list(filter(lambda s: s, map(
        lambda anchor: anchor.get("href"),
        soup.find_all("a", {"class": "courseBox"})
    )))
    course_ids = list(map(lambda href: href.split("/")[-1], hrefs))

    if by_name:
        return list(map(get_course_name, course_ids))

    return course_ids


def get_course_name(course_id):
    result = pylifttk.gradescope.api.request(endpoint="courses/{}".format(course_id))
    soup = _bs4.BeautifulSoup(result.content.decode())
    header_element = soup.find("header", {"class": "courseHeader"})
    if header_element:
        course_name = header_element.find("h1").text.replace(" ", "")

        course_term = header_element.find("div", {"class": "courseHeader--term"}).text
        course_term = course_term.replace("Fall ", "F")
        course_term = course_term.replace("Spring ", "S")
        return {"name": course_name, "term": course_term, "id": course_id}