import os
import platform
import subprocess
import shutil
import logging
import time
import glob
import ctypes
import threading

logging.basicConfig(level=logging.INFO, format='[ForensicWiper] %(message)s')

class ForensicWiper:
    def __init__(self):
        self.os_name = platform.system().lower()
        self.is_admin = self.check_admin()
        self.stop_wipe = threading.Event()

    def check_admin(self):
        try:
            if self.os_name == "windows":
                return ctypes.windll.shell32.IsUserAnAdmin() != 0
            else:
                return os.geteuid() == 0
        except Exception:
            return False

    def secure_delete(self, filepath, passes=3):
        """
        حذف آمن مع عدد تمريرات عشوائية لزيادة الصعوبة في الاسترجاع.
        """
        if os.path.isfile(filepath):
            try:
                length = os.path.getsize(filepath)
                with open(filepath, 'ba+', buffering=0) as f:
                    for _ in range(passes):
                        if self.stop_wipe.is_set():
                            logging.info("تم إيقاف عملية الحذف الآمن.")
                            return
                        f.seek(0)
                        f.write(os.urandom(length))
                os.remove(filepath)
                logging.info(f"✅ حذف آمن: {filepath}")
            except Exception as e:
                logging.warning(f"⚠️ فشل حذف {filepath}: {e}")

    def wipe_temp_files(self):
        logging.info("🔄 مسح الملفات المؤقتة...")
        paths = []
        if self.os_name == "windows":
            paths = [os.environ.get("TEMP"), os.environ.get("TMP")]
        else:
            paths = ["/tmp", "/var/tmp", "/dev/shm"]

        for path in paths:
            if path and os.path.exists(path):
                for root, dirs, files in os.walk(path):
                    if self.stop_wipe.is_set():
                        logging.info("تم إيقاف مسح الملفات المؤقتة.")
                        return
                    for file in files:
                        self.secure_delete(os.path.join(root, file))
                    for d in dirs:
                        try:
                            shutil.rmtree(os.path.join(root, d), ignore_errors=True)
                        except Exception as e:
                            logging.warning(f"⚠️ فشل حذف المجلد {d}: {e}")
                logging.info(f"✅ تم تنظيف: {path}")

    def clear_command_history(self):
        logging.info("🔄 مسح سجل الأوامر...")
        try:
            if self.os_name == "windows":
                history_file = os.path.expandvars(r'%APPDATA%\Microsoft\Windows\PowerShell\PSReadLine\ConsoleHost_history.txt')
                if os.path.exists(history_file):
                    self.secure_delete(history_file)
            else:
                history_files = [
                    "~/.bash_history", "~/.zsh_history", "~/.config/fish/fish_history"
                ]
                for hist in history_files:
                    if self.stop_wipe.is_set():
                        logging.info("تم إيقاف مسح سجل الأوامر.")
                        return
                    path = os.path.expanduser(hist)
                    if os.path.exists(path):
                        self.secure_delete(path)
                subprocess.call("history -c", shell=True)
        except Exception as e:
            logging.warning(f"⚠️ خطأ في مسح التاريخ: {e}")

    def wipe_logs(self):
        logging.info("🔄 مسح سجلات النظام...")
        logs = []
        if self.os_name == "windows":
            if self.is_admin:
                for logname in ["System", "Security", "Application"]:
                    try:
                        subprocess.run(["wevtutil", "cl", logname], check=True)
                        logging.info(f"✅ تم مسح سجل: {logname}")
                    except subprocess.CalledProcessError:
                        logging.warning(f"⚠️ فشل مسح سجل: {logname}")
            else:
                logging.warning("⚠️ تحتاج صلاحيات مسؤول لمسح سجلات Windows.")
        else:
            patterns = [
                "/var/log/*.log", "/var/log/**/*.log",
                "/var/log/wtmp", "/var/log/btmp", "/var/log/lastlog"
            ]
            for pattern in patterns:
                if self.stop_wipe.is_set():
                    logging.info("تم إيقاف مسح سجلات النظام.")
                    return
                logs.extend(glob.glob(pattern, recursive=True))
            for log in logs:
                self.secure_delete(log)

    def wipe_free_space(self, max_mb=500):
        logging.info("🔄 مسح المساحة الحرة (حتى {} ميجابايت)...".format(max_mb))
        try:
            dummy_path = "/tmp/wipefile" if self.os_name != "windows" else "C:\\wipefile.tmp"
            with open(dummy_path, 'wb') as f:
                total_written = 0
                chunk_size = 10 * 1024 * 1024  # 10 ميجابايت
                while total_written < max_mb * 1024 * 1024:
                    if self.stop_wipe.is_set():
                        logging.info("تم إيقاف مسح المساحة الحرة.")
                        break
                    f.write(os.urandom(chunk_size))
                    total_written += chunk_size
            logging.info("✅ تم مسح جزء من المساحة الحرة.")
        except Exception as e:
            logging.warning(f"⚠️ خطأ أثناء مسح المساحة الحرة: {e}")
        finally:
            if os.path.exists(dummy_path):
                try:
                    os.remove(dummy_path)
                    logging.info("✅ تم حذف الملف الوهمي لمسح المساحة الحرة.")
                except Exception as e:
                    logging.warning(f"⚠️ فشل حذف الملف الوهمي: {e}")

    def wipe_external_drive(self, drive_path, confirm=True):
        logging.info(f"⚠️ جاري مسح القرص الخارجي: {drive_path}")
        if confirm:
            user_input = input("هل أنت متأكد؟ اكتب YES للمتابعة: ").strip()
            if user_input != "YES":
                logging.info("❌ تم الإلغاء.")
                return
        try:
            if self.os_name == 'windows':
                subprocess.run(["cipher", "/w:" + drive_path], check=True)
            else:
                with open(drive_path, 'wb') as f:
                    block_size = 1024 * 1024
                    for _ in range(10000):  # يجب تعديل حسب حجم القرص فعليًا
                        if self.stop_wipe.is_set():
                            logging.info("تم إيقاف مسح القرص الخارجي.")
                            return
                        f.write(os.urandom(block_size))
            logging.info("✅ تم مسح القرص الخارجي بنجاح.")
        except Exception as e:
            logging.error(f"❌ فشل مسح القرص: {e}")

    def wipe_all(self):
        logging.info("🚨 بدء محو كامل الآثار...")
        if not self.is_admin:
            logging.warning("⚠️ تنبيه: بعض العمليات تتطلب صلاحيات المسؤول.")
        self.wipe_temp_files()
        self.clear_command_history()
        self.wipe_logs()
        self.wipe_free_space()
        logging.info("✅ تم محو جميع الآثار.")

    def stop(self):
        logging.info("🛑 إيقاف عملية المسح...")
        self.stop_wipe.set()

# --- واجهة برمجية لاستدعاء الوظائف بدون تفاعل ---

def run_wipe_all():
    wiper = ForensicWiper()
    wiper.wipe_all()

def run_wipe_temp():
    wiper = ForensicWiper()
    wiper.wipe_temp_files()

def run_clear_history():
    wiper = ForensicWiper()
    wiper.clear_command_history()

def run_wipe_logs():
    wiper = ForensicWiper()
    wiper.wipe_logs()

def run_wipe_free_space():
    wiper = ForensicWiper()
    wiper.wipe_free_space()

# --- واجهة تفاعلية اختيارية ---

def interactive_menu():
    wiper = ForensicWiper()
    while True:
        print("\n=== Forensic Wiper | قائمة المحو الآمن ===")
        print("1. محو الملفات المؤقتة")
        print("2. مسح سجل الأوامر")
        print("3. مسح سجلات النظام")
        print("4. مسح المساحة الحرة")
        print("5. مسح قرص خارجي")
        print("6. تنفيذ الكل")
        print("0. خروج")
        choice = input("اختر رقم العملية: ").strip()

        if choice == '1':
            wiper.wipe_temp_files()
        elif choice == '2':
            wiper.clear_command_history()
        elif choice == '3':
            wiper.wipe_logs()
        elif choice == '4':
            wiper.wipe_free_space()
        elif choice == '5':
            drive = input("أدخل مسار القرص الخارجي (/dev/sdX أو E:): ").strip()
            wiper.wipe_external_drive(drive)
        elif choice == '6':
            wiper.wipe_all()
        elif choice == '0':
            print("👋 وداعًا.")
            break
        else:
            print("❌ خيار غير صحيح. حاول مرة أخرى.")

if __name__ == "__main__":
    interactive_menu()
