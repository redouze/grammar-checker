import tkinter as tk
from tkinter import ttk
from tkinter.scrolledtext import ScrolledText
from tkinter import filedialog, messagebox
import language_tool_python # type: ignore
import threading

class GrammarChecker(language_tool_python.LanguageTool):
    def __init__(self, language="en-US"):
        super().__init__(language)
        self.check("Blank content with a mistaek")
        self.language_codes = {
            # germanic
            "English (US)": "en-US",
            "English (GB)": "en-GB",
            "English (Australia)": "en-AU",
            "English (Canada)": "en-CA",
            "English (New Zealand)": "en-NZ",
            "German": "de-DE",
            "German (Austria)": "de-AT",
            "German (Switzerland)": "de-CH",
            "Dutch": "nl",
            "Dutch (Netherlands)": "nl-NL",
            "Dutch (Belgium)": "nl-BE",
            "Danish": "da",
            "Swedish": "sv",
            "Norwegian": "no",
            "Icelandic": "is",
            
            # slavic
            "Ukrainian": "uk",
            "Polish": "pl",
            "Russian": "ru",
            "Slovak": "sk",
            "Slovenian": "sl",
            "Czech": "cs",
            "Croatian": "hr",
            "Serbian": "sr",
            "Bulgarian": "bg",
            "Macedonian": "mk",

            # romance
            "Spanish": "es",
            "Spanish (Spain)": "es-ES",
            "Spanish (Mexico)": "es-MX",
            "French": "fr",
            "French (France)": "fr-FR",
            "French (Canada)": "fr-CA",
            "French (Belgium)": "fr-BE",
            "French (Switzerland)": "fr-CH",
            "Portuguese": "pt",
            "Portuguese (Brazil)": "pt-BR",
            "Portuguese (Portugal)": "pt-PT",
            "Italian": "it",
            "Italian (Italy)": "it-IT",
            "Catalan": "ca",
            "Romanian": "ro",
            
            # chinese
            "Chinese (Simplified)": "zh-CN",
            "Chinese (Traditional)": "zh-TW",
            
            # others
            "Esperanto": "eo",
            "Greek": "el",
            "Finnish": "fi",
            "Irish": "ga",
            "Estonian": "et",
            "Lithuanian": "lt",
            "Latvian": "lv",
            "Tagalog": "tl",
            "Hindi": "hi",
            "Bengali": "bn",
            "Malayalam": "ml",
            "Tamil": "ta",
            "Telugu": "te",
            "Bengali": "bn",
            "Icelandic": "is",
            "Maltese": "mt",
        }

    def check_text(self, text):
        return self.check(text)

class GUI(tk.Tk):
    def __init__(self):
        super().__init__()
        self.checker = GrammarChecker()

        self.title("Grammar Checker")
        self.geometry("1200x600")
        self.grid_rowconfigure(1, weight=1)
        self.grid_columnconfigure(0, weight=2)
        self.grid_columnconfigure(1, weight=1)

        self.suggestions = []

        self.top_bar = tk.Frame(self, bg="#333")
        self.top_bar.grid(row=0, column=0, columnspan=2, sticky="ew")

        self.openfile_btn = tk.Button(self.top_bar, text="Open File", command=lambda: self.open_file(), bg="#D5BA33", font="Arial 12")
        self.openfile_btn.pack(side=tk.LEFT, padx=10, pady=5)

        self.fix_btn = tk.Button(self.top_bar, text="Fix All Mistakes", command=lambda: self.fix_all_mistakes(), bg="#D5BA33", font="Arial 12")
        self.fix_btn.pack(side=tk.LEFT, padx=10, pady=5)

        self.savefile_btn = tk.Button(self.top_bar, text="Save File", command=self.save_file, bg="#D5BA33", font="Arial 12")
        self.savefile_btn.pack(side=tk.LEFT, padx=10, pady=5)

        self.language_selector = ttk.Combobox(self.top_bar, values=list(self.checker.language_codes.keys()), state="readonly")
        self.language_selector.pack(side=tk.LEFT, padx=10, pady=5)
        self.language_selector.bind("<<ComboboxSelected>>", self.language_option_select)
        self.language_selector.set("English (US)")

        self.editor_container = tk.Frame(self, bg="#FFF")
        self.editor_container.grid(row=1, column=0, sticky="nsew", padx=(10, 5), pady=10)

        self.texteditor = ScrolledText(self.editor_container, font="Arial 14", wrap=tk.WORD)
        self.check_id = None
        self.texteditor.bind("<KeyRelease>", lambda event: self.delay_checker())
        self.texteditor.pack(expand=True, fill=tk.BOTH)

        self.sugg_container = tk.Frame(self, bg="#EEE")
        self.sugg_container.grid(row=1, column=1, sticky="nsew", padx=(5, 10), pady=10)

        self.sugg_btn_ctn = tk.Frame(self.sugg_container, bg="#EEE")
        self.sugg_btn_ctn.pack(fill=tk.X, padx=5, pady=(5, 10))

        self.replacement_var = tk.StringVar()
        self.replacement_var.set("Replacement")
        self.dropdown_menu = tk.OptionMenu(self.sugg_btn_ctn, self.replacement_var, "No suggestion selected")
        self.dropdown_menu.pack(side=tk.LEFT, padx=5)

        self.replace_btn = tk.Button(
            self.sugg_btn_ctn,
            text="Replace with Selected",
            command=lambda: self.replace_with(self.suggestion_pick(), self.replacement_var.get()),
            bg="#D5BA33",
            font="Arial 12",
        )
        self.replace_btn.pack(side=tk.LEFT, padx=5)

        self.sugg_label = tk.Label(self.sugg_container, text="Suggestions", bg="#EEE", font="Arial 12 bold")
        self.sugg_label.pack(anchor=tk.N, pady=5)

        self.sugg_list = tk.Listbox(self.sugg_container, font="Arial 12", bg="#FFF")
        self.sugg_list.bind("<<ListboxSelect>>", self.suggestion_pick)
        self.sugg_list.pack(expand=True, fill=tk.BOTH, padx=5, pady=5)

    def update_suggestions(self, match_reps):
        self.dropdown_menu["menu"].delete(0, "end")
        for option in match_reps:
            self.dropdown_menu["menu"].add_command(label=option, command=lambda value=option: self.replacement_var.set(value))

    def check(self, event=None):
        content = self.texteditor.get("1.0", tk.END).strip()

        for tag in self.texteditor.tag_names():
            self.texteditor.tag_delete(tag)
        self.sugg_list.delete(0, tk.END)
        self.suggestions.clear()

        matches = self.checker.check(content)
        
        for match in matches:
            start_pos = match.offset
            end_pos = start_pos + match.errorLength

            start_index = f"1.0+{start_pos}c"
            end_index = f"1.0+{end_pos}c"

            self.texteditor.tag_add("error", start_index, end_index)
            if match.replacements:
                self.sugg_list.insert(
                    tk.END,
                    f"{(self.texteditor.get('1.0', tk.END).strip())[start_pos:end_pos]} -> {', '.join(match.replacements)}"
                )
                self.suggestions.append((start_pos, end_pos, match.replacements))
                self.replacement_var.set("Select an option")
                self.update_suggestions(match.replacements)

        self.texteditor.tag_config("error", foreground="red")

    def open_file(self):
        file_path = filedialog.askopenfilename(
            title="Відкрити файл",
            filetypes=(("Text Files", "*.txt"), ("All Files", "*.*"))
        )
        if file_path:
            try:
                with open(file_path, "r", encoding="utf-8") as file:
                    content = file.read()
                self.texteditor.delete("1.0", tk.END)
                self.texteditor.insert(tk.END, content)
                self.thread_check()
            except Exception as e:
                tk.messagebox.showerror("Помилка", f"Не вдалося відкрити файл: {e}")

    def fix_all_mistakes(self, event=None):
        content = self.texteditor.get("1.0", tk.END).strip()
        corrected_content = self.checker.correct(content)
        self.texteditor.delete("1.0", tk.END)
        self.texteditor.insert("1.0", corrected_content)
        for tag in self.texteditor.tag_names():
            self.texteditor.tag_delete(tag)
        self.sugg_list.delete(0, tk.END)
        self.suggestions.clear()
        self.thread_check()
        if(len(self.suggestions)>0):
            self.fix_all_mistakes()

    def replace_with(self, selected_suggestion, replacement):
        if selected_suggestion is not None and replacement != "Select an option":
            suggestion = self.suggestions[selected_suggestion]
            start_index = f"1.0+{suggestion[0]}c"
            end_index = f"1.0+{suggestion[1]}c"
            self.texteditor.delete(start_index, end_index)
            self.texteditor.insert(start_index, replacement)
            self.thread_check()

    def suggestion_pick(self, event=None):
        selected = self.sugg_list.curselection()
        if selected:
            self.update_suggestions(self.suggestions[selected[0]][2])
            return selected[0]
        return None

    def save_file(self, event=None):
        file_path = filedialog.asksaveasfilename(
            title="Save File",
            defaultextension=".txt",
            filetypes=(("Text Files", "*.txt"), ("All Files", "*.*"))
        )
        if file_path:
            try:
                with open(file_path, "w", encoding="utf-8") as file:
                    content = self.texteditor.get("1.0", tk.END).strip()
                    file.write(content)
                messagebox.showinfo("Success", f"File saved as {file.name}")
            except Exception as e:
                messagebox.showerror("Error", f"Could not save file: {e}")

    def language_option_select(self, event=None):
        selected_option = self.language_selector.get()
        messagebox.showinfo("Grammar Checker", f"Please wait, this could take a while...")
        self.checker.__init__(self.checker.language_codes[selected_option])
        messagebox.showinfo("Grammar Checker", f"Language {selected_option} selected!")

    def delay_checker(self):
        if self.check_id:
            self.texteditor.after_cancel(self.check_id)
        self.check_id = self.texteditor.after(100, self.thread_check)


    def thread_check(self):
        threading.Thread(target=self.check, daemon=True).start()

app = GUI()

app.mainloop()
app.checker.close()