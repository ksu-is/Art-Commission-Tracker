import tkinter as tk
from tkinter import ttk, messagebox
import customtkinter as ctk
import database
import datetime
from matplotlib.figure import Figure
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

STATUS_OPTIONS = ["Not Started", "In Progress", "Completed"]
TYPE_OPTIONS = ["Portrait", "Half Body", "Full Body", "Chibi", "Emote", "Environment", "Other"]

CREME = "#F5EFE6"
CREME_2 = "#EDE3D2"
BROWN = "#5A3E2B"
BROWN_DARK = "#3E2A1D"
ACCENT = "#B08968"
TEXT_DARK = "#2B1B12"

ctk.set_appearance_mode("light")
ctk.set_default_color_theme("blue")


class App:
    def __init__(self, root):
        self.root = root
        self.root.title("Art Commission Tracker")
        self.root.geometry("1000x700")
        self.root.configure(fg_color=CREME)
        self.configure_treeview_style()
        self.create_main_menu()

    def setup_popup(self, win, w=900, h=600):
        win.configure(fg_color=CREME)
        win.geometry(f"{w}x{h}")
        win.transient(self.root)
        win.lift()
        win.focus_force()
        win.attributes("-topmost", True)
        win.after(150, lambda: win.attributes("-topmost", False))

    def themed_button(self, parent, text, cmd, width=140):
        return ctk.CTkButton(
            parent,
            text=text,
            command=cmd,
            width=width,
            height=42,
            fg_color=BROWN,
            hover_color=BROWN_DARK,
            text_color=CREME,
            corner_radius=14,
            font=("Arial", 15, "bold"),
        )

    def configure_treeview_style(self):
        style = ttk.Style()
        style.theme_use("clam")

        style.configure(
            "Treeview",
            background=CREME_2,
            fieldbackground=CREME_2,
            foreground=TEXT_DARK,
            rowheight=30,
            bordercolor=BROWN,
            borderwidth=1,
            font=("Arial", 13),
        )

        style.configure(
            "Treeview.Heading",
            background=BROWN,
            foreground=CREME,
            relief="flat",
            font=("Arial", 14, "bold"),
        )
        style.map("Treeview.Heading", background=[("active", BROWN_DARK)])

    # MAIN MENU 
    def create_main_menu(self):
        for widget in self.root.winfo_children():
            widget.destroy()

        container = ctk.CTkFrame(self.root, fg_color=CREME, corner_radius=0)
        container.pack(fill="both", expand=True, padx=30, pady=30)

        header = ctk.CTkFrame(container, fg_color=CREME, corner_radius=16)
        header.pack(fill="x", pady=(0, 20))

        title = ctk.CTkLabel(
            header,
            text="Art Commission Tracker",
            font=("Arial", 62, "bold"),
            text_color=BROWN_DARK
        )
        title.pack(anchor="w", padx=10, pady=(10, 0))

        subtitle = ctk.CTkLabel(
            header,
            text="Your all-in-one solution for managing art commissions with ease",
            font=("Arial", 22),
            text_color=BROWN
        )
        subtitle.pack(anchor="w", padx=10, pady=(0, 10))

        card = ctk.CTkFrame(container, fg_color=CREME_2, corner_radius=18)
        card.pack(fill="both", expand=True, padx=10, pady=10)

        btn_grid = ctk.CTkFrame(card, fg_color="transparent")
        btn_grid.pack(pady=20)

        def styled_btn(text, cmd):
            return ctk.CTkButton(
                btn_grid,
                text=text,
                command=cmd,
                width=300,
                height=60,
                fg_color=BROWN,
                hover_color=BROWN_DARK,
                text_color=CREME,
                corner_radius=18,
                font=("Arial", 18, "bold")
            )

        styled_btn("Add New Commission", self.open_add_form).grid(row=0, column=0, padx=18, pady=18)
        styled_btn("View All Commissions", self.open_view_page).grid(row=0, column=1, padx=18, pady=18)
        styled_btn("Summary Report", self.open_summary).grid(row=1, column=0, padx=18, pady=18)
        styled_btn("Exit", self.root.destroy).grid(row=1, column=1, padx=18, pady=18)

        # Current Commissions section 
        current_frame = ctk.CTkFrame(card, fg_color=CREME, corner_radius=16)
        current_frame.pack(fill="both", expand=True, padx=18, pady=(10, 18))

        ctk.CTkLabel(
            current_frame,
            text="Current Commissions",
            font=("Arial", 20, "bold"),
            text_color=BROWN_DARK
        ).pack(anchor="w", padx=12, pady=(12, 6))

        self.current_list = ttk.Treeview(
            current_frame,
            columns=("deadline", "client", "title", "status"),
            show="headings",
            height=8
        )
        self.current_list.heading("deadline", text="Deadline")
        self.current_list.heading("client", text="Client")
        self.current_list.heading("title", text="Title")
        self.current_list.heading("status", text="Status")

        self.current_list.column("deadline", width=140)
        self.current_list.column("client", width=180)
        self.current_list.column("title", width=380)
        self.current_list.column("status", width=140)

        self.current_list.pack(fill="both", expand=True, padx=12, pady=(0, 12))

        self.refresh_current_commissions()

    def refresh_current_commissions(self):
        for row in self.current_list.get_children():
            self.current_list.delete(row)

        rows = database.get_commissions(status="All", sort_by="deadline")

        active = [r for r in rows if r[6] in ("Not Started", "In Progress")]

        for r in active[:10]:
            # r = (id, client, title, type, price, deadline, status, notes)
            deadline = r[5] if r[5] else ""
            self.current_list.insert("", "end", values=(deadline, r[1], r[2], r[6]))

    # ADD / EDIT Commissions
    def open_add_form(self, edit_id=None):
        self.form = ctk.CTkToplevel(self.root)
        self.form.title("Add New Commission" if edit_id is None else "Edit Commission")
        self.setup_popup(self.form, 760, 620)

        card = ctk.CTkFrame(self.form, fg_color=CREME_2, corner_radius=18)
        card.pack(fill="both", expand=True, padx=20, pady=20)

        labels = ["Client Name", "Title", "Type", "Price ($)", "Deadline (YYYY-MM-DD)", "Status", "Notes"]
        self.entries = {}

        for i, label_text in enumerate(labels):
            lab = ctk.CTkLabel(card, text=label_text, text_color=BROWN_DARK, font=("Arial", 18, "bold"))
            lab.grid(row=i, column=0, padx=12, pady=10, sticky="w")

            if label_text == "Notes":
                entry = ctk.CTkTextbox(card, width=420, height=140, fg_color=CREME, text_color=TEXT_DARK)
            elif label_text == "Type":
                var = ctk.StringVar(value=TYPE_OPTIONS[0])
                entry = ctk.CTkComboBox(card, values=TYPE_OPTIONS, variable=var, state="readonly", width=420)
            elif label_text == "Status":
                var = ctk.StringVar(value=STATUS_OPTIONS[0])
                entry = ctk.CTkComboBox(card, values=STATUS_OPTIONS, variable=var, state="readonly", width=420)
            else:
                entry = ctk.CTkEntry(card, width=420, fg_color=CREME, text_color=TEXT_DARK)

            entry.grid(row=i, column=1, padx=12, pady=10, sticky="w")
            self.entries[label_text] = entry

        save_button = ctk.CTkButton(
            card,
            text="Save",
            command=lambda: self.save_commission(edit_id),
            fg_color=BROWN,
            hover_color=BROWN_DARK,
            text_color=CREME,
            corner_radius=14,
            font=("Arial", 14, "bold"),
            width=220,
            height=46
        )
        save_button.grid(row=len(labels), column=0, columnspan=2, pady=18)

        card.grid_columnconfigure(0, weight=0)
        card.grid_columnconfigure(1, weight=1)

        if edit_id is not None:
            self.prefill_form(edit_id)

    def prefill_form(self, comm_id):
        row = database.get_commission_by_id(comm_id)
        if not row:
            messagebox.showerror("Error", "Record not found.")
            return

        _, client, title, type_, price, deadline, status, notes = row

        self.entries["Client Name"].delete(0, tk.END)
        self.entries["Client Name"].insert(0, client)

        self.entries["Title"].delete(0, tk.END)
        self.entries["Title"].insert(0, title)

        try:
            self.entries["Type"].set(type_ if type_ else TYPE_OPTIONS[0])
        except Exception:
            pass

        self.entries["Price ($)"].delete(0, tk.END)
        self.entries["Price ($)"].insert(0, str(price) if price else "")

        self.entries["Deadline (YYYY-MM-DD)"].delete(0, tk.END)
        self.entries["Deadline (YYYY-MM-DD)"].insert(0, deadline if deadline else "")

        try:
            self.entries["Status"].set(status if status else STATUS_OPTIONS[0])
        except Exception:
            pass

        self.entries["Notes"].delete("1.0", tk.END)
        self.entries["Notes"].insert("1.0", notes if notes else "")

    def save_commission(self, edit_id=None):
        try:
            client = self.entries["Client Name"].get().strip()
            title = self.entries["Title"].get().strip()
            type_ = self.entries["Type"].get().strip()
            price_text = self.entries["Price ($)"].get().strip()
            price = float(price_text) if price_text else 0.0
            deadline = self.entries["Deadline (YYYY-MM-DD)"].get().strip()
            status = self.entries["Status"].get().strip()
            notes = self.entries["Notes"].get("1.0", tk.END).strip()

            if not client or not title:
                messagebox.showerror("Validation Error", "Client and Title are required fields.")
                return

            if deadline:
                try:
                    datetime.datetime.strptime(deadline, "%Y-%m-%d")
                except ValueError:
                    messagebox.showerror("Validation Error", "Deadline must be in YYYY-MM-DD format.")
                    return

            if edit_id is None:
                database.add_commission(client, title, type_, price, deadline, status, notes)
                messagebox.showinfo("Saved", "Commission added successfully.")
            else:
                database.update_commission(edit_id, client, title, type_, price, deadline, status, notes)
                messagebox.showinfo("Updated", "Commission updated successfully.")

            self.form.destroy()

            # refresh lists if open
            try:
                self.refresh_table()
            except Exception:
                pass

            # refresh main menu current list (if visible)
            try:
                self.refresh_current_commissions()
            except Exception:
                pass

        except Exception as e:
            messagebox.showerror("Error", f"Failed to save commission: {e}")

    # VIEW PAGE
    def open_view_page(self):
        self.view_win = ctk.CTkToplevel(self.root)
        self.view_win.title("Commission List")
        self.setup_popup(self.view_win, 1180, 650)

        top_frame = ctk.CTkFrame(self.view_win, fg_color="transparent")
        top_frame.pack(fill="x", padx=12, pady=10)

        ctk.CTkLabel(top_frame, text="Filter by status:", text_color=BROWN_DARK, font=("Arial", 15, "bold")).pack(side="left")

        self.status_var = ctk.StringVar(value="All")
        status_options = ["All"] + STATUS_OPTIONS
        status_menu = ctk.CTkComboBox(
            top_frame, values=status_options, variable=self.status_var, state="readonly", width=180
        )
        status_menu.pack(side="left", padx=8)
        status_menu.bind("<<ComboboxSelected>>", lambda e: self.refresh_table())

        ctk.CTkLabel(top_frame, text="Sort by:", text_color=BROWN_DARK, font=("Arial", 15, "bold")).pack(side="left", padx=(12, 0))

        # DISPLAY LABELS
        self.sort_var = ctk.StringVar(value="Deadline")
        sort_options = ["Deadline", "Client", "Price", "Status", "Title", "Type", "ID"]
        sort_menu = ctk.CTkComboBox(
            top_frame, values=sort_options, variable=self.sort_var, state="readonly", width=180
        )
        sort_menu.pack(side="left", padx=8)
        sort_menu.bind("<<ComboboxSelected>>", lambda e: self.refresh_table())

        self.themed_button(top_frame, "Refresh", self.refresh_table, width=120).pack(side="left", padx=8)
        self.themed_button(top_frame, "Mark Complete", self.mark_selected_complete, width=160).pack(side="left", padx=8)
        self.themed_button(top_frame, "Edit Selected", self.edit_selected, width=150).pack(side="left", padx=8)
        self.themed_button(top_frame, "Delete Selected", self.delete_selected, width=150).pack(side="left", padx=8)

        cols = ("id", "client", "title", "type", "price", "deadline", "status")
        self.tree = ttk.Treeview(self.view_win, columns=cols, show="headings")

        for c in cols:
            self.tree.heading(c, text=c.title())
            self.tree.column(c, minwidth=60, width=160)

        self.tree.pack(fill="both", expand=True, padx=12, pady=12)
        self.refresh_table()

    def refresh_table(self):
        for row in self.tree.get_children():
            self.tree.delete(row)

        status = self.status_var.get() if hasattr(self, "status_var") else "All"

        # MAP dropdown labels -> database keys
        sort_display = self.sort_var.get() if hasattr(self, "sort_var") else "Deadline"
        sort_map = {
            "Deadline": "deadline",
            "Client": "client",
            "Price": "price",
            "Status": "status",
            "Title": "title",
            "Type": "type",
            "ID": "id",
        }
        sort_by = sort_map.get(sort_display, "deadline")

        rows = database.get_commissions(status=status, sort_by=sort_by)

        for r in rows:
            price_display = f"${r[4]:.2f}" if r[4] is not None else ""
            self.tree.insert("", "end", values=(r[0], r[1], r[2], r[3], price_display, r[5], r[6]))

    # Row Actions
    def get_selected_id(self):
        sel = self.tree.selection()
        if not sel:
            messagebox.showwarning("No selection", "Please select a commission first.")
            return None
        item = self.tree.item(sel[0])
        return item["values"][0]

    def delete_selected(self):
        cid = self.get_selected_id()
        if not cid:
            return
        if messagebox.askyesno("Confirm Delete", "Are you sure you want to delete this commission?"):
            database.delete_commission(cid)
            self.refresh_table()
            try:
                self.refresh_current_commissions()
            except Exception:
                pass

    def mark_selected_complete(self):
        cid = self.get_selected_id()
        if not cid:
            return
        database.mark_complete(cid)
        self.refresh_table()
        try:
            self.refresh_current_commissions()
        except Exception:
            pass

    def edit_selected(self):
        cid = self.get_selected_id()
        if not cid:
            return
        self.open_add_form(edit_id=cid)

    # SUMMARY 
    def open_summary(self):
        total, completed, in_progress, not_started, income = database.get_summary()
        income_by_type = database.get_income_by_type()

        summary_win = ctk.CTkToplevel(self.root)
        summary_win.title("Summary Dashboard")
        self.setup_popup(summary_win, 650, 720)

        card = ctk.CTkFrame(summary_win, fg_color=CREME_2, corner_radius=18)
        card.pack(fill="both", expand=True, padx=20, pady=20)

        ctk.CTkLabel(card, text="Summary Dashboard", font=("Arial", 22, "bold"),
                     text_color=BROWN_DARK).pack(pady=(15, 10))

        stats = ctk.CTkFrame(card, fg_color=CREME, corner_radius=14)
        stats.pack(fill="x", padx=15, pady=(0, 12))

        def stat_line(text, bold=False):
            f = ("Arial", 18, "bold") if bold else ("Arial", 16)
            ctk.CTkLabel(stats, text=text, font=f, text_color=TEXT_DARK).pack(pady=5)

        stat_line(f"Total Commissions: {total}")
        stat_line(f"Not Started: {not_started}")
        stat_line(f"In Progress: {in_progress}")
        stat_line(f"Completed: {completed}")
        stat_line(f"Total Income (Completed): ${income:.2f}", bold=True)

        chart_holder = ctk.CTkFrame(card, fg_color=CREME, corner_radius=14)
        chart_holder.pack(fill="both", expand=True, padx=15, pady=10)

        if not income_by_type:
            ctk.CTkLabel(chart_holder, text="No completed commissions to chart yet.",
                         text_color=BROWN, font=("Arial", 14)).pack(pady=25)
            return

        labels = [row[0] for row in income_by_type]
        values = [row[1] for row in income_by_type]

        fig = Figure(figsize=(5.2, 4.6), dpi=100)
        ax = fig.add_subplot(111)
        ax.pie(values, labels=labels, autopct="%1.1f%%", startangle=90)
        ax.set_title("Income by Commission Type")

        canvas = FigureCanvasTkAgg(fig, master=chart_holder)
        canvas.draw()
        canvas.get_tk_widget().pack(fill="both", expand=True, padx=10, pady=10)


if __name__ == "__main__":
    root = ctk.CTk()
    app = App(root)
    root.mainloop()
