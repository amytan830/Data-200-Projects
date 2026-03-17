import unittest
import csv
import os
import time
import random
import shutil
from Tan_Lab1 import (
    Student, Professor, Course, Grades,
    StudentService, ProfessorService, CourseService,
    HashTable, grade_scale,
    load_students, load_courses, load_professors
)

#  Original(real) files: backed up before every test, restored after — never overwritten
#  Test files: written during tests, kept after so grader can inspect them

real_students_file= "students.csv"
real_course_file= "courses.csv"
real_professors_file = "professor.csv"

backup_students_file= "students_backup.csv"
backup_course_file= "courses_backup.csv"
backup_professors_file = "professor_backup.csv"

test_student_file= "test_students.csv"
test_course_file= "test_courses.csv"
test_professors_file = "test_professors.csv"


#  Test Data
TEST_COURSES = {
    "DATA200": {"course_name": "Data Science", "credits": 3},
    "CS101":{"course_name":"Intro to CS","credits": 4},
    "MAT202":{"course_name":"Calculus II","credits": 4},
    "ENG150":{"course_name":"English Comp","credits": 3},
}


#  Ensures real CSV files are not modified by the tests

def backup_real_files():
    """Copy all real CSV files to backup before each test."""
    for real, bak in [
        (real_students_file,backup_students_file),
        (real_course_file,backup_course_file),
        (real_professors_file, backup_professors_file),
    ]:
        if os.path.exists(real):
            shutil.copy(real, bak)


def restore_real_files():
    """Restore all real CSV files from backup after each test."""
    for real, bak in [
        (real_students_file,backup_students_file),
        (real_course_file,backup_course_file),
        (real_professors_file, backup_professors_file),
    ]:
        if os.path.exists(bak):
            shutil.move(bak, real)



# Generating data 

def generate_students(existing, target=1000):
    """
    Top up an existing student list to reach the target count.
    Uses T-prefixed IDs so generated records are distinguishable
    from real students (S-prefixed).
    """
    grades= ["A", "B", "C", "D", "F"]
    firstnames = ["James", "Emma", "Liam", "Olivia", "Noah", "Ava",
                  "Sophia", "Mason", "Isabella", "Logan", "Ethan", "Mia",
                  "Lucas", "Harper", "Aiden", "Ella", "Jackson", "Scarlett",
                  "Sebastian", "Grace", "Owen", "Chloe", "Carter", "Penelope",
                  "Julian", "Layla", "Levi", "Riley", "Mateo", "Zoey"]
    lastnames  = ["Smith", "Johnson", "Williams", "Brown", "Jones",
                  "Garcia", "Miller", "Davis", "Wilson", "Taylor",
                  "Anderson", "Thomas", "Jackson", "White", "Harris",
                  "Martin", "Thompson", "Moore", "Lee", "Clark",
                  "Lewis", "Hall", "Allen", "Young", "Walker",
                  "King", "Scott", "Green", "Adams", "Baker"]
    course_ids = list(TEST_COURSES.keys())

    students= list(existing)
    existing_ids = {s.student_id for s in students}
    i = len(students) + 1

    while len(students) < target:
        student_id = f"T{i:04d}"
        if student_id in existing_ids:
            i += 1
            continue
        first = random.choice(firstnames)
        last = random.choice(lastnames)
        students.append(Student(
            student_id,
            f"{first.lower()}.{last.lower()}{i}@test.edu",
            first,
            last,
            random.choice(course_ids),
            random.choice(grades),
            random.randint(50, 100)
        ))
        existing_ids.add(student_id)
        i += 1

    return students


