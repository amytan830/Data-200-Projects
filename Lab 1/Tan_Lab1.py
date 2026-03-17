# CheckMyGradeApp— Tan_Lab1.py

# Import Modules
import csv
from statistics import mean, median
import time

# Define professor rank that has special admin property
privileged_ranks = {"Professor & Administrator"}

# Data Structures 
class Stack:
    """LIFO structure for undo grade history."""
    def __init__(self):
        self.items = []

    def push(self, item):
        self.items.append(item)

    def pop(self):
        if self.is_empty():
            return None
        return self.items.pop()

    def peek(self):
        if self.is_empty():
            return None
        return self.items[-1]

    def is_empty(self):
        return len(self.items) == 0

    def size(self):
        return len(self.items)


class Queue:
    """FIFO structure for student enrollment processing."""
    def __init__(self):
        self.items = []

    def enqueue(self, item):
        self.items.append(item)

    def dequeue(self):
        if self.is_empty():
            return None
        return self.items.pop(0)

    def is_empty(self):
        return len(self.items) == 0

    def size(self):
        return len(self.items)


class HashTable:
    """Hash table for fast O(1) course lookup by course_id."""
    def __init__(self):
        self.table = {}

    def insert(self, key, value):
        """Insert a course into the hash table."""
        self.table[key] = value

    def lookup(self, key):
        """Look up a course by course_id — O(1)."""
        return self.table.get(key, None)

    def delete(self, key):
        """Remove a course from the hash table."""
        if key in self.table:
            del self.table[key]

    def build_from_dict(self, courses_dict):
        """Build hash table from courses dict."""
        for course_id, info in courses_dict.items():
            self.table[course_id] = info

    def size(self):
        return len(self.table)


#  Password Security 
class TextSecurity:
    """Encrypts and decrypts text using Caesar cipher."""
    def __init__(self, shift):
        self.s = shift
        self.s = self.s % 26

    def _convert(self, text, s):
        result = ""
        for ch in text:
            if ch.isupper():
                result += chr((ord(ch) - 65 + s) % 26 + 65)
            elif ch.islower():
                result += chr((ord(ch) - 97 + s) % 26 + 97)
            elif ch.isdigit():
                result += chr((ord(ch) - 48 + s) % 10 + 48)
            else:
                result += ch
        return result

    def encrypt_password(self, text):
        return self._convert(text, self.s)

    def decrypt_password(self, text):
        return self._convert(text, -self.s)


#  Login 
class LoginUser:
    """Handles authentication logic."""
    def __init__(self, users):
        self.users = users
        self.cipher= TextSecurity(4)

    def login(self, email, password):
        for u in self.users:
            if u.user_id == email:
                if self.cipher.decrypt_password(u.password) == password:
                    return u
        return None

    def logout(self, user):
        print("Goodbye!")
        print(f"**{user.user_id}** is logged out.")

    def change_password(self, user, login_filename="login_encrypted.csv"):
        """Allows a user to change their password, encrypts new password, and stores in login_encrypted.csv """

        current_pw = input("Enter your current password: ")
        if self.cipher.decrypt_password(user.password) != current_pw:
            print("Current password is incorrect. Unable to verify")
            return False
        new_pw = input("Enter NEW password: ")
        confirm_pw = input("Confirm NEW password: ")
        if new_pw != confirm_pw:
            print("New passwords do not match.")
            return False
        if not new_pw.strip():
            print("New password cannot be empty.")
            return False
        encrypted = self.cipher.encrypt_password(new_pw)
        user.password = encrypted
        for u in self.users:
            if u.user_id == user.user_id:
                u.password = encrypted
                break
        rows = []
        with open(login_filename, newline="") as f:
            reader = csv.DictReader(f)
            fieldnames = reader.fieldnames
            for row in reader:
                if row["user_id"] == user.user_id:
                    row["password"] = encrypted
                rows.append(row)
        with open(login_filename, "w", newline="") as f:
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(rows)
        print("Password updated successfully!")
        return True


class LoginAccount:
    """Stores login data (email, password, role)."""
    def __init__(self, user_id, password, role):
        self.user_id = user_id
        self.password = password
        self.role = role


# Map CSV column names to constructor arguments in the right order 
def load_users(filename):
    users = []
    with open(filename, newline="") as file:
        reader = csv.DictReader(file)
        for row in reader:
            users.append(LoginAccount(row["user_id"], row["password"], row["role"]))
    return users


def load_courses(filename):
    """Load courses as dict: {course_id: {course_name, credits}}"""
    courses = {}
    with open(filename, newline="") as file:
        reader = csv.DictReader(file)
        for row in reader:
            courses[row["course_id"]] = {"course_name": row["course_name"],
                                         "credits": int(row["credits"])}
    return courses


def load_students(filename):
    students = []
    with open(filename, newline="") as file:
        reader = csv.DictReader(file)
        for row in reader:
            students.append(Student(
                row["student_id"],
                row["email_address"],
                row["first_name"],
                row["last_name"],
                row["course_id"],
                row["grade"],
                row["marks"]
            ))
    return students


def load_professors(filename):
    professors = []
    with open(filename, newline="") as file:
        reader = csv.DictReader(file)
        for row in reader:
            professors.append(Professor(
                row["professor_id"],
                row["first_name"],
                row["last_name"],
                row["email_address"],
                row["course_id"],
                row["rank"]
            ))
    return professors


#  Classes 

