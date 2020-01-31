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
import pylifttk.integrations.final_grades as pyltkfg

def get_late_data():
    # student_id -> float of late days (including alloted)
    return {
        "student1": 1.0,
        "student7": 2.5,    
    }

# Miscellaneous late data calculation
late_data = get_late_data()

student_data = pyltkfg.compute_final_grade_data(
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

with the following sample configuration (authentication content blanked out):

```yaml
# Course information

course: COS126
term: F2019


# Authentication credentials and tokens

csstaff:
  username: "**********"
  password: "**********"

codePost:
  api_key: "**********"

ed:
  username: "**********"
  password: "**********"

gradescope:
  username: "**********"
  password: "**********"

tigerfile:
  token: "**********"

labqueue:
  username: "**********"
  password: "**********"

canvas:
  token: "**********"


# Mappings between the names of various services that this library is integrating

normalizations:
  - source: runscript
    destination: tigerfile
    mapping:
      hello: Hello
      loops: Loops
      nbody: NBody
      sierpinski: Sierpinski
      hamming: Hamming
      lfsr: LFSR
      guitar: Guitar
      markov: Markov
      tsp: TSP
      atomic: Atomic
  - source: tigerfile
    destination: codepost
    mapping:
      Hello: Hello
      Loops: Loops
      NBody: NBody
      Sierpinski: Sierpinski
      Hamming: Hamming
      LFSR: LFSR
      Guitar: Guitar
      Markov: Markov
      TSP: "TSPP"
      Atomic: Atomic


# Course policy constants

policy:
  cutoffs:
    "A" : 93
    "A-": 90
    "B+": 87
    "B" : 83
    "B-": 80
    "C+": 77
    "C" : 73
    "C-": 70
    "D" : 60
    "F" : 0

  lateness:
    allotted: 4
    penalty: 0.5
    grace_minutes: 180

  totals:
    Hello: 4.0
    Loops: 4.0
    NBody: 4.0
    Sierpinski: 4.0
    Hamming: 4.0
    Programming Exam 1: 7.5
    Written Exam 1: 17.5
    LFSR: 5.0
    Guitar: 5.0
    Markov: 5.0
    TSPP: 5.0
    Programming Exam 2: 7.5
    Written Exam 2: 17.5
    Atomic: 10.0

  weights:
    - name: "assignments"
      weight: 40.0
      content:
        - Hello
        - Loops
        - NBody
        - Sierpinski
        - Hamming
        - LFSR
        - Guitar
        - Markov
        - TSPP

    - name: "final project"
      weight: 10.0
      content:
        - Atomic

    - name: "written exams"
      weight: 35.0
      content:
        - Written Exam 1
        - Written Exam 2

    - name: "programming exams"
      weight: 15.0
      content:
        - Programming Exam 1
        - Programming Exam 2
```