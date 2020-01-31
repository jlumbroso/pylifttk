# pylifttk

This is a Python utility library for Princeton COS' LIFT.

This library tries to conveniently integrate a collection of educational tech tools used at Princeton's Department of Computer Science, to facilitate exchanges of data between those platforms.


## Services integrated by this library

This library integrates:
- codePost (roster, grades);
- Ed Discussion (roster);
- CSStaff Course API (roster, assignments);
- TigerFile (roster, assignments, submissions);
- GradeScope (roster, grades).


## Configuration file

Since this library integrates the functionality of several platforms, it requires access to credentials for each of those platforms. As such the `config.yaml` file does a lot of the heavy lifting. *Note that each subsection of the file is only loaded if the corresponding submodules are loaded in Python.*

```yaml
course: COS126
term: F2019

csstaff:
  username: "cos126api"
  password: "" # email csstaff@princeton.edu

codePost:
  api_key: "" #

ed:
  username: "" # credentials for https://us.edstem.org
  password: ""

gradescope:
  username: "" # credentials for https://gradescope.com
  password: ""

tigerfile:
  token: "" # token obtained from https://adm.cs.princeton.edu
```

## Example

This snippet computes final grades:

```python
# Miscellaneous late data calculation
late_data = get_late_data()

student_data = compute_final_grade_data(
    course_name="COS126",
    course_term="F2019",
    ignore_missing_assessment=False,
    skipped_assessments=None,
    override_cutoffs={
        "A+": 100.0,
        "A" : 92.49,
        "A-": 89.50,
        "B+": 87.00,
        "B" : 82.75,
        "B-": 80.00,
        "C+": 77.00,
        "C" : 73.00,
        "C-": 69.00,
        "D" : 55.0
    },
    late_data=late_data)
```