def write_test_students(students, filename=test_student_file):
    with open(filename, "w", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(["student_id", "email_address", "first_name",
                         "last_name", "course_id", "grade", "marks"])
        for s in students:
            writer.writerow([s.student_id, s.email_address, s.first_name,
                             s.last_name, s.course_id, s.grade, s.mark])


def write_test_courses(courses, filename=test_course_file):
    with open(filename, "w", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(["course_id", "course_name", "credits"])
        for course_id, info in courses.items():
            writer.writerow([course_id, info["course_name"], info["credits"]])


def write_test_professors(professors, filename=test_professors_file):
    with open(filename, "w", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(["professor_id", "first_name", "last_name",
                         "email_address", "course_id", "rank"])
        for p in professors:
            writer.writerow([p.professor_id, p.first_name, p.last_name,
                             p.email_address, p.course_id, p.rank])



#  Test Student Records

class TestStudentRecords(unittest.TestCase):

    def setUp(self):
        backup_real_files()
        try:
            existing = load_students(real_students_file)
        except FileNotFoundError:
            existing = []

        self.students = generate_students(existing, target=1000)
        write_test_students(self.students)
        write_test_courses(TEST_COURSES)

        course_index = HashTable()
        course_index.build_from_dict(TEST_COURSES)
        self.service = StudentService(self.students, TEST_COURSES, course_index)

    def tearDown(self):
        # Restore real files — test CSVs kept intentionally for grader
        restore_real_files()

    def test_has_1000_records(self):
        
        self.assertGreaterEqual(len(self.service.students), 1000)
        print(f"\n[pass] Total student records: {len(self.service.students)}")

    def test_load_from_csv(self):
        
        self.service.save_students(test_student_file)
        reloaded = load_students(test_student_file)
        self.assertGreaterEqual(len(reloaded), 1000)
        print(f"\n[pass] Loaded {len(reloaded)} records from {test_student_file} successfully.")

    def test_add_student(self):
        
        initial_count = len(self.service.students)
        new_student = Student(
            "NEW001", "new.student@test.edu",
            "New", "Student", "DATA200", "A", 95
        )
        self.service.students.append(new_student)
        self.service.save_students(test_student_file)

        reloaded = load_students(test_student_file)
        self.assertEqual(len(reloaded), initial_count + 1)
        self.assertIn("NEW001", [s.student_id for s in reloaded])
        print(f"\n[pass] Student added. Count: {initial_count} -> {len(reloaded)}")

    def test_delete_student(self):
        
        initial_count = len(self.service.students)
        target= next(s for s in self.service.students
                         if s.student_id.startswith("T"))
        target_id = target.student_id

        self.service.students = [s for s in self.service.students
                                  if s.student_id != target_id]
        self.service.save_students(test_student_file)

        reloaded = load_students(test_student_file)
        self.assertEqual(len(reloaded), initial_count - 1)
        self.assertNotIn(target_id, [s.student_id for s in reloaded])
        print(f"\n[pass] Student deleted. Count: {initial_count} -> {len(reloaded)}")

    def test_modify_student(self):
       
        target= next(s for s in self.service.students
                         if s.student_id.startswith("T"))
        target_id = target.student_id

        self.service.update_personal_info(
            target.email_address, first_name="UpdatedName"
        )

        updated = next((s for s in self.service.students
                        if s.student_id == target_id), None)
        self.assertIsNotNone(updated)
        self.assertEqual(updated.first_name, "UpdatedName")
        print(f"\n[pass] Student modified. New first name: {updated.first_name}")



#  Test Searching function


class TestSearch(unittest.TestCase):

    def setUp(self):
        
        backup_real_files()
        try:
            existing = load_students(real_students_file)
        except FileNotFoundError:
            existing = []

        self.students = generate_students(existing, target=1000)
        course_index= HashTable()
        course_index.build_from_dict(TEST_COURSES)
        self.service= StudentService(self.students, TEST_COURSES, course_index)

    def tearDown(self):
        restore_real_files()

    def test_search_by_name(self):
     
        target= self.students[0].last_name
        start= time.time()
        results = self.service.search_by_name(target)
        elapsed = time.time() - start

        self.assertIsInstance(results, list)
        print(f"\n[pass] Search by name '{target}': "
              f"{len(results)} result(s) found in {elapsed:.6f} seconds")

    def test_search_by_email(self):
       
        target= self.students[0].email_address
        start = time.time()
        results= self.service.search_by_email(target)
        elapsed= time.time() - start

        self.assertGreater(len(results), 0)
        print(f"\n[pass] Search by email '{target}': "
              f"{len(results)} result(s) found in {elapsed:.6f} seconds")

    def test_search_by_student_id(self):
        
        target= self.students[0].student_id
        start = time.time()
        results = self.service.search_by_student_id(target)
        elapsed = time.time() - start

        self.assertGreater(len(results), 0)
        self.assertEqual(results[0].student_id, target)
        print(f"\n[pass] Search by ID '{target}': "
              f"{len(results)} result(s) found in {elapsed:.6f} seconds")

    def test_search_no_results(self):
       
        start= time.time()
        results = self.service.search_by_name("ZZZNOMATCH")
        elapsed = time.time() - start

        self.assertEqual(len(results), 0)
        print(f"\n[pass] Search no results: 0 found in {elapsed:.6f} seconds")


# Test sorting records

class TestSort(unittest.TestCase):

    def setUp(self):
        
        backup_real_files()
        try:
            existing = load_students(real_students_file)
        except FileNotFoundError:
            existing = []
        self.students = generate_students(existing, target=1000)
        course_index  = HashTable()
        course_index.build_from_dict(TEST_COURSES)
        self.service  = StudentService(self.students, TEST_COURSES, course_index)

    def tearDown(self):
        restore_real_files()

    def test_sort_by_marks_ascending(self):
        start= time.time()
        sorted_students = sorted(self.service.students, key=lambda s: s.mark)
        elapsed= time.time() - start

        marks = [s.mark for s in sorted_students]
        self.assertEqual(marks, sorted(marks))
        print(f"\n[pass] Sort by marks ascending in {elapsed:.6f} seconds. "
              f"Range: {marks[0]} -> {marks[-1]}")

    def test_sort_by_marks_descending(self):
       
        start= time.time()
        sorted_students = sorted(self.service.students,
                                 key=lambda s: s.mark, reverse=True)
        elapsed= time.time() - start

        marks = [s.mark for s in sorted_students]
        self.assertEqual(marks, sorted(marks, reverse=True))
        print(f"\n[pass] Sort by marks descending in {elapsed:.6f} seconds. "
              f"Range: {marks[0]} -> {marks[-1]}")

    def test_sort_by_email_ascending(self):
        
        start= time.time()
        sorted_students = sorted(self.service.students,
                                 key=lambda s: s.email_address.lower())
        elapsed= time.time() - start

        emails = [s.email_address.lower() for s in sorted_students]
        self.assertEqual(emails, sorted(emails))
        print(f"\n[pass] Sort by email ascending in {elapsed:.6f} seconds.")

    def test_sort_by_email_descending(self):
        
        start= time.time()
        sorted_students = sorted(self.service.students,
                                 key=lambda s: s.email_address.lower(),
                                 reverse=True)
        elapsed= time.time() - start

        emails = [s.email_address.lower() for s in sorted_students]
        self.assertEqual(emails, sorted(emails, reverse=True))
        print(f"\n[pass] Sort by email descending in {elapsed:.6f} seconds.")



#  TestCourseRecords

class TestCourseRecords(unittest.TestCase):

    def setUp(self):
        
        backup_real_files()
        self.courses = {
            "DATA200": {"course_name": "Data Science", "credits": 3},
            "CS101":   {"course_name": "Intro to CS",  "credits": 4}
            }
        write_test_courses(self.courses)
        self.service = CourseService(self.courses, test_course_file)

    def tearDown(self):
        # Restore real files — test_courses.csv kept intentionally
        restore_real_files()

    def test_add_course(self):
      
        result = self.service.add_new_course("BIO110", "Biology", 3)
        self.assertTrue(result)
        self.assertIn("BIO110", self.service.courses)
        self.assertEqual(self.service.courses["BIO110"]["credits"], 3)

        reloaded = load_courses(test_course_file)
        self.assertIn("BIO110", reloaded)
        self.assertEqual(reloaded["BIO110"]["credits"], 3)
        print("\n[pass] Course added: BIO110 - Biology (3 credits)")

    def test_add_duplicate_course(self):
        
        result = self.service.add_new_course("DATA200", "Duplicate", 3)
        self.assertFalse(result)
        print("\n[pass] Duplicate course rejected.")

    def test_delete_course(self):
        
        result = self.service.delete_new_course("CS101")
        self.assertTrue(result)
        self.assertNotIn("CS101", self.service.courses)

        reloaded = load_courses(test_course_file)
        self.assertNotIn("CS101", reloaded)
        print("\n[pass] Course deleted: CS101")

    def test_delete_nonexistent_course(self):
        
        result = self.service.delete_new_course("FAKE999")
        self.assertFalse(result)
        print("\n[pass] Delete nonexistent course rejected.")

    def test_modify_course_name(self):
        
        result = self.service.modify_course(
            "DATA200", new_course_name="Advanced Data Science")
        self.assertTrue(result)
        self.assertEqual(
            self.service.courses["DATA200"]["course_name"], "Advanced Data Science")
        reloaded = load_courses(test_course_file)
        self.assertEqual(reloaded["DATA200"]["course_name"], "Advanced Data Science")
        print("\n[pass] Course name modified: DATA200 -> Advanced Data Science")

    def test_modify_course_credits(self):
       
        result = self.service.modify_course("DATA200", new_credits=4)
        self.assertTrue(result)
        self.assertEqual(self.service.courses["DATA200"]["credits"], 4)

        reloaded = load_courses(test_course_file)
        self.assertEqual(reloaded["DATA200"]["credits"], 4)
        print("\n[pass] Course credits modified: DATA200 -> 4 credits")

    def test_modify_course_name_and_credits(self):
       
        result = self.service.modify_course("CS101", new_course_name="Advanced CS", new_credits=3)
        self.assertTrue(result)
        self.assertEqual(self.service.courses["CS101"]["course_name"], "Advanced CS")
        self.assertEqual(self.service.courses["CS101"]["credits"], 3)
        print("\n[pass] Course modified: CS101 -> Advanced CS (3 credits)")



#  TestProfessorRecords

class TestProfessorRecords(unittest.TestCase):

    def setUp(self):
        """Back up real files, set up test professors."""
        backup_real_files()
        self.courses = {
            "DATA200": {"course_name": "Data Science", "credits": 3},
            "CS101":   {"course_name": "Intro to CS",  "credits": 4}
        }
        self.professors = [
            Professor("P001", "Michael", "John",
                      "michael@test.edu", "DATA200", "Senior Professor"),
            Professor("P002", "Sarah", "Lee",
                      "sarah@test.edu", "CS101", "Professor")
        ]
        write_test_professors(self.professors)
        write_test_courses(self.courses)

        course_index   = HashTable()
        course_index.build_from_dict(self.courses)
        course_service = CourseService(self.courses, test_course_file)
        self.service   = ProfessorService(
            self.professors, [], self.courses, course_service, course_index
        )

    def tearDown(self):
        # Restore real files — test_professors.csv kept intentionally
        restore_real_files()

    def test_add_professor(self):
        
        result = self.service.add_new_professor("P003", "Jane", "Doe","jane@test.edu", "DATA200", "Assistant Professor")
        self.assertTrue(result)
        self.assertIn("P003", [p.professor_id for p in self.service.professors])
        print("\n[pass] Professor added: P003 - Jane Doe")

    def test_add_duplicate_professor(self):
       
        result = self.service.add_new_professor("P001", "Fake", "Prof", "fake@test.edu", "DATA200", "Professor")
        self.assertFalse(result)
        print("\n[pass] Duplicate professor rejected.")

    def test_delete_professor(self):
        
        result = self.service.delete_professor("P002")
        self.assertTrue(result)
        self.assertNotIn("P002", [p.professor_id for p in self.service.professors])
        print("\n[pass] Professor deleted: P002")

    def test_delete_nonexistent_professor(self):
        
        result = self.service.delete_professor("FAKE999")
        self.assertFalse(result)
        print("\n[pass] Delete nonexistent professor rejected.")

    def test_modify_professor_rank(self):
       
        result = self.service.modify_professor_details("P001", rank="Distinguished Professor")
        self.assertTrue(result)
        prof = next(p for p in self.service.professors if p.professor_id == "P001")
        self.assertEqual(prof.rank, "Distinguished Professor")
        print(f"\n[pass] Professor rank modified: P001 -> {prof.rank}")

    def test_modify_professor_course(self):
        
        result = self.service.modify_professor_details("P002", course_id="DATA200")
        self.assertTrue(result)
        prof = next(p for p in self.service.professors if p.professor_id == "P002")
        self.assertEqual(prof.course_id, "DATA200")
        print(f"\n[pass] Professor course modified: P002 -> {prof.course_id}")



#  TestGrades

class TestGrades(unittest.TestCase):

    def test_grades_initial_values(self):
        """Verifies Grades object stores grade_id, grade, marks_range correctly."""
        g = Grades("G1", "A", "90-100")
        self.assertEqual(g.grade_id, "G1")
        self.assertEqual(g.grade, "A")
        self.assertEqual(g.marks_range, "90-100")
        print("\n[pass] Grades object created: G1 - A (90-100)")

    def test_add_grade(self):
        """Verifies add_grade() updates both grade and marks_range."""
        g = Grades("G1", "A", "90-100")
        g.add_grade("B", "80-89")
        self.assertEqual(g.grade, "B")
        self.assertEqual(g.marks_range, "80-89")
        print("\n[pass] Grade updated: A -> B (80-89)")

    def test_delete_grade(self):
        """Verifies delete_grade() clears both fields."""
        g = Grades("G1", "A", "90-100")
        g.delete_grade()
        self.assertEqual(g.grade, "")
        self.assertEqual(g.marks_range, "")
        print("\n[pass] Grade deleted: fields cleared")

    def test_modify_grade(self):
        """Verifies modify_grade() updates only the specified field."""
        g = Grades("G1", "A", "90-100")
        g.modify_grade(grade="C")
        self.assertEqual(g.grade, "C")
        self.assertEqual(g.marks_range, "90-100")  # unchanged
        print("\n[pass] Grade modified: A -> C, range unchanged")

    def test_grade_scale_completeness(self):
        """Verifies grade_scale contains all five expected grades."""
        grades = [g.grade for g in grade_scale]
        for expected in ["A", "B", "C", "D", "F"]:
            self.assertIn(expected, grades)
        print("\n[pass] grade_scale contains all 5 grades: A B C D F")


if __name__ == "__main__":
    unittest.main(verbosity=2)
