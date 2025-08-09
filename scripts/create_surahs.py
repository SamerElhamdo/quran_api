#!/usr/bin/env python3
"""
Create Surahs Script
إنشاء السور في قاعدة البيانات
"""

import sys
from pathlib import Path

# إضافة مسار المشروع إلى Python path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from app.extensions import db
from app.models.quran import Surah
from app import create_app


def create_surahs():
    """إنشاء جميع السور في قاعدة البيانات"""
    app = create_app()
    
    with app.app_context():
        print("جاري إنشاء السور...")
        
        # حذف السور الموجودة
        Surah.query.delete()
        
        # بيانات السور
        surahs_data = [
            {"id": 1, "name_arabic": "الفاتحة", "name_english": "Al-Fatiha", "total_ayahs": 7, "revelation_type": "Meccan", "juz": 1},
            {"id": 2, "name_arabic": "البقرة", "name_english": "Al-Baqarah", "total_ayahs": 286, "revelation_type": "Medinan", "juz": 1},
            {"id": 3, "name_arabic": "آل عمران", "name_english": "Aal-Imran", "total_ayahs": 200, "revelation_type": "Medinan", "juz": 3},
            {"id": 4, "name_arabic": "النساء", "name_english": "An-Nisa", "total_ayahs": 176, "revelation_type": "Medinan", "juz": 4},
            {"id": 5, "name_arabic": "المائدة", "name_english": "Al-Ma'idah", "total_ayahs": 120, "revelation_type": "Medinan", "juz": 6},
            {"id": 6, "name_arabic": "الأنعام", "name_english": "Al-An'am", "total_ayahs": 165, "revelation_type": "Meccan", "juz": 7},
            {"id": 7, "name_arabic": "الأعراف", "name_english": "Al-A'raf", "total_ayahs": 206, "revelation_type": "Meccan", "juz": 8},
            {"id": 8, "name_arabic": "الأنفال", "name_english": "Al-Anfal", "total_ayahs": 75, "revelation_type": "Medinan", "juz": 9},
            {"id": 9, "name_arabic": "التوبة", "name_english": "At-Tawbah", "total_ayahs": 129, "revelation_type": "Medinan", "juz": 10},
            {"id": 10, "name_arabic": "يونس", "name_english": "Yunus", "total_ayahs": 109, "revelation_type": "Meccan", "juz": 11},
            {"id": 11, "name_arabic": "هود", "name_english": "Hud", "total_ayahs": 123, "revelation_type": "Meccan", "juz": 11},
            {"id": 12, "name_arabic": "يوسف", "name_english": "Yusuf", "total_ayahs": 111, "revelation_type": "Meccan", "juz": 12},
            {"id": 13, "name_arabic": "الرعد", "name_english": "Ar-Ra'd", "total_ayahs": 43, "revelation_type": "Medinan", "juz": 13},
            {"id": 14, "name_arabic": "إبراهيم", "name_english": "Ibrahim", "total_ayahs": 52, "revelation_type": "Meccan", "juz": 13},
            {"id": 15, "name_arabic": "الحجر", "name_english": "Al-Hijr", "total_ayahs": 99, "revelation_type": "Meccan", "juz": 14},
            {"id": 16, "name_arabic": "النحل", "name_english": "An-Nahl", "total_ayahs": 128, "revelation_type": "Meccan", "juz": 14},
            {"id": 17, "name_arabic": "الإسراء", "name_english": "Al-Isra", "total_ayahs": 111, "revelation_type": "Meccan", "juz": 15},
            {"id": 18, "name_arabic": "الكهف", "name_english": "Al-Kahf", "total_ayahs": 110, "revelation_type": "Meccan", "juz": 15},
            {"id": 19, "name_arabic": "مريم", "name_english": "Maryam", "total_ayahs": 98, "revelation_type": "Meccan", "juz": 16},
            {"id": 20, "name_arabic": "طه", "name_english": "Ta-Ha", "total_ayahs": 135, "revelation_type": "Meccan", "juz": 16},
            {"id": 21, "name_arabic": "الأنبياء", "name_english": "Al-Anbiya", "total_ayahs": 112, "revelation_type": "Meccan", "juz": 17},
            {"id": 22, "name_arabic": "الحج", "name_english": "Al-Hajj", "total_ayahs": 78, "revelation_type": "Medinan", "juz": 17},
            {"id": 23, "name_arabic": "المؤمنون", "name_english": "Al-Mu'minun", "total_ayahs": 118, "revelation_type": "Meccan", "juz": 18},
            {"id": 24, "name_arabic": "النور", "name_english": "An-Nur", "total_ayahs": 64, "revelation_type": "Medinan", "juz": 18},
            {"id": 25, "name_arabic": "الفرقان", "name_english": "Al-Furqan", "total_ayahs": 77, "revelation_type": "Meccan", "juz": 19},
            {"id": 26, "name_arabic": "الشعراء", "name_english": "Ash-Shu'ara", "total_ayahs": 227, "revelation_type": "Meccan", "juz": 19},
            {"id": 27, "name_arabic": "النمل", "name_english": "An-Naml", "total_ayahs": 93, "revelation_type": "Meccan", "juz": 19},
            {"id": 28, "name_arabic": "القصص", "name_english": "Al-Qasas", "total_ayahs": 88, "revelation_type": "Meccan", "juz": 20},
            {"id": 29, "name_arabic": "العنكبوت", "name_english": "Al-Ankabut", "total_ayahs": 69, "revelation_type": "Meccan", "juz": 20},
            {"id": 30, "name_arabic": "الروم", "name_english": "Ar-Rum", "total_ayahs": 60, "revelation_type": "Meccan", "juz": 21},
            {"id": 31, "name_arabic": "لقمان", "name_english": "Luqman", "total_ayahs": 34, "revelation_type": "Meccan", "juz": 21},
            {"id": 32, "name_arabic": "السجدة", "name_english": "As-Sajdah", "total_ayahs": 30, "revelation_type": "Meccan", "juz": 21},
            {"id": 33, "name_arabic": "الأحزاب", "name_english": "Al-Ahzab", "total_ayahs": 73, "revelation_type": "Medinan", "juz": 21},
            {"id": 34, "name_arabic": "سبأ", "name_english": "Saba", "total_ayahs": 54, "revelation_type": "Meccan", "juz": 22},
            {"id": 35, "name_arabic": "فاطر", "name_english": "Fatir", "total_ayahs": 45, "revelation_type": "Meccan", "juz": 22},
            {"id": 36, "name_arabic": "يس", "name_english": "Ya-Sin", "total_ayahs": 83, "revelation_type": "Meccan", "juz": 22},
            {"id": 37, "name_arabic": "الصافات", "name_english": "As-Saffat", "total_ayahs": 182, "revelation_type": "Meccan", "juz": 23},
            {"id": 38, "name_arabic": "ص", "name_english": "Sad", "total_ayahs": 88, "revelation_type": "Meccan", "juz": 23},
            {"id": 39, "name_arabic": "الزمر", "name_english": "Az-Zumar", "total_ayahs": 75, "revelation_type": "Meccan", "juz": 23},
            {"id": 40, "name_arabic": "غافر", "name_english": "Ghafir", "total_ayahs": 85, "revelation_type": "Meccan", "juz": 23},
            {"id": 41, "name_arabic": "فصلت", "name_english": "Fussilat", "total_ayahs": 54, "revelation_type": "Meccan", "juz": 24},
            {"id": 42, "name_arabic": "الشورى", "name_english": "Ash-Shura", "total_ayahs": 53, "revelation_type": "Meccan", "juz": 24},
            {"id": 43, "name_arabic": "الزخرف", "name_english": "Az-Zukhruf", "total_ayahs": 89, "revelation_type": "Meccan", "juz": 24},
            {"id": 44, "name_arabic": "الدخان", "name_english": "Ad-Dukhan", "total_ayahs": 59, "revelation_type": "Meccan", "juz": 25},
            {"id": 45, "name_arabic": "الجاثية", "name_english": "Al-Jathiyah", "total_ayahs": 37, "revelation_type": "Meccan", "juz": 25},
            {"id": 46, "name_arabic": "الأحقاف", "name_english": "Al-Ahqaf", "total_ayahs": 35, "revelation_type": "Meccan", "juz": 25},
            {"id": 47, "name_arabic": "محمد", "name_english": "Muhammad", "total_ayahs": 38, "revelation_type": "Medinan", "juz": 26},
            {"id": 48, "name_arabic": "الفتح", "name_english": "Al-Fath", "total_ayahs": 29, "revelation_type": "Medinan", "juz": 26},
            {"id": 49, "name_arabic": "الحجرات", "name_english": "Al-Hujurat", "total_ayahs": 18, "revelation_type": "Medinan", "juz": 26},
            {"id": 50, "name_arabic": "ق", "name_english": "Qaf", "total_ayahs": 45, "revelation_type": "Meccan", "juz": 26},
            {"id": 51, "name_arabic": "الذاريات", "name_english": "Adh-Dhariyat", "total_ayahs": 60, "revelation_type": "Meccan", "juz": 27},
            {"id": 52, "name_arabic": "الطور", "name_english": "At-Tur", "total_ayahs": 49, "revelation_type": "Meccan", "juz": 27},
            {"id": 53, "name_arabic": "النجم", "name_english": "An-Najm", "total_ayahs": 62, "revelation_type": "Meccan", "juz": 27},
            {"id": 54, "name_arabic": "القمر", "name_english": "Al-Qamar", "total_ayahs": 55, "revelation_type": "Meccan", "juz": 27},
            {"id": 55, "name_arabic": "الرحمن", "name_english": "Ar-Rahman", "total_ayahs": 78, "revelation_type": "Meccan", "juz": 27},
            {"id": 56, "name_arabic": "الواقعة", "name_english": "Al-Waqi'ah", "total_ayahs": 96, "revelation_type": "Meccan", "juz": 28},
            {"id": 57, "name_arabic": "الحديد", "name_english": "Al-Hadid", "total_ayahs": 29, "revelation_type": "Medinan", "juz": 28},
            {"id": 58, "name_arabic": "المجادلة", "name_english": "Al-Mujadilah", "total_ayahs": 22, "revelation_type": "Medinan", "juz": 28},
            {"id": 59, "name_arabic": "الحشر", "name_english": "Al-Hashr", "total_ayahs": 24, "revelation_type": "Medinan", "juz": 28},
            {"id": 60, "name_arabic": "الممتحنة", "name_english": "Al-Mumtahanah", "total_ayahs": 13, "revelation_type": "Medinan", "juz": 28},
            {"id": 61, "name_arabic": "الصف", "name_english": "As-Saf", "total_ayahs": 14, "revelation_type": "Medinan", "juz": 29},
            {"id": 62, "name_arabic": "الجمعة", "name_english": "Al-Jumu'ah", "total_ayahs": 11, "revelation_type": "Medinan", "juz": 29},
            {"id": 63, "name_arabic": "المنافقون", "name_english": "Al-Munafiqun", "total_ayahs": 11, "revelation_type": "Medinan", "juz": 29},
            {"id": 64, "name_arabic": "التغابن", "name_english": "At-Taghabun", "total_ayahs": 18, "revelation_type": "Medinan", "juz": 29},
            {"id": 65, "name_arabic": "الطلاق", "name_english": "At-Talaq", "total_ayahs": 12, "revelation_type": "Medinan", "juz": 29},
            {"id": 66, "name_arabic": "التحريم", "name_english": "At-Tahrim", "total_ayahs": 12, "revelation_type": "Medinan", "juz": 30},
            {"id": 67, "name_arabic": "الملك", "name_english": "Al-Mulk", "total_ayahs": 30, "revelation_type": "Meccan", "juz": 29},
            {"id": 68, "name_arabic": "القلم", "name_english": "Al-Qalam", "total_ayahs": 52, "revelation_type": "Meccan", "juz": 29},
            {"id": 69, "name_arabic": "الحاقة", "name_english": "Al-Haqqah", "total_ayahs": 52, "revelation_type": "Meccan", "juz": 29},
            {"id": 70, "name_arabic": "المعارج", "name_english": "Al-Ma'arij", "total_ayahs": 44, "revelation_type": "Meccan", "juz": 29},
            {"id": 71, "name_arabic": "نوح", "name_english": "Nuh", "total_ayahs": 28, "revelation_type": "Meccan", "juz": 29},
            {"id": 72, "name_arabic": "الجن", "name_english": "Al-Jinn", "total_ayahs": 28, "revelation_type": "Meccan", "juz": 29},
            {"id": 73, "name_arabic": "المزمل", "name_english": "Al-Muzzammil", "total_ayahs": 20, "revelation_type": "Meccan", "juz": 29},
            {"id": 74, "name_arabic": "المدثر", "name_english": "Al-Muddathir", "total_ayahs": 56, "revelation_type": "Meccan", "juz": 29},
            {"id": 75, "name_arabic": "القيامة", "name_english": "Al-Qiyamah", "total_ayahs": 40, "revelation_type": "Meccan", "juz": 29},
            {"id": 76, "name_arabic": "الإنسان", "name_english": "Al-Insan", "total_ayahs": 31, "revelation_type": "Medinan", "juz": 29},
            {"id": 77, "name_arabic": "المرسلات", "name_english": "Al-Mursalat", "total_ayahs": 50, "revelation_type": "Meccan", "juz": 29},
            {"id": 78, "name_arabic": "النبأ", "name_english": "An-Naba", "total_ayahs": 40, "revelation_type": "Meccan", "juz": 30},
            {"id": 79, "name_arabic": "النازعات", "name_english": "An-Nazi'at", "total_ayahs": 46, "revelation_type": "Meccan", "juz": 30},
            {"id": 80, "name_arabic": "عبس", "name_english": "Abasa", "total_ayahs": 42, "revelation_type": "Meccan", "juz": 30},
            {"id": 81, "name_arabic": "التكوير", "name_english": "At-Takwir", "total_ayahs": 29, "revelation_type": "Meccan", "juz": 30},
            {"id": 82, "name_arabic": "الانفطار", "name_english": "Al-Infitar", "total_ayahs": 19, "revelation_type": "Meccan", "juz": 30},
            {"id": 83, "name_arabic": "المطففين", "name_english": "Al-Mutaffifin", "total_ayahs": 36, "revelation_type": "Meccan", "juz": 30},
            {"id": 84, "name_arabic": "الانشقاق", "name_english": "Al-Inshiqaq", "total_ayahs": 25, "revelation_type": "Meccan", "juz": 30},
            {"id": 85, "name_arabic": "البروج", "name_english": "Al-Buruj", "total_ayahs": 22, "revelation_type": "Meccan", "juz": 30},
            {"id": 86, "name_arabic": "الطارق", "name_english": "At-Tariq", "total_ayahs": 17, "revelation_type": "Meccan", "juz": 30},
            {"id": 87, "name_arabic": "الأعلى", "name_english": "Al-A'la", "total_ayahs": 19, "revelation_type": "Meccan", "juz": 30},
            {"id": 88, "name_arabic": "الغاشية", "name_english": "Al-Ghashiyah", "total_ayahs": 26, "revelation_type": "Meccan", "juz": 30},
            {"id": 89, "name_arabic": "الفجر", "name_english": "Al-Fajr", "total_ayahs": 30, "revelation_type": "Meccan", "juz": 30},
            {"id": 90, "name_arabic": "البلد", "name_english": "Al-Balad", "total_ayahs": 20, "revelation_type": "Meccan", "juz": 30},
            {"id": 91, "name_arabic": "الشمس", "name_english": "Ash-Shams", "total_ayahs": 15, "revelation_type": "Meccan", "juz": 30},
            {"id": 92, "name_arabic": "الليل", "name_english": "Al-Layl", "total_ayahs": 21, "revelation_type": "Meccan", "juz": 30},
            {"id": 93, "name_arabic": "الضحى", "name_english": "Ad-Duha", "total_ayahs": 11, "revelation_type": "Meccan", "juz": 30},
            {"id": 94, "name_arabic": "الشرح", "name_english": "Ash-Sharh", "total_ayahs": 8, "revelation_type": "Meccan", "juz": 30},
            {"id": 95, "name_arabic": "التين", "name_english": "At-Tin", "total_ayahs": 8, "revelation_type": "Meccan", "juz": 30},
            {"id": 96, "name_arabic": "العلق", "name_english": "Al-Alaq", "total_ayahs": 19, "revelation_type": "Meccan", "juz": 30},
            {"id": 97, "name_arabic": "القدر", "name_english": "Al-Qadr", "total_ayahs": 5, "revelation_type": "Meccan", "juz": 30},
            {"id": 98, "name_arabic": "البينة", "name_english": "Al-Bayyinah", "total_ayahs": 8, "revelation_type": "Medinan", "juz": 30},
            {"id": 99, "name_arabic": "الزلزلة", "name_english": "Az-Zalzalah", "total_ayahs": 8, "revelation_type": "Medinan", "juz": 30},
            {"id": 100, "name_arabic": "العاديات", "name_english": "Al-Adiyat", "total_ayahs": 11, "revelation_type": "Meccan", "juz": 30},
            {"id": 101, "name_arabic": "القارعة", "name_english": "Al-Qari'ah", "total_ayahs": 11, "revelation_type": "Meccan", "juz": 30},
            {"id": 102, "name_arabic": "التكاثر", "name_english": "At-Takathur", "total_ayahs": 8, "revelation_type": "Meccan", "juz": 30},
            {"id": 103, "name_arabic": "العصر", "name_english": "Al-Asr", "total_ayahs": 3, "revelation_type": "Meccan", "juz": 30},
            {"id": 104, "name_arabic": "الهمزة", "name_english": "Al-Humazah", "total_ayahs": 9, "revelation_type": "Meccan", "juz": 30},
            {"id": 105, "name_arabic": "الفيل", "name_english": "Al-Fil", "total_ayahs": 5, "revelation_type": "Meccan", "juz": 30},
            {"id": 106, "name_arabic": "قريش", "name_english": "Quraysh", "total_ayahs": 4, "revelation_type": "Meccan", "juz": 30},
            {"id": 107, "name_arabic": "الماعون", "name_english": "Al-Ma'un", "total_ayahs": 7, "revelation_type": "Meccan", "juz": 30},
            {"id": 108, "name_arabic": "الكوثر", "name_english": "Al-Kawthar", "total_ayahs": 3, "revelation_type": "Meccan", "juz": 30},
            {"id": 109, "name_arabic": "الكافرون", "name_english": "Al-Kafirun", "total_ayahs": 6, "revelation_type": "Meccan", "juz": 30},
            {"id": 110, "name_arabic": "النصر", "name_english": "An-Nasr", "total_ayahs": 3, "revelation_type": "Medinan", "juz": 30},
            {"id": 111, "name_arabic": "المسد", "name_english": "Al-Masad", "total_ayahs": 5, "revelation_type": "Meccan", "juz": 30},
            {"id": 112, "name_arabic": "الإخلاص", "name_english": "Al-Ikhlas", "total_ayahs": 4, "revelation_type": "Meccan", "juz": 30},
            {"id": 113, "name_arabic": "الفلق", "name_english": "Al-Falaq", "total_ayahs": 5, "revelation_type": "Meccan", "juz": 30},
            {"id": 114, "name_arabic": "الناس", "name_english": "An-Nas", "total_ayahs": 6, "revelation_type": "Meccan", "juz": 30}
        ]
        
        # إنشاء السور
        for surah_data in surahs_data:
            surah = Surah(**surah_data)
            db.session.add(surah)
        
        db.session.commit()
        print(f"✅ تم إنشاء {len(surahs_data)} سورة بنجاح!")


if __name__ == "__main__":
    try:
        create_surahs()
    except Exception as e:
        print(f"❌ خطأ في إنشاء السور: {str(e)}")
        sys.exit(1) 