class Person:
    def __init__(self, first_name, last_name, email_address):
        self.first_name = first_name
        self.last_name = last_name
        self.email_address = email_address

    @property
    def full_name(self):
        return f"{self.first_name} {self.last_name}"


class Student(Person):
    def __init__(self, student_id, email_address, first_name, last_name, course_id, grade, mark):
        super().__init__(first_name, last_name, email_address)
        self.student_id = student_id
        self.course_id = course_id
        self.grade = grade
        self.mark = int(mark) if mark else 0


class Professor(Person):
    def __init__(self, professor_id, first_name, last_name, email_address,course_id, rank):
        super().__init__(first_name, last_name, email_address)
        self.professor_id = professor_id
        self.course_id = course_id
        self.rank = rank


class Course:
    def __init__(self, course_id, course_name, credits):
        self.course_id = course_id
        self.course_name = course_name
        self.credits = int(credits)


class Grades:
    """Stores grade information for a student in a course."""
    def __init__(self, grade_id, grade, marks_range):
        self.grade_id= grade_id
        self.grade= grade
        self.marks_range = marks_range

    def display_grade_report(self):
        print(f"Grade ID: {self.grade_id}")
        print(f"Grade:{self.grade}")
        print(f"Range:{self.marks_range}")

    def add_grade(self, grade, marks_range):
        self.grade= grade
        self.marks_range = marks_range

    def delete_grade(self):
        self.grade= ""
        self.marks_range = ""

    def modify_grade(self, grade=None, marks_range=None):
        if grade is not None: self.grade = grade
        if marks_range is not None: self.marks_range = marks_range


#  Standard grade scale 
grade_scale = [
    Grades("G1", "A", "90-100"),
    Grades("G2", "B", "80-89"),
    Grades("G3", "C", "70-79"),
    Grades("G4", "D", "60-69"),
    Grades("G5", "F", "0-59"),
]


