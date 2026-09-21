# -*- coding: utf-8 -*-
import os
import sys
import re
import tkinter as tk
from tkinter import filedialog, messagebox, ttk
import customtkinter as ctk

# ตั้งค่าธีมเป็นสว่าง (Light Mode) คลีนสบายตา
ctk.set_appearance_mode("Light")
ctk.set_default_color_theme("blue")

class ROMTidyApp(ctk.CTk):
    def __init__(self):
        super().__init__()

        self.title("ROMTidy v0.1 (Beta) - Retro Handheld Edition")
        self.geometry("1100x750")
        self.minsize(950, 650)

        self.folder_path = tk.StringVar()
        self.scanned_files = []

        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(1, weight=1)

        # --- Top Panel: เลือกโฟลเดอร์รอม ---
        self.top_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.top_frame.grid(row=0, column=0, sticky="ew", padx=15, pady=(15, 5))
        self.top_frame.grid_columnconfigure(1, weight=1)

        self.folder_label = ctk.CTkLabel(self.top_frame, text="โฟลเดอร์รอม:", font=ctk.CTkFont(family="Tahoma", size=12, weight="bold"))
        self.folder_label.grid(row=0, column=0, padx=(0, 10), sticky="w")

        self.folder_entry = ctk.CTkEntry(self.top_frame, textvariable=self.folder_path, font=ctk.CTkFont(family="Tahoma", size=12), height=32)
        self.folder_entry.grid(row=0, column=1, sticky="ew", padx=(0, 10))

        self.browse_btn = ctk.CTkButton(
            self.top_frame, text="เลือกโฟลเดอร์...", command=self.browse_folder,
            font=ctk.CTkFont(family="Tahoma", size=12), width=110, height=32,
            fg_color="#3b82f6", hover_color="#2563eb"
        )
        self.browse_btn.grid(row=0, column=2, sticky="e")

        # --- Main Workspace Panel ---
        self.main_workspace = ctk.CTkFrame(self, fg_color="#f8fafc", border_width=1, border_color="#cbd5e1", corner_radius=6)
        self.main_workspace.grid(row=1, column=0, sticky="nsew", padx=15, pady=5)
        self.main_workspace.grid_columnconfigure(0, weight=1)
        self.main_workspace.grid_rowconfigure(1, weight=1)

        # แผงแสดงสถานะการทำงาน (ฟอนต์ใหญ่ อ่านง่าย ชัดเจน)
        self.info_frame = ctk.CTkFrame(self.main_workspace, fg_color="transparent")
        self.info_frame.grid(row=0, column=0, sticky="ew", padx=10, pady=10)
        
        self.info_label = ctk.CTkLabel(
            self.info_frame, 
            text="ระบบจัดการชื่อไฟล์อัตโนมัติ: ลบแท็กขยะ ([n], [i], [!]), จัดช่องว่าง, และรักษารหัสภาษาไทย/อังกฤษ ([T-En] / [T-Th]) ให้เรียบร้อย", 
            font=ctk.CTkFont(family="Segoe UI", size=13, weight="bold"),
            text_color="#1e293b"
        )
        self.info_label.grid(row=0, column=0, sticky="w", padx=5)

        # ตารางแสดงรายการไฟล์ (Original / Preview / Size)
        self.table_frame = ctk.CTkFrame(self.main_workspace, fg_color="white", border_width=1, border_color="#cbd5e1")
        self.table_frame.grid(row=1, column=0, sticky="nsew", padx=10, pady=(0, 10))
        self.table_frame.grid_columnconfigure(0, weight=1)
        self.table_frame.grid_rowconfigure(0, weight=1)

        columns = ("original", "preview", "size")
        self.tree = ttk.Treeview(self.table_frame, columns=columns, show="headings", selectmode="extended")
        self.tree.heading("original", text="ชื่อไฟล์เดิม (Original)")
        self.tree.heading("preview", text="ชื่อไฟล์หลังจัดระเบียบ (Preview)")
        self.tree.heading("size", text="ขนาดไฟล์")
        
        self.tree.column("original", width=440, anchor="w")
        self.tree.column("preview", width=480, anchor="w")
        self.tree.column("size", width=100, anchor="center")

        tree_scroll = ttk.Scrollbar(self.table_frame, orient="vertical", command=self.tree.yview)
        self.tree.configure(yscrollcommand=tree_scroll.set)

        self.tree.grid(row=0, column=0, sticky="nsew")
        tree_scroll.grid(row=0, column=1, sticky="ns")

        # --- Bottom Panel: ปุ่มควบคุมการทำงาน ---
        self.bottom_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.bottom_frame.grid(row=2, column=0, sticky="ew", padx=15, pady=(5, 15))
        self.bottom_frame.grid_columnconfigure(1, weight=1)

        self.select_all_btn = ctk.CTkButton(self.bottom_frame, text="เลือกทั้งหมด", width=100, height=30, fg_color="#64748b", hover_color="#475569", command=self.select_all)
        self.select_all_btn.grid(row=0, column=0, padx=(0, 5))
        
        self.deselect_all_btn = ctk.CTkButton(self.bottom_frame, text="ยกเลิกเลือกทั้งหมด", width=110, height=30, fg_color="#64748b", hover_color="#475569", command=self.deselect_all)
        self.deselect_all_btn.grid(row=0, column=1, padx=5, sticky="w")

        self.execute_btn = ctk.CTkButton(
            self.bottom_frame, text="ดำเนินการเปลี่ยนชื่อ", command=self.start_rename,
            font=ctk.CTkFont(family="Tahoma", size=12, weight="bold"), height=34, width=170,
            fg_color="#10b981", hover_color="#059669"
        )
        self.execute_btn.grid(row=0, column=2, sticky="e")

    def browse_folder(self):
        dir_selected = filedialog.askdirectory()
        if dir_selected:
            self.folder_path.set(dir_selected)
            self.load_files_in_folder(dir_selected)

    def load_files_in_folder(self, path):
        for item in self.tree.get_children():
            self.tree.delete(item)
        try:
            files = os.listdir(path)
            valid_exts = (
                '.nes', '.gb', '.gbc', '.sfc', '.smc', '.bin', '.md', '.pce', 
                '.gba', '.nds', '.z64', '.n64', '.v64', '.gdi', '.zip', 
                '.cue', '.chd', '.iso', '.cso', '.rvz'
            )
            self.scanned_files = [f for f in files if os.path.isfile(os.path.join(path, f)) and f.lower().endswith(valid_exts)]
            
            for f in self.scanned_files:
                file_path = os.path.join(path, f)
                file_size = f"{os.path.getsize(file_path) / (1024*1024):.2f} MB"
                new_name = self.generate_new_name(f)
                self.tree.insert("", "end", values=(f, new_name, file_size))
        except Exception as e:
            messagebox.showerror("เกิดข้อผิดพลาด", f"ไม่สามารถอ่านโฟลเดอร์ได้: {e}")

    def generate_new_name(self, filename):
        name, ext = os.path.splitext(filename)
        
        # 1. รักษาสถานะภาษาเดิม [T-En] หรือ [T-Th]
        translation_tag = ""
        if re.search(r'\[T-En', name, flags=re.IGNORECASE):
            translation_tag = "[T-En]"
        elif re.search(r'\[T-Th', name, flags=re.IGNORECASE):
            translation_tag = "[T-Th]"

        # 2. ตัดเครดิตการแปลยาวๆ ออก
        clean_name = re.sub(r'\s*\[T-[A-Za-z0-9\s\-\.]+\]', '', name, flags=re.IGNORECASE)
        
        # 3. ลบแท็กขยะ [n], [i], [!] ออกอย่างหมดจด
        clean_name = re.sub(r'\s*\[[a-zA-Z!]\]', '', clean_name)
        
        # 4. จัดการช่องว่างและขีดล่าง
        clean_name = clean_name.replace("_", " ").strip()
        clean_name = re.sub(r'\s+', ' ', clean_name)
        
        # 5. คืนค่าป้ายภาษาเดิม หรือเติม (USA) ถ้าไม่มีโซน
        if translation_tag:
            clean_name = f"{clean_name} {translation_tag}"
        else:
            if not any(region in clean_name for region in ["(USA)", "(Japan)", "(Europe)", "(Asia)"]):
                clean_name = f"{clean_name} (USA)"
            
        return f"{clean_name}{ext}"

    def start_rename(self):
        current_path = self.folder_path.get()
        if not current_path or not self.scanned_files:
            messagebox.showwarning("แจ้งเตือน", "กรุณาเลือกโฟลเดอร์รอมก่อนดำเนินการ")
            return
        
        if messagebox.askyesno("ยืนยันการเปลี่ยนชื่อ", f"คุณต้องการเปลี่ยนชื่อไฟล์ทั้งหมด {len(self.scanned_files)} ไฟล์ ใช่หรือไม่?"):
            success = 0
            error = 0
            for item in self.tree.get_children():
                vals = self.tree.item(item, "values")
                old_name, new_name = vals[0], vals[1]
                old_path = os.path.join(current_path, old_name)
                new_path = os.path.join(current_path, new_name)
                try:
                    if old_path != new_path:
                        if os.path.exists(new_path):
                            error += 1
                            continue
                        os.rename(old_path, new_path)
                    success += 1
                except:
                    error += 1
            
            messagebox.showinfo("สำเร็จ", f"เปลี่ยนชื่อไฟล์สำเร็จทั้งหมด {success} ไฟล์! (ข้าม/ชื่อซ้ำ: {error})")
            self.load_files_in_folder(current_path)

    def select_all(self):
        for item in self.tree.get_children():
            self.tree.selection_add(item)

    def deselect_all(self):
        for item in self.tree.get_children():
            self.tree.selection_remove(item)

if __name__ == "__main__":
    app = ROMTidyApp()
    app.mainloop()