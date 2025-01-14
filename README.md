# grammar-check-gui

GUI для перевірки правильності граматики

# Інсталяція

Перед запуском не забудьте завантажити обов'язкові бібліотеки:

```
pip install nltk
```

forget:
import json
import tkinter as tk
import re
from tkinter.scrolledtext import ScrolledText
from tkinter import filedialog
import language_tool_python


checker = language_tool_python.LanguageTool("en-US")

root = tk.Tk()
root.title("Grammar Checker")
root.minsize(300, 300)
root.maxsize(800, 800)
root.geometry("600x600")
root["bg"] = "#D5BA33"

def check(event=None):
    content = text.get("1.0", tk.END).strip()

    for tag in text.tag_names():
        text.tag_delete(tag)

    matches = checker.check(content)

    for match in matches:
        start_pos = match.offset
        end_pos = match.offset + match.errorLength

        start_index = f"1.0+{start_pos}c"
        end_index = f"1.0+{end_pos}c"

        text.tag_add("error", start_index, end_index)

    text.tag_config("error", foreground="red")

def open_file():
    file_path = filedialog.askopenfilename(
        title="Відкрити файл",
        filetypes=(("Text Files", "*.txt"), ("All Files", "*.*"))
    )
    if file_path:
        try:
            with open(file_path, "r", encoding="utf-8") as file:
                content = file.read()
            text.delete("1.0", tk.END)
            text.insert(tk.END, content)
            check()
        except Exception as e:
            tk.messagebox.showerror("Помилка", f"Не вдалося відкрити файл: {e}")

frame = tk.Frame(root, bg="#FFFFFF")
frame.pack(expand=True, fill=tk.BOTH, padx=10, pady=10)

text = ScrolledText(root, font="Aerial 14", wrap=tk.WORD)
text.bind("<KeyRelease>", check)
text.pack(expand=True, fill=tk.BOTH)

open_button = tk.Button(root, text="Відкрити файл", command=open_file, bg="#D5BA33", font="Aerial 12")
open_button.pack(pady=5)

root.mainloop()
