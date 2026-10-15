# PawConnect — Şagirdlərin Müdafiə və Çıxış Bələdçisi (Student Defense Guide)

**Olimpiada:** Atlântia International STEM Olympiad  
**Kateqoriya:** SW01 — Software Projects  
**Vaxt:** 3 Dəqiqəlik Təqdimat + Münsiflərin Sual-Cavabı (SW01.5.6)  
**Komanda:** 10–14 Yaşlı Şagirdlər və Mentor  

---

## 1. 3 Dəqiqəlik Çıxış Ssenarisi (3-Minute Presentation Pitch)

### 0:00 – 0:45 | Giriş və Problem (1-ci Şagird)
> *"Hörmətli münsiflər heyəti, salam! Bizim komandamızın layihəsi **PawConnect — Heyvanların Sahibləndirilməsi və Tibbi Qeydiyyat Sistemi** adlanır.  
> Bu gün şəhərlərimizdə və sığınacaqlarda minlərlə sahibsiz heyvan var. Lakin insanlar hansı sığınacaqda hansı heyvanın olduğunu, onların peyvəndlərinin vurulub-vurulmadığını bilmirlər. Həmçinin ailələr bəzən öz həyat tərzinə uyğun olmayan heyvanı götürür və sonradan təəssüf ki, onu geri qaytarırlar.  
> Biz PawConnect ilə bu problemi vahid rəqəmsal platformada həll etdik!"*

### 0:45 – 1:45 | Canlı Nümayiş (Live Demo) (2-ci Şagird)
> *(Kompüterdə saytı göstərərək):*  
> *"Layihəmizdə 3 əsas yenilik var:  
> 1. **Rəqəmsal Tibbi Pasport:** Hər heyvanın profili ilə yanaşı, onun quduzluq və kompleks peyvəndlərinin tarixi, baytar həkimi və növbəti doza vaxtı dəqiq qeyd olunur.  
> 2. **Smart Matcher (Ağıllı Seçim):** Ailə 4 sadə suala cavab verir (mənzildə yaşayır, uşaq var və s.) və bizim alqoritmimiz ona ən uyğun heyvanı faiz göstəricisi ilə tövsiyə edir.  
> 3. **Sığınacaq İdarəetmə Paneli:** Sığınacaq işçiləri daxil olan müraciətləri yoxlayır və bir kliklə təsdiq edərək heyvanın statusunu avtomatik olaraq 'Sahibləndirildi' kimi qeyd edir."*

### 1:45 – 2:30 | Texniki Arxitektura (3-cü Şagird)
> *"Layihəmiz modul arxitekturaya əsaslanır:  
> • **Frontend:** Tailwind CSS ilə müasir, responsiv və 3 dilli (Azərbaycan, İngilis və Rus) interfeys.  
> • **Backend:** Python dilində FastAPI freymvorku. FastAPI asinxron işləyir və çox sürətlidir.  
> • **Verilənlər Bazası:** SQLite və PostgreSQL. Layihəmiz həm internetdə, həm də olimpiada qaydalarına uyğun olaraq internetsiz (offline) tam rejimdə işləyir."*

### 2:30 – 3:00 | Nəticə və Təşəkkür (Bütün Komanda)
> *"Biz inanırıq ki, PawConnect sığınacaqlardakı heyvanların təhlükəsiz və sağlam ailələrə qovuşmasına real kömək edəcək. Diqqətiniz üçün təşəkkür edirik, suallarınızı cavablandırmağa hazırıq!"*

---

## 2. Münsiflərin Şagirdlərə Verə Biləcəyi Suallar və Hazır Cavablar (SW01.5.7)

### Sual 1: "Bu layihədə Input (Giriş) və Output (Çıxış) haradadır?"
* **Cavab:**  
  *"Giriş (Input) istifadəçinin verdiyi parametrlərdir: axtarış sözü, anket forması və ya uyğunlaşdırma testinin cavabları.  
  Server bu məlumatı Python ilə emal edir (Processing), bazada axtarır və çıxış (Output) olaraq JSON API və ya vizual veb səhifə qaytarır."*

### Sual 2: "Smart Matcher alqoritmi necə işləyir?"
* **Cavab:**  
  *"Alqoritm `app/routers/api_quiz.py` faylında yerləşir. Heyvana ilkin 80 bal verilir. Əgər ailə mənzildə yaşayırsa və heyvan çox böyük və hiperaktivdirsə, xal azaldılır. Əgər evdə uşaq varsa və heyvan uşaqlarla mehribandırsa, +15 bal əlavə olunur. Nəticədə 0–100% arası uyğunluq dərəcəsi çıxarılır."*

### Sual 3: "Niyə məhz FastAPI və Python seçdiniz?"
* **Cavab:**  
  *"Python bizim məktəbdə öyrəndiyimiz ən oxunaqlı və güclü dildir. FastAPI isə həm asinxron olduğu üçün çox sürətlidir, həm də avtomatik olaraq `/docs` ünvanında canlı API sənədləşməsi yaradır."*

### Sual 4: "Yarış keçirilən yerdə internet kəsilsə, layihəniz işləyəcəkmi?"
* **Cavab:**  
  *"Bəli! Atlântia qaydası SW01.5.9 tələb edir ki, sistem lokalda da işləsin. Biz layihəni elə qurduq ki, `run_offline.bat` faylını basdıqda daxili SQLite bazası ilə heç bir internet olmadan 100% tam funksiyalarla işləyir."*

### Sual 5: "Peyvənd pasportu nəyə lazımdır?"
* **Cavab:**  
  *"İnsanlar adətən heyvanın xəstə olmasından və ya quduzluq peyvəndinin vaxtının keçməsindən qorxurlar. PawConnect-də hər bir peyvəndin tarixi və həkimi qeyd olunur və vaxtı keçən peyvəndlər idarəetmə panelində qırmızı rənglə dərhal xəbərdarlıq edilir."*
