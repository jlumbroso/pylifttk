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