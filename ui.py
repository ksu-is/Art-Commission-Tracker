import tkinter as tk
from tkinter import ttk, messagebox
import database
import datetime

STATUS_OPTIONS = ["Not Started", "In Progress", "Completed"]
TYPE_OPTIONS = ["Portrait", "Full Body", "Chibi", "Icon", "Other"]

def create_main_menu(self):
        for widget in self.root.winfo_children():
            widget.destroy()

        title = tk.Label(self.root, text="Art Commission Tracker", font=("Arial", 24))
        title.pack(pady=20)

        btn_frame = tk.Frame(self.root)
        btn_frame.pack(pady=10)

        btn_add = tk.Button(btn_frame, text="Add New Commission", width=20, command=self.open_add_form)
        btn_add.grid(row=0, column=0, padx=10, pady=10)

        btn_view = tk.Button(btn_frame, text="View All Commissions", width=20, command=self.open_view_page)
        btn_view.grid(row=0, column=1, padx=10, pady=10)

        btn_summary = tk.Button(btn_frame, text="Summary Report", width=20, command=self.open_summary)
        btn_summary.grid(row=0, column=2, padx=10, pady=10)

        btn_export = tk.Button(self.root, text="Export CSV", width=20, command=self.export_csv)
        btn_export.pack(pady=10)

        btn_exit = tk.Button(self.root, text="Exit", width=10, command=self.root.destroy)
        btn_exit.pack(pady=20)    