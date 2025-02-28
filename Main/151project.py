import tkinter as tk
from tkinter import ttk
from tkinter import messagebox
import os
import re
import csv

CSV_FILE = os.path.join(os.path.dirname(__file__), 'student_data.csv')

window = tk.Tk()
window.geometry("1250x500")
window.title("Student Data")


college_courses = {
    "COE - College of Engineering": [
        "DCET - Diploma in Chemical Engineering Technology",
        "BSCerE - Bachelor of Science in Ceramic Engineering",
        "BSCE - Bachelor of Science in Civil Engineering",
        "BSEE - Bachelor of Science in Electrical Engineering",
        "BSME - Bachelor of Science in Mechanical Engineering",
        "BSChE - Bachelor of Science in Chemical Engineering",
        "BSMetE - Bachelor of Science in Metallurgical Engineering",
        "BSCpE - Bachelor of Science in Computer Engineering",
        "BSMinE - Bachelor of Science in Mining Engineering",
        "BSECE - Bachelor of Science in Electronics & Communications Engineering",
        "BSEnET - Bachelor of Science in Environmental Engineering"
    ],
    "CSM - College of Science and Mathematics": [
        "BSBio-Bot - Bachelor of Science in Biology (Botany)",
        "BSChem - Bachelor of Science in Chemistry",
        "BSMath - Bachelor of Science in Mathematics",
        "BSPhys - Bachelor of Science in Physics",
        "BSBio-Zoo - Bachelor of Science in Biology (Zoology)",
        "BSBio-Mar - Bachelor of Science in Biology (Marine)",
        "BSBio-Gen - Bachelor of Science in Biology (General)",
        "BSStat - Bachelor of Science in Statistics"
    ],
    "CCS - College of Computer Studies": [
        "BSCS - Bachelor of Science in Computer Science",
        "BSIT - Bachelor of Science in Information Technology",
        "BSIS - Bachelor of Science in Information Systems",
        "BSCA - Bachelor of Science in Computer Application"
    ],
    "CED - College of Education": [
        "BEEd-SciMath - Bachelor of Elementary Education (Science and Mathematics)",
        "BEEd-Lang - Bachelor of Elementary Education (Language Education)",
        "BSEd-Bio - Bachelor of Secondary Education (Biology)",
        "BSEd-Chem - Bachelor of Secondary Education (Chemistry)",
        "BSEd-Phys - Bachelor of Secondary Education (Physics)",
        "BSEd-Math - Bachelor of Secondary Education (Mathematics)",
        "BPEd - Bachelor of Physical Education",
        "BTLED-HE - Bachelor of Technology and Livelihood Education (Home Economics)",
        "BTLed-IA - Bachelor of Technology and Livelihood Education (Industrial Arts)",
        "BTVTED-DT - Bachelor of Technical-Vocational Teacher Education (Drafting Technology)"
    ],
    "CASS - College of Arts and Social Sciences": [
        "BA-ELS - Bachelor of Arts in English Language Studies",
        "BA-LCS - Bachelor of Arts in Literary and Cultural Studies",
        "BA-FIL - Bachelor of Arts in Filipino",
        "BA-PAN - Bachelor of Arts in Panitikan",
        "BA-POLSCI - Bachelor of Arts in Political Science",
        "BA-PSY - Bachelor of Arts in Psychology",
        "BA-SOC - Bachelor of Arts in Sociology",
        "BA-HIS-IH - Bachelor of Arts in History (International History Track)",
        "BS-PHIL-AE - Bachelor of Science in Philosophy",
        "BS-PSY - Bachelor of Science in Psychology"
    ],
    "CEBA - College of Economics, Business & Accountancy": [
        "BS-ACC - Bachelor of Science in Accountancy",
        "BSBA-BE - Bachelor of Science in Business Administration (Business Economics)",
        "BSBA-MM - Bachelor of Science in Business Administration (Marketing Management)",
        "BS-ENT - Bachelor of Science in Entrepreneurship",
        "BSHM - Bachelor of Science in Hospitality Management"
    ],
    "CHS - College of Health Sciences": [
        "BSN - Bachelor of Science in Nursing"
    ]
}

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


def add_student():
    def save_student():
        global count
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
        
        table.insert("", "end", values=(student_idno, student_firstname, student_lastname, 
                                        student_age, student_gender, student_yearlevel, 
                                        selected_college, full_course_name))

        all_students.append((student_idno, student_firstname, student_lastname, 
                           student_age, student_gender, student_yearlevel, 
                           selected_college, full_course_name))
        save_to_csv()
        new_window.destroy()
        search_student()

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

    vcmd_char = new_window.register(validate_char)
    vcmd_int = new_window.register(validate_int)
    vcmd_idno = new_window.register(validate_idno)
    
    label_idno = tk.Label(new_window, text="ID#:", bg="#800000", fg="white")
    label_idno.grid(row=1, column=0)
    label_idno = tk.Label(new_window, text="(e.g., YYYY-NNNN)", bg="#800000", fg="white")
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
        deleted_values = table.item(selected_item)['values']

        table.delete(selected_item)
        
        all_students = [student for student in all_students if student != deleted_values]
        
        
        data = []
        if entry_search.get().strip():  
            data = all_students  
        else:
            data = [table.item(item)['values'] for item in table.get_children()]
            
        try:
            with open(CSV_FILE, 'w', newline='') as csvfile:
                writer = csv.writer(csvfile)
                writer.writerow(columns)
                writer.writerows(data)
        except Exception as e:
            messagebox.showerror("Error", f"Failed to save data: {str(e)}")