#  ProfessorService stores all functions a professor can perform
class ProfessorService:
    def __init__(self, professors_list, students_list, courses_dict, course_service, course_index):
        self.professors= professors_list
        self.students= students_list
        self.courses= courses_dict
        self.grade_undo_stack = Stack()
        self.course_service = course_service
        self.course_index = course_index
       
    def update_login_file(self, email, action, role="Professor", password="ChangeMe123"):
        filename = "login_encrypted.csv"
        cipher = TextSecurity(4)

        rows = []
        with open(filename, newline="") as f:
            reader = csv.DictReader(f)
            fieldnames = reader.fieldnames
            for row in reader:
                if action == "delete" and row["user_id"].lower() == email.lower():
                    continue
                rows.append(row)

        if action == "add":
            # Check if login already exists
            existing_ids = [r["user_id"].lower() for r in rows]
            if email.lower() in existing_ids:
                return False  # already exists
            rows.append({
                "user_id": email,
                "password": cipher.encrypt_password(password),
                "role": role
            })

        with open(filename, "w", newline="") as f:
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(rows)

        return True

    def get_course_info(self, course_id):
        """Look up course name and credits from hash table — O(1)."""
        info = self.course_index.lookup(course_id)
        if info:
            return info.get("course_name", "N/A"), info.get("credits", "N/A")
        return "N/A", "N/A"

    def get_professor_rank(self, email):
        """Return rank of professor by email."""
        prof = next((p for p in self.professors if p.email_address == email), None)
        return prof.rank if prof else ""

    #  Course Management 

    def manage_courses_menu(self):
        """Sub-menu for course management — privileged rank only."""
        while True:
            self.course_service.display_courses()
            print("\n1. Add a course")
            print("2. Delete a course")
            print("3. Modify a course")
            print("4. Back")

            choice = input("Choose an option: ").strip()

            if choice == "1":
                course_id= input("Enter new course ID: ").strip().upper()
                course_name = input("Enter course name: ").strip()
                while True:
                    credits_input = input("Enter credits (1-6): ").strip()
                    if credits_input.isdigit() and 1 <= int(credits_input) <= 6:
                        break
                    print("Please enter a number between 1 and 6.")
                self.course_service.add_new_course(course_id, course_name, int(credits_input))
                # Keep hash table in sync
                self.course_index.insert(course_id, {
                    "course_name": course_name,
                    "credits": int(credits_input)
                })

            elif choice == "2":
                course_id = input("Enter course ID to delete: ").strip().upper()

                affected = [p for p in self.professors if p.course_id == course_id]
                affected_students = [s for s in self.students if s.course_id == course_id]

                if affected:
                    print(f"Warning: {len(affected)} professor(s) are assigned to {course_id}:")
                    for p in affected:
                        print(f"  {p.professor_id} - {p.full_name}")

                if affected_students:
                    print(f"Warning: {len(affected_students)} student record(s) are enrolled in {course_id}.")

                if affected or affected_students:
                    print("Deleting this course will set professors to 'UNASSIGNED' and remove enrolled students.")
                    confirm = input("Are you sure? Type 'yes' to confirm: ").strip().lower()
                    if confirm != "yes":
                        print("Cancelled.")
                        continue

                deleted = self.course_service.delete_new_course(course_id)
                if not deleted:
                    continue

                self.course_index.delete(course_id)

                if affected:
                    for p in affected:
                        p.course_id = "UNASSIGNED"
                    self.save_professors()
                    print(f"{len(affected)} professor(s) updated to UNASSIGNED.")

                if affected_students:
                    self.students = [s for s in self.students if s.course_id != course_id]
                    self.save_students()
                    print(f"{len(affected_students)} student record(s) removed.")

            elif choice == "3":
                course_id = input("Enter course ID to modify: ").strip().upper()
                print("Leave blank to keep current value.")
                new_name = input("New course name: ").strip() or None
                new_credits = input("New credits (1-6): ").strip() or None
                if new_credits is not None:
                    if not new_credits.isdigit() or not (1 <= int(new_credits) <= 6):
                        print("Invalid credits value. Keeping current.")
                        new_credits = None
                self.course_service.modify_course(course_id, new_name, new_credits)
                # Keep hash table in sync
                existing = self.course_index.lookup(course_id)
                if existing:
                    if new_name:
                        existing["course_name"] = new_name
                    if new_credits:
                        existing["credits"] = int(new_credits)
                    self.course_index.insert(course_id, existing)

            elif choice == "4":
                break
            else:
                print("Invalid choice.")

    #  Professor Management 

    def manage_professors_menu(self, requesting_email):
        """Sub-menu for professor management — privileged rank only."""
        requester = next((p for p in self.professors if p.email_address == requesting_email), None)
        if not requester:
            print("Professor not found.")
            return

        while True:
            print("\n=========================== Professor List =============================")
            print(f"{'ID':<8} {'Name':<25} {'Rank':<30} {'Course':<10}")
            print("-" * 76)
            for p in self.professors:
                print(f"{p.professor_id:<8} {p.full_name:<25} {p.rank:<30} {p.course_id:<10}")
            print("=" * 76)

            print("\n1. Add a professor")
            print("2. Delete a professor")
            print("3. Modify professor details")
            print("4. Back")

            choice = input("Choose an option: ").strip()

            if choice == "1":
                existing_nums = []
                for p in self.professors:
                    if p.professor_id.startswith("P") and p.professor_id[1:].isdigit():
                        existing_nums.append(int(p.professor_id[1:]))
                next_num= max(existing_nums) + 1 if existing_nums else 1
                professor_id = f"P{next_num:03d}"
                print(f"Generated Professor ID: {professor_id}")

                first_name = input("First name: ").strip().replace(",", "")
                last_name = input("Last name: ").strip().replace(",", "")
                email= input("Email: ").strip()
                course_id  = input("Course ID: ").strip().upper()

                # Validate course exists before adding professor
                if course_id and course_id not in self.courses:
                    print(f"Course ID '{course_id}' does not exist. Professor not added.")
                else:
                    rank = input("Rank: ").strip()
                    self.add_new_professor(
                        professor_id, first_name, last_name, email, course_id, rank
                    )
            elif choice == "2":
                professor_id = input("Enter professor ID to delete: ").strip()
                if professor_id == requester.professor_id:
                    print("You cannot delete your own account.")
                else:
                    self.delete_professor(professor_id)
            elif choice == "3":
                professor_id  = input("Enter professor ID to modify: ").strip()
                print("Leave blank to keep current value.")
                new_rank= input("New rank: ").strip() or None
                new_course_id = input("New course ID: ").strip().upper() or None
                new_first_name = input("New first name: ").strip() or None
                new_last_name = input("New last name: ").strip() or None
              
                # Validate course_id exists before modifying
                if new_course_id is not None and new_course_id not in self.courses:
                    print(f"Course ID '{new_course_id}' does not exist. Modification cancelled.")
                else:
                    self.modify_professor_details(
                        professor_id,
                        first_name=new_first_name,
                        last_name=new_last_name,
                        course_id=new_course_id,
                        rank=new_rank
                    )
            elif choice == "4":
                break
            else:
                print("Invalid choice.")

    #  Professor Profile 

    def professor_details(self, email):
        prof = next((p for p in self.professors if p.email_address == email), None)
        if not prof:
            print("Professor not found.")
            return
        # Use hash table for O(1) course lookup
        course_name, course_credits = self.get_course_info(prof.course_id)
        print("========== Professor Details ================")
        print(f"Name:          {prof.full_name}")
        print(f"Professor ID:  {prof.professor_id}")
        print(f"Email:         {prof.email_address}")
        print(f"Rank:          {prof.rank}")
        print(f"Course taught: {prof.course_id} - {course_name} ({course_credits} credits)")
        print("==============================================")

    #  Grade Report 

    def display_grade_report(self, email):
        prof = next((p for p in self.professors if p.email_address == email), None)
        if not prof:
            print("Professor not found.")
            return

        course_students = [s for s in self.students if s.course_id == prof.course_id]
        if not course_students:
            print(f"No students found for course {prof.course_id}")
            return

        # Use hash table for O(1) course lookup
        course_name, course_credits = self.get_course_info(prof.course_id)

        print(f"\nCourse grade report for {prof.course_id}: {course_name} ({course_credits} credits)")
        print(f"{'Student Id':<12} {'Name':<20} {'Grade':<6} {'Marks':<6}")
        print("-" * 50)

        for s in course_students:
            print(f"{s.student_id:<12} {s.full_name:<20} {s.grade:<6} {s.mark:<6}")

        marks = [s.mark for s in course_students]
        print("=" * 50)
        print(f"Average mark: {mean(marks):.2f}")
        print(f"Median mark:{median(marks):.2f}")

        grade_counts = {"A": 0, "B": 0, "C": 0, "D": 0, "F": 0}
        for s in course_students:
            if s.grade in grade_counts:
                grade_counts[s.grade] += 1

        total = len(course_students)
        print("\nGrade Distribution")
        print(f"{'Grade':<8} {'Count':<8} {'Percentage':<10}")
        print("-" * 28)
        for gs in grade_scale:
            count= grade_counts.get(gs.grade, 0)
            percentage = (count / total * 100) if total > 0 else 0
            print(f"{gs.grade:<8} {count:<8} {percentage:.1f}%")
        print("=" * 50)

        print("\n1. Sort students")
        print("2. Back")
        choice = input("Choose an option: ").strip()
        if choice == "1":
            self.sort_students(email)
        elif choice == "2":
            return
        else:
            print("Invalid choice.")

    #  Grade Management 

    def modify_grade_menu(self, professor_email):
        while True:
            print("1. Add/Update Grade")
            print("2. Delete grade")
            print("3. Return")
            choice = input("Which action would you like to perform?: ")
            if choice == "1":
                self.add_grade(professor_email)
            elif choice == "2":
                self.delete_grade(professor_email)
            elif choice == "3":
                break
            else:
                print("Invalid choice.")

    def add_grade(self, professor_email):
        """Assign or update a grade for a student."""
        prof = next((p for p in self.professors if p.email_address == professor_email), None)
        if not prof:
            print("Professor not found.")
            return

        student_id = input("Enter student Id: ")
        found = None
        for s in self.students:
            if s.student_id == student_id and s.course_id == prof.course_id:
                found = s
                break
        if not found:
            print("Student not found in your course")
            return

        print(f"Making updates to {found.full_name}'s grade for {prof.course_id}")
        print(f"Current grade: {found.grade} ({found.mark})")
        print("Adding grade..." if (found.grade == "" or found.mark == 0)
              else "Updating existing grade...")

        valid_grades = {"A", "B", "C", "D", "F"}
        while True:
            new_grade = input("Enter grade(A-F): ").upper()
            if new_grade in valid_grades:
                break
            print("Invalid grade")

        while True:
            mark_input = input("Enter mark(0-100): ")
            if mark_input.isdigit():
                new_mark = int(mark_input)
                if 0 <= new_mark <= 100:
                    break
            print("Invalid mark. Please enter a number from 0 to 100.")

        self.grade_undo_stack.push({
            "student_id": found.student_id,
            "course_id":found.course_id,
            "grade":found.grade,
            "mark":found.mark
        })
        found.grade = new_grade
        found.mark= new_mark

        self.save_students()
        print("Student grade updated successfully!")

        undo = input("Would you like to undo this change? (yes/no): ").strip().lower()
        if undo == "yes":
            self.undo_last_grade()

    def undo_last_grade(self):
        """Undo the last grade change."""
        if self.grade_undo_stack.is_empty():
            print("Nothing to undo.")
            return False
        previous = self.grade_undo_stack.pop()
        for s in self.students:
            if s.student_id == previous["student_id"] and s.course_id == previous["course_id"]:
                s.grade = previous["grade"]
                s.mark= previous["mark"]
                self.save_students()
                print(f"Undone. {s.full_name}'s grade restored to {s.grade} ({s.mark}).")
                return True
        print("Student record not found for undo.")
        return False

    def delete_grade(self, professor_email):
        """Clear a student's grade and mark."""
        prof = next((p for p in self.professors if p.email_address == professor_email), None)
        if not prof:
            print("Professor not found.")
            return

        student_id = input("Enter student Id: ")
        found = None
        for s in self.students:
            if s.student_id == student_id and s.course_id == prof.course_id:
                found = s
                break
        if not found:
            print("Student not found in your course")
            return

        print(f"Making updates to {found.full_name}'s grade for {prof.course_id}")
        print(f"Current grade: {found.grade} ({found.mark})")

        self.grade_undo_stack.push({
            "student_id": found.student_id,
            "course_id":found.course_id,
            "grade":found.grade,
            "mark":found.mark
        })

        found.grade = ""
        found.mark = 0
        self.save_students()
        print("Grade removed.")

        undo = input("Would you like to undo this change? (yes/no): ").strip().lower()
        if undo == "yes":
            self.undo_last_grade()

    #  Search functions

    def search_students(self, professor_email):
        """Search students in professor's course by name or ID and print time taken."""
        prof = next((p for p in self.professors if p.email_address == professor_email), None)
        if not prof:
            print("Professor not found.")
            return

        print("\nSearch by:")
        print("1. Student name")
        print("2. Student ID")
        print("3. Student email")
        print("4. Back")

        choice = input("Choose: ").strip()
        if choice == "4":
            return

        term = input("Enter search value: ").strip()
        if not term:
            print("Search value cannot be empty.")
            return

        if choice == "1":
            term_lower = term.lower()
            start= time.time()
            results= [s for s in self.students if s.course_id == prof.course_id and
                          (term_lower in s.first_name.lower() or term_lower in s.last_name.lower())]
            elapsed = time.time() - start

        elif choice == "2":
            start= time.time()
            results = [s for s in self.students if s.student_id == term and s.course_id == prof.course_id]
            elapsed = time.time() - start
        
        elif choice == "3":
            start   = time.time()
            results = [s for s in self.students if s.email_address.lower() == term.lower() and s.course_id == prof.course_id]
            elapsed = time.time() - start

        else:
            print("Invalid choice.")
            return

        if not results:
            print(f"No students found matching '{term}' in {prof.course_id}.")
            print(f"Search completed in {elapsed:.6f} seconds.")
            return

        print(f"\nSearch results for '{term}' in {prof.course_id}:")
        print(f"{'Student Id':<12} {'Name':<20} {'Grade':<6} {'Marks':<6}")
        print("-" * 50)
        for s in results:
            print(f"{s.student_id:<12} {s.full_name:<20} {s.grade:<6} {s.mark:<6}")
        print(f"\n{len(results)} result(s) found in {elapsed:.6f} seconds.")

    #  Student Management 
    def add_new_student(self, professor_email):
        """Add one or more students to professor's course using a queue."""
        prof = next((p for p in self.professors if p.email_address == professor_email), None)
        if not prof:
            print("Professor not found.")
            return

        enrollment_queue = Queue()

        # Calculate starting ID once before the loop to avoid collisions
        existing_nums = []
        for s in self.students:
            if s.student_id.startswith("S") and s.student_id[1:].isdigit():
                existing_nums.append(int(s.student_id[1:]))
        next_num = max(existing_nums) + 1 if existing_nums else 1

        while True:
            print("\nEnter student details (or press Enter on first name to finish):")
            first_name = input("First name (or press Enter to finish): ").strip().replace(",", "")
            if not first_name:
                break

            last_name = input("Last name: ").strip().replace(",", "")
            email = input("Email: ").strip()

            if not last_name or not email:
                print("Last name and email are required.")
                continue

            # Prevent duplicate enrollment in the same course
            duplicate_enrollment = next(
                (s for s in self.students
                if s.email_address.lower() == email.lower()
                and s.course_id == prof.course_id),
                None
            )
            if duplicate_enrollment:
                print("Student is already enrolled in this course.")
                continue

            # Auto-generate unique student ID
            student_id = f"S{next_num:03d}"
            print(f"Generated Student ID: {student_id}")
            next_num += 1

            new_student = Student(
                student_id, email, first_name, last_name,
                prof.course_id, "", 0
            )
            enrollment_queue.enqueue(new_student)
            print(f"Added {first_name} {last_name} to enrollment queue.")

        if enrollment_queue.is_empty():
            print("No students to enroll.")
            return

        count = 0
        while not enrollment_queue.is_empty():
            student = enrollment_queue.dequeue()

            login_added = self.update_login_file(
                student.email_address, "add", role="Student"
            )
            if not login_added:
                print(f"Skipping {student.first_name} {student.last_name}: login already exists.")
                continue

            self.students.append(student)
            count += 1

        self.save_students()
        print(f"\n{count} student(s) successfully enrolled in {prof.course_id}.")

    def delete_new_student(self, professor_email):
        """Remove a student from professor's course only."""
        prof = next((p for p in self.professors if p.email_address == professor_email), None)
        if not prof:
            print("Professor not found.")
            return False

        student_id = input("Enter student ID to remove (or press enter to cancel): ").strip()
        found = next((s for s in self.students if s.student_id == student_id and s.course_id == prof.course_id), None)
        if not found:
            print("Student not found in your course.")
            return False

        print(f"Are you sure you want to remove {found.full_name} from {prof.course_id}?")
        confirm = input("Type 'yes' to confirm: ").strip().lower()
        if confirm != "yes":
            print("Cancelled.")
            return False

        self.students.remove(found)
        self.update_login_file(found.email_address, "delete") 
        self.save_students()
        print(f"{found.full_name} removed from {prof.course_id}.")
        return True

    def save_students(self, filename="students.csv"):
        with open(filename, "w", newline="") as f:
            writer = csv.writer(f)
            writer.writerow(["student_id", "email_address", "first_name",
                             "last_name", "course_id", "grade", "marks"])
            for s in self.students:
                writer.writerow([s.student_id, s.email_address, s.first_name,
                                 s.last_name, s.course_id, s.grade, s.mark])

    #  Course Details / Sort 

    def show_course_details_by_professor(self, email):
        prof = next((p for p in self.professors if p.email_address == email), None)
        if not prof:
            print("Professor not found.")
            return

        # Use hash table for O(1) course lookup
        course_name, course_credits = self.get_course_info(prof.course_id)

        print("========== Course Details ===========")
        print(f"Course ID:   {prof.course_id}")
        print(f"Course name: {course_name}")
        print(f"Credits:     {course_credits}")
        co_professors = [p for p in self.professors if p.course_id == prof.course_id]
        print("Taught by:")
        for p in co_professors:
            print(f"  Professor {p.full_name} ({p.rank})")
        print("======================================")

        enrolled_students = [s for s in self.students if s.course_id == prof.course_id]
        print("Students enrolled:")
        print(f"{'Student Id':<12} {'Name':<20}")
        print("-" * 35)
        for s in enrolled_students:
            print(f"{s.student_id:<12} {s.full_name:<20}")
        print("-" * 35)
        print(f"Total students enrolled: {len(enrolled_students)}")

        choice = input("Would you like to sort the records by student name? (yes/no): ").lower()
        if choice == "yes":
                print("\nOrder:")
                print("1. Ascending")
                print("2. Descending")
                reverse = input("Choose sort order: ").strip() == "2"

                sorted_students = sorted(
                enrolled_students,
                key=lambda s: (s.last_name.lower(), s.first_name.lower()),
                reverse=reverse)

                print(f"\n{'Student Id':<12} {'Name':<20}")
                print("-" * 35)
                for s in sorted_students:
                    print(f"{s.student_id:<12} {s.full_name:<20}")
        elif choice != "no":
            print("Not a valid choice")
            


            
    def sort_students(self, professor_email):
        """Sort and display students in professor's course."""
        prof = next((p for p in self.professors if p.email_address == professor_email), None)
        if not prof:
            print("Professor not found.")
            return

        course_students = [s for s in self.students if s.course_id == prof.course_id]
        if not course_students:
            print("No students found in your course.")
            return

        print("\nSort by:")
        print("1. Name (Last name, then First name)")
        print("2. Marks")
        print("3. Grade")
        sort_choice = input("Choose: ").strip()

        print("\nOrder:")
        print("1. Ascending")
        print("2. Descending")
        reverse = input("Choose: ").strip() == "2"

        if sort_choice == "1":
            sorted_students = sorted(
                course_students,
                key=lambda s: (s.last_name.lower(), s.first_name.lower()),
                reverse=reverse
            )
        elif sort_choice == "2":
            sorted_students = sorted(course_students, key=lambda s: s.mark, reverse=reverse)
        elif sort_choice == "3":
            sorted_students = sorted(course_students,
                                     key=lambda s: s.grade.lower(), reverse=reverse)
        else:
            print("Invalid choice.")
            return

        print(f"\n{'Student Id':<12} {'Name':<20} {'Grade':<6} {'Marks':<6}")
        print("-" * 50)
        for s in sorted_students:
            print(f"{s.student_id:<12} {s.full_name:<20} {s.grade:<6} {s.mark:<6}")

    #  Professor modifications

    def add_new_professor(self, professor_id, first_name, last_name,
                          email_address, course_id, rank):
        for p in self.professors:
            if p.professor_id == professor_id:
                print("Professor ID already exists.")
                return False
            if p.email_address.lower() == email_address.lower():
                print("Professor email already exists.")
                return False
        new_professor = Professor(
            professor_id, first_name, last_name, email_address, course_id, rank
        )
        self.professors.append(new_professor)
        self.save_professors()
        self.update_login_file(email_address, "add", role="Professor")
        print("Professor added successfully.")
        return True

    def delete_professor(self, professor_id):
        for i, p in enumerate(self.professors):
            if p.professor_id == professor_id:
                email = p.email_address
                del self.professors[i]
                self.save_professors()
                self.update_login_file(email, "delete")
                print("Professor deleted successfully.")
                return True
        print("Professor not found.")
        return False

    def modify_professor_details(self, professor_id, first_name=None, last_name=None, email_address=None, course_id=None, rank=None):
        prof = next((p for p in self.professors if p.professor_id == professor_id), None)
        if not prof:
            print("Professor not found.")
            return False
        if first_name is not None: prof.first_name= first_name
        if last_name is not None: prof.last_name= last_name
        if email_address is not None: prof.email_address = email_address
        if course_id is not None: prof.course_id= course_id
        if rank is not None: prof.rank= rank
        self.save_professors()
        print("Professor details updated successfully.")
        return True

    def save_professors(self, filename="professor.csv"):
        with open(filename, "w", newline="") as f:
            writer = csv.writer(f)
            writer.writerow(["professor_id", "first_name", "last_name","email_address", "course_id", "rank"])
            for p in self.professors:
                writer.writerow([p.professor_id, p.first_name, p.last_name,
                                 p.email_address, p.course_id, p.rank])


