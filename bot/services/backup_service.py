"""
سرویس پشتیبان‌گیری و بازیابی دیتابیس

دیتابیس ما یک فایل SQLite تکیه که روی Volume ذخیره میشه (روی Railway)
این ماژول اجازه میده ادمین:
۱- یه کپی از فایل فعلی دیتابیس بگیره (بک‌آپ) و دانلودش کنه
۲- یه فایل .db آپلود کنه و کاملاً جایگزین فایل فعلی بشه (ریستور)

نکته امنیتی: قبل از ریستور یه بک‌آپ خودکار از وضعیت فعلی می‌گیریم
تا اگه فایل آپلودی خراب بود بشه برگشت
"""

import os
import shutil
from datetime import datetime

from bot.config.settings import settings

BACKUP_DIR_NAME = "backups"


def _backup_dir() -> str:
    base = os.path.dirname(settings.db_path) or "."
    path = os.path.join(base, BACKUP_DIR_NAME)
    os.makedirs(path, exist_ok=True)
    return path


def create_backup_copy() -> str:
    """
    یه کپی فوری از فایل دیتابیس فعلی می‌سازه و مسیرش رو برمی‌گردونه
    این تابع sync هست چون فقط کپی فایله (نه query دیتابیس)
    """
    if not os.path.exists(settings.db_path):
        raise FileNotFoundError("فایل دیتابیس پیدا نشد")

    timestamp = datetime.utcnow().strftime("%Y%m%d_%H%M%S")
    backup_path = os.path.join(_backup_dir(), f"tiryaki_backup_{timestamp}.db")
    shutil.copyfile(settings.db_path, backup_path)
    return backup_path


def restore_from_file(uploaded_file_path: str) -> str:
    """
    فایل آپلودشده رو جایگزین فایل دیتابیس فعلی می‌کنه
    قبلش یه بک‌آپ خودکار از وضعیت فعلی می‌گیره (safety_backup)
    برمی‌گردونه مسیر بک‌آپ ایمنی که قبل از ریستور گرفته شد
    """
    safety_backup_path = None
    if os.path.exists(settings.db_path):
        timestamp = datetime.utcnow().strftime("%Y%m%d_%H%M%S")
        safety_backup_path = os.path.join(
            _backup_dir(), f"pre_restore_safety_{timestamp}.db"
        )
        shutil.copyfile(settings.db_path, safety_backup_path)

    shutil.copyfile(uploaded_file_path, settings.db_path)
    return safety_backup_path or ""


def list_backups() -> list[str]:
    backup_dir = _backup_dir()
    files = [f for f in os.listdir(backup_dir) if f.endswith(".db")]
    files.sort(reverse=True)
    return [os.path.join(backup_dir, f) for f in files]
