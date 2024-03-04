#!/usr/bin/env python
# coding: utf-8

# In[ ]:


import json
import sys
import os
import tkinter as tk
from tkinter import ttk, messagebox, simpledialog, Toplevel, LEFT
from datetime import datetime

class EisenhowerMatrixGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Eisenhower Matrix")
        self.root.geometry("1400x380")
        self.task_details = {}

        # Set the theme using ttk.Style
        style = ttk.Style()
        style.theme_use('clam')  # Set the theme

        # Setup left and right frames
        left_frame = ttk.Frame(root)
        left_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        right_frame = ttk.Frame(root)
        right_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)

        self.init_right_click_menu()  # Initialize the right-click menu

        # Quadrants setup
        self.quadrants = ["Important & Urgent", "Important & Not Urgent",
                          "Not Important & Urgent", "Not Important & Not Urgent"]
        self.trees = {}
        for i, quadrant in enumerate(self.quadrants):
            frame = ttk.LabelFrame(left_frame, text=quadrant, labelanchor='n')
            frame.grid(row=i//2, column=i%2, padx=5, pady=5, sticky='nsew')
            tree = ttk.Treeview(frame, columns=("Task", "Date Created"), show='headings', height=5, selectmode='extended')
            tree.heading('Task', text='Task')  # Set heading for task column
            tree.heading('Date Created', text='Date Created')  # Set heading for date column
            tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
            scrollbar = ttk.Scrollbar(frame, orient="vertical", command=tree.yview)
            scrollbar.pack(side=tk.RIGHT, fill="y")
            tree.configure(yscrollcommand=scrollbar.set)
            tree.bind("<Button-3>", self.on_task_right_click)  # Bind right-click event
            tree.bind("<Double-1>", self.on_task_click)
            self.trees[quadrant] = tree

        # "Add Task" button setup
        button_frame = ttk.Frame(left_frame)
        button_frame.grid(row=2, column=0, columnspan=2, pady=10)
        add_button = ttk.Button(button_frame, text="Add Task", command=self.add_task)
        add_button.pack(side=tk.LEFT, padx=10)

        # Completed Tasks setup
        completed_label = ttk.Label(right_frame, text="Completed Tasks", font=('Arial', 14, 'bold'))
        completed_label.pack(pady=(0, 5))
        self.completed_tree = ttk.Treeview(right_frame, columns=("Task", "Completion Date"), show='headings', height=8)
        self.completed_tree.heading('Task', text='Task')  # Set heading for task column in completed tasks
        self.completed_tree.heading('Completion Date', text='Completion Date')
        self.completed_tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        completed_scrollbar = ttk.Scrollbar(right_frame, orient="vertical", command=self.completed_tree.yview)
        completed_scrollbar.pack(side=tk.RIGHT, fill="y")
        self.completed_tree.configure(yscrollcommand=completed_scrollbar.set)
        self.completed_tree.bind("<Button-3>", self.on_completed_task_right_click)
        self.completed_tree.bind("<Double-1>", self.on_task_click)
        self.load_tasks_from_file()
        
        for quadrant, tree in self.trees.items():
            tree.bind("<Double-1>", self.on_task_click)
    
    def on_completed_task_right_click(self, event):
        try:
            # Identify the item where the right-click occurred
            self.completed_tree.identify_row(event.y)
            item_id = self.completed_tree.focus()
            if item_id:
                self.selected_completed_item = item_id
                self.completed_tasks_right_click_menu.tk_popup(event.x_root, event.y_root)
        finally:
            self.completed_tasks_right_click_menu.grab_release()
    
    def delete_completed_task(self):
        if self.selected_completed_item:
            self.completed_tree.delete(self.selected_completed_item)
            self.save_tasks_to_file()  # Save changes
            self.selected_completed_item = None  # Reset selection
    
    def save_tasks_to_file(self):
        tasks_data = {}
        for quadrant, tree in self.trees.items():
            tasks_data[quadrant] = []
            for item in tree.get_children():
                task, date = tree.item(item, 'values')
                tasks_data[quadrant].append({'task': task, 'date': date})

        # Add completed tasks
        tasks_data["Completed Tasks"] = []
        for item in self.completed_tree.get_children():
            task, date = self.completed_tree.item(item, 'values')
            tasks_data["Completed Tasks"].append({'task': task, 'date': date})

        file_path = os.path.join(os.path.expanduser('~'), r'C:\Users\bioen\Python\Task organization project data\tasks_data.json')
        with open(r'C:\Users\bioen\Python\Task organization project data\tasks_data.json', 'w') as outfile:
            json.dump(tasks_data, outfile, indent=4)
    
    def load_tasks_from_file(self):
       
        file_path = os.path.join(os.path.expanduser('~'), r'C:\Users\bioen\Python\Task organization project data\tasks_data.json')
        try:
            with open(r'C:\Users\bioen\Python\Task organization project data\tasks_data.json', 'r') as infile:
                tasks_data = json.load(infile)

            for quadrant, tasks in tasks_data.items():
                if quadrant != "Completed Tasks":
                    tree = self.trees[quadrant]
                    for task_info in tasks:
                        tree.insert('', 'end', values=(task_info['task'], task_info['date']), tags=('incomplete',))
                else:
                    for task_info in tasks:
                        self.completed_tree.insert('', 'end', values=(task_info['task'], task_info['date']))

        except FileNotFoundError:
            print("No previous tasks data found. Starting fresh.")
    
    def init_right_click_menu(self):
        # Menu for quadrants
        self.quadrant_right_click_menu = tk.Menu(self.root, tearoff=0)
        mark_as_menu = tk.Menu(self.quadrant_right_click_menu, tearoff=0)
        mark_as_menu.add_command(label="Pending", command=lambda: self.mark_task_status("Pending"))
        mark_as_menu.add_command(label="In Progress", command=lambda: self.mark_task_status("In Progress"))
        mark_as_menu.add_command(label="Completed", command=self.mark_task_completed)
        self.quadrant_right_click_menu.add_cascade(label="Mark as", menu=mark_as_menu)
        self.quadrant_right_click_menu.add_command(label="Delete Task", command=self.delete_task)

        # Menu for completed tasks
        self.completed_tasks_right_click_menu = tk.Menu(self.root, tearoff=0)
        self.completed_tasks_right_click_menu.add_command(label="Delete Task", command=self.delete_completed_task)
    
    def on_task_right_click(self, event):
        tree = event.widget
        region = tree.identify_region(event.x, event.y)
        if region == "cell" or region == "tree":
            item_id = tree.identify_row(event.y)
            if item_id:
                if item_id not in tree.selection():
                    tree.selection_set(item_id)  # Select the item under cursor if not already selected
                self.selected_tree = tree
                # Show context menu near the cursor
                self.quadrant_right_click_menu.tk_popup(event.x_root, event.y_root)
    
    def mark_task_status(self, status):
        selected_items = self.selected_tree.selection()  # Get all selected items
        for item_id in selected_items:
            task, date = self.selected_tree.item(item_id, 'values')
            # Strip any existing status symbol from the task name
            if task.startswith(("○ ", "⏳ ", "✔ ")):
                task_name = task[2:]  # Remove the first two characters (symbol and space)
            else:
                task_name = task

            if status == "Pending":
                updated_task = f"○ {task_name}"  # Update to Pending
            elif status == "In Progress":
                updated_task = f"⏳ {task_name}"  # Update to In Progress
            else:
                # If status is unrecognized or "Completed", do not update the task here
                continue

            # Update the task in its current Treeview to reflect the new status
            self.selected_tree.item(item_id, values=(updated_task, date))

        self.save_tasks_to_file()

    def mark_task_completed(self):
        selected_items = self.selected_tree.selection()  # Get all selected items
        for item_id in selected_items:
            task, date = self.selected_tree.item(item_id, 'values')
            task_name = task[2:] if task.startswith(('○', '⏳')) else task
            completed_task = f"✔ {task_name}"
            completion_date = datetime.now().strftime("%d-%m-%Y")
            self.completed_tree.insert('', 'end', values=(completed_task, completion_date))
            self.selected_tree.delete(item_id)
        self.save_tasks_to_file()

    def delete_task(self):
        selected_items = self.selected_tree.selection()  # Get all selected items
        for item_id in selected_items:
            self.selected_tree.delete(item_id)
        self.save_tasks_to_file()  # Save changes to file

    def add_task(self):
        task_name = simpledialog.askstring("Input", "What task do you want to add?")
        if task_name:
            description = simpledialog.askstring("Description", "Enter a description for the task:")
            current_date = datetime.now().strftime("%d-%m-%Y")
            task_with_status = f"○ {task_name}"  # Prefix with circle for incomplete tasks
            quadrant_key = self.ask_quadrant_questions(task_name)
            item_id = self.trees[quadrant_key].insert('', 'end', values=(task_with_status, current_date), tags=('incomplete',))
            # Store description and initialize updates list for the new task
            self.task_details[item_id] = {'description': description, 'updates': []}
            self.save_tasks_to_file()
    
    def on_task_click(self, event):
        tree = event.widget
        item_id = tree.focus()
        if item_id and item_id in self.task_details:
            # Correctly calling show_task_details with both item_id and tree
            self.show_task_details(item_id, tree)
    
    def show_task_details(self, item_id, tree):
        if item_id not in self.task_details:
            messagebox.showinfo("Error", "Task details not found.")
            return

        task_info = self.task_details[item_id]
        description = task_info.get('description', 'No description provided.')
        updates = task_info.get('updates', [])

        detail_win = Toplevel(self.root)
        detail_win.title("Task Details and Updates")

        # Align text to left
        ttk.Label(detail_win, text="Description:", anchor="w").pack(fill='x')
        ttk.Label(detail_win, text=description, anchor="w").pack(fill='x')

        if updates:
            ttk.Label(detail_win, text="Updates:", anchor="w").pack(fill='x')
            for update in updates:
                update_text, update_date = update.get('text', ''), update.get('date', '')
                ttk.Label(detail_win, text=f"{update_date}: {update_text}", anchor="w").pack(fill='x')

        ttk.Label(detail_win, text="Add Update:", anchor="w").pack(fill='x')
        update_entry = ttk.Entry(detail_win)
        update_entry.pack(fill='x')

        def save_update():
            new_update = update_entry.get().strip()
            if new_update:
                # Include the date with each update
                update_with_date = {
                    'text': new_update,
                    'date': datetime.now().strftime("%Y-%m-%d")
                }
                self.task_details[item_id]['updates'].append(update_with_date)
                self.save_tasks_to_file()
                detail_win.destroy()

        # Button to save the update
        ttk.Button(detail_win, text="Save Update", command=save_update).pack()
    
    def ask_quadrant_questions(self, task):
        urgent = messagebox.askyesno("Question", "Is the task urgent?")
        important = messagebox.askyesno("Question", "Is the task important?")
        if important and urgent:
            return "Important & Urgent"
        elif important:
            return "Important & Not Urgent"
        elif urgent:
            return "Not Important & Urgent"
        else:
            return "Not Important & Not Urgent"


if __name__ == "__main__":
    log_file_path = r'C:\Users\bioen\Python\Task organization project data\your_log_file.log'
    with open(log_file_path, "a") as log_file:
        # Redirect standard output and standard error to the log file
        sys.stdout = log_file
        sys.stderr = log_file

        root = tk.Tk()
        app = EisenhowerMatrixGUI(root)
        root.mainloop()


# In[ ]:




