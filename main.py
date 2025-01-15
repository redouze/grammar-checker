import json
import tkinter as tk
import re
from tkinter.scrolledtext import ScrolledText
from tkinter import filedialog, messagebox
import language_tool_python

checker = language_tool_python.LanguageTool("en-US")
suggestions = []

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
            sugg_list.insert(tk.END, f"{(texteditor.get("1.0", tk.END).strip())[start_pos:end_pos]} -> {', '.join(match.replacements)}")
            suggestions.append((start_pos, end_pos, match.replacements[0]))

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
            check()
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
    check()

def replace_with_best(selected_suggestion):
    if selected_suggestion != None:
        suggestion = suggestions[selected_suggestion]
        start_index = f"1.0+{suggestion[0]}c"
        end_index = f"1.0+{suggestion[1]}c"
        corrected_content = suggestion[2]
        texteditor.delete(start_index, end_index)
        texteditor.insert(start_index, corrected_content)
        check()

def suggestion_pick():
    if sugg_list.curselection():
        return sugg_list.curselection()[0]
    return None

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

editor_container = tk.Frame(root, bg="#FFF")
editor_container.grid(row=1, column=0, sticky="nsew", padx=(10, 5), pady=10)

texteditor = ScrolledText(editor_container, font="Arial 14", wrap=tk.WORD)
texteditor.bind("<KeyRelease>", check)
texteditor.pack(expand=True, fill=tk.BOTH)

sugg_container = tk.Frame(root, bg="#EEE")
sugg_container.grid(row=1, column=1, sticky="nsew", padx=(5, 10), pady=10)

sugg_btn_ctn = tk.Frame(sugg_container, bg="#EEE")
sugg_btn_ctn.pack(fill=tk.X, padx=5, pady=(5, 10))

best_btn = tk.Button(sugg_btn_ctn, text="Replace with Best Option",  command=lambda: replace_with_best(suggestion_pick()), bg="#D5BA33", font="Arial 12")
best_btn.pack(side=tk.LEFT, padx=5)

showrepl_btn = tk.Button(sugg_btn_ctn, text="Show All Options", bg="#D5BA33", font="Arial 12")
showrepl_btn.pack(side=tk.LEFT, padx=5)

sugg_label = tk.Label(sugg_container, text="Suggestions", bg="#EEE", font="Arial 12 bold")
sugg_label.pack(anchor=tk.N, pady=5)

sugg_list = tk.Listbox(sugg_container, font="Arial 12", bg="#FFF")
sugg_list.pack(expand=True, fill=tk.BOTH, padx=5, pady=5)

root.mainloop()