#  StudentService 

class StudentService:
    def __init__(self, students_list, courses_dict, course_index):
        self.students = students_list
        self.courses = courses_dict
        self.course_index= course_index

    #  Search 

    def search_by_name(self, name):
        name_lower = name.lower()
        return [s for s in self.students
                if name_lower in s.first_name.lower()
                or name_lower in s.last_name.lower()]

    def search_by_email(self, email):
        return [s for s in self.students
                if email.lower() == s.email_address.lower()]

    def search_by_student_id(self, student_id):
        return [s for s in self.students if s.student_id == student_id]

    #  Grade / Mark helpers 

    def check_my_grades(self, email):
        """Return list of (course_id, grade) for a student."""
        return [(s.course_id, s.grade) for s in self._records_for_email(email)]

    def check_my_marks(self, email):
        """Return list of (course_id, mark) for a student."""
        return [(s.course_id, s.mark) for s in self._records_for_email(email)]

    def _records_for_email(self, email):
        return [s for s in self.students if s.email_address == email]

    #  Display 

    def display_records(self, email):
        """Display student personal info and enrolled courses with credits."""
        records = self._records_for_email(email)
        if not records:
            print("No records found.")
            return

        student = records[0]
        print("========== Student Profile ==========")
        print(f"Student ID:  {student.student_id}")
        print(f"Name:        {student.full_name}")
        print(f"Email:       {student.email_address}")
        print("=====================================")

        print(f"\nEnrolled Courses:")
        print(f"{'Course ID':<12} {'Course Name':<30} {'Credits':<8}")
        print("-" * 52)
        for s in records:
            info = self.course_index.lookup(s.course_id)
            course_name = info["course_name"] if info else "N/A"
            course_credits = info["credits"] if info else "N/A"
            print(f"{s.course_id:<12} {course_name:<30} {course_credits:<8}")

        edit_choice = input("\nWould you like to edit any information? (yes/no): ").lower()
        if edit_choice == "yes":
            print("1. Update first name")
            print("2. Update last name")
            print("3. Back")
            choice = input("Choose an option: ").strip()
            if choice == "1":
                new_value = input("Enter new first name: ").strip()
                if new_value:
                    self.update_personal_info(email, first_name=new_value)
                else:
                    print("First name cannot be empty.")
            elif choice == "2":
                new_value = input("Enter new last name: ").strip()
                if new_value:
                    self.update_personal_info(email, last_name=new_value)
                else:
                    print("Last name cannot be empty.")
            elif choice == "3":
                return
            else:
                print("Invalid choice.")

    def display_grade_report(self, email):
        """Display student grade report with credits, stats, and distribution."""
        records = self._records_for_email(email)
        if not records:
            print("No records found.")
            return

        student = records[0]
        grades = dict(self.check_my_grades(email))
        marks= dict(self.check_my_marks(email))

        print(f"\n====================== Grade Report: {student.full_name} ===========================")
        print(f"{'Course ID':<12} {'Course Name':<35} {'Credits':<9} {'Grade':<8} {'Marks':<6}")
        print("-" * 70)

        for s in records:
            info = self.course_index.lookup(s.course_id)
            course_name = info["course_name"] if info else "N/A"
            course_credits = info["credits"] if info else "N/A"
            print(f"{s.course_id:<12} {course_name:<35} {course_credits:<9} "
                  f"{grades.get(s.course_id, ''):<8} {marks.get(s.course_id, 0):<6}")

        mark_values = [m for m in marks.values() if m > 0]
        if mark_values:
            print("=" * 70)
            print(f"Average mark: {mean(mark_values):.2f}")
            print(f"Median mark:  {median(mark_values):.2f}")

        grade_counts = {"A": 0, "B": 0, "C": 0, "D": 0, "F": 0}
        graded_values = [grade for grade in grades.values() if grade in grade_counts]
        for grade in graded_values:
            grade_counts[grade] += 1
        total = len(records)
        print("\nGrade Distribution:")
        print(f"{'Grade':<8} {'Count':<8} {'Percentage':<10}")
        print("-" * 35)
        for gs in grade_scale:
            count= grade_counts.get(gs.grade, 0)
            percentage = (count / total * 100) if total > 0 else 0
            print(f"{gs.grade:<8} {count:<8} {percentage:.1f}%{'':<10}")
        print("=" * 70)

    def display_marks_only(self, email):
        """Show only course_id and marks."""
        records = self._records_for_email(email)
        if not records:
            print("No records found")
            return
        student = records[0]
        print(f"{student.full_name}'s Marks")
        print(f"{'Course ID':<12} {'Course Name':<30} {'Marks':<6}")
        print("-" * 50)
        for s in records:
            info = self.course_index.lookup(s.course_id)
            course_name = info["course_name"] if info else "N/A"
            print(f"{s.course_id:<12} {course_name:<30} {s.mark:<6}")

    def display_grades_only(self, email):
        """Show only course_id and grades."""
        records = self._records_for_email(email)
        if not records:
            print("No records found.")
            return
        student = records[0]
        print(f"{student.full_name}'s Grades")
        print(f"{'Course ID':<12} {'Course Name':<30} {'Grade':<6}")
        print("-" * 50)
        for s in records:
            info = self.course_index.lookup(s.course_id)
            course_name = info["course_name"] if info else "N/A"
            print(f"{s.course_id:<12} {course_name:<30} {s.grade:<6}")

    #  Update 

    def update_personal_info(self, email, first_name=None, last_name=None):
        records = self._records_for_email(email)
        if not records:
            print("Student not found.")
            return False
        for s in records:
            if first_name is not None: s.first_name = first_name
            if last_name  is not None: s.last_name  = last_name
        self.save_students()
        print("Profile updated successfully.")
        return True

    def save_students(self, filename="students.csv"):
        with open(filename, "w", newline="") as f:
            writer = csv.writer(f)
            writer.writerow(["student_id", "email_address", "first_name", "last_name", "course_id", "grade", "marks"])
            for s in self.students:
                writer.writerow([s.student_id, s.email_address, s.first_name, s.last_name, s.course_id, s.grade, s.mark])


#  CourseService 

class CourseService:
    def __init__(self, courses_dict, filename="courses.csv"):
        self.courses= courses_dict
        self.filename = filename

    def display_courses(self):
        """Display all courses with credits."""
        if not self.courses:
            print("No courses found.")
            return
        print("\n=============== Course List ==================")
        print(f"{'Course ID':<12} {'Course Name':<30} {'Credits':<8}")
        print("-" * 52)
        for course_id, info in self.courses.items():
            print(f"{course_id:<12} {info['course_name']:<30} {info['credits']:<8}")

    def add_new_course(self, course_id, course_name, credits):
        """Add a new course."""
        if not course_id:
            print("Course ID cannot be empty.")
            return False
        if not course_name:
            print("Course name cannot be empty.")
            return False
        if course_id in self.courses:
            print("Course ID already exists.")
            return False
        
        new_course = Course(course_id, course_name, credits)
        self.courses[new_course.course_id] = {
            "course_name": new_course.course_name,
            "credits": new_course.credits
        }
        self.save_courses()
        print("Course added successfully.")
        return True

    def delete_new_course(self, course_id):
        """Delete a course by course_id."""
        if course_id not in self.courses:
            print("Course not found.")
            return False
        del self.courses[course_id]
        self.save_courses()
        print("Course deleted successfully.")
        return True

    def modify_course(self, course_id, new_course_name=None, new_credits=None):
        """Modify an existing course."""
        if course_id not in self.courses:
            print("Course not found.")
            return False
        if new_course_name is not None:
            self.courses[course_id]["course_name"] = new_course_name
        if new_credits is not None:
            self.courses[course_id]["credits"] = int(new_credits)
        self.save_courses()
        print("Course updated successfully.")
        return True

    def save_courses(self):
        """Write courses back to CSV."""
        with open(self.filename, "w", newline="") as f:
            writer = csv.writer(f)
            writer.writerow(["course_id", "course_name", "credits"])
            for course_id, info in self.courses.items():
                writer.writerow([course_id, info["course_name"], info["credits"]])


