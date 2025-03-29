import os
import tkinter as tk
from tkinter import filedialog, messagebox, scrolledtext
import threading

# --- 配置 ---
# 支持的图片文件扩展名 (小写)
SUPPORTED_EXTENSIONS = {'.jpg', '.jpeg', '.png', '.gif', '.bmp', '.tiff', '.webp'}

# --- 核心重命名逻辑 ---
def rename_images_in_folder(folder_path, log_callback):
    """
    重命名指定文件夹内的图片文件。
    文件名格式: 文件夹名_序号.原扩展名
    """
    try:
        folder_name = os.path.basename(folder_path)
        if not folder_name: # 避免根目录 (如 C:\) 导致空名字
             log_callback(f"跳过根目录或无效路径: {folder_path}")
             return 0

        count = 1
        renamed_count = 0
        log_callback(f"--- 开始处理文件夹: {folder_path} ---")

        # 获取目录下所有文件/文件夹，并排序，保证重命名顺序相对稳定
        items = sorted(os.listdir(folder_path))

        for filename in items:
            original_full_path = os.path.join(folder_path, filename)

            # 仅处理文件
            if os.path.isfile(original_full_path):
                # 获取文件扩展名并转为小写进行比较
                _, ext = os.path.splitext(filename)
                if ext.lower() in SUPPORTED_EXTENSIONS:
                    # 构建新文件名
                    new_filename = f"{folder_name}_{count}{ext}"
                    new_full_path = os.path.join(folder_path, new_filename)

                    # 避免重命名为自身或覆盖已存在的目标文件 (虽然计数器通常能避免)
                    if original_full_path == new_full_path:
                        log_callback(f"跳过（新旧名称相同）: {filename}")
                        count += 1 # 即使跳过也要增加计数器，以防后续文件重名
                        continue
                    elif os.path.exists(new_full_path):
                         log_callback(f"警告：目标文件已存在，跳过重命名: {filename} -> {new_filename}")
                         # 可以选择是跳过这个文件，还是尝试下一个序号，这里选择跳过原文件
                         continue # 跳过这个文件的重命名

                    # 执行重命名
                    try:
                        os.rename(original_full_path, new_full_path)
                        log_callback(f"成功: '{filename}' -> '{new_filename}'")
                        renamed_count += 1
                        count += 1
                    except OSError as e:
                        log_callback(f"错误: 重命名 '{filename}' 失败 - {e}")
                # else:
                #     log_callback(f"跳过（非图片）: {filename}") # 可以取消注释以记录非图片文件

        log_callback(f"--- 文件夹处理完毕: {folder_path} | 重命名 {renamed_count} 个文件 ---")
        return renamed_count

    except Exception as e:
        log_callback(f"!!! 处理文件夹 '{folder_path}' 时发生严重错误: {e}")
        return 0

def rename_images_recursively(root_dir, log_callback):
    """
    递归遍历 root_dir 下的所有子文件夹，并调用 rename_images_in_folder 处理。
    """
    total_renamed = 0
    if not os.path.isdir(root_dir):
        log_callback(f"错误：选择的路径不是一个有效的文件夹: {root_dir}")
        return 0

    log_callback(f"=== 开始递归处理根目录: {root_dir} ===")

    # os.walk 遍历目录树
    # topdown=False 确保先处理子文件夹，再处理父文件夹（如果需要的话，但这里顺序不关键）
    for dirpath, dirnames, filenames in os.walk(root_dir, topdown=True):
        # 对当前遍历到的 dirpath 执行重命名逻辑
        # 注意：os.walk 本身会遍历所有层级，我们只需要在每个层级调用处理函数
        renamed_in_folder = rename_images_in_folder(dirpath, log_callback)
        total_renamed += renamed_in_folder

        # 可选：在这里加一些延时，如果文件非常多，防止界面卡顿 (更好的方法是用线程)
        # import time
        # time.sleep(0.01)

    log_callback(f"=== 递归处理完成 ===\n总共重命名了 {total_renamed} 个图片文件。")
    return total_renamed

