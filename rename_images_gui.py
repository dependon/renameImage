import os
import tkinter as tk
from tkinter import filedialog, messagebox, scrolledtext, ttk
import threading
from language_manager import LanguageManager

SUPPORTED_EXTENSIONS = {'.jpg', '.jpeg', '.png', '.gif', '.bmp', '.tiff', '.webp'}

# --- 核心重命名逻辑 ---
def rename_images_in_folder(folder_path, log_callback):
    try:
        folder_name = os.path.basename(folder_path)
        if not folder_name:
             log_callback(lang_manager.get_text('skip_root').format(folder_path=folder_path))
             return 0

        count = 1
        renamed_count = 0
        log_callback(lang_manager.get_text('start_processing').format(folder_path=folder_path))

        items = sorted(os.listdir(folder_path))

        for filename in items:
            original_full_path = os.path.join(folder_path, filename)

            if os.path.isfile(original_full_path):
                _, ext = os.path.splitext(filename)
                if ext.lower() in SUPPORTED_EXTENSIONS:
                    new_filename = f"{folder_name}_{count}{ext}"
                    new_full_path = os.path.join(folder_path, new_filename)

                    if original_full_path == new_full_path:
                        log_callback(lang_manager.get_text('skip_same_name').format(filename=filename))
                        count += 1
                        continue
                    elif os.path.exists(new_full_path):
                         log_callback(lang_manager.get_text('warning_existing_file').format(filename=filename, new_filename=new_filename))
                         continue

                    try:
                        os.rename(original_full_path, new_full_path)
                        log_callback(lang_manager.get_text('success').format(filename=filename, new_filename=new_filename))
                        renamed_count += 1
                        count += 1
                    except OSError as e:
                        log_callback(lang_manager.get_text('error_rename').format(filename=filename, error=str(e)))

        log_callback(lang_manager.get_text('folder_processed').format(folder_path=folder_path, renamed_count=renamed_count))
        return renamed_count

    except Exception as e:
        log_callback(lang_manager.get_text('unexpected_error').format(error=str(e)))
        return 0

def rename_images_recursively(root_dir, log_callback):
    total_renamed = 0
    if not os.path.isdir(root_dir):
        log_callback(lang_manager.get_text('invalid_folder_error'))
        return 0

    log_callback(lang_manager.get_text('recursive_start').format(root_dir=root_dir))

    for dirpath, dirnames, filenames in os.walk(root_dir, topdown=True):
        renamed_in_folder = rename_images_in_folder(dirpath, log_callback)
        total_renamed += renamed_in_folder

    log_callback(lang_manager.get_text('recursive_complete').format(total_renamed=total_renamed))
    return total_renamed

# --- GUI 部分 ---
class RenamerApp:
    def __init__(self, master):
        self.master = master
        self.lang_manager = LanguageManager()
        self.update_window_title()

        self.selected_folder = tk.StringVar()
        self.is_running = False

        # 创建语言选择下拉框
        self.create_language_selector()

        # 文件夹选择部分
        tk.Label(master, text=self.lang_manager.get_text('select_folder')).grid(row=1, column=0, padx=5, pady=5)
        self.folder_entry = tk.Entry(master, textvariable=self.selected_folder, width=50, state='readonly')
        self.folder_entry.grid(row=1, column=1, padx=5, pady=5, sticky="ew")
        self.browse_button = tk.Button(master, text=self.lang_manager.get_text('browse'), command=self.browse_folder)
        self.browse_button.grid(row=1, column=2, padx=5, pady=5)

        # 开始按钮
        self.rename_button = tk.Button(master, text=self.lang_manager.get_text('start_rename'), command=self.start_renaming_thread)
        self.rename_button.grid(row=2, column=0, columnspan=3, padx=5, pady=10)

        # 日志区域
        tk.Label(master, text=self.lang_manager.get_text('log')).grid(row=3, column=0, padx=5, pady=5, sticky="w")
        self.log_area = scrolledtext.ScrolledText(master, wrap=tk.WORD, height=15, width=70)
        self.log_area.grid(row=4, column=0, columnspan=3, padx=5, pady=5, sticky="nsew")
        self.log_area.config(state='disabled')

        # 布局配置
        master.grid_columnconfigure(1, weight=1)
        master.grid_rowconfigure(4, weight=1)

    def create_language_selector(self):
        languages = self.lang_manager.get_supported_languages()
        current_lang = self.lang_manager.get_current_language()
        
        frame = tk.Frame(self.master)
        frame.grid(row=0, column=0, columnspan=3, padx=5, pady=5, sticky="e")
        
        # 获取当前语言的本地化名称
        current_lang_name = languages[current_lang]
        self.lang_var = tk.StringVar(value=current_lang_name)
        
        # 创建语言代码到本地化名称的映射
        self.lang_code_to_name = languages
        self.lang_name_to_code = {v: k for k, v in languages.items()}
        
        self.lang_combobox = ttk.Combobox(frame, textvariable=self.lang_var, values=list(languages.values()), state='readonly', width=10)
        self.lang_combobox.bind('<<ComboboxSelected>>', self.on_language_change)
        self.lang_combobox.pack(side=tk.RIGHT)

    def on_language_change(self, event=None):
        selected_lang_name = self.lang_var.get()
        selected_lang_code = self.lang_name_to_code[selected_lang_name]
        if self.lang_manager.load_language(selected_lang_code):
            self.update_ui_texts()

    def update_ui_texts(self):
        self.update_window_title()
        self.browse_button.config(text=self.lang_manager.get_text('browse'))
        self.rename_button.config(text=self.lang_manager.get_text('start_rename') if not self.is_running else self.lang_manager.get_text('processing'))
        
        # Update label texts
        for widget in self.master.grid_slaves():
            if isinstance(widget, tk.Label):
                if widget.grid_info()['row'] == 1:  # Select folder label
                    widget.config(text=self.lang_manager.get_text('select_folder'))
                elif widget.grid_info()['row'] == 3:  # Log label
                    widget.config(text=self.lang_manager.get_text('log'))

    def update_window_title(self):
        self.master.title(self.lang_manager.get_text('title'))

    def log(self, message):
        def _update_log():
            self.log_area.config(state='normal')
            self.log_area.insert(tk.END, message + "\n")
            self.log_area.see(tk.END)
            self.log_area.config(state='disabled')
        self.master.after(0, _update_log)

    def browse_folder(self):
        if self.is_running:
            messagebox.showwarning(self.lang_manager.get_text('title'), self.lang_manager.get_text('task_running'))
            return
        folder = filedialog.askdirectory()
        if folder:
            self.selected_folder.set(folder)

    def start_renaming_thread(self):
        if self.is_running:
            messagebox.showwarning(self.lang_manager.get_text('title'), self.lang_manager.get_text('task_running'))
            return

        root_dir = self.selected_folder.get()
        if not root_dir:
            messagebox.showerror(self.lang_manager.get_text('title'), self.lang_manager.get_text('select_folder_error'))
            return
        if not os.path.isdir(root_dir):
            messagebox.showerror(self.lang_manager.get_text('title'), self.lang_manager.get_text('invalid_folder_error'))
            return

        if not messagebox.askyesno(self.lang_manager.get_text('title'),
                                  self.lang_manager.get_text('confirm_operation').format(folder=os.path.basename(root_dir))):
            return

        self.log_area.config(state='normal')
        self.log_area.delete('1.0', tk.END)
        self.log_area.config(state='disabled')
        self.rename_button.config(state='disabled', text=self.lang_manager.get_text('processing'))
        self.browse_button.config(state='disabled')
        self.is_running = True

        self.rename_thread = threading.Thread(target=self.run_rename_task, args=(root_dir,))
        self.rename_thread.daemon = True
        self.rename_thread.start()

    def run_rename_task(self, root_dir):
        try:
            rename_images_recursively(root_dir, self.log)
        except Exception as e:
            self.log(self.lang_manager.get_text('unexpected_error').format(error=str(e)))
        finally:
            self.master.after(0, self.on_rename_complete)

    def on_rename_complete(self):
        messagebox.showinfo(self.lang_manager.get_text('title'), self.lang_manager.get_text('completed'))
        self.rename_button.config(state='normal', text=self.lang_manager.get_text('start_rename'))
        self.browse_button.config(state='normal')
        self.is_running = False

# --- 主程序入口 ---
if __name__ == "__main__":
    lang_manager = LanguageManager()
    root = tk.Tk()
    app = RenamerApp(root)
    root.mainloop()