# نقاط الوصول (API Endpoints) - تطبيق تعلم القرآن

## نظرة عامة
التطبيق يعمل على المنفذ **5001** ويستخدم البادئة `/api/v1/` لجميع نقاط الوصول.

## نقاط الوصول المتاحة

### 1. المصادقة (Authentication) - `/api/v1/auth`

#### التسجيل
- **POST** `/api/v1/auth/register`
- **الوصف**: تسجيل مستخدم جديد
- **المعاملات المطلوبة**: 
  - `email_or_phone`: البريد الإلكتروني أو رقم الهاتف
  - `password`: كلمة المرور
  - `display_name`: اسم المستخدم المعروض
- **مثال**:
```bash
curl -X POST "http://localhost:5001/api/v1/auth/register" \
  -H "Content-Type: application/json" \
  -d '{"email_or_phone": "user@example.com", "password": "password123", "display_name": "User Name"}'
```

#### تسجيل الدخول
- **POST** `/api/v1/auth/login`
- **الوصف**: تسجيل دخول المستخدم
- **المعاملات المطلوبة**:
  - `email_or_phone`: البريد الإلكتروني أو رقم الهاتف
  - `password`: كلمة المرور
- **مثال**:
```bash
curl -X POST "http://localhost:5001/api/v1/auth/login" \
  -H "Content-Type: application/json" \
  -d '{"email_or_phone": "user@example.com", "password": "password123"}'
```

#### تحديث الرمز المميز
- **POST** `/api/v1/auth/refresh`
- **الوصف**: تحديث رمز الوصول باستخدام رمز التحديث
- **المعاملات المطلوبة**: `refresh_token` في الرأس

#### الملف الشخصي
- **GET** `/api/v1/auth/profile` - الحصول على الملف الشخصي
- **PUT** `/api/v1/auth/profile` - تحديث الملف الشخصي
- **POST** `/api/v1/auth/change-password` - تغيير كلمة المرور

### 2. المحتوى (Content) - `/api/v1/content`

#### السور
- **GET** `/api/v1/content/surah/{surah_id}`
- **الوصف**: الحصول على معلومات السورة
- **المعاملات**: `surah_id` (1-114)
- **مثال**:
```bash
curl "http://localhost:5001/api/v1/content/surah/1"
```

#### الآيات
- **GET** `/api/v1/content/surah/{surah_id}/ayah/{ayah_no}`
- **الوصف**: الحصول على معلومات آية محددة
- **المعاملات**: `surah_id` و `ayah_no`
- **مثال**:
```bash
curl "http://localhost:5001/api/v1/content/surah/1/ayah/1"
```

#### البحث
- **GET** `/api/v1/content/search?q={query}`
- **الوصف**: البحث في نص القرآن
- **المعاملات**: `q` (نص البحث)، `page`، `per_page`
- **مثال**:
```bash
curl "http://localhost:5001/api/v1/content/search?q=الفاتحة"
```

#### المقرئون
- **GET** `/api/v1/content/reciters` - قائمة المقرئين
- **GET** `/api/v1/content/reciters/{reciter_id}` - معلومات مقرئ محدد
- **مثال**:
```bash
curl "http://localhost:5001/api/v1/content/reciters"
curl "http://localhost:5001/api/v1/content/reciters/1"
```

#### رابط الصوت
- **GET** `/api/v1/content/audio-url`
- **الوصف**: الحصول على رابط الصوت لآية محددة
- **المعاملات**: `surah_id`، `ayah_no`، `reciter_id` (اختياري)
- **يتطلب**: مصادقة JWT

#### إعدادات المستخدم
- **GET** `/api/v1/content/user-settings` - الحصول على الإعدادات
- **PUT** `/api/v1/content/user-settings` - تحديث الإعدادات
- **يتطلب**: مصادقة JWT

### 3. قوائم التشغيل (Playlists) - `/api/v1/playlists`

#### إدارة القوائم
- **GET** `/api/v1/playlists/` - قائمة قوائم التشغيل
- **POST** `/api/v1/playlists/` - إنشاء قائمة جديدة
- **GET** `/api/v1/playlists/{playlist_id}` - تفاصيل قائمة محددة
- **PUT** `/api/v1/playlists/{playlist_id}` - تحديث قائمة
- **DELETE** `/api/v1/playlists/{playlist_id}` - حذف قائمة

#### عناصر القائمة
- **POST** `/api/v1/playlists/{playlist_id}/items` - إضافة عنصر
- **PUT** `/api/v1/playlists/{playlist_id}/items/{position}` - تحديث عنصر
- **DELETE** `/api/v1/playlists/{playlist_id}/items/{position}` - حذف عنصر
- **POST** `/api/v1/playlists/{playlist_id}/items/reorder` - إعادة ترتيب العناصر

**يتطلب جميع نقاط الوصول**: مصادقة JWT

### 4. المراجعة (Review) - `/api/v1/review`

#### قائمة المراجعة
- **GET** `/api/v1/review/queue` - قائمة المراجعة
- **GET** `/api/v1/review/queue/{item_id}` - تفاصيل عنصر مراجعة
- **POST** `/api/v1/review/queue/{item_id}/complete` - إكمال مراجعة
- **POST** `/api/v1/review/queue/{item_id}/skip` - تخطي مراجعة

#### إدارة المراجعة
- **POST** `/api/v1/review/generate` - إنشاء قائمة مراجعة جديدة
- **DELETE** `/api/v1/review/queue/clear-completed` - مسح المراجعات المكتملة
- **GET** `/api/v1/review/stats` - إحصائيات المراجعة

**يتطلب جميع نقاط الوصول**: مصادقة JWT

### 5. الإحصائيات (Stats) - `/api/v1/stats`

#### نظرة عامة
- **GET** `/api/v1/stats/overview` - إحصائيات عامة
- **GET** `/api/v1/stats/progress` - إحصائيات التقدم
- **GET** `/api/v1/stats/timeline` - الجدول الزمني
- **GET** `/api/v1/stats/achievements` - الإنجازات
- **GET** `/api/v1/stats/leaderboard` - لوحة المتصدرين

**يتطلب جميع نقاط الوصول**: مصادقة JWT

### 6. الإدارة (Admin) - `/api/v1/admin`

#### إدارة المستخدمين
- **GET** `/api/v1/admin/users` - قائمة المستخدمين
- **GET** `/api/v1/admin/users/{user_id}` - تفاصيل مستخدم
- **PUT** `/api/v1/admin/users/{user_id}` - تحديث مستخدم
- **DELETE** `/api/v1/admin/users/{user_id}` - حذف مستخدم

#### إدارة المقرئين
- **POST** `/api/v1/admin/reciters` - إنشاء مقرئ جديد
- **PUT** `/api/v1/admin/reciters/{reciter_id}` - تحديث مقرئ

#### إحصائيات النظام
- **GET** `/api/v1/admin/stats/overview` - إحصائيات النظام
- **GET** `/api/v1/admin/system/health` - صحة النظام

**يتطلب جميع نقاط الوصول**: مصادقة JWT + صلاحيات المدير

## ملاحظات مهمة

### المصادقة
- معظم نقاط الوصول تتطلب مصادقة JWT
- استخدم `Authorization: Bearer {token}` في رأس الطلب
- يمكن الحصول على الرمز من نقطة تسجيل الدخول

### التقييد
- بعض نقاط الوصول لديها قيود على عدد الطلبات
- التسجيل: 5 طلبات في الدقيقة
- تسجيل الدخول: 10 طلبات في الدقيقة
- إنشاء قوائم التشغيل: 10 طلبات في الدقيقة

### الترقيم
- معرفات السور: 1-114
- أرقام الآيات: تبدأ من 1
- معرفات المقرئين: تبدأ من 1

### الأخطاء
- `400`: خطأ في البيانات المرسلة
- `401`: غير مصرح (يتطلب مصادقة)
- `403`: ممنوع (يتطلب صلاحيات)
- `404`: المورد غير موجود
- `500`: خطأ داخلي في الخادم

## أمثلة على الاستخدام

### الحصول على معلومات سورة الفاتحة
```bash
curl "http://localhost:5001/api/v1/content/surah/1"
```

### البحث عن آيات تحتوي على كلمة "الرحمن"
```bash
curl "http://localhost:5001/api/v1/content/search?q=الرحمن"
```

### الحصول على قائمة المقرئين
```bash
curl "http://localhost:5001/api/v1/content/reciters"
```

### إنشاء قائمة تشغيل جديدة (يتطلب مصادقة)
```bash
curl -X POST "http://localhost:5001/api/v1/playlists/" \
  -H "Authorization: Bearer YOUR_JWT_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"title": "قائمة المراجعة اليومية"}'
``` 