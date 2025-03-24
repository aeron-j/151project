import tkinter as tk
from tkinter import ttk
from tkinter import messagebox
import os
import re
import csv
import tkinter.simpledialog as simpledialog

CSV_FILE = os.path.join(os.path.dirname(__file__), 'student_data.csv')
COLLEGE_CSV = os.path.join(os.path.dirname(__file__), 'colleges.csv')
COURSE_CSV = os.path.join(os.path.dirname(__file__), 'courses.csv')

window = tk.Tk()
window.geometry("1250x500")
window.title("Student Data")

college_courses = {}

def load_college_courses_from_csv():
    global college_courses
    college_courses.clear()
    
    
    if not os.path.exists(COLLEGE_CSV):
        with open(COLLEGE_CSV, 'w', newline='') as csvfile:
            writer = csv.writer(csvfile)
            writer.writerow(["College Code", "College Name"])
    
    
    if not os.path.exists(COURSE_CSV):
        with open(COURSE_CSV, 'w', newline='') as csvfile:
            writer = csv.writer(csvfile)
            writer.writerow(["College", "Course Code", "Course Name"])
    
    try:
        
        with open(COLLEGE_CSV, 'r') as csvfile:
            reader = csv.reader(csvfile)
            next(reader)  
            for row in reader:
                if row:  
                    college_code, college_name = row
                    college_full = f"{college_code} - {college_name}"
                    college_courses[college_full] = []
        
        
        with open(COURSE_CSV, 'r') as csvfile:
            reader = csv.reader(csvfile)
            next(reader)  
            for row in reader:
                if row:  
                    college, course_code, course_name = row
                    course_full = f"{course_code} - {course_name}"
                    if college in college_courses:
                        college_courses[college].append(course_full)
                        
    except Exception as e:
        print(f"Error loading college courses: {e}")
        messagebox.showerror("Error", f"Failed to load college and course data: {str(e)}")

load_college_courses_from_csv()

class CollegeCourseManager:
    def __init__(self, main_window, college_courses, CSV_FILE):
        self.main_window = main_window
        self.original_college_courses = college_courses.copy()  
        self.college_courses = college_courses.copy()  
        self.CSV_FILE = CSV_FILE
        
        
        self.window = tk.Toplevel(main_window)
        self.window.title("College and Course Management")
        self.window.geometry("1200x500")
        self.window.config(bg="#800000")

        
        self.college_frame = tk.Frame(self.window, bg="#800000")
        self.college_frame.pack(side=tk.LEFT, padx=10, pady=10, fill=tk.BOTH, expand=False)

        self.course_frame = tk.Frame(self.window, bg="#800000")
        self.course_frame.pack(side=tk.RIGHT, padx=10, pady=10, fill=tk.BOTH, expand=True)

        
        tk.Label(self.college_frame, text="Colleges", bg="#800000", fg="white", 
                font=("Arial", 14, "bold")).pack(pady=10)
        
       
        self.college_columns = ("College Name", "Number of Courses")
        self.college_table = ttk.Treeview(self.college_frame, columns=self.college_columns, 
                                        show="headings", height=15)
        for col in self.college_columns:
            self.college_table.heading(col, text=col)
            self.college_table.column(col, width=150)
        self.college_table.pack(fill=tk.BOTH, expand=True)

        
        college_button_frame = tk.Frame(self.college_frame, bg="#800000")
        college_button_frame.pack(pady=10)
        
        tk.Button(college_button_frame, text="Add", bg="#7d6a69", fg="white", 
                 command=self.add_college, width=8).pack(side=tk.LEFT, padx=2)
        tk.Button(college_button_frame, text="Edit", bg="#7d6a69", fg="white", 
                 command=self.edit_college, width=8).pack(side=tk.LEFT, padx=2)
        tk.Button(college_button_frame, text="Delete", bg="#7d6a69", fg="white", 
                 command=self.delete_college, width=8).pack(side=tk.LEFT, padx=2)

       
        tk.Label(self.course_frame, text="Courses", bg="#800000", fg="white", 
                font=("Arial", 14, "bold")).pack(pady=10)
        
        
        filter_frame = tk.Frame(self.course_frame, bg="#800000")
        filter_frame.pack(pady=5)
        
        tk.Label(filter_frame, text="Filter by College:", 
                bg="#800000", fg="white").pack(side=tk.LEFT, padx=5)
        self.college_filter_var = tk.StringVar()
        self.college_filter_var.set("All Colleges")  
        
       
        college_options = ["All Colleges"] + list(self.college_courses.keys())
        self.college_filter_dropdown = ttk.Combobox(filter_frame, 
                                                  textvariable=self.college_filter_var, 
                                                  values=college_options, 
                                                  state='readonly', width=30)
        self.college_filter_dropdown.pack(side=tk.LEFT, padx=5)
        
      
        tk.Button(filter_frame, text="Apply Filter", 
                 bg="#7d6a69", fg="white",
                 command=self.refresh_courses).pack(side=tk.LEFT, padx=5)

        
        self.course_columns = ("College", "Course Code", "Course Name")
        self.course_table = ttk.Treeview(self.course_frame, columns=self.course_columns, 
                                       show="headings")
        for col in self.course_columns:
            self.course_table.heading(col, text=col)
            if col == "Course Name":
                self.course_table.column(col, width=300)
            else:
                self.course_table.column(col, width=150)
        self.course_table.pack(fill=tk.BOTH, expand=True)

        
        course_button_frame = tk.Frame(self.course_frame, bg="#800000")
        course_button_frame.pack(pady=10)
        
        tk.Button(course_button_frame, text="Add", bg="#7d6a69", fg="white", 
                 command=self.add_course, width=8).pack(side=tk.LEFT, padx=2)
        tk.Button(course_button_frame, text="Edit", bg="#7d6a69", fg="white", 
                 command=self.edit_course, width=8).pack(side=tk.LEFT, padx=2)
        tk.Button(course_button_frame, text="Delete", bg="#7d6a69", fg="white", 
                 command=self.delete_course, width=8).pack(side=tk.LEFT, padx=2)

        
        self.refresh_tables()
        
        
        self.college_table.bind("<<TreeviewSelect>>", self.on_college_select)
        self.college_table.bind("<Double-1>", self.on_college_double_click)
        self.course_table.bind("<Double-1>", self.on_course_double_click)

    def save_to_csv(self):
        try:
            
            with open(COLLEGE_CSV, 'w', newline='') as csvfile:
                writer = csv.writer(csvfile)
                writer.writerow(["College Code", "College Name"])
                for college in self.college_courses.keys():
                    code, name = college.split(' - ', 1)
                    writer.writerow([code, name])
            
            
            with open(COURSE_CSV, 'w', newline='') as csvfile:
                writer = csv.writer(csvfile)
                writer.writerow(["College", "Course Code", "Course Name"])
                for college, courses in self.college_courses.items():
                    for course in courses:
                        code, name = course.split(' - ', 1)
                        writer.writerow([college, code, name])
                        
            
            global college_courses
            college_courses.clear()
            college_courses.update(self.college_courses)
            
        except Exception as e:
            messagebox.showerror("Error", f"Failed to save college/course data: {str(e)}")
            
    def refresh_tables(self):
        self.populate_college_table()
        self.populate_course_table()

    def populate_college_table(self):
        
        for item in self.college_table.get_children():
            self.college_table.delete(item)
        
        
        for college, courses in self.college_courses.items():
            self.college_table.insert("", "end", values=(college, len(courses)))

    def populate_course_table(self):
        self.refresh_courses()

    def refresh_courses(self):
        
        for item in self.course_table.get_children():
            self.course_table.delete(item)
        
        selected_college = self.college_filter_var.get()
        
        
        if selected_college == "All Colleges":
            
            for college, courses in self.college_courses.items():
                for course in courses:
                    course_code, course_name = course.split(' - ', 1)
                    self.course_table.insert("", "end", values=(college, course_code, course_name))
        else:
            
            for course in self.college_courses.get(selected_college, []):
                course_code, course_name = course.split(' - ', 1)
                self.course_table.insert("", "end", values=(selected_college, course_code, course_name))

    def on_college_select(self, event):
        pass
        
    def highlight_courses_for_college(self, college_name):
        
        for item in self.course_table.get_children():
            self.course_table.selection_remove(item)
        
        
        for item in self.course_table.get_children():
            if self.course_table.item(item)['values'][0] == college_name:
                self.course_table.selection_add(item)
    
    def on_college_double_click(self, _):
        
        selected_items = self.college_table.selection()
        
        for item in selected_items:
            self.college_table.selection_remove(item)

    def on_course_double_click(self, _):
        
        selected_items = self.course_table.selection()
        
        for item in selected_items:
            self.course_table.selection_remove(item)

    def add_college(self):
        
        add_college_dialog = tk.Toplevel(self.window)
        add_college_dialog.title("Add New College")
        add_college_dialog.geometry("400x200")
        add_college_dialog.config(bg="#800000")
        
        add_college_dialog.transient(self.window)
        add_college_dialog.grab_set()
        
        tk.Label(add_college_dialog, text="College Code (e.g., CCS):", 
                bg="#800000", fg="white").pack(pady=5)
        college_code_entry = self.create_validated_entry(add_college_dialog, "code")
        college_code_entry.pack(pady=5)
        
        tk.Label(add_college_dialog, text="College Name (e.g., College of Computer Studies):", 
                bg="#800000", fg="white").pack(pady=5)
        college_name_entry = self.create_validated_entry(add_college_dialog, "text")
        college_name_entry.config(width=50)
        college_name_entry.pack(pady=5)
        
        def save_college():
            college_code = college_code_entry.get().strip().upper()
            college_name = college_name_entry.get().strip().title()
            
            if self.validate_college_input(college_code, college_name):
                new_college = f"{college_code} - {college_name}"
                self.college_courses[new_college] = []
                self.save_to_csv()
                self.refresh_tables()
                add_college_dialog.destroy()
        
        tk.Button(add_college_dialog, text="Save", bg="#7d6a69", fg="white", 
                 command=save_college).pack(pady=10)

    def delete_college(self):
        global all_students
        selected_college = self.college_table.selection()
        if not selected_college:
            messagebox.showwarning("No Selection", "Please select a college to delete.")
            return
        
        college_name = self.college_table.item(selected_college)['values'][0]
        confirm = messagebox.askyesno("Delete Confirmation", 
                                     f"Are you sure you want to delete {college_name} and all its courses?\n" 
                                     "This will also clear this college from all affected student records.")
        
        if confirm:
            
            updated_students = []
            for student in all_students:
                if student[6] == college_name:  
                    
                    updated_student = student[:6] + ("", "") + student[8:] if len(student) > 8 else student[:6] + ("", "")
                    updated_students.append(updated_student)
                else:
                    updated_students.append(student)
            
            
            all_students.clear()
            all_students.extend(updated_students)
            
            
            del self.college_courses[college_name]
            
            
            self.save_to_csv()
            save_to_csv()  
            
            
            self.refresh_tables()
            refresh_table()  

    def edit_college(self):
        selected_college = self.college_table.selection()
        if not selected_college:
            messagebox.showwarning("No Selection", "Please select a college to edit.")
            return
        
        old_college_full = self.college_table.item(selected_college)['values'][0]
        old_college_code, old_college_name = old_college_full.split(' - ')
        
        
        edit_college_dialog = tk.Toplevel(self.window)
        edit_college_dialog.title("Edit College")
        edit_college_dialog.geometry("400x200")
        edit_college_dialog.config(bg="#800000")
        
        edit_college_dialog.transient(self.window)
        edit_college_dialog.grab_set()
        
        tk.Label(edit_college_dialog, text="College Code:", 
                bg="#800000", fg="white").pack(pady=5)
        college_code_entry = self.create_validated_entry(edit_college_dialog, "code")
        college_code_entry.insert(0, old_college_code)
        college_code_entry.pack(pady=5)
        
        tk.Label(edit_college_dialog, text="College Name:", 
                bg="#800000", fg="white").pack(pady=5)
        college_name_entry = self.create_validated_entry(edit_college_dialog, "text")
        college_name_entry.insert(0, old_college_name)
        college_name_entry.config(width=50)
        college_name_entry.pack(pady=5)
        
        def save_changes():
            new_college_code = college_code_entry.get().strip().upper()
            new_college_name = college_name_entry.get().strip().title()
            
            if self.validate_college_input(new_college_code, new_college_name, 
                                         old_college_code, old_college_name):
                new_college_full = f"{new_college_code} - {new_college_name}"
                courses = self.college_courses.pop(old_college_full)
                self.college_courses[new_college_full] = courses
                self.save_to_csv()
                self.refresh_tables()
                edit_college_dialog.destroy()
        
        tk.Button(edit_college_dialog, text="Save Changes", bg="#7d6a69", fg="white", 
                 command=save_changes).pack(pady=10)

    def add_course(self):
        
        add_course_dialog = tk.Toplevel(self.window)
        add_course_dialog.title("Add New Course")
        add_course_dialog.geometry("600x250")
        add_course_dialog.config(bg="#800000")
        
        add_course_dialog.transient(self.window)
        add_course_dialog.grab_set()
        
        
        tk.Label(add_course_dialog, text="Select College:", 
                bg="#800000", fg="white").pack(pady=5)
        college_var = tk.StringVar()
        college_dropdown = ttk.Combobox(add_course_dialog, 
                                      textvariable=college_var,
                                      values=list(self.college_courses.keys()), 
                                      state='readonly')
        college_dropdown.pack(pady=5)
        
        
        tk.Label(add_course_dialog, text="Course Code (e.g., BSCS):", 
                bg="#800000", fg="white").pack(pady=5)
        course_code_entry = self.create_validated_entry(add_course_dialog, "code")
        course_code_entry.pack(pady=5)
        
        
        tk.Label(add_course_dialog, text="Course Name:", 
                bg="#800000", fg="white").pack(pady=5)
        course_name_entry = self.create_validated_entry(add_course_dialog, "text")
        course_name_entry.config(width=80)
        course_name_entry.pack(pady=5)
        
        def save_course():
            selected_college = college_var.get()
            course_code = course_code_entry.get().strip().upper()
            course_name = course_name_entry.get().strip().title()
            
            if self.validate_course_input(selected_college, course_code, course_name):
                new_course = f"{course_code} - {course_name}"
                self.college_courses[selected_college].append(new_course)
                self.save_to_csv()
                self.refresh_tables()
                add_course_dialog.destroy()
        
        tk.Button(add_course_dialog, text="Save", 
                 bg="#7d6a69", fg="white",
                 command=save_course).pack(pady=20)

    def delete_course(self):
        global all_students
        selected_course = self.course_table.selection()
        if not selected_course:
            messagebox.showwarning("No Selection", "Please select a course to delete.")
            return
        
        course_info = self.course_table.item(selected_course)['values']
        college, course_code, course_name = course_info
        full_course = f"{course_code} - {course_name}"
        
        confirm = messagebox.askyesno("Delete Confirmation", 
                                     f"Are you sure you want to delete {full_course}?\n"
                                     "This will also clear this course from all affected student records.")
        
        if confirm:
            
            updated_students = []
            for student in all_students:
                if student[6] == college and student[7].startswith(course_code):
                    
                    updated_student = student[:7] + ("",) + student[8:] if len(student) > 8 else student[:7] + ("",)
                    updated_students.append(updated_student)
                else:
                    updated_students.append(student)
            
            
            all_students.clear()
            all_students.extend(updated_students)
            
            
            self.college_courses[college].remove(full_course)
            
            
            self.save_to_csv()
            save_to_csv()  
            
            
            self.refresh_tables()
            refresh_table()  

    def edit_course(self):
        selected_course = self.course_table.selection()
        if not selected_course:
            messagebox.showwarning("No Selection", "Please select a course to edit.")
            return
        
        
        course_info = self.course_table.item(selected_course)['values']
        college, old_course_code, old_course_name = course_info
        old_full_course = f"{old_course_code} - {old_course_name}"
        
       
        edit_course_dialog = tk.Toplevel(self.window)
        edit_course_dialog.title(f"Edit Course in {college}")
        edit_course_dialog.geometry("600x200")
        edit_course_dialog.config(bg="#800000")
        
        edit_course_dialog.transient(self.window)
        edit_course_dialog.grab_set()
        
        tk.Label(edit_course_dialog, text="Course Code:", 
                bg="#800000", fg="white").pack(pady=5)
        course_code_entry = self.create_validated_entry(edit_course_dialog, "code")
        course_code_entry.insert(0, old_course_code)
        course_code_entry.pack(pady=5)
        
        tk.Label(edit_course_dialog, text="Course Name:", 
                bg="#800000", fg="white").pack(pady=5)
        course_name_entry = self.create_validated_entry(edit_course_dialog, "text")
        course_name_entry.insert(0, old_course_name)
        course_name_entry.config(width=80)
        course_name_entry.pack(pady=5)
        
        def save_changes():
            new_course_code = course_code_entry.get().strip().upper()
            new_course_name = course_name_entry.get().strip().title()
            
            if self.validate_course_input(college, new_course_code, new_course_name,
                                        old_course_code, old_course_name):
                new_full_course = f"{new_course_code} - {new_course_name}"
                index = self.college_courses[college].index(old_full_course)
                self.college_courses[college][index] = new_full_course
                self.save_to_csv()
                self.refresh_tables()
                edit_course_dialog.destroy()
                
        tk.Button(edit_course_dialog, text="Save Changes", 
                 bg="#7d6a69", fg="white",
                 command=save_changes).pack(pady=10)

    def check_college_duplicate(self, college_code, college_name, old_code=None, old_name=None):
        
        for existing in self.college_courses.keys():
            existing_code, existing_name = existing.split(' - ', 1)
            
            
            if old_code and old_name and existing_code == old_code and existing_name == old_name:
                continue
                
           
            if college_code.upper() == existing_code.upper():
                messagebox.showerror("Duplicate Error", 
                                    f"College code '{college_code}' already exists in the system.")
                return True
                
            
            if college_name.lower() == existing_name.lower():
                messagebox.showerror("Duplicate Error", 
                                    f"A college with name '{college_name}' already exists.")
                return True
        return False

    def check_course_duplicate(self, college, course_code, course_name, old_course=None):
        
        old_code = None
        old_name = None
        
        if old_course:
            old_parts = old_course.split(' - ', 1)
            if len(old_parts) == 2:
                old_code, old_name = old_parts
        
       
        for existing in self.college_courses[college]:
            existing_code, existing_name = existing.split(' - ', 1)
            
            
            if old_code and old_name and existing_code == old_code and existing_name == old_name:
                continue
                
           
            if course_code.upper() == existing_code.upper():
                messagebox.showerror("Duplicate Error", 
                                    f"Course code '{course_code}' already exists in {college}.")
                return True
                
            
            if course_name.lower() == existing_name.lower():
                messagebox.showerror("Duplicate Error", 
                                    f"A course with name '{course_name}' already exists in {college}.")
                return True
        
       
        for other_college, courses in self.college_courses.items():
            if other_college == college:
                continue  
                
            for existing in courses:
                existing_code, existing_name = existing.split(' - ', 1)
                
                
                if course_code.upper() == existing_code.upper():
                    messagebox.showerror("Duplicate Error", 
                                        f"Course code '{course_code}' already exists in {other_college}.")
                    return True
        
        return False

    def validate_code_format(self, code, type_name):
        
        if not code.isalpha():
            messagebox.showerror("Invalid Format", 
                                f"{type_name} code must contain only letters.")
            return False
        return True

    def validate_text_only(self, text, field_name):
        
        if any(char.isdigit() for char in text):
            messagebox.showerror("Invalid Input", 
                                f"{field_name} must not contain numbers.")
            return False
        return True

    def create_validated_entry(self, parent, validate_type="text"):
        
        entry = tk.Entry(parent)
        
        if validate_type == "text":
            
            def validate_text(char):
                return not char.isdigit()
                
            vcmd = (parent.register(validate_text), '%S')
            entry.config(validate="key", validatecommand=vcmd)
        
        elif validate_type == "code":
            
            def validate_code(char):
                return char.isalpha()
                
            vcmd = (parent.register(validate_code), '%S')
            entry.config(validate="key", validatecommand=vcmd)
            
        return entry

    def validate_college_input(self, college_code, college_name, old_code=None, old_name=None):
       
        
        if not college_code or not college_name:
            messagebox.showerror("Error", "All fields must be filled")
            return False
            
        
        college_code = college_code.upper()
        college_name = college_name.title()
        
        
        for existing in self.college_courses.keys():
            existing_code, existing_name = existing.split(' - ')
            
           
            if old_code and old_name:
                if existing_code == old_code and existing_name == old_name:
                    continue
                    
            
            if college_code == existing_code:
                messagebox.showerror("Duplicate Error", 
                                   f"College code '{college_code}' already exists")
                return False
                
            
            if college_name.lower() == existing_name.lower():
                messagebox.showerror("Duplicate Error",
                                   f"College name '{college_name}' already exists")
                return False
                
        return True

    def validate_course_input(self, college, course_code, course_name, old_code=None, old_name=None):
        
        
        if not course_code or not course_name:
            messagebox.showerror("Error", "All fields must be filled")
            return False
            
        
        course_code = course_code.upper()
        course_name = course_name.title()
        
        
        for existing in self.college_courses[college]:
            existing_code, existing_name = existing.split(' - ')
            
            
            if old_code and old_name:
                if existing_code == old_code and existing_name == old_name:
                    continue
                    
            
            if course_code == existing_code:
                messagebox.showerror("Duplicate Error",
                                   f"Course code '{course_code}' already exists in {college}")
                return False
                
            
            if course_name.lower() == existing_name.lower():
                messagebox.showerror("Duplicate Error",
                                   f"Course name '{course_name}' already exists in {college}")
                return False
        
        
        for other_college, courses in self.college_courses.items():
            if other_college != college:
                for course in courses:
                    existing_code, existing_name = course.split(' - ')
                    
                    
                    if course_code == existing_code:
                        messagebox.showerror("Duplicate Error",
                                           f"Course code '{course_code}' already exists in {other_college}")
                        return False
                    
                    
                    if course_name.lower() == existing_name.lower():
                        messagebox.showerror("Duplicate Error",
                                           f"Course name '{course_name}' already exists in {other_college}")
                        return False
                        
        return True

def is_duplicate_id(idno, current_item=None):
    if current_item:
        current_id = table.item(current_item)['values'][0]
        if idno == current_id:  
            return False
    
    for item in table.get_children():
        if current_item and item == current_item: 
            continue
        if table.item(item)['values'][0] == idno:  
            return True
    return False


def refresh_table():
    global current_page, total_pages
    table.delete(*table.get_children())
    
    filtered_students = get_filtered_students()
    total_pages = max(1, (len(filtered_students) + rows_per_page - 1) // rows_per_page)
    
    
    current_page = min(current_page, total_pages)
    
    
    start_idx = (current_page - 1) * rows_per_page
    end_idx = min(start_idx + rows_per_page, len(filtered_students))
    
    
    for student in filtered_students[start_idx:end_idx]:
        table.insert("", "end", values=student)
    
    
    total_students = len(filtered_students)
    page_info.config(text=f"Page {current_page} of {total_pages} | Total: {total_students} students")
    btn_first.config(state="normal" if current_page > 1 else "disabled")
    btn_prev.config(state="normal" if current_page > 1 else "disabled")
    btn_next.config(state="normal" if current_page < total_pages else "disabled")
    btn_last.config(state="normal" if current_page < total_pages else "disabled")
    
    if sort_options.get():
        sort_table()


def add_student():
    def save_student():
        global all_students
        student_idno = entry_idno.get()
        student_firstname = entry_firstname.get().upper()
        student_lastname = entry_lastname.get().upper()
        student_age = entry_age.get()
        student_gender = gender_var.get()
        student_yearlevel = yearlevel_var.get()
        selected_college = college_var.get()
        selected_course_abbr = course_var.get()

        
        if not all([student_firstname, student_lastname, student_age, student_gender, 
                   student_idno, student_yearlevel, selected_college, selected_course_abbr]):
            msg = messagebox.showwarning("Missing Input", "Please fill in all fields.", parent=new_window)
            return

        if is_duplicate_id(student_idno):
            messagebox.showwarning("Duplicate ID", "This ID number already exists.", parent=new_window)
            return

        if not re.match(r'^\d{4}-\d{4}$', student_idno):
            msg = messagebox.showwarning("Invalid ID#", "ID# must be in the format YYYY-NNNN.", parent=new_window)
            return
        
        
        full_course_name = next((course for course in college_courses[selected_college] 
                               if course.startswith(selected_course_abbr)), "")
        
        
        new_student = (student_idno, student_firstname, student_lastname, 
                      student_age, student_gender, student_yearlevel, 
                      selected_college, full_course_name)
        
        
        all_students.append(new_student)
        
        
        refresh_table()
        
        
        save_to_csv()
        new_window.destroy()

    
    def validate_char(char):
        return char.isalpha() or char == "" or char == " "

    def validate_int(char):
        return char.isdigit() or char == ""

    def validate_idno(char):
        return re.match(r'^\d{0,4}(-\d{0,4})?$', char) is not None
    
    def update_courses(*args):
        selected_college = college_var.get()
        course_options = college_courses.get(selected_college, [])
        course_dropdown['values'] = [course.split(' - ')[0] for course in course_options]  
        course_var.set('')  

    new_window = tk.Toplevel(window)
    new_window.geometry("400x300")
    new_window.title("Add New Student")
    new_window.config(bg="#800000")
    
    new_window.transient(window)
    new_window.grab_set()

    vcmd_char = new_window.register(validate_char)
    vcmd_int = new_window.register(validate_int)
    vcmd_idno = new_window.register(validate_idno)
    
    label_idno = tk.Label(new_window, text="ID#:", bg="#800000", fg="white")
    label_idno.grid(row=1, column=0)
    label_idno = tk.Label(new_window, text="(ex. YYYY-NNNN)", bg="#800000", fg="white")
    label_idno.grid(row=1, column=2, padx=(0, 20))
    entry_idno = tk.Entry(new_window, validate="key", validatecommand=(vcmd_idno, '%P'))
    entry_idno.grid(row=1, column=1)

    label_name = tk.Label(new_window, text="First Name:", bg="#800000", fg="white")
    label_name.grid(row=2, column=0)
    entry_firstname = tk.Entry(new_window, validate="key", validatecommand=(vcmd_char, '%S'))
    entry_firstname.grid(row=2, column=1)
    
    label_lastname = tk.Label(new_window, text="Last Name:", bg="#800000", fg="white")
    label_lastname.grid(row=3, column=0)
    entry_lastname = tk.Entry(new_window, validate="key", validatecommand=(vcmd_char, '%S'))
    entry_lastname.grid(row=3, column=1)
    
    label_age = tk.Label(new_window, text="Age:", bg="#800000", fg="white")
    label_age.grid(row=4, column=0)
    entry_age = tk.Entry(new_window, validate="key", validatecommand=(vcmd_int, '%S'))
    entry_age.grid(row=4, column=1)

    
    label_gender = tk.Label(new_window, text="Gender:", bg="#800000", fg="white")
    label_gender.grid(row=5, column=0)
    gender_var = tk.StringVar(new_window)
    gender_choices = ["Male", "Female", "Others"]
    gender_dropdown = ttk.Combobox(new_window, textvariable=gender_var, values=gender_choices, state='readonly')
    gender_dropdown.grid(row=5, column=1)

    
    label_yearlevel = tk.Label(new_window, text="Year Level:", bg="#800000", fg="white")
    label_yearlevel.grid(row=6, column=0)
    yearlevel_var = tk.StringVar(new_window)
    yearlevel_choices = ["1st", "2nd", "3rd", "4th", "5+"]
    yearlevel_dropdown = ttk.Combobox(new_window, textvariable=yearlevel_var, values=yearlevel_choices, state='readonly')
    yearlevel_dropdown.grid(row=6, column=1)

    
    label_college = tk.Label(new_window, text="College:", bg="#800000", fg="white")
    label_college.grid(row=7, column=0)
    college_var = tk.StringVar(new_window)
    college_dropdown = ttk.Combobox(new_window, textvariable=college_var, values=list(college_courses.keys()), state='readonly')
    college_dropdown.grid(row=7, column=1)
    college_dropdown.bind("<<ComboboxSelected>>", update_courses)

   
    label_course = tk.Label(new_window, text="Course:", bg="#800000", fg="white")
    label_course.grid(row=8, column=0)
    course_var = tk.StringVar(new_window)
    course_dropdown = ttk.Combobox(new_window, textvariable=course_var, values=[], state='readonly')
    course_dropdown.grid(row=8, column=1)

    button_save = tk.Button(new_window, text="Save", bg="#d9a300", command=save_student)
    button_save.grid(row=9, column=0, columnspan=2, pady=10)


def delete_student():
    global all_students
    selected_item = table.selection()
    if not selected_item:
        messagebox.showwarning("No Selection", "Please select a student to delete.")
        return

    confirm = messagebox.askyesno("Delete Confirmation", "Are you sure you want to delete this student?")
    if confirm:
        deleted_id = table.item(selected_item)['values'][0]
        
        
        all_students = [student for student in all_students if student[0] != deleted_id]
        
        save_to_csv()
        
        refresh_table()


def update_student():
    selected_item = table.selection()
    if not selected_item:
        messagebox.showwarning("No Selection", "Please select a student to update.")
        return
    
    current_values = table.item(selected_item)['values']
    
    def save_changes():
        global all_students
        student_idno = entry_idno.get()
        student_firstname = entry_firstname.get().upper()
        student_lastname = entry_lastname.get().upper()
        student_age = entry_age.get()
        student_gender = gender_var.get()
        student_yearlevel = yearlevel_var.get()
        selected_college = college_var.get()
        selected_course_abbr = course_var.get()

        if not all([student_firstname, student_lastname, student_age, student_gender, 
                   student_idno, student_yearlevel, selected_college, selected_course_abbr]):
            msg = messagebox.showwarning("Missing Input", "Please fill in all fields.", parent=update_window)
            return

        if is_duplicate_id(student_idno, selected_item):
            messagebox.showwarning("Duplicate ID", "This ID number already exists.", parent=update_window)
            return

        if not re.match(r'^\d{4}-\d{4}$', student_idno):
            msg = messagebox.showwarning("Invalid ID#", "ID# must be in the format YYYY-NNNN.", parent=update_window)
            return
        
        full_course_name = next((course for course in college_courses[selected_college] 
                               if course.startswith(selected_course_abbr)), "")
        
        
        updated_student = (student_idno, student_firstname, student_lastname, 
                          student_age, student_gender, student_yearlevel, 
                          selected_college, full_course_name)
        
        
        original_id = table.item(selected_item)['values'][0]
        
        
        for i, student in enumerate(all_students):
            if student[0] == original_id:  
                all_students[i] = updated_student
                break
        
       
        save_to_csv()
        
        refresh_table()
        
        update_window.destroy()

    
    def validate_char(current_value, inserted_char):
        return all(c.isalpha() or c.isspace() for c in current_value + inserted_char) or inserted_char == ""

    def validate_int(char):
        return char.isdigit() or char == ""

    def validate_idno(char):
        return re.match(r'^\d{0,4}(-\d{0,4})?$', char) is not None
    
    def update_courses(*args):
        selected_college = college_var.get()
        course_options = college_courses.get(selected_college, [])
        course_dropdown['values'] = [course.split(' - ')[0] for course in course_options]  
        if not course_var.get() or course_var.get() not in [c.split(' - ')[0] for c in course_options]:
            course_var.set('')  

    update_window = tk.Toplevel(window)
    update_window.geometry("400x300")
    update_window.title("Update Student")
    update_window.config(bg="#800000")
    
    update_window.transient(window)
    update_window.grab_set()
    
    vcmd_char = update_window.register(lambda current, inserted: validate_char(current, inserted))
    vcmd_int = update_window.register(validate_int)
    vcmd_idno = update_window.register(validate_idno)

    label_idno = tk.Label(update_window, text="ID#:", bg="#800000", fg="white")
    label_idno.grid(row=1, column=0)
    entry_idno = tk.Entry(update_window, validate="key", validatecommand=(vcmd_idno, '%P'))
    entry_idno.insert(0, current_values[0])
    entry_idno.grid(row=1, column=1)

    label_name = tk.Label(update_window, text="First Name:", bg="#800000", fg="white")
    label_name.grid(row=2, column=0)
    entry_firstname = tk.Entry(update_window, validate="key", validatecommand=(vcmd_char, '%P', '%S'))
    entry_firstname.insert(0, current_values[1])
    entry_firstname.grid(row=2, column=1)

    label_lastname = tk.Label(update_window, text="Last Name:", bg="#800000", fg="white")
    label_lastname.grid(row=3, column=0)
    entry_lastname = tk.Entry(update_window, validate="key", validatecommand=(vcmd_char, '%P', '%S'))
    entry_lastname.insert(0, current_values[2])
    entry_lastname.grid(row=3, column=1)

    label_age = tk.Label(update_window, text="Age:", bg="#800000", fg="white")
    label_age.grid(row=4, column=0)
    entry_age = tk.Entry(update_window, validate="key", validatecommand=(vcmd_int, '%S'))
    entry_age.insert(0, current_values[3])
    entry_age.grid(row=4, column=1)

    
    label_gender = tk.Label(update_window, text="Gender:", bg="#800000", fg="white")
    label_gender.grid(row=5, column=0)
    gender_var = tk.StringVar(update_window)
    gender_choices = ["Male", "Female", "Others"]
    gender_dropdown = ttk.Combobox(update_window, textvariable=gender_var, values=gender_choices, state='readonly')
    gender_dropdown.grid(row=5, column=1)
    gender_var.set(current_values[4]) 

   
    label_yearlevel = tk.Label(update_window, text="Year Level:", bg="#800000", fg="white")
    label_yearlevel.grid(row=6, column=0)
    yearlevel_var = tk.StringVar(update_window)
    yearlevel_choices = ["1st", "2nd", "3rd", "4th", "5+"]
    yearlevel_dropdown = ttk.Combobox(update_window, textvariable=yearlevel_var, values=yearlevel_choices, state='readonly')
    yearlevel_dropdown.grid(row=6, column=1)
    yearlevel_var.set(current_values[5])  

   
    label_college = tk.Label(update_window, text="College:", bg="#800000", fg="white")
    label_college.grid(row=7, column=0)
    college_var = tk.StringVar(update_window)
    college_dropdown = ttk.Combobox(update_window, textvariable=college_var, values=list(college_courses.keys()), state='readonly')
    college_dropdown.grid(row=7, column=1)
    college_dropdown.bind("<<ComboboxSelected>>", update_courses)
  
    college_var.set(current_values[6])


    label_course = tk.Label(update_window, text="Course:", bg="#800000", fg="white")
    label_course.grid(row=8, column=0)
    course_var = tk.StringVar(update_window)
    course_dropdown = ttk.Combobox(update_window, textvariable=course_var, values=[], state='readonly')
    course_dropdown.grid(row=8, column=1)

    update_courses()
    
    
    full_course = current_values[7]
    course_abbr = full_course.split(' - ')[0] if ' - ' in full_course else full_course
    course_var.set(course_abbr)

    button_save = tk.Button(update_window, text="Save Changes", bg="#d9a300", command=save_changes)
    button_save.grid(row=9, column=0, columnspan=2, pady=10)


def sort_table():
    sort_by = sort_options.get()
    if not sort_by:
        return
    
    global all_students, current_page
    
    if sort_by == "Original Order":
        
        try:
            with open(CSV_FILE, 'r') as csvfile:
                reader = csv.reader(csvfile)
                next(reader)  
                original_students = []
                for row in reader:
                    if not row or row[0] == "Colleges and Courses":
                        break
                    if len(row) == len(columns):
                        original_students.append(tuple(row))
                all_students = original_students
        except Exception as e:
            print(f"Error restoring original order: {e}")
    else:
        col_index = columns.index(sort_by)
        if sort_by == "Age":
            all_students = sorted(all_students, 
                key=lambda x: int(x[col_index]) if x[col_index].isdigit() else x[col_index])
        else:
            all_students = sorted(all_students, 
                key=lambda x: str(x[col_index]))
    
    
    display_current_page()


def display_current_page():
    global current_page, total_pages
    
    
    table.delete(*table.get_children())
    
    
    filtered_students = get_filtered_students()
    total_pages = max(1, (len(filtered_students) + rows_per_page - 1) // rows_per_page)
    current_page = min(current_page, total_pages)
    
    
    start_idx = (current_page - 1) * rows_per_page
    end_idx = min(start_idx + rows_per_page, len(filtered_students))
    
    
    for student in filtered_students[start_idx:end_idx]:
        table.insert("", "end", values=student)
    
    
    page_info.config(text=f"Page {current_page} of {total_pages} | Total: {len(filtered_students)} students")
    
    
    btn_first.config(state="normal" if current_page > 1 else "disabled")
    btn_prev.config(state="normal" if current_page > 1 else "disabled")
    btn_next.config(state="normal" if current_page < total_pages else "disabled")
    btn_last.config(state="normal" if current_page < total_pages else "disabled")


def clear_table():
    global all_students
    confirm = messagebox.askyesno("Clear Data Confirmation", "Are you sure you want to clear all data?")
    if confirm:
        
        all_students = []
        
        
        for item in table.get_children():
            table.delete(item)
        
        
        try:
            with open(CSV_FILE, 'w', newline='') as csvfile:
                writer = csv.writer(csvfile)
                writer.writerow(columns)  
        except Exception as e:
            messagebox.showerror("Error", f"Failed to clear data: {str(e)}")
        
        entry_search.delete(0, 'end')


all_students = []

current_page = 1
rows_per_page = 20
total_pages = 1

def calculate_total_pages():
    global total_pages
    filtered_students = get_filtered_students()
    total_pages = max(1, (len(filtered_students) + rows_per_page - 1) // rows_per_page)
    return total_pages

def get_filtered_students():
    search_text = entry_search.get().strip().lower()
    if not search_text:
        return all_students
    
    filtered = []
    for student in all_students:
        
        if search_text in ["male", "female", "others"]:
            if student[4].lower() == search_text:
                filtered.append(student)
       
        elif any(search_text in str(val).lower() for val in student):
            filtered.append(student)
            
    return filtered

def go_to_page(page_num):
    global current_page
    if 1 <= page_num <= total_pages:
        current_page = page_num
        refresh_table()

def search_student(event=None):
    global current_page
    current_page = 1  
    refresh_table()  


def save_to_csv():
    try:
        with open(CSV_FILE, 'w', newline='') as csvfile:
            writer = csv.writer(csvfile)
            writer.writerow(columns)  
            writer.writerows(all_students)  
    except Exception as e:
        messagebox.showerror("Error", f"Failed to save data: {str(e)}")


def load_initial_data():
    global all_students
    all_students = []
    
    if not os.path.exists(CSV_FILE):
        with open(CSV_FILE, 'w', newline='') as csvfile:
            writer = csv.writer(csvfile)
            writer.writerow(columns)
        return
    
    try:
        with open(CSV_FILE, 'r') as csvfile:
            reader = csv.reader(csvfile)
            header = next(reader)
            
            for row in reader:
                if not row:
                    continue
                if row[0] == "Colleges and Courses":
                    break
                if len(row) == len(columns):
                    all_students.append(tuple(row))
        
        refresh_table()
        
    except Exception as e:
        print(f"Load error: {e}")
        messagebox.showerror("Load Error", f"Failed to load data: {str(e)}")

def validate_idno(char):
    return re.match(r'^\d{0,4}(-\d{0,4})?$', char) is not None

vcmd_idno_main = window.register(validate_idno)

icon = tk.PhotoImage(file=os.path.join(os.path.dirname(__file__), 'student.png'))
window.iconphoto(True, icon)
window.config(bg="#800000")


control_frame = tk.Frame(window, bg="#800000")
control_frame.grid(row=0, column=0, padx=10, pady=10, sticky="n")

button_add = tk.Button(control_frame, text="Add Student", bg="#7d6a69", fg="white", command=add_student)
button_add.grid(row=0, column=0, pady=5)

button_delete = tk.Button(control_frame, text="Delete Student", bg="#7d6a69", fg="white", command=delete_student)
button_delete.grid(row=1, column=0, pady=5)

button_update = tk.Button(control_frame, text="Update Student", bg="#7d6a69", fg="white", command=update_student)
button_update.grid(row=2, column=0, pady=5)

columns = ("ID#","First Name", "Last Name", "Age", "Gender", "Year Level", "College", "Course")

label_search = tk.Label(control_frame, text="Search:", bg="#800000", fg="white")
label_search.grid(row=3, column=0, pady=5)
entry_search = tk.Entry(control_frame)
entry_search.bind("<KeyRelease>", search_student)
entry_search.grid(row=4, column=0, pady=5)

label_sort = tk.Label(control_frame, text="Sort By:",bg="#800000", fg="white")
label_sort.grid(row=5, column=0, pady=5)
sort_options = ttk.Combobox(control_frame, 
                           values=("Original Order", "First Name", "Last Name", "Age", 
                                 "Gender", "ID#", "Year Level", "College", "Course"), 
                           state="readonly")
sort_options.grid(row=6, column=0, pady=5)
button_sort = tk.Button(control_frame, text="Sort", bg="#7d6a69", fg="white", command=sort_table)
button_sort.grid(row=7, column=0, pady=5)

button_clear = tk.Button(control_frame, text="Clear Data", bg="#7d6a69", fg="white", command=clear_table)
button_clear.grid(row=8, column=0, pady=50)

button_manage_colleges = tk.Button(control_frame, text="Manage Colleges and Courses", 
                                 bg="#7d6a69", fg="white", 
                                 command=lambda: CollegeCourseManager(window, college_courses, 
                                                                    CSV_FILE))
button_manage_colleges.grid(row=9, column=0, pady=5)


table_frame = tk.Frame(window)
table_frame.grid(row=0, column=1, padx=10, pady=10, sticky="nsew")


window.grid_columnconfigure(1, weight=1)
window.grid_rowconfigure(0, weight=1)


columns = ("ID#","First Name", "Last Name", "Age", "Gender", "Year Level", "College", "Course")
table = ttk.Treeview(table_frame, columns=columns, show="headings")
table.heading("ID#", text="ID#")
table.heading("First Name", text="First Name")
table.heading("Last Name", text="Last Name")
table.heading("Age", text="Age")
table.heading("Gender", text="Gender")
table.heading("Year Level", text="Year Level")
table.heading("College", text="College")
table.heading("Course", text="Course")


for col in columns:
    table.column(col, width=100, stretch=True)


table.grid(row=0, column=0, sticky="nsew")

pagination_frame = tk.Frame(table_frame, bg="#800000")
pagination_frame.grid(row=1, column=0, sticky="ew", pady=5)

btn_first = tk.Button(pagination_frame, text="<<", command=lambda: go_to_page(1),
                     bg="#7d6a69", fg="white")
btn_first.pack(side=tk.LEFT, padx=5)

btn_prev = tk.Button(pagination_frame, text="<", command=lambda: go_to_page(current_page - 1),
                    bg="#7d6a69", fg="white")
btn_prev.pack(side=tk.LEFT, padx=5)

page_info = tk.Label(pagination_frame, text="Page 1 of 1", bg="#800000", fg="white")
page_info.pack(side=tk.LEFT, padx=10)

btn_next = tk.Button(pagination_frame, text=">", command=lambda: go_to_page(current_page + 1),
                    bg="#7d6a69", fg="white")
btn_next.pack(side=tk.LEFT, padx=5)

btn_last = tk.Button(pagination_frame, text=">>", command=lambda: go_to_page(total_pages),
                    bg="#7d6a69", fg="white")
btn_last.pack(side=tk.LEFT, padx=5)

table_frame.grid_columnconfigure(0, weight=1)
table_frame.grid_rowconfigure(0, weight=1)

load_initial_data()

def clear_selection(event):
    for item in table.selection():
        table.selection_remove(item)

table.bind("<Double-1>", clear_selection)

def adjust_rows_per_page(event=None):
    global rows_per_page, current_page
    
    
    table_height = table_frame.winfo_height()
    row_height = 25  
    header_height = 25  
    pagination_height = 35  
    
    
    available_height = table_height - header_height - pagination_height
    new_rows_per_page = max(1, available_height // row_height)
    
    
    if new_rows_per_page != rows_per_page:
        rows_per_page = new_rows_per_page
        refresh_table()

window.bind("<Configure>", adjust_rows_per_page)

window.mainloop()