#!/usr/bin/env python3
"""
Quran Import Script
يستورد القرآن الكريم من ملف quran.json المحلي إلى قاعدة البيانات
"""

import json
import sqlite3
import os
import sys
from pathlib import Path
from typing import Dict, List, Optional
import time

# إضافة مسار المشروع إلى Python path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from app.extensions import db
from app.models.quran import Reciter, AyahIndex
from app import create_app


class QuranImporter:
    """فئة لاستيراد القرآن الكريم"""
    
    def __init__(self):
        self.app = create_app()
        self.quran_data = {}
        self.reciters_data = []
        
    def load_quran_json(self) -> Dict:
        """تحميل بيانات القرآن من ملف quran.json المحلي"""
        quran_file = project_root / "quran.json"
        
        if not quran_file.exists():
            raise FileNotFoundError(f"ملف القرآن غير موجود: {quran_file}")
        
        print(f"جاري قراءة ملف القرآن: {quran_file}")
        
        with open(quran_file, 'r', encoding='utf-8') as f:
            return json.load(f)
    
    def download_reciters_data(self) -> List[Dict]:
        """تحميل بيانات القراء المعروفين"""
        reciters = [
            {
                "code": "mishary",
                "name": "مشاري العفاسي",
                "bitrate_kbps": 128,
                "base_url": "https://server8.mp3quran.net/mishary"
            },
            {
                "code": "sudais",
                "name": "عبد الرحمن السديس",
                "bitrate_kbps": 128,
                "base_url": "https://server8.mp3quran.net/sudais"
            },
            {
                "code": "ghamdi",
                "name": "سعد الغامدي",
                "bitrate_kbps": 128,
                "base_url": "https://server8.mp3quran.net/ghamdi"
            },
            {
                "code": "shuraim",
                "name": "سعود الشريم",
                "bitrate_kbps": 128,
                "base_url": "https://server8.mp3quran.net/shuraim"
            },
            {
                "code": "maher",
                "name": "ماهر المعيقلي",
                "bitrate_kbps": 128,
                "base_url": "https://server8.mp3quran.net/maher"
            }
        ]
        return reciters
    
    def create_surah_info(self) -> Dict[int, Dict]:
        """إنشاء معلومات السور"""
        surahs = {
            1: {"name_arabic": "الفاتحة", "name_english": "Al-Fatiha", "total_ayahs": 7, "revelation_type": "Meccan", "juz": 1},
            2: {"name_arabic": "البقرة", "name_english": "Al-Baqarah", "total_ayahs": 286, "revelation_type": "Medinan", "juz": 1},
            3: {"name_arabic": "آل عمران", "name_english": "Aal-Imran", "total_ayahs": 200, "revelation_type": "Medinan", "juz": 3},
            4: {"name_arabic": "النساء", "name_english": "An-Nisa", "total_ayahs": 176, "revelation_type": "Medinan", "juz": 4},
            5: {"name_arabic": "المائدة", "name_english": "Al-Ma'idah", "total_ayahs": 120, "revelation_type": "Medinan", "juz": 6},
            6: {"name_arabic": "الأنعام", "name_english": "Al-An'am", "total_ayahs": 165, "revelation_type": "Meccan", "juz": 7},
            7: {"name_arabic": "الأعراف", "name_english": "Al-A'raf", "total_ayahs": 206, "revelation_type": "Meccan", "juz": 8},
            8: {"name_arabic": "الأنفال", "name_english": "Al-Anfal", "total_ayahs": 75, "revelation_type": "Medinan", "juz": 9},
            9: {"name_arabic": "التوبة", "name_english": "At-Tawbah", "total_ayahs": 129, "revelation_type": "Medinan", "juz": 10},
            10: {"name_arabic": "يونس", "name_english": "Yunus", "total_ayahs": 109, "revelation_type": "Meccan", "juz": 11},
            # يمكن إضافة باقي السور هنا...
        }
        return surahs
    
    def calculate_page_number(self, surah_id: int, ayah_no: int) -> int:
        """حساب رقم الصفحة (تقريبي)"""
        # هذا حساب تقريبي - يمكن استخدام جدول دقيق من مصادر موثوقة
        base_pages = {
            1: 1, 2: 2, 3: 50, 4: 77, 5: 106, 6: 128, 7: 151, 8: 177, 9: 187, 10: 208
        }
        
        if surah_id in base_pages:
            base_page = base_pages[surah_id]
            # حساب تقريبي للصفحة بناءً على رقم الآية
            estimated_page = base_page + (ayah_no // 10)
            return max(1, estimated_page)
        
        # حساب عام
        return 1 + ((surah_id - 1) * 2) + (ayah_no // 15)
    
    def import_reciters(self) -> None:
        """استيراد القراء"""
        with self.app.app_context():
            print("جاري استيراد القراء...")
            
            # حذف القراء الموجودين
            Reciter.query.delete()
            
            for reciter_data in self.reciters_data:
                reciter = Reciter(**reciter_data)
                db.session.add(reciter)
            
            db.session.commit()
            print(f"✅ تم استيراد {len(self.reciters_data)} قارئ")
    
    def import_quran_text(self, quran_data: Dict) -> None:
        """استيراد نص القرآن من ملف quran.json"""
        with self.app.app_context():
            print("جاري استيراد نص القرآن...")
            
            # حذف البيانات الموجودة
            AyahIndex.query.delete()
            
            total_verses = 0
            
            # استخراج الآيات من البيانات
            for surah_id_str, verses in quran_data.items():
                surah_id = int(surah_id_str)
                print(f"جاري معالجة السورة {surah_id}...")
                
                for verse in verses:
                    chapter = verse.get('chapter')
                    verse_number = verse.get('verse')
                    text_arabic = verse.get('text', '')
                    
                    if chapter and verse_number and text_arabic:
                        page = self.calculate_page_number(chapter, verse_number)
                        
                        ayah_index = AyahIndex(
                            surah_id=chapter,
                            ayah_no=verse_number,
                            text_plain=text_arabic,
                            page=page
                        )
                        db.session.add(ayah_index)
                        total_verses += 1
                
                # حفظ كل 100 آية لتجنب استهلاك الذاكرة
                if total_verses % 100 == 0:
                    db.session.commit()
                    print(f"تم حفظ {total_verses} آية...")
            
            # حفظ باقي الآيات
            db.session.commit()
            print(f"✅ تم استيراد {total_verses} آية بنجاح!")
    
    def run_import(self) -> None:
        """تشغيل عملية الاستيراد"""
        try:
            print("🚀 بدء استيراد القرآن الكريم...")
            
            # تحميل بيانات القرآن
            self.quran_data = self.load_quran_json()
            
            # استيراد القراء
            self.reciters_data = self.download_reciters_data()
            self.import_reciters()
            
            # استيراد القرآن
            self.import_quran_text(self.quran_data)
            
            print("✅ تم استيراد القرآن بنجاح!")
            
        except Exception as e:
            print(f"❌ خطأ في الاستيراد: {str(e)}")
            raise


def main():
    """الدالة الرئيسية"""
    import argparse
    
    parser = argparse.ArgumentParser(description="استيراد القرآن الكريم من ملف quran.json")
    parser.add_argument("--test", action="store_true", help="تشغيل في وضع الاختبار")
    
    args = parser.parse_args()
    
    importer = QuranImporter()
    
    if args.test:
        print("🧪 تشغيل في وضع الاختبار...")
        # يمكن إضافة اختبارات هنا
        return
    
    try:
        importer.run_import()
    except KeyboardInterrupt:
        print("\n⏹️ تم إيقاف العملية بواسطة المستخدم")
    except Exception as e:
        print(f"❌ فشل الاستيراد: {str(e)}")
        sys.exit(1)


if __name__ == "__main__":
    main() 