import tkinter as tk
from tkinter import ttk, messagebox
import database
import datetime

STATUS_OPTIONS = ["Not Started", "In Progress", "Completed"]
TYPE_OPTIONS = ["Portrait", "Full Body", "Chibi", "Icon", "Other"]

class App:
    def __init__(self, root):
        self.root = root
        self.root.title("Art Commission Tracker")
        self.root.geometry("800x600")
        self.create_main_menu()

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

        btn_exit = tk.Button(self.root, text="Exit", width=10, command=self.root.destroy)
        btn_exit.pack(pady=20)

    def open_add_form(self, edit_id=None):
        self.form = tk.Toplevel(self.root)
        self.form.title("Add New Commission" if edit_id is None else "Edit Commission")
        self.form.geometry("500x550")
        labels = ["Client Name", "Title", "Type", "Price ($)", "Deadline (YYYY-MM-DD)", "Status", "Notes"]
        self.entries = {}

        for i, label_text in enumerate(labels):
            label = tk.Label(self.form, text=label_text)
            label.grid(row=i, column=0, padx=10, pady=5, sticky="w")

            if label_text == "Notes":
                entry = tk.Text(self.form, width=40, height=6)
            elif label_text == "Type":
                var = tk.StringVar(value=TYPE_OPTIONS[0])
                entry = ttk.Combobox(self.form, textvariable=var, values=TYPE_OPTIONS, state="readonly")
            elif label_text == "Status":
                var = tk.StringVar(value=STATUS_OPTIONS[0])
                entry = ttk.Combobox(self.form, textvariable=var, values=STATUS_OPTIONS, state="readonly")
            else:
                entry = tk.Entry(self.form, width=40)

            entry.grid(row=i, column=1, padx=10, pady=5)
            self.entries[label_text] = entry

        save_button = tk.Button(self.form, text="Save", width=15, command=lambda: self.save_commission(edit_id))
        save_button.grid(row=len(labels), column=0, columnspan=2, pady=15)

        if edit_id is not None:
            self.prefill_form(edit_id)

    def prefill_form(self, comm_id):
        row = database.get_commission_by_id(comm_id)
        if not row:
            messagebox.showerror("Error", "Record not found.")
            return
        # row = (id, client, title, type, price, deadline, status, notes)
        _, client, title, type_, price, deadline, status, notes = row
        self.entries["Client Name"].delete(0, tk.END); self.entries["Client Name"].insert(0, client)
        self.entries["Title"].delete(0, tk.END); self.entries["Title"].insert(0, title)
        try:
            self.entries["Type"].set(type_ if type_ else TYPE_OPTIONS[0])
        except Exception:
            pass
        self.entries["Price ($)"].delete(0, tk.END); self.entries["Price ($)"].insert(0, str(price) if price else "")
        self.entries["Deadline (YYYY-MM-DD)"].delete(0, tk.END); self.entries["Deadline (YYYY-MM-DD)"].insert(0, deadline if deadline else "")
        try:
            self.entries["Status"].set(status if status else STATUS_OPTIONS[0])
        except Exception:
            pass
        self.entries["Notes"].delete("1.0", tk.END); self.entries["Notes"].insert("1.0", notes if notes else "")

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
            # basic date format check
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
            # refresh view if open
            try:
                self.refresh_table()
            except Exception:
                pass
        except Exception as e:
            messagebox.showerror("Error", f"Failed to save commission: {e}")

    def open_view_page(self):
        self.view_win = tk.Toplevel(self.root)
        self.view_win.title("Commission List")
        self.view_win.geometry("900x500")

        top_frame = tk.Frame(self.view_win)
        top_frame.pack(fill="x", padx=10, pady=5)

        tk.Label(top_frame, text="Filter by status:").pack(side="left")
        self.status_var = tk.StringVar(value="All")
        status_options = ["All"] + STATUS_OPTIONS
        status_menu = ttk.Combobox(top_frame, textvariable=self.status_var, values=status_options, state="readonly", width=15)
        status_menu.pack(side="left", padx=5)
        status_menu.bind("<<ComboboxSelected>>", lambda e: self.refresh_table())

        tk.Button(top_frame, text="Refresh", command=self.refresh_table).pack(side="left", padx=5)
        tk.Button(top_frame, text="Mark Complete", command=self.mark_selected_complete).pack(side="left", padx=5)
        tk.Button(top_frame, text="Edit Selected", command=self.edit_selected).pack(side="left", padx=5)
        tk.Button(top_frame, text="Delete Selected", command=self.delete_selected).pack(side="left", padx=5)

        cols = ("id","client","title","type","price","deadline","status")
        self.tree = ttk.Treeview(self.view_win, columns=cols, show="headings")
        for c in cols:
            self.tree.heading(c, text=c.title())
            self.tree.column(c, minwidth=50, width=120)
        self.tree.pack(fill="both", expand=True, padx=10, pady=10)

        self.refresh_table()

    def refresh_table(self):
        for row in self.tree.get_children():
            self.tree.delete(row)
        status = self.status_var.get() if hasattr(self, "status_var") else "All"
        if status == "All":
            rows = database.get_commissions_sorted_by_deadline()
        else:
            rows = database.get_commissions_by_status(status)
        for r in rows:
            # r = (id, client, title, type, price, deadline, status, notes)
            price_display = f"${r[4]:.2f}" if r[4] is not None else ""
            self.tree.insert("", "end", values=(r[0], r[1], r[2], r[3], price_display, r[5], r[6]))

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

    def mark_selected_complete(self):
        cid = self.get_selected_id()
        if not cid:
            return
        database.mark_complete(cid)
        self.refresh_table()

    def edit_selected(self):
        cid = self.get_selected_id()
        if not cid:
            return
        self.open_add_form(edit_id=cid)

    def open_summary(self):
        total, completed, income = database.get_summary()
        summary_win = tk.Toplevel(self.root)
        summary_win.title("Summary Dashboard")
        summary_win.geometry("350x200")
        tk.Label(summary_win, text=f"Total Commissions: {total}", font=("Arial", 12)).pack(pady=8)
        tk.Label(summary_win, text=f"Completed Commissions: {completed}", font=("Arial", 12)).pack(pady=8)
        tk.Label(summary_win, text=f"Total Income (Completed): ${income:.2f}", font=("Arial", 12)).pack(pady=8)
        tk.Button(summary_win, text="Export Summary CSV", command=self.export_csv).pack(pady=10)


if __name__ == "__main__":
    root = tk.Tk()
    app = App(root)
    root.mainloop()