#  Menus 

def student_menu(auth, student_service, course_service, user):
    while True:
        print(" ***** Student Menu ***** ")
        print("1. Check my grades")
        print("2. Check my marks")
        print("3. View my profile")
        print("4. View grade report")
        print("5. View course catalog")
        print("6. Change password")
        print("7. Logout")

        choice = input("What would you like to do? Choose one of the above options: ")

        if choice == "1":
            student_service.display_grades_only(user.user_id)
        elif choice == "2":
            student_service.display_marks_only(user.user_id)
        elif choice == "3":
            student_service.display_records(user.user_id)
        elif choice == "4":
            student_service.display_grade_report(user.user_id)
        elif choice == "5":
            course_service.display_courses()
        elif choice == "6":
            auth.change_password(user, "login_encrypted.csv")
        elif choice == "7":
            auth.logout(user)
            return "logout"
        else:
            print("Invalid choice. Try again.")


def professor_menu(auth, professor_service, user):
    while True:
        print(" ***** Professor Menu ***** ")
        print("1.  View my profile")
        print("2.  Display course grade report") # sort_students() is available here
        print("3.  Manage student grade(s)")
        print("4.  View course details") # sort_students() is available here
        print("5.  Add student(s) to my course")
        print("6.  Remove student from my course")
        print("7.  Search student records")


        # Options 8 and 9 only shown to Professor & Administrator
        if professor_service.get_professor_rank(user.user_id) in privileged_ranks:
            print("8.  Manage courses")
            print("9.  Manage professors")
            print("10. Change password")
            print("11. Logout")
        else:
            print("8.  Change password")
            print("9.  Logout")

        choice = input("What would you like to do? Choose one of the above options: ")

        if choice == "1":
            professor_service.professor_details(user.user_id)
        elif choice == "2":
            professor_service.display_grade_report(user.user_id)
        elif choice == "3":
            professor_service.modify_grade_menu(user.user_id)
        elif choice == "4":
            professor_service.show_course_details_by_professor(user.user_id)
        elif choice == "5":
            professor_service.add_new_student(user.user_id)
        elif choice == "6":
            professor_service.delete_new_student(user.user_id)
        
        elif choice == "7":
            professor_service.search_students(user.user_id)
        
        elif choice == "8":
            if professor_service.get_professor_rank(user.user_id) in privileged_ranks:
                professor_service.manage_courses_menu()
            else:
                auth.change_password(user, "login_encrypted.csv")
        elif choice == "9":
            if professor_service.get_professor_rank(user.user_id) in privileged_ranks:
                professor_service.manage_professors_menu(user.user_id)
            else:
                auth.logout(user)
                return "logout"
        elif choice == "10":
            auth.change_password(user, "login_encrypted.csv")
        elif choice == "11":
            auth.logout(user)
            return "logout"
        else:
            print("Invalid choice.")


#  Main 

def CheckMyGrade():
    while True:
        print("Welcome to CheckMyGrade! This is an evaluation tool for assessing students' grades.\n"
              "There are different access areas depending on your role.")
        print("Please login to proceed...")

        users = load_users("login_encrypted.csv")
        auth  = LoginUser(users)

        email= input("User Id (email): ")
        password = input("Password: ")
        user= auth.login(email, password)

        if not user:
            print("Invalid login. Routing back to main page...")
            continue

    #Demonstrate encrypt/decrypt is working
        #cipher= TextSecurity(4)
        #encrypted = cipher.encrypt_password(password)
        #decrypted = cipher.decrypt_password(encrypted)
        #print(f"\nPassword encrypted: {encrypted}")
        #print(f" Password decrypted: {decrypted}")
        #print(f" Match verified:{decrypted == password}")

        print(f"\nLogin successful. Role: {user.role}")

        students_list = load_students("students.csv")
        courses_dict = load_courses("courses.csv")
        professor_list = load_professors("professor.csv")
        course_service = CourseService(courses_dict, "courses.csv")

        # Build has table to share between both service classes 
        course_index = HashTable()
        course_index.build_from_dict(courses_dict)

        if user.role == "Student":
            student_service = StudentService(students_list, courses_dict, course_index)
            result = student_menu(auth, student_service, course_service, user)
            if result == "logout":
                continue

        elif user.role == "Professor" or user.role == "Professor & Administrator":
            professor_service = ProfessorService(professor_list, students_list, courses_dict, course_service, course_index)
            result = professor_menu(auth, professor_service, user)
            if result == "logout":
                continue

        else:
            print("Chosen role not implemented yet.")
            return


if __name__ == "__main__":
    CheckMyGrade()
