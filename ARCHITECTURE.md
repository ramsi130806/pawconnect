# PawConnect — Software Architecture Record (SW01.5 / D5)

**Project:** PawConnect (Animal Shelter Adoption & Medical Passport System)  
**Competition:** Atlântia International STEM Olympiad  
**Category:** SW01: Software Projects  
**Target Level:** Level 04 / 05 (Junior Explorers / Active Inventors, Ages 10–14)

---

## 1. High-Level Architecture Diagram (Mermaid)

```mermaid
flowchart TD
    subgraph ClientLayer ["1. Presentation Layer (User Interface)"]
        UI_Web["Modern Web UI (Tailwind CSS, Lucide Icons)"]
        UI_Lang["Multilingual Selector (AZ / EN / RU)"]
        UI_Passport["Digital Vaccine Passport Card"]
        UI_Admin["Shelter Management Dashboard"]
        UI_Quiz["Interactive Smart Matcher Quiz"]
    end

    subgraph AppLayer ["2. Application Layer (FastAPI Asynchronous Backend)"]
        Router_Pages["Web Page Routers (Jinja2 Templates)"]
        Router_Pets["Pets API (/api/pets)"]
        Router_Adoptions["Adoption Workflow API (/api/adoptions)"]
        Router_Vaccines["Vaccine Tracker API (/api/vaccines)"]
        Router_Quiz["Smart Matcher Algorithm Engine (/api/quiz/match)"]
        Validation["Input Validation (Pydantic V2 Schemas)"]
    end

    subgraph ServiceLayer ["3. Business Logic & Processing"]
        Logic_Match["Compatibility Matching (Weights: Space, Energy, Kids, Pets)"]
        Logic_StatusSync["Adoption State Machine (Pending -> Reviewing -> Approved -> Adopted)"]
        Logic_Health["Vaccine Expiration & Overdue Calculation"]
    end

    subgraph DataLayer ["4. Persistence & Database Layer"]
        ORM["SQLAlchemy Object Relational Mapper"]
        DB_SQLite["Local Database: SQLite (Zero-config Offline Demo)"]
        DB_Postgres["Production Cloud Database: PostgreSQL (Render / Railway)"]
    end

    UI_Web --> Router_Pages
    UI_Admin --> Router_Adoptions
    UI_Quiz --> Router_Quiz
    UI_Passport --> Router_Vaccines

    Router_Pets --> Validation
    Router_Adoptions --> Logic_StatusSync
    Router_Quiz --> Logic_Match
    Router_Vaccines --> Logic_Health

    Validation --> ORM
    Logic_StatusSync --> ORM
    Logic_Match --> ORM
    Logic_Health --> ORM

    ORM --> DB_SQLite
    ORM -.-> DB_Postgres
```

---

## 2. Input $\rightarrow$ Processing $\rightarrow$ Output Model (For Student Defense)

| Step | Component | Description for 10–14 Year Olds |
| :--- | :--- | :--- |
| **INPUT** | User Interface / Web Forms | Vətəndaş və ya sığınacaq işçisi formaya məlumatları daxil edir (məsələn: heyvan növü, ailənin mənzil şəraiti, peyvənd tarixi). |
| **PROCESSING** | FastAPI Backend & Pydantic | Server daxil olan məlumatları `schemas.py` ilə yoxlayır, `api_quiz.py` ilə uyğunluq faizini hesablayır və ya müraciət statusunu dəyişir. |
| **OUTPUT** | Database & UI Render | Nəticə verilənlər bazasında saxlanılır və istifadəçiyə zəngin vizual kartlar, peyvənd pasportu və bildiriş kimi qaytarılır. |

---

## 3. Database Schema Overview

* **Shelter:** Sığınacaqların adı, şəhəri, ünvanı, əlaqə vasitələri.
* **Pet:** Heyvanın adı, növü, cinsi, yaşı, ölçüsü, bioqrafiyası, xarakter xüsusiyyətləri, mikroçip ID-si, sterilizasiya statusu və sahibləndirmə vəziyyəti (`available`, `pending`, `adopted`).
* **VaccineRecord:** Peyvəndin adı, vurulma tarixi, növbəti doza tarixi, partiya nömrəsi, baytar həkim və klinika, status (`valid`, `upcoming`, `overdue`).
* **AdoptionApplication:** Müraciət edənin adı, əlaqə nömrəsi, e-poçtu, yaşayış yeri (mənzil / həyətli ev), evdə uşaq və ya digər heyvanın olub-olmaması, müraciət statusu (`pending`, `reviewing`, `approved`, `rejected`).
