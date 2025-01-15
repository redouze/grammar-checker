import tkinter as tk
from tkinter import ttk
from tkinter.scrolledtext import ScrolledText
from tkinter import filedialog, messagebox
import language_tool_python
import threading

language_codes = {
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

checker = language_tool_python.LanguageTool("en-US")
checker.check("Blank content with a mistaek")
suggestions = []

def update_suggestions(match_reps):
    dropdown_menu["menu"].delete(0, "end")
    for option in match_reps:
        dropdown_menu["menu"].add_command(label=option, command=lambda value=option: replacement_var.set(value))

def check(event=None):
    content = texteditor.get("1.0", tk.END).strip()

    for tag in texteditor.tag_names():
        texteditor.tag_delete(tag)
    sugg_list.delete(0, tk.END)
    suggestions.clear()

    matches = checker.check(content)
    
    for match in matches:
        start_pos = match.offset
        end_pos = start_pos + match.errorLength

        start_index = f"1.0+{start_pos}c"
        end_index = f"1.0+{end_pos}c"

        texteditor.tag_add("error", start_index, end_index)
        if match.replacements:
            sugg_list.insert(
                tk.END,
                f"{(texteditor.get('1.0', tk.END).strip())[start_pos:end_pos]} -> {', '.join(match.replacements)}"
            )
            suggestions.append((start_pos, end_pos, match.replacements))
            replacement_var.set("Select an option")
            update_suggestions(match.replacements)

    texteditor.tag_config("error", foreground="red")

def open_file():
    file_path = filedialog.askopenfilename(
        title="Відкрити файл",
        filetypes=(("Text Files", "*.txt"), ("All Files", "*.*"))
    )
    if file_path:
        try:
            with open(file_path, "r", encoding="utf-8") as file:
                content = file.read()
            texteditor.delete("1.0", tk.END)
            texteditor.insert(tk.END, content)
            thread_check()
        except Exception as e:
            tk.messagebox.showerror("Помилка", f"Не вдалося відкрити файл: {e}")

def fix_all_mistakes(event=None):
    content = texteditor.get("1.0", tk.END).strip()
    corrected_content = checker.correct(content)
    texteditor.delete("1.0", tk.END)
    texteditor.insert("1.0", corrected_content)
    for tag in texteditor.tag_names():
        texteditor.tag_delete(tag)
    sugg_list.delete(0, tk.END)
    suggestions.clear()
    thread_check()
    if(len(suggestions)>0):
        fix_all_mistakes()

def replace_with(selected_suggestion, replacement):
    if selected_suggestion is not None and replacement != "Select an option":
        suggestion = suggestions[selected_suggestion]
        start_index = f"1.0+{suggestion[0]}c"
        end_index = f"1.0+{suggestion[1]}c"
        texteditor.delete(start_index, end_index)
        texteditor.insert(start_index, replacement)
        thread_check()

def suggestion_pick(event=None):
    selected = sugg_list.curselection()
    if selected:
        update_suggestions(suggestions[selected[0]][2])
        return selected[0]
    return None

def save_file(event=None):
    file_path = filedialog.asksaveasfilename(
        title="Save File",
        defaultextension=".txt",
        filetypes=(("Text Files", "*.txt"), ("All Files", "*.*"))
    )
    if file_path:
        try:
            with open(file_path, "w", encoding="utf-8") as file:
                content = texteditor.get("1.0", tk.END).strip()
                file.write(content)
            messagebox.showinfo("Success", f"File saved as {file.name}")
        except Exception as e:
            messagebox.showerror("Error", f"Could not save file: {e}")

def language_option_select(event=None):
    global checker
    selected_option = language_selector.get()
    messagebox.showinfo("Grammar Checker", f"Please wait, this could take a while...")
    checker = language_tool_python.LanguageTool(language_codes[selected_option])
    checker.check("Blank content with a mistaek")
    messagebox.showinfo("Grammar Checker", f"Language {selected_option} selected!")

def delay_checker():
    global check_id
    if check_id:
        texteditor.after_cancel(check_id)
    check_id = texteditor.after(100, thread_check)

def thread_check():
    threading.Thread(target=check, daemon=True).start()

root = tk.Tk()
root.title("Grammar Checker")
root.geometry("1200x600")
root.grid_rowconfigure(1, weight=1)
root.grid_columnconfigure(0, weight=2)
root.grid_columnconfigure(1, weight=1)

top_bar = tk.Frame(root, bg="#333")
top_bar.grid(row=0, column=0, columnspan=2, sticky="ew")

openfile_btn = tk.Button(top_bar, text="Open File", command=lambda: open_file(), bg="#D5BA33", font="Arial 12")
openfile_btn.pack(side=tk.LEFT, padx=10, pady=5)

fix_btn = tk.Button(top_bar, text="Fix All Mistakes", command=lambda: fix_all_mistakes(), bg="#D5BA33", font="Arial 12")
fix_btn.pack(side=tk.LEFT, padx=10, pady=5)

savefile_btn = tk.Button(top_bar, text="Save File", command=save_file, bg="#D5BA33", font="Arial 12")
savefile_btn.pack(side=tk.LEFT, padx=10, pady=5)

language_selector = ttk.Combobox(top_bar, values=list(language_codes.keys()), state="readonly")
language_selector.pack(side=tk.LEFT, padx=10, pady=5)
language_selector.bind("<<ComboboxSelected>>", language_option_select)
language_selector.set("English (US)")

editor_container = tk.Frame(root, bg="#FFF")
editor_container.grid(row=1, column=0, sticky="nsew", padx=(10, 5), pady=10)

texteditor = ScrolledText(editor_container, font="Arial 14", wrap=tk.WORD)
check_id = None
texteditor.bind("<KeyRelease>", lambda event: delay_checker())
texteditor.pack(expand=True, fill=tk.BOTH)

sugg_container = tk.Frame(root, bg="#EEE")
sugg_container.grid(row=1, column=1, sticky="nsew", padx=(5, 10), pady=10)

sugg_btn_ctn = tk.Frame(sugg_container, bg="#EEE")
sugg_btn_ctn.pack(fill=tk.X, padx=5, pady=(5, 10))

replacement_var = tk.StringVar()
replacement_var.set("Replacement")
dropdown_menu = tk.OptionMenu(sugg_btn_ctn, replacement_var, "No suggestion selected")
dropdown_menu.pack(side=tk.LEFT, padx=5)

replace_btn = tk.Button(
    sugg_btn_ctn,
    text="Replace with Selected",
    command=lambda: replace_with(suggestion_pick(), replacement_var.get()),
    bg="#D5BA33",
    font="Arial 12",
)
replace_btn.pack(side=tk.LEFT, padx=5)

sugg_label = tk.Label(sugg_container, text="Suggestions", bg="#EEE", font="Arial 12 bold")
sugg_label.pack(anchor=tk.N, pady=5)

sugg_list = tk.Listbox(sugg_container, font="Arial 12", bg="#FFF")
sugg_list.bind("<<ListboxSelect>>", suggestion_pick)
sugg_list.pack(expand=True, fill=tk.BOTH, padx=5, pady=5)

root.mainloop()
checker.close()