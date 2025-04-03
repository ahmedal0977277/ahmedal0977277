import sys
import os
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtGui import *
import subprocess
import platform

class MTKRootTool(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("MTK Root Tool - MTK Client Edition")
        self.setWindowIcon(QIcon('icon.ico'))
        self.setup_ui()
        
        # متغيرات الأداة
        self.scatter_file = ""
        self.boot_img = ""
        self.patched_boot = ""
        
    def setup_ui(self):
        # إنشاء التبويبات
        tabs = QTabWidget()
        
        # تبويب الروت الرئيسي
        root_tab = QWidget()
        root_layout = QVBoxLayout()
        
        # عناصر واجهة الروت
        self.status_label = QLabel("الحالة: جاهز")
        self.progress = QProgressBar()
        
        btn_setup = QPushButton("إعداد البيئة")
        btn_setup.clicked.connect(self.setup_environment)
        
        btn_select_files = QPushButton("اختر ملفات الروت")
        btn_select_files.clicked.connect(self.select_files)
        
        btn_patch = QPushButton("تعديل boot.img")
        btn_patch.clicked.connect(self.patch_boot)
        
        btn_flash = QPushButton("فلاش الروت")
        btn_flash.clicked.connect(self.flash_phone)
        
        # إضافة العناصر للواجهة
        root_layout.addWidget(self.status_label)
        root_layout.addWidget(self.progress)
        root_layout.addWidget(btn_setup)
        root_layout.addWidget(btn_select_files)
        root_layout.addWidget(btn_patch)
        root_layout.addWidget(btn_flash)
        root_tab.setLayout(root_layout)
        
        # تبويب الإعدادات
        settings_tab = QWidget()
        settings_layout = QVBoxLayout()
        
        # ... (إضافة عناصر الإعدادات هنا)
        
        settings_tab.setLayout(settings_layout)
        
        # إضافة التبويبات
        tabs.addTab(root_tab, "الروت")
        tabs.addTab(settings_tab, "الإعدادات")
        
        self.setCentralWidget(tabs)
    
    def setup_environment(self):
        self.update_status("جارٍ إعداد البيئة...")
        
        # تثبيت متطلبات MTK Client
        try:
            if platform.system() == "Windows":
                subprocess.run(["pip", "install", "mtk"], check=True)
            else:
                subprocess.run(["pip3", "install", "mtk"], check=True)
                
            self.update_status("تم إعداد البيئة بنجاح")
            QMessageBox.information(self, "تم", "تم تثبيت MTK Client بنجاح!")
        except Exception as e:
            self.show_error(f"فشل إعداد البيئة: {str(e)}")
    
    def select_files(self):
        # اختيار ملف scatter
        scatter, _ = QFileDialog.getOpenFileName(self, "اختر ملف scatter.txt", "", "Text Files (*.txt)")
        if scatter:
            self.scatter_file = scatter
            
        # اختيار ملف boot.img
        boot, _ = QFileDialog.getOpenFileName(self, "اختر ملف boot.img", "", "Image Files (*.img)")
        if boot:
            self.boot_img = boot
            
        self.update_status("تم تحميل الملفات المطلوبة")
    
    def patch_boot(self):
        if not self.boot_img:
            self.show_error("الرجاء اختيار ملف boot.img أولاً")
            return
            
        self.update_status("جارٍ تعديل boot.img...")
        
        try:
            # استخدام Magisk لتعديل boot.img
            result = subprocess.run(["magisk", "--patch", self.boot_img], 
                                   capture_output=True, text=True)
            
            if "Failed" in result.stderr:
                raise Exception(result.stderr)
                
            self.patched_boot = "magisk_patched.img"
            self.update_status("تم تعديل boot.img بنجاح")
            QMessageBox.information(self, "تم", "تم تعديل ملف boot.img بنجاح!")
        except Exception as e:
            self.show_error(f"فشل تعديل boot.img: {str(e)}")
    
    def flash_phone(self):
        if not all([self.scatter_file, self.patched_boot]):
            self.show_error("الرجاء اختيار جميع الملفات المطلوبة")
            return
            
        self.update_status("جارٍ فلاش الروت...")
        
        try:
            # استخدام MTK Client للفلاش
            cmd = [
                "mtk",
                "rl",
                "boot_a",
                self.patched_boot,
                "--scatter",
                self.scatter_file
            ]
            
            process = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            
            while True:
                output = process.stdout.readline()
                if output == b'' and process.poll() is not None:
                    break
                if output:
                    self.update_status(output.decode().strip())
            
            self.update_status("تم فلاش الروت بنجاح!")
            QMessageBox.information(self, "تم", "تم عمل روت للجهاز بنجاح!")
        except Exception as e:
            self.show_error(f"فشل عملية الفلاش: {str(e)}")
    
    def update_status(self, message):
        self.status_label.setText(f"الحالة: {message}")
        QApplication.processEvents()
    
    def show_error(self, message):
        QMessageBox.critical(self, "خطأ", message)
        self.update_status("خطأ: " + message)

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MTKRootTool()
    window.show()
    sys.exit(app.exec_())