# 🐾 PawConnect — Animal Shelter Adoption & Medical Passport System

[![FastAPI](https://img.shields.io/badge/FastAPI-0.110+-009688.svg?style=flat&logo=fastAPI&logoColor=white)](https://fastapi.tiangolo.com)
[![Python](https://img.shields.io/badge/Python-3.12%20%7C%203.14-3776AB.svg?style=flat&logo=python&logoColor=white)](https://www.python.org)
[![TailwindCSS](https://img.shields.io/badge/Tailwind_CSS-3.4-38B2AC.svg?style=flat&logo=tailwind-css&logoColor=white)](https://tailwindcss.com)
[![License](https://img.shields.io/badge/Competition-Atlantia_SW01-orange.svg)]()

> **PawConnect** sığınacaqlardakı heyvanların profillərini, rəqəmsal peyvənd pasportlarını və sahibləndirmə müraciətlərini vahid platformada idarə edən tamfunksiyalı (full-stack) veb sistemdir.  
> **Atlântia International STEM Olympiad (Category SW01: Software Projects)** tələblərinə və qaydalarına tam uyğunlaşdırılmışdır.

---

## 🌟 Əsas Xüsusiyyətlər (Core Features)

1. **Axtarış və Çoxmeyarlı Filtrlər (Pet Catalog):**
   * Növ (İt, Pişik, Dovşan, Quş), Cinsiyyət, Ölçü, Sığınacaq və Açar sözlərlə axtarış.
2. **Rəqəmsal Tibbi Pasport (Digital Medical Passport):**
   * Hər heyvanın quduzluq, parazit və kompleks peyvəndlərinin vurulma tarixi, növbəti doza vaxtı, partiya nömrəsi və təsdiq edən baytar həkim qeydi.
   * Çap edilə bilən rəsmi pasport formatı.
3. **Smart Matcher Alqoritmi (Ağıllı Seçim):**
   * Ailənin mənzil sahəsi (mənzil / həyətli ev), aktivlik dərəcəsi və evdə uşaq/heyvan olub-olmamasını nəzərə alaraq ən uyğun heyvanları faiz dərəcəsi ilə tövsiyə edir.
4. **Sığınacaq İdarəetmə Paneli (Shelter Management Dashboard):**
   * Canlı KPI göstəriciləri (Bazada olan heyvanlar, daxil olan müraciətlər, sahibləndirilənlər, vaxtı keçən peyvəndlər).
   * Müraciətlərin bir kliklə təsdiqi / imtinası və heyvanın statusunun avtomatik yenilənməsi.
   * Bazaya yeni heyvan və tibbi qeydlərin əlavə olunması forması.
5. **3 Dilli İnterfeys (Multilingual):**
   * **Azərbaycan (AZ)**, **İngilis (EN)** və **Rus (RU)** dillərində tam lokallaşdırma.
6. **Avtomatlaşdırılmış Testlər (Automated Test Suite):**
   * `pytest` ilə bütün səhifə və API marşrutlarının 100% testlərlə əhatə olunması.

---

## 🚀 Layihəni Kompüterdə İşə Salmaq (Local / Offline Run)

Atlântia qaydası **SW01.5.9** tələbinə əsasən, yarış məkanında internet olmasa belə sistem yerli kompüterdə 100% tam rejimdə işləyir.

### Metod 1: Tək Kliklə (Tövsiyə olunur)
Windows-da layihə qovluğunda olan `run_offline.bat` faylını iki dəfə klikləyin. Server işə düşəcək və brauzer avtomatik açılacaq:
```
http://localhost:8000
```

### Metod 2: Terminal ilə (PowerShell / CMD)
```powershell
# 1. Virtual mühiti aktivləşdirin
.\venv\Scripts\Activate.ps1

# 2. Serveri işə salın
uvicorn app.main:app --reload --port 8000
```

---

## 🧪 Avtomatlaşdırılmış Testlərin İşə Salınması

Münsiflərə kodun etibarlılığını və sabitliyini (Functionality & Stability — 30 bal) nümayiş etdirmək üçün:
```powershell
.\venv\Scripts\python -m pytest -v
```
Bütün 7 əsas test uğurla (`PASSED`) icra olunacaq.

---

## 🌐 Saytı İnternetdə Canlıya Yerləşdirmək (Cloud Deployment Guide)

Layihə **Render.com** və ya **Railway** platformalarında **pulsuz** yerləşdirilmək üçün tam konfiqurasiya edilib (`render.yaml` və `Dockerfile` daxildir).

### Addım-addım Render.com Təlimatı:
1. Layihə qovluğunu GitHub-a yükləyin (və ya `git push` edin):
   ```bash
   git init
   git add .
   git commit -m "PawConnect initial release"
   # GitHub repozitoriyanıza bağlayın və push edin
   ```
2. [Render.com](https://render.com) saytında qeydiyyatdan keçin (GitHub ilə daxil olun).
3. **New +** düyməsini sıxın və **Web Service** seçin.
4. GitHub-dakı `PawConnect` repozitoriyanızı seçin.
5. Aşağıdakı ayarları daxil edin:
   * **Name:** `pawconnect`
   * **Runtime:** `Python 3`
   * **Build Command:** `pip install -r requirements.txt`
   * **Start Command:** `uvicorn app.main:app --host 0.0.0.0 --port $PORT`
6. **Create Web Service** düyməsini sıxın. 2-3 dəqiqə ərzində saytınız canlı linkdə (məsələn: `https://pawconnect.onrender.com`) fəaliyyətə başlayacaq!

---

## 📂 Layihənin Qovluq Quruluşu (Folder Structure)

```
PawConnect/
│
├── app/
│   ├── database.py         # SQLite / PostgreSQL verilənlər bazası bağlantısı
│   ├── models.py           # SQLAlchemy cədvəl modelləri (Shelter, Pet, Vaccine, Application)
│   ├── schemas.py          # Pydantic V2 giriş-çıxış validasiyası
│   ├── i18n.py             # 3 dilli lüğət (Azərbaycan, İngilis, Rus)
│   ├── seed.py             # 25+ real heyvan, peyvənd və sığınacaq bazası generasiyası
│   ├── main.py             # FastAPI əsas tətbiqi, CORS və statik fayllar
│   ├── routers/
│   │   ├── pages.py        # Veb səhifələrin Jinja2 şablonları
│   │   ├── api_pets.py     # Heyvanların REST API-si
│   │   ├── api_adoptions.py# Sahibləndirmə müraciətləri və status sinxronizasiyası
│   │   ├── api_vaccines.py # Peyvənd pasportu və vaxtı keçən vaksin xəbərdarlıqları
│   │   ├── api_quiz.py     # Smart Matcher uyğunluq hesablama mühərriki
│   │   └── api_shelters.py # Sığınacaqların siyahısı və məlumatları
│   └── templates/          # HTML interfeys şablonları (Tailwind CSS)
│       ├── base.html       # Ümumi naviqasiya və dil seçici
│       ├── index.html      # Ana səhifə, statistika və vitrin
│       ├── pets.html       # Axtarış və filtrləmə kataloqu
│       ├── pet_detail.html # Heyvan profili, tibbi pasport və müraciət forması
│       ├── quiz.html       # Ağıllı uyğunlaşdırma testi
│       ├── admin.html      # Sığınacaq idarəetmə paneli
│       └── about.html      # STEM Olimpiada haqqında məlumat
│
├── tests/
│   └── test_pawconnect.py  # Pytest avtomatlaşdırılmış test dəsti
│
├── ARCHITECTURE.md         # SW01.5 D5 Arxitektura hesabatı (Mermaid diaqramları ilə)
├── STUDENT_DEFENSE_GUIDE.md# 10-14 yaşlı şagirdlər üçün 3 dəqiqəlik çıxış ssenarisi və sual-cavablar
├── run_offline.bat         # Olimpiada üçün internetsiz tək kliklə başlatma
├── run_offline.ps1         # PowerShell başlatma skripti
├── Dockerfile              # Konteynerizasiya faylı
├── render.yaml             # Render.com avtomatik deploy konfiqurasiyası
├── requirements.txt        # Python asılılıqları
└── README.md               # Əsas bələdçi sənəd
```

---

## 🏆 Atlântia STEM Olympiad — Qiymətləndirmə Meyarlarına Uyğunluq

| Meyar (SW01.6.1) | Maks. Bal | PawConnect Həlli |
| :--- | :---: | :--- |
| **Funksionallıq və Sabitlik** | **30** | Hər hansı xətasız işləyən asinxron arxitektura, tam avtomatlaşdırılmış `pytest` testləri (100% keçir), oflayn ehtiyat rejim. |
| **İnnovasiya və Orijinallıq** | **25** | Rəqəmsal peyvənd pasportu, vaxtı keçən vaksin xəbərdarlığı və ailə-heyvan uyğunluğunu hesablayan **Smart Matcher alqoritmi**. |
| **Kod Keyfiyyəti və Arxitektura** | **25** | Təmiz modul bölgüsü (UI $\rightarrow$ App Logic $\rightarrow$ Services $\rightarrow$ DB), Pydantic V2 validasiyası, `/docs` interaktiv API sənədləşməsi. |
| **İstifadəçi Təcrübəsi və Faydalılıq** | **20** | Tailwind CSS ilə estetik dizayn, tam responsiv interfeys, 3 dilli dəstək (AZ/EN/RU), sığınacaqlar üçün real idarəetmə paneli. |

---
**Hazırladı:** PawConnect Komandası (Mentor & 10–14 Yaşlı İnnovator Şagirdlər)  
**Tədbir:** Atlântia International STEM Olympiad — Software Projects (SW01)
