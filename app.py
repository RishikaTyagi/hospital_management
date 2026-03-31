import tkinter as tk
from tkinter import ttk, messagebox
import subprocess
import os

BACKEND_CMD = "backend.exe"

class HospitalApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Hospital Management System")
        self.geometry("600x600")
        
        # Determine paths
        self.backend_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), BACKEND_CMD)
        
        # Theme setup
        self.is_dark_mode = True
        self.apply_theme()
        
        # Container for screens
        self.container = tk.Frame(self, bg=self.bg_col)
        self.container.pack(fill=tk.BOTH, expand=True)
        
        self.show_main_menu()

    def apply_theme(self):
        if self.is_dark_mode:
            self.bg_col = "#2E2E2E"
            self.fg_col = "#FFFFFF"
            self.btn_bg = "#444444"
            self.btn_fg = "#FFFFFF"
            self.entry_bg = "#555555"
            self.entry_fg = "#FFFFFF"
        else:
            self.bg_col = "#F0F0F0"
            self.fg_col = "#000000"
            self.btn_bg = "#E0E0E0"
            self.btn_fg = "#000000"
            self.entry_bg = "#FFFFFF"
            self.entry_fg = "#000000"
            
        self.configure(bg=self.bg_col)
        
        # Update styling elements if possible dynamically
        style = ttk.Style(self)
        style.theme_use('clam')
        style.configure("TLabel", background=self.bg_col, foreground=self.fg_col, font=("Arial", 12))
        style.configure("Header.TLabel", font=("Arial", 16, "bold"))
        style.configure("TButton", font=("Arial", 11), padding=5, background=self.btn_bg, foreground=self.btn_fg)
        
        # Rebuild current screen if needed
        if hasattr(self, 'container'):
            for child in self.container.winfo_children():
                child.destroy()
            self.show_main_menu()

    def toggle_theme(self):
        self.is_dark_mode = not self.is_dark_mode
        self.apply_theme()

    def run_backend(self, args):
        try:
            cmd = [self.backend_path] + [str(a) for a in args]
            result = subprocess.run(cmd, capture_output=True, text=True, check=False)
            output = result.stdout.strip()
            if output.startswith("ERROR:"):
                messagebox.showerror("Error", output)
                return None
            return output
        except FileNotFoundError:
            messagebox.showerror("Error", "Backend executable not found! Did you compile backend.c?")
            return None

    def clear_container(self):
        for widget in self.container.winfo_children():
            widget.destroy()
        self.container.configure(bg=self.bg_col)
        
        # Top bar with theme toggle
        top_bar = tk.Frame(self.container, bg=self.bg_col)
        top_bar.pack(fill=tk.X, pady=5, padx=10)
        
        theme_btn = tk.Button(top_bar, text="Toggle Dark/Light", command=self.toggle_theme,
                              bg=self.btn_bg, fg=self.btn_fg, relief=tk.FLAT)
        theme_btn.pack(side=tk.RIGHT)
        
        btn_back = tk.Button(top_bar, text="< Back to Main Menu", command=self.show_main_menu,
                             bg=self.btn_bg, fg=self.btn_fg, relief=tk.FLAT)
        if hasattr(self, 'current_screen') and self.current_screen != 'main':
            btn_back.pack(side=tk.LEFT)

    def show_main_menu(self):
        self.current_screen = 'main'
        self.clear_container()
        
        title = ttk.Label(self.container, text="Hospital Management System", style="Header.TLabel")
        title.pack(pady=30)
        
        options = [
            ("1. Patient Registration", self.show_registration),
            ("2. Treat Patient", self.show_treat_patient),
            ("3. Display Remaining Patients", self.show_remaining),
            ("4. Search Patient by ID", self.show_search),
            ("5. Show History", self.show_history),
            ("6. Exit", self.destroy)
        ]
        
        for text, command in options:
            btn = tk.Button(self.container, text=text, command=command, width=30,
                            bg=self.btn_bg, fg=self.btn_fg, font=("Arial", 12), pady=5)
            btn.pack(pady=10)

    def show_registration(self):
        self.current_screen = 'registration'
        self.clear_container()
        
        title = ttk.Label(self.container, text="Patient Registration", style="Header.TLabel")
        title.pack(pady=10)
        
        form_frame = tk.Frame(self.container, bg=self.bg_col)
        form_frame.pack(pady=10)
        
        fields = ["Name:", "Age:", "Gender:", "Phone No:", "Department:", "Severity (1-10):"]
        self.entries = {}
        
        for i, field in enumerate(fields):
            lbl = ttk.Label(form_frame, text=field)
            lbl.grid(row=i, column=0, sticky='w', pady=10, padx=10)
            
            if field == "Gender:":
                var = tk.StringVar()
                cb = ttk.Combobox(form_frame, textvariable=var, values=["Male", "Female", "Other"], state="readonly")
                cb.grid(row=i, column=1, pady=10, padx=10)
                self.entries[field] = var
            elif field == "Department:":
                var = tk.StringVar()
                cb = ttk.Combobox(form_frame, textvariable=var, values=["Cardiology", "Neurology", "Orthopedics", "Pediatrics", "General"], state="readonly")
                cb.grid(row=i, column=1, pady=10, padx=10)
                self.entries[field] = var
            else:
                ent = tk.Entry(form_frame, bg=self.entry_bg, fg=self.entry_fg, insertbackground=self.entry_fg)
                ent.grid(row=i, column=1, pady=10, padx=10)
                self.entries[field] = ent
                
        def submit():
            name = self.entries["Name:"].get().replace(" ", "_").replace("|", "") # sanitize spaces for CLI
            age = self.entries["Age:"].get()
            gender = self.entries["Gender:"].get()
            phone = self.entries["Phone No:"].get()
            dept = self.entries["Department:"].get()
            severity = self.entries["Severity (1-10):"].get()
            
            if not name or not age or not gender or not phone or not dept or not severity:
                messagebox.showerror("Error", "All fields are required!")
                return
                
            res = self.run_backend(["register", name, age, gender, phone, dept, severity])
            if res:
                messagebox.showinfo("Success", res)
                self.show_main_menu()
                
        btn = tk.Button(self.container, text="Register", command=submit, bg="#4CAF50", fg="white", font=("Arial", 12, "bold"))
        btn.pack(pady=20)

    def show_treat_patient(self):
        self.current_screen = 'treat'
        self.clear_container()
        
        title = ttk.Label(self.container, text="Treating Patient...", style="Header.TLabel")
        title.pack(pady=10)
        
        res = self.run_backend(["treat"])
        if res:
            if res.startswith("TREATED:"):
                data = res.replace("TREATED:", "").strip().split("|")
                info = (f"Treated Patient Details:\n\n"
                        f"ID: {data[0]}\n"
                        f"Name: {data[1].replace('_',' ')}\n"
                        f"Age: {data[2]}\n"
                        f"Gender: {data[3]}\n"
                        f"Phone: {data[4]}\n"
                        f"Department: {data[5]}\n"
                        f"Severity: {data[6]}")
                lbl = ttk.Label(self.container, text=info, justify=tk.LEFT)
                lbl.pack(pady=20)
            else:
                lbl = ttk.Label(self.container, text=res)
                lbl.pack(pady=20)

    def show_remaining(self):
        self.current_screen = 'remaining'
        self.clear_container()
        
        title = ttk.Label(self.container, text="Remaining Patients", style="Header.TLabel")
        title.pack(pady=10)
        
        res = self.run_backend(["list"])
        if res is not None:
            text_area = tk.Text(self.container, bg=self.entry_bg, fg=self.entry_fg, height=20, width=70)
            text_area.pack(pady=10, padx=20)
            text_area.insert(tk.END, "TYPE|ID|Name|Age|Gender|Phone|Dept|Severity\n")
            text_area.insert(tk.END, "-"*65 + "\n")
            if res.strip():
                for line in res.split("\n"):
                    cols = line.split("|")
                    if len(cols) == 8:
                        text_area.insert(tk.END, f"{cols[0]:10} | {cols[1]:3} | {cols[2].replace('_',' '):15} | {cols[3]:3} | {cols[4]:6} | {cols[5]:12} | {cols[6]:12} | {cols[7]}\n")
            else:
                text_area.insert(tk.END, "No remaining patients.\n")
            text_area.config(state=tk.DISABLED)

    def show_search(self):
        self.current_screen = 'search'
        self.clear_container()
        
        title = ttk.Label(self.container, text="Search Patient", style="Header.TLabel")
        title.pack(pady=10)
        
        search_frame = tk.Frame(self.container, bg=self.bg_col)
        search_frame.pack(pady=10)
        
        ttk.Label(search_frame, text="Patient ID:").pack(side=tk.LEFT, padx=5)
        ent = tk.Entry(search_frame, bg=self.entry_bg, fg=self.entry_fg, insertbackground=self.entry_fg)
        ent.pack(side=tk.LEFT, padx=5)
        
        result_lbl = ttk.Label(self.container, text="")
        result_lbl.pack(pady=20)
        
        def do_search():
            pid = ent.get()
            if not pid:
                return
            res = self.run_backend(["search", pid])
            if res:
                if res.startswith("FOUND:"):
                    # Format: FOUND: id|name|age|gender|phone|dept|severity|(filename)
                    parts = res.replace("FOUND:", "").strip().split("|")
                    r_text = f"FOUND in {parts[7]}\n\nName: {parts[1].replace('_',' ')}\nAge: {parts[2]}\nDept: {parts[5]}"
                    result_lbl.config(text=r_text)
                else:
                    result_lbl.config(text=res)
                    
        btn = tk.Button(search_frame, text="Search", command=do_search, bg=self.btn_bg, fg=self.btn_fg)
        btn.pack(side=tk.LEFT, padx=5)

    def show_history(self):
        self.current_screen = 'history'
        self.clear_container()
        
        title = ttk.Label(self.container, text="Served Patients History", style="Header.TLabel")
        title.pack(pady=10)
        
        res = self.run_backend(["history"])
        if res is not None:
            text_area = tk.Text(self.container, bg=self.entry_bg, fg=self.entry_fg, height=20, width=70)
            text_area.pack(pady=10, padx=20)
            text_area.insert(tk.END, "ID|Name|Age|Gender|Phone|Dept|Severity\n")
            text_area.insert(tk.END, "-"*65 + "\n")
            if res.strip():
                for line in res.split("\n"):
                    cols = line.split("|")
                    if len(cols) == 7:
                        text_area.insert(tk.END, f"{cols[0]:3} | {cols[1].replace('_',' '):15} | {cols[2]:3} | {cols[3]:6} | {cols[4]:12} | {cols[5]:12} | {cols[6]}\n")
            else:
                text_area.insert(tk.END, "History is empty.\n")
            text_area.config(state=tk.DISABLED)
            
        def do_clear():
            if messagebox.askyesno("Confirm", "Are you sure you want to clear history?"):
                c_res = self.run_backend(["clear_history"])
                if c_res:
                    messagebox.showinfo("Cleared", c_res)
                    self.show_main_menu()
                    
        btn_clear = tk.Button(self.container, text="Clear History", command=do_clear, bg="#F44336", fg="white")
        btn_clear.pack(pady=10)

if __name__ == "__main__":
    app = HospitalApp()
    app.mainloop()