def update_student():
    selected_item = table.selection()
    if not selected_item:
        messagebox.showwarning("No Selection", "Please select a student to update.")
        return
    
    current_values = table.item(selected_item)['values']
    
    def save_changes():
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
        
        table.item(selected_item, values=(student_idno, student_firstname, student_lastname, 
                                          student_age, student_gender, student_yearlevel, 
                                          selected_college, full_course_name))
        
     
        global all_students
        for i, student in enumerate(all_students):
            if student[0] == current_values[0]:  
                all_students[i] = (student_idno, student_firstname, student_lastname,
                                 student_age, student_gender, student_yearlevel,
                                 selected_college, full_course_name)
                break
                
        save_to_csv()
        update_window.destroy()
       
        search_student()

    def validate_char(current_value, inserted_char):
        return all(c.isalpha() or c.isspace() for c in current_value + inserted_char)

    def validate_int(char):
        return char.isdigit() or char == ""

    def validate_idno(char):
        return re.match(r'^\d{0,4}(-\d{0,4})?$', char) is not None
    
    def update_courses(*args):
        selected_college = college_var.get()
        course_options = college_courses.get(selected_college, [])
        course_dropdown['values'] = [course.split(' - ')[0] for course in course_options]  
        course_var.set('')  

    update_window = tk.Toplevel(window)
    update_window.geometry("400x300")
    update_window.title("Update Student")
    update_window.config(bg="#800000")
    
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
    course_var.set(current_values[7])

    button_save = tk.Button(update_window, text="Save Changes", bg="#d9a300", command=save_changes)
    button_save.grid(row=9, column=0, columnspan=2, pady=10)

def sort_table():
    sort_by = sort_options.get()
    if not sort_by:
        messagebox.showwarning("No Selection", "Please select a column to sort by.")
        return

    col_index = columns.index(sort_by)
    data = [(table.set(child, col_index), child) for child in table.get_children('')]
    data.sort(reverse=False)

    for index, (_, child) in enumerate(data):
        table.move(child, '', index)

def clear_table():
    global all_students
    confirm = messagebox.askyesno("Clear Data Confirmation", "Are you sure you want to clear all data?")
    if confirm:
        for item in table.get_children():
            table.delete(item)

        all_students = []
        
        try:
            with open(CSV_FILE, 'w', newline='') as csvfile:
                writer = csv.writer(csvfile)
                writer.writerow(columns)  
        except Exception as e:
            messagebox.showerror("Error", f"Failed to clear data: {str(e)}")
        
        entry_search.delete(0, 'end')

all_students = []

def search_student(event=None):
    global all_students
    search_text = entry_search.get().strip().lower()

    
    if not all_students:
        all_students = [table.item(item)['values'] for item in table.get_children()]

   
    table.delete(*table.get_children())

    
    students_to_show = all_students
    if search_text:
        students_to_show = [
            student for student in all_students 
            if any(str(field).lower().startswith(search_text) for field in student)
        ]

   
    for student in students_to_show:
        table.insert("", "end", values=student)

def save_to_csv():
    data = []
    for item in table.get_children():
        data.append(table.item(item)['values'])
    
    try:
        with open(CSV_FILE, 'w', newline='') as csvfile:
            writer = csv.writer(csvfile)
            writer.writerow(columns) 
            writer.writerows(data)    
    except Exception as e:
        messagebox.showerror("Error", f"Failed to save data: {str(e)}")

def load_initial_data():
    if os.path.exists(CSV_FILE):
        try:
            with open(CSV_FILE, 'r') as csvfile:
                reader = csv.reader(csvfile)
                next(reader)  
                for row in reader:
                    table.insert("", "end", values=row)
        except Exception as e:
            messagebox.showerror("Error", f"Failed to load data: {str(e)}")

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
sort_options = ttk.Combobox(control_frame, values=("First Name","Last Name","Age", "Gender","ID#", "Year Level", "College", "Course"), state="readonly")
sort_options.grid(row=6, column=0, pady=5)
button_sort = tk.Button(control_frame, text="Sort", bg="#7d6a69", fg="white", command=sort_table)
button_sort.grid(row=7, column=0, pady=5)

button_clear = tk.Button(control_frame, text="Clear Data", bg="#7d6a69", fg="white", command=clear_table)
button_clear.grid(row=8, column=0, pady=50)


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


scrollbar = ttk.Scrollbar(table_frame, orient="vertical", command=table.yview)
table.configure(yscrollcommand=scrollbar.set)
scrollbar.grid(row=0, column=1, sticky="ns")


table.grid(row=0, column=0, sticky="nsew")


table_frame.grid_columnconfigure(0, weight=1)
table_frame.grid_rowconfigure(0, weight=1)

load_initial_data()

def clear_selection(event):
    for item in table.selection():
        table.selection_remove(item)

table.bind("<Double-1>", clear_selection)

window.mainloop()