
import csv as _csv


def parse_csv(content):
    records = [
        record
        for record in _csv.DictReader(
            content.decode().splitlines(),
            quotechar='"',
            delimiter=',',
            quoting=_csv.QUOTE_ALL,
            skipinitialspace=True)
    ]
    return records


def shortened_grade_record(record):
    return {
        "name": record.get("Name", None),
        "sid": record.get("SID", None),
        "email": record.get("Email", None),
        "score": record.get("Total Score", 0.0),
        "graded": record.get("Status", None) == "Graded",
        "view_count": record.get("View Count", 0),
        "id": record.get("Submission ID", None),
    }