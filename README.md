# 📖 Quran Learning API

تطبيق خلفي متقدم لتعلم القرآن الكريم وحفظه، مبني باستخدام Flask مع واجهة برمجة REST API شاملة.

## 🌟 المميزات

- **نظام مصادقة متقدم** مع JWT tokens
- **إدارة المستخدمين** مع أدوار مختلفة (طالب، معلم، مدير)
- **تتبع التقدم** في حفظ القرآن
- **قوائم التشغيل** المخصصة
- **نظام المراجعة** الذكي
- **إدارة القراء** والاستماع
- **نظام التنزيلات** للمحتوى
- **إحصائيات مفصلة** للتقدم
- **واجهة إدارية** شاملة
- **دعم متعدد اللغات** (العربية والإنجليزية)

## 🏗️ البنية التقنية

### التقنيات المستخدمة
- **Backend Framework**: Flask 3.0+
- **Database**: SQLite (Development) / PostgreSQL (Production)
- **ORM**: SQLAlchemy 2.0+
- **Authentication**: JWT Extended
- **API Documentation**: Flask-Smorest
- **Rate Limiting**: Flask-Limiter
- **Password Hashing**: Argon2
- **Task Scheduling**: APScheduler
- **CORS Support**: Flask-CORS

### متطلبات النظام
- Python 3.11+
- SQLite 3.x (Development)
- PostgreSQL 12+ (Production)

## 🚀 التثبيت والتشغيل

### 1. استنساخ المشروع
```bash
git clone <repository-url>
cd quran_api
```

### 2. إنشاء البيئة الافتراضية
```bash
python -m venv venv
source venv/bin/activate  # على Linux/Mac
# أو
venv\Scripts\activate     # على Windows
```

### 3. تثبيت المتطلبات
```bash
pip install -r requirements.txt
```

### 4. إعداد متغيرات البيئة
```bash
cp env.example .env
# قم بتعديل ملف .env حسب إعداداتك
```

### 5. تهيئة قاعدة البيانات
```bash
flask db init
flask db migrate -m "Initial migration"
flask db upgrade
```

### 6. تشغيل التطبيق
```bash
# بيئة التطوير
python run.py

# أو مع متغير المنفذ
PORT=5001 python run.py

# بيئة الإنتاج
gunicorn -w 4 -b 0.0.0.0:5000 wsgi:app
```

## 📁 بنية المشروع

```
quran_api/
├── app/                    # التطبيق الرئيسي
│   ├── __init__.py        # تهيئة التطبيق
│   ├── config.py          # إعدادات التطبيق
│   ├── extensions.py      # إضافات Flask
│   ├── admin/             # مسارات الإدارة
│   ├── auth/              # نظام المصادقة
│   ├── content/           # إدارة المحتوى
│   ├── models/            # نماذج قاعدة البيانات
│   ├── playlists/         # إدارة قوائم التشغيل
│   ├── review/            # نظام المراجعة
│   ├── schemas/           # مخططات البيانات
│   ├── settings/          # إعدادات المستخدم
│   ├── stats/             # الإحصائيات
│   └── utils/             # الأدوات المساعدة
├── migrations/             # ترحيلات قاعدة البيانات
├── tests/                  # اختبارات الوحدة
├── scripts/                # سكريبتات مساعدة
├── requirements.txt        # متطلبات Python
├── pyproject.toml         # إعدادات المشروع
├── run.py                 # تشغيل التطبيق
└── wsgi.py                # نقطة الدخول للإنتاج
```

## 🔐 نماذج قاعدة البيانات

### المستخدمون (Users)
- معلومات الحساب الأساسية
- أدوار المستخدم (طالب، معلم، مدير)
- إعدادات اللغة والمنطقة الزمنية

### إعدادات المستخدم (UserSettings)
- اختيار القارئ المفضل
- سرعة التشغيل الافتراضية
- تفعيل قواعد التجويد
- حجم الخط

### التقدم (Progress)
- تتبع حفظ السور والآيات
- تاريخ الحفظ والمراجعة
- مستوى الإتقان

### قوائم التشغيل (Playlists)
- قوائم مخصصة للحفظ
- ترتيب السور والآيات
- مشاركة القوائم

### المراجعة (Review)
- جدول المراجعة التلقائي
- توقيت المراجعة
- تتبع النسيان

## 🌐 واجهة البرمجة (API)

### المصادقة (Authentication)
```
POST /api/v1/auth/register          # تسجيل مستخدم جديد
POST /api/v1/auth/login             # تسجيل الدخول
POST /api/v1/auth/refresh           # تحديث التوكن
GET  /api/v1/auth/profile           # الملف الشخصي
PUT  /api/v1/auth/profile           # تحديث الملف
POST /api/v1/auth/change-password   # تغيير كلمة المرور
```

### المحتوى (Content)
```
GET  /api/v1/content/reciters                    # قائمة القراء
GET  /api/v1/content/reciters/{id}               # تفاصيل القارئ
GET  /api/v1/content/search                      # البحث في القرآن
GET  /api/v1/content/surah/{id}                  # معلومات السورة
GET  /api/v1/content/ayah/{surah_id}/{ayah_no}   # معلومات الآية
```

### التقدم (Progress)
```
GET  /api/v1/progress/                           # ملخص التقدم
POST /api/v1/progress/memorize                    # تسجيل حفظ جديد
PUT  /api/v1/progress/update                      # تحديث التقدم
GET  /api/v1/progress/surah/{id}                  # تقدم سورة محددة
```

### قوائم التشغيل (Playlists)
```
GET  /api/v1/playlists/                          # قوائم المستخدم
POST /api/v1/playlists/                          # إنشاء قائمة جديدة
GET  /api/v1/playlists/{id}                      # تفاصيل القائمة
PUT  /api/v1/playlists/{id}                      # تحديث القائمة
DELETE /api/v1/playlists/{id}                    # حذف القائمة
```

### المراجعة (Review)
```
GET  /api/v1/review/queue                         # قائمة المراجعة
POST /api/v1/review/mark-reviewed                 # تسجيل المراجعة
GET  /api/v1/review/schedule                      # جدول المراجعة
```

### الإحصائيات (Statistics)
```
GET  /api/v1/stats/overview                      # نظرة عامة
GET  /api/v1/stats/daily                          # إحصائيات يومية
GET  /api/v1/stats/weekly                         # إحصائيات أسبوعية
GET  /api/v1/stats/monthly                        # إحصائيات شهرية
```

### الإدارة (Admin)
```
GET  /api/v1/admin/users                          # إدارة المستخدمين
PUT  /api/v1/admin/users/{id}/role                # تغيير دور المستخدم
GET  /api/v1/admin/stats                          # إحصائيات النظام
```

## 🔧 الإعدادات

### متغيرات البيئة
```bash
# إعدادات التطبيق
FLASK_APP=run.py
FLASK_ENV=development
SECRET_KEY=your-secret-key-here

# قاعدة البيانات
DATABASE_URL=sqlite:///instance/quran_dev.db  # للتطوير
# DATABASE_URL=postgresql://user:pass@localhost/quran_db  # للإنتاج

# JWT
JWT_SECRET_KEY=your-jwt-secret
JWT_ACCESS_TOKEN_EXPIRES=3600  # ساعة واحدة
JWT_REFRESH_TOKEN_EXPIRES=2592000  # 30 يوم

# Rate Limiting
RATELIMIT_STORAGE_URL=memory://
RATELIMIT_DEFAULT=100/hour
```

## 🧪 الاختبارات

### تشغيل الاختبارات
```bash
# تشغيل جميع الاختبارات
pytest

# مع تقرير التغطية
pytest --cov=quran_api --cov-report=html

# اختبارات محددة
pytest tests/test_auth.py
pytest tests/test_content.py
```

### اختبارات API
```bash
# اختبار تسجيل مستخدم جديد
curl -X POST http://localhost:5001/api/v1/auth/register \
  -H "Content-Type: application/json" \
  -d '{
    "email_or_phone": "test@example.com",
    "password": "test123",
    "display_name": "Test User"
  }'

# اختبار تسجيل الدخول
curl -X POST http://localhost:5001/api/v1/auth/login \
  -H "Content-Type: application/json" \
  -d '{
    "email_or_phone": "test@example.com",
    "password": "test123"
  }'
```

## 📊 قاعدة البيانات

### إنشاء قاعدة البيانات
```bash
# تهيئة الترحيلات
flask db init

# إنشاء ترحيل جديد
flask db migrate -m "Description of changes"

# تطبيق الترحيلات
flask db upgrade

# التراجع عن آخر ترحيل
flask db downgrade
```

### استيراد البيانات الأولية
```bash
# إضافة قراء (مثال)
python scripts/seed_data.py

# أو عبر Flask shell
flask shell
>>> from app.models.quran import Reciter
>>> from app.extensions import db
>>> reciter = Reciter(code="mishary", name="مشاري العفاسي", bitrate_kbps=128, base_url="https://example.com/audio/")
>>> db.session.add(reciter)
>>> db.session.commit()
```

## 🚀 النشر والإنتاج

### استخدام Gunicorn
```bash
gunicorn -w 4 -b 0.0.0.0:5000 --timeout 120 wsgi:app
```

### استخدام Docker (اختياري)
```dockerfile
FROM python:3.11-slim

WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt

COPY . .
EXPOSE 5000

CMD ["gunicorn", "-w", "4", "-b", "0.0.0.0:5000", "wsgi:app"]
```

### متغيرات الإنتاج
```bash
FLASK_ENV=production
DATABASE_URL=postgresql://user:pass@localhost/quran_db
SECRET_KEY=very-long-secure-secret-key
JWT_SECRET_KEY=very-long-secure-jwt-key
```

## 🤝 المساهمة

1. Fork المشروع
2. إنشاء فرع للميزة الجديدة (`git checkout -b feature/AmazingFeature`)
3. Commit التغييرات (`git commit -m 'Add some AmazingFeature'`)
4. Push إلى الفرع (`git push origin feature/AmazingFeature`)
5. فتح Pull Request

## 📝 الترخيص

هذا المشروع مرخص تحت رخصة MIT. راجع ملف `LICENSE` للتفاصيل.

## 📞 الدعم

- **المطور**: Quran Learn Team
- **البريد الإلكتروني**: support@quranlearn.com
- **المسائل**: [GitHub Issues](https://github.com/quranlearn/quran-api/issues)
- **التوثيق**: [API Documentation](https://docs.quranlearn.com)

## 🙏 الشكر

شكر خاص لجميع المساهمين والمطورين الذين ساعدوا في تطوير هذا المشروع.

---

**ملاحظة**: هذا التطبيق مصمم خصيصاً لتعلم القرآن الكريم وحفظه. يرجى استخدامه باحترام وتقدير للكتاب المقدس. 