# --- GUI 部分 ---
class RenamerApp:
    def __init__(self, master):
        self.master = master
        master.title("图片批量重命名工具")
        master.geometry("600x400") # 设置窗口大小

        self.selected_folder = tk.StringVar()
        self.is_running = False # 标记是否正在运行

        # --- 控件 ---
        # 文件夹选择
        tk.Label(master, text="选择根文件夹:").grid(row=0, column=0, padx=5, pady=5, sticky="w")
        self.folder_entry = tk.Entry(master, textvariable=self.selected_folder, width=50, state='readonly')
        self.folder_entry.grid(row=0, column=1, padx=5, pady=5, sticky="ew")
        self.browse_button = tk.Button(master, text="浏览...", command=self.browse_folder)
        self.browse_button.grid(row=0, column=2, padx=5, pady=5)

        # 开始按钮
        self.rename_button = tk.Button(master, text="开始重命名", command=self.start_renaming_thread)
        self.rename_button.grid(row=1, column=0, columnspan=3, padx=5, pady=10)

        # 日志区域
        tk.Label(master, text="处理日志:").grid(row=2, column=0, padx=5, pady=5, sticky="w")
        self.log_area = scrolledtext.ScrolledText(master, wrap=tk.WORD, height=15, width=70)
        self.log_area.grid(row=3, column=0, columnspan=3, padx=5, pady=5, sticky="nsew")
        self.log_area.config(state='disabled') # 默认不可编辑

        # --- 布局配置 ---
        master.grid_columnconfigure(1, weight=1) # 让输入框随窗口拉伸
        master.grid_rowconfigure(3, weight=1)    # 让日志区随窗口拉伸

    def log(self, message):
        """安全地向日志区域添加消息 (GUI线程安全)"""
        def _update_log():
            self.log_area.config(state='normal')
            self.log_area.insert(tk.END, message + "\n")
            self.log_area.see(tk.END) # 滚动到底部
            self.log_area.config(state='disabled')
        # 使用 after 确保在主线程中更新 GUI
        self.master.after(0, _update_log)

    def browse_folder(self):
        """打开文件夹选择对话框"""
        if self.is_running:
            messagebox.showwarning("提示", "正在处理中，请稍候...")
            return
        folder = filedialog.askdirectory()
        if folder:
            self.selected_folder.set(folder)
            self.log(f"已选择文件夹: {folder}")

    def start_renaming_thread(self):
        """启动重命名过程 (使用线程避免GUI卡死)"""
        if self.is_running:
            messagebox.showwarning("提示", "任务已经在运行中！")
            return

        root_dir = self.selected_folder.get()
        if not root_dir:
            messagebox.showerror("错误", "请先选择一个根文件夹！")
            return
        if not os.path.isdir(root_dir):
             messagebox.showerror("错误", "选择的路径不是一个有效的文件夹！")
             return

        # 确认操作
        if not messagebox.askyesno("确认操作", f"确定要递归重命名文件夹 '{os.path.basename(root_dir)}' 及其所有子文件夹下的图片吗？\n此操作不可撤销！"):
            return

        # 清空日志区，禁用按钮，设置运行状态
        self.log_area.config(state='normal')
        self.log_area.delete('1.0', tk.END)
        self.log_area.config(state='disabled')
        self.rename_button.config(state='disabled', text="处理中...")
        self.browse_button.config(state='disabled')
        self.is_running = True

        # 创建并启动线程
        self.rename_thread = threading.Thread(target=self.run_rename_task, args=(root_dir,))
        self.rename_thread.daemon = True # 允许主程序退出时线程也退出
        self.rename_thread.start()

        # 可以选择轮询检查线程状态，但更简单的方法是在线程结束时调用一个函数来恢复UI
        # 这里选择在 run_rename_task 结束时调用 on_rename_complete

    def run_rename_task(self, root_dir):
        """在单独的线程中执行实际的重命名工作"""
        try:
            rename_images_recursively(root_dir, self.log)
        except Exception as e:
            self.log(f"!!! 发生未预料的严重错误: {e}")
        finally:
            # 任务完成，安排在主线程中恢复UI
            self.master.after(0, self.on_rename_complete)

    def on_rename_complete(self):
        """重命名完成后在主线程中调用的函数，用于恢复UI状态"""
        messagebox.showinfo("完成", "图片重命名处理已完成！请查看日志了解详情。")
        self.rename_button.config(state='normal', text="开始重命名")
        self.browse_button.config(state='normal')
        self.is_running = False


# --- 主程序入口 ---
if __name__ == "__main__":
    root = tk.Tk()
    app = RenamerApp(root)
    root.mainloop()