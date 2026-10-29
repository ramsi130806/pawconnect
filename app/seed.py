import os
import sqlite3
from datetime import date, timedelta, datetime
from sqlalchemy import inspect, text
from app.database import SessionLocal, engine, Base
from app.models import Shelter, Pet, VaccineRecord, AdoptionApplication, User, Favorite
from app.auth import hash_password

def migrate_database_schema():
    """Ensure all required columns exist in SQLite without dropping user data."""
    try:
        with engine.connect() as conn:
            # Check SQLite table info for pets
            result = conn.execute(text("PRAGMA table_info(pets)"))
            columns = [row[1] for row in result.fetchall()]

            if "description_en" not in columns:
                conn.execute(text("ALTER TABLE pets ADD COLUMN description_en TEXT"))
            if "description_ru" not in columns:
                conn.execute(text("ALTER TABLE pets ADD COLUMN description_ru TEXT"))
            if "personality_en" not in columns:
                conn.execute(text("ALTER TABLE pets ADD COLUMN personality_en VARCHAR(150)"))
            if "personality_ru" not in columns:
                conn.execute(text("ALTER TABLE pets ADD COLUMN personality_ru VARCHAR(150)"))

            # Link adoption applications to user accounts (for "My Applications")
            result = conn.execute(text("PRAGMA table_info(adoption_applications)"))
            app_columns = [row[1] for row in result.fetchall()]
            if app_columns and "user_id" not in app_columns:
                conn.execute(text("ALTER TABLE adoption_applications ADD COLUMN user_id INTEGER REFERENCES users(id)"))
            conn.commit()
    except Exception as e:
        print(f"Schema migration notice (already applied or not SQLite): {e}")


# Complete multilingual data for pets
PETS_I18N = {
    "Baron": {
        "desc_en": "Baron is an intelligent, loyal, and protective German Shepherd mix. He knows key obedience commands and has a strong protective nature.",
        "desc_ru": "Барон — умный, преданный и защитный метис немецкой овчарки. Отлично знает основные команды послушания и обладает развитым охранным инстинктом.",
        "pers_en": "Loyal, Smart, Protective, Active",
        "pers_ru": "Преданный, Умный, Защитник, Активный"
    },
    "Luna": {
        "desc_en": "Luna is one of the friendliest dogs in the world! She adores children, loves fetching balls, and enjoys cozy cuddles.",
        "desc_ru": "Луна — одно из самых ласковых созданий на свете! Безумно любит детей, обожает играть в мяч и нежиться в объятиях.",
        "pers_en": "Friendly, Playful, Affectionate, Great with kids",
        "pers_ru": "Дружелюбная, Жизнерадостная, Ласковая, Любит детей"
    },
    "Milo": {
        "desc_en": "With his silky ears and soulful eyes, Milo is well-suited for peaceful apartment living. He eagerly looks forward to daily park strolls.",
        "desc_ru": "С шелковистыми ушками и выразительным взглядом, Майло прекрасно подходит для спокойной жизни в квартире. С нетерпением ждет прогулок в парке.",
        "pers_en": "Calm, Sensitive, Faithful",
        "pers_ru": "Спокойный, Чуткий, Верный"
    },
    "Qaytar": {
        "desc_en": "Ideal companion for a rural home or farm. Highly weather-resilient with a robust physique and patient temperament.",
        "desc_ru": "Идеальный выбор для загородного дома или фермерского хозяйства. Устойчив к холодам, обладает крепким телосложением и выдержкой.",
        "pers_en": "Brave, Protective, Resilient",
        "pers_ru": "Смелый, Защитник, Выносливый"
    },
    "Bobi": {
        "desc_en": "Bobi is a small beagle with a huge heart of an explorer. Always keeping his nose to the ground in search of new scents.",
        "desc_ru": "Боби — небольшая собака с огромным сердцем исследователя. Всегда держит нос по ветру в поисках новых интересных запахов.",
        "pers_en": "Curious, Cheerful, Playful",
        "pers_ru": "Любознательный, Веселый, Игривый"
    },
    "Bəyaz": {
        "desc_en": "Beyaz wins every heart with her radiant smile. She has a fluffy white coat and loves regular grooming.",
        "desc_ru": "Беяз покоряет каждого своей искренней улыбкой. Обладает густой белоснежной шерстью и очень любит расчесывание.",
        "pers_en": "Sweet, Agile, Cleanly",
        "pers_ru": "Милая, Шустрая, Чистоплотная"
    },
    "Reks": {
        "desc_en": "A tireless fountain of energy! Loves running, jumping, and agility games. Perfect match for active individuals.",
        "desc_ru": "Неиссякаемый источник энергии! Обожает бегать, прыгать и играть в аджилити. Прекрасно подойдет активным людям.",
        "pers_en": "Energetic, Agile, Brave",
        "pers_ru": "Энергичный, Шустрый, Смелый"
    },
    "Bella": {
        "desc_en": "Bella is a trained, calm, and sweet-tempered lady. She has a deep love for swimming and water play.",
        "desc_ru": "Белла — обученная, очень спокойная и доброжелательная леди. Безумно любит купаться и играть с водой.",
        "pers_en": "Patient, Friendly, Affectionate",
        "pers_ru": "Терпеливая, Дружелюбная, Ласковая"
    },
    "Məstan": {
        "desc_en": "Mastan is an aristocratic cat with plush smoke-grey fur and amber eyes. Calm, independent, and tidy.",
        "desc_ru": "Мэстан — кот-аристократ с плюшевой дымчато-серой шерстью и янтарными глазами. Спокойный, независимый и чистоплотный.",
        "pers_en": "Aristocratic, Independent, Cleanly",
        "pers_ru": "Аристократичный, Независимый, Чистоплотный"
    },
    "Pamıq": {
        "desc_en": "Pamıq is a gentle Persian mix with angel-white fur. She loves resting beside you and purring peacefully.",
        "desc_ru": "Памыг — нежная белоснежная кошечка. Обожает сидеть рядом, петь мурлыкающие песенки и дарить покой.",
        "pers_en": "Gentle, Calm, Sweet",
        "pers_ru": "Нежная, Спокойная, Милая"
    },
    "Simba": {
        "desc_en": "A charming ginger kitten with bright orange stripes! Plays with feathers, chases laser pointers, and brings joyful laughter.",
        "desc_ru": "Обаятельный рыжий непоседа с яркими полосками! Ловит перышки, бегает за лазером и дарит море веселья.",
        "pers_en": "Playful, Curious, Social",
        "pers_ru": "Игривый, Любознательный, Общительный"
    },
    "Qaraqulaq": {
        "desc_en": "An elegant, completely black miniature panther. Very affectionate once he gets to know you, with immaculate litter habits.",
        "desc_ru": "Элегантная грациозная мини-пантера. Очень ласков с теми, кому доверяет, и имеет безупречные домашние манеры.",
        "pers_en": "Smart, Cleanly, Affectionate",
        "pers_ru": "Умный, Чистоплотный, Ласковый"
    },
    "Tarzan": {
        "desc_en": "A handsome Siberian mix with a fluffy tail. Brave and inquisitive, always curious about high vantage points.",
        "desc_ru": "Красивый сибирский метис с пушистым хвостом. Смелый и любознательный, любит исследовать высокие точки в доме.",
        "pers_en": "Brave, Curious, Calm",
        "pers_ru": "Смелый, Любознательный, Спокойный"
    },
    "Boncuk": {
        "desc_en": "Boncuk is an adorable lop-eared rabbit with soft grey fur. Calm and gentle, loves eating fresh carrots and parsley.",
        "desc_ru": "Бонджук — очаровательный вислоухий кролик с мягкой серой шерсткой. Тихий и ласковый, любит морковку и свежую зелень.",
        "pers_en": "Gentle, Peaceful, Calm",
        "pers_ru": "Нежный, Миролюбивый, Спокойный"
    },
    "Koko": {
        "desc_en": "A vibrant green parrot with sunny yellow feathers. Whistles cheerful melodies and can mimic short phrases.",
        "desc_ru": "Яркий попугай с изумрудно-желтым оперением. Насвистывает веселые мелодии и может повторять короткие звуки.",
        "pers_en": "Musical, Talkative, Cheerful",
        "pers_ru": "Музыкальный, Говорящий, Веселый"
    },
    "Zümrüd": {
        "desc_en": "With her big amber eyes and folded ears, Zümrüd is a true aristocrat. She adores cuddles and gentle petting.",
        "desc_ru": "С большими янтарными глазами и загнутыми ушками Зюмрюд — настоящая кошка-аристократка. Обожает объятия и ласку.",
        "pers_en": "Gentle, Sweet, Patient",
        "pers_ru": "Нежная, Милая, Терпеливая"
    },
    "Leo": {
        "desc_en": "Despite his giant body, Leo has a heart as tender as a bird's. You'll love watching him play with the water tap and purr.",
        "desc_ru": "Несмотря на огромное тело, у Лео нежное, как у птички, сердце. Вы будете в восторге от того, как он играет с краном и мурлычет.",
        "pers_en": "Giant, Friendly, Water-loving",
        "pers_ru": "Огромный, Дружелюбный, Любит воду"
    },
    "Pamuk": {
        "desc_en": "Pamuk catches every eye with her stunning odd-coloured eyes. She was rescued from the street as a kitten and is now completely healthy.",
        "desc_ru": "Памук притягивает взгляды своими удивительными разноцветными глазами. Её спасли с улицы котёнком, и теперь она полностью здорова.",
        "pers_en": "Rare, Playful, Eye-catching",
        "pers_ru": "Редкая, Игривая, Яркая"
    },
    "Kömür": {
        "desc_en": "With his shiny black coat and yellow eyes, Kömür looks like a little panther. Very smart and quiet.",
        "desc_ru": "Блестящей чёрной шерстью и жёлтыми глазами Кёмюр похож на маленькую пантеру. Очень умный и тихий.",
        "pers_en": "Mysterious, Gentle, Cuddly",
        "pers_ru": "Загадочный, Нежный, Любит руки"
    },
    "Maya": {
        "desc_en": "A beautiful girl who loves to 'talk' (meow), bonds deeply with her owner and doesn't like being left home alone.",
        "desc_ru": "Красавица, которая любит «поговорить» (помяукать), сильно привязывается к хозяину и не любит оставаться дома одна.",
        "pers_en": "Sociable, Sensitive, Blue-eyed",
        "pers_ru": "Общительная, Чуткая, Голубоглазая"
    },
    "Topuş": {
        "desc_en": "Topuş is very calm and adores fresh carrots and clover. He patiently waits to be petted and have his nose stroked.",
        "desc_ru": "Топуш очень спокойный, обожает свежую морковку и клевер. Терпеливо ждёт, когда его погладят по носику.",
        "pers_en": "Calm, Silky, Harmless",
        "pers_ru": "Спокойный, Шелковистый, Безобидный"
    },
    "Kökə": {
        "desc_en": "With the thick fur around his head, Kökə looks like a little lion. He loves roaming the room outside his cage.",
        "desc_ru": "Благодаря густой шерсти вокруг головы Кёкя похож на маленького льва. Любит гулять по комнате вне клетки.",
        "pers_en": "Curious, Cheerful, Soft",
        "pers_ru": "Любознательный, Весёлый, Мягкий"
    },
    "Çiko": {
        "desc_en": "Çiko is a real music lover — he chirps every morning and is learning to repeat the word 'Salam'.",
        "desc_ru": "Чико — настоящий меломан: щебечет по утрам и учится повторять слово «Салам».",
        "pers_en": "Musical, Lively, Colourful",
        "pers_ru": "Музыкальный, Живой, Яркий"
    },
    "Riko": {
        "desc_en": "A talented parrot who can whistle and repeat melodies. Loves sitting on your shoulder and watching around.",
        "desc_ru": "Талантливый попугай, умеющий свистеть и повторять мелодии. Любит сидеть на плече и наблюдать за всем вокруг.",
        "pers_en": "Smart, Melodic, Friendly",
        "pers_ru": "Умный, Мелодичный, Дружелюбный"
    },
    "Çarli": {
        "desc_en": "With the qualities of a perfect companion and guide dog, Çarli is fully ready for a family.",
        "desc_ru": "Обладая качествами идеального компаньона и собаки-поводыря, Чарли полностью готов к жизни в семье.",
        "pers_en": "Patient, Loyal, Family-loving",
        "pers_ru": "Терпеливый, Преданный, Любит семью"
    },
    "Oskar": {
        "desc_en": "With ice-blue eyes and an endless love of running, Oskar is looking for an owner who enjoys mountain hikes and jogging.",
        "desc_ru": "С ледяными голубыми глазами и безграничной любовью к бегу, Оскар ищет хозяина, который любит горные походы и пробежки.",
        "pers_en": "Free-spirited, Athletic, Strong",
        "pers_ru": "Свободолюбивый, Спортивный, Сильный"
    },
    "Pudra": {
        "desc_en": "The calmest and most elegant cat in the world. She spends 90% of her life resting on soft pillows.",
        "desc_ru": "Самая спокойная и благородная кошка на свете. 90% жизни проводит, отдыхая на мягких подушках.",
        "pers_en": "Laid-back, Calm, Majestic",
        "pers_ru": "Ленивая, Спокойная, Величественная"
    },
    "Tobi": {
        "desc_en": "With his hypoallergenic coat, Tobi is an irreplaceable friend for apartment living. Very eager to learn.",
        "desc_ru": "Благодаря гипоаллергенной шерсти Тоби — незаменимый друг для квартиры. Очень любит учиться.",
        "pers_en": "Smart, Hypoallergenic, Cheerful",
        "pers_ru": "Умный, Гипоаллергенный, Весёлый"
    },
    "Badam": {
        "desc_en": "According to tradition, tricolour cats bring abundance and luck to a home — Badam shows her love by purring.",
        "desc_ru": "По народному поверью, трёхцветные кошки приносят в дом достаток и удачу — Бадам выражает свою любовь мурлыканьем.",
        "pers_en": "Lucky, Gentle, Friendly",
        "pers_ru": "Приносящая удачу, Кроткая, Дружелюбная"
    }
}


# Medical passport update: additional vaccine records, several of them overdue.
# Format: (pet name, vaccine name, administered days ago, next dose in days (negative = overdue),
#          batch number, vet, clinic, note)
VACCINE_UPDATES = [
    ("Baron", "Leptospiroz (Nobivac Lepto)", 410, -45, "LEP-2025-3310", "Dr. Rəşad Əliyev", "Baku Vet Clinic", "Annual booster missed"),
    ("Qaytar", "Bordetella (Kennel öskürəyi)", 395, -30, "BOR-2025-0712", "Dr. Leyla Məmmədova", "VetCare Mərkəzi", "Booster overdue"),
    ("Qaytar", "Antiparazitar Müalicə (Dehelmintizasiya)", 120, -30, "DEW-2026-0410", "Dr. Leyla Məmmədova", "VetCare Mərkəzi", "Quarterly deworming overdue"),
    ("Reks", "Leptospiroz (Nobivac Lepto)", 380, -15, "LEP-2025-3388", "Dr. Rəşad Əliyev", "Baku Vet Clinic", "Annual booster missed"),
    ("Zümrüd", "FeLV (Pişik Leykemiyası)", 390, -25, "FLV-2025-1150", "Dr. Nigar Qasımova", "Cat Health Center", "Booster overdue"),
    ("Leo", "Antiparazitar Müalicə (Dehelmintizasiya)", 135, -45, "DEW-2026-0322", "Dr. Nigar Qasımova", "Cat Health Center", "Quarterly deworming overdue"),
    ("Kökə", "RHDV2 Dovşan Vaksini (Eravac)", 385, -20, "RHD-2025-0901", "Dr. Rəşad Əliyev", "Exotic Vet Baku", "Annual booster missed"),
    ("Riko", "Poliomavirus (APV) Quş Vaksini", 400, -35, "APV-2025-0077", "Dr. Rəşad Əliyev", "Exotic Vet Baku", "Booster overdue"),
    ("Çiko", "Poliomavirus (APV) Quş Vaksini", 200, 165, "APV-2026-0145", "Dr. Rəşad Əliyev", "Exotic Vet Baku", None),
    ("Oskar", "Bordetella (Kennel öskürəyi)", 372, -7, "BOR-2025-0790", "Dr. Leyla Məmmədova", "VetCare Mərkəzi", "Booster overdue"),
    ("Tobi", "Leptospiroz (Nobivac Lepto)", 350, 15, "LEP-2025-3402", "Dr. Rəşad Əliyev", "Baku Vet Clinic", "Booster due soon"),
    # Pets from the default seed (fresh deployments)
    ("Koko", "Poliomavirus (APV) Quş Vaksini", 400, -35, "APV-2025-0081", "Dr. Rəşad Əliyev", "Exotic Vet Baku", "Booster overdue"),
    ("Boncuk", "RHDV2 Dovşan Vaksini (Eravac)", 385, -20, "RHD-2025-0915", "Dr. Rəşad Əliyev", "Exotic Vet Baku", "Annual booster missed"),
]


def apply_vaccine_updates(db):
    """Idempotently add the medical passport updates (skips records that already exist)."""
    today = date.today()
    added = 0
    for pet_name, vax_name, given_ago, due_in, batch, vet, clinic, note in VACCINE_UPDATES:
        pet = db.query(Pet).filter(Pet.name == pet_name).first()
        if not pet:
            continue
        exists = db.query(VaccineRecord).filter(
            VaccineRecord.pet_id == pet.id,
            VaccineRecord.vaccine_name == vax_name
        ).first()
        if exists:
            continue
        next_due = today + timedelta(days=due_in)
        db.add(VaccineRecord(
            pet_id=pet.id,
            vaccine_name=vax_name,
            administered_date=today - timedelta(days=given_ago),
            next_due_date=next_due,
            batch_number=batch,
            vet_name=vet,
            clinic_name=clinic,
            status="overdue" if due_in < 0 else ("upcoming" if due_in <= 30 else "valid"),
            notes=note
        ))
        added += 1
    if added:
        db.commit()

    # Keep stored status column in sync with the real due dates
    changed = False
    for record in db.query(VaccineRecord).all():
        live = record.computed_status
        if record.status != live:
            record.status = live
            changed = True
    if changed:
        db.commit()


def seed_database():
    """Populates database with shelters, pets, users, and handles schema updates seamlessly."""
    migrate_database_schema()
    Base.metadata.create_all(bind=engine)
    db = SessionLocal()

    try:
        # 1. Ensure Shelters exist
        if db.query(Shelter).count() == 0:
            print("Seeding initial shelters...")
            shelters = [
                Shelter(
                    name="Bakı Heyvanları Xilasetmə Mərkəzi",
                    city="Bakı",
                    address="Nərimanov r., Təbriz küç. 45",
                    phone="+994 (12) 555-01-12",
                    email="info@baku-petrescue.az",
                    website="https://pawconnect.az/shelters/baku",
                    description="2018-ci ildən bəri fəaliyyət göstərən, sahibsiz heyvanların müalicəsi, peyvəndlənməsi və sahibləndirilməsi ilə məşğul olan aparıcı sığınacaq."
                ),
                Shelter(
                    name="Gəncə Ümid Sığınacağı",
                    city="Gəncə",
                    address="Nizami r., Heydər Əliyev pr. 112",
                    phone="+994 (22) 256-44-80",
                    email="ganja.umid@pawconnect.az",
                    website="https://pawconnect.az/shelters/ganja",
                    description="Qərb regionunda tərk edilmiş və yardıma ehtiyacı olan heyvanları reabilitasiya edən şəfqət mərkəzi."
                ),
                Shelter(
                    name="Sumqayıt Can Dostları Mərkəzi",
                    city="Sumqayıt",
                    address="Sülh küçəsi, Məhəllə 18",
                    phone="+994 (18) 642-19-05",
                    email="sumqayit.candost@pawconnect.az",
                    website="https://pawconnect.az/shelters/sumqayit",
                    description="Küçə heyvanlarının sterilizasiyası, vaksinasiyası və daimi ailələrə qovuşdurulması üçün könüllü mərkəz."
                ),
                Shelter(
                    name="Şamaxı Şəfqət Evi",
                    city="Şamaxı",
                    address="Şamaxı-Çuxuryurd yolu, km 4",
                    phone="+994 (20) 265-11-20",
                    email="shamakhi.haven@pawconnect.az",
                    website="https://pawconnect.az/shelters/shamakhi",
                    description="Təbiət qoynunda yerləşən, xüsusi qayğıya ehtiyacı olan travmalı heyvanların bərpa mərkəzi."
                )
            ]
            db.add_all(shelters)
            db.commit()

        shelters_list = db.query(Shelter).all()
        s1 = shelters_list[0].id
        s2 = shelters_list[1].id if len(shelters_list) > 1 else s1
        s3 = shelters_list[2].id if len(shelters_list) > 2 else s1
        s4 = shelters_list[3].id if len(shelters_list) > 3 else s1

        # 2. Ensure Pets exist
        if db.query(Pet).count() == 0:
            print("Seeding initial pets...")
            sample_pets = [
                Pet(
                    name="Baron", species="dog", breed="Alman Çoban İti (Qarışıq)", gender="Male",
                    age_years=2, age_months=4, size="Large", coat_color="Qara və Qonur",
                    description="Baron çox intellektual, cəsur və sadiq bir itdir. Əsas komandaları ('otur', 'əl ver', 'gözlə') mükəmməl bilir. Qoruma instinkti yüksəkdir.",
                    description_en=PETS_I18N["Baron"]["desc_en"], description_ru=PETS_I18N["Baron"]["desc_ru"],
                    personality="Sadiq, Ağıllı, Qoruyucu, Aktiv", personality_en=PETS_I18N["Baron"]["pers_en"], personality_ru=PETS_I18N["Baron"]["pers_ru"],
                    photo_url="/static/img/pets/baron.jpg", status="available", energy_level=4,
                    good_with_children=True, good_with_other_pets=False, house_trained=True,
                    microchip_id="AZ-982-100-8801", neutered=True, shelter_id=s1
                ),
                Pet(
                    name="Luna", species="dog", breed="Golden Retriever", gender="Female",
                    age_years=1, age_months=8, size="Medium", coat_color="Qızılı",
                    description="Luna dünyadakı ən mehriban varlıqlardan biridir! Uşaqları hədsiz sevir, topla oynamağa bayılır və qucaqda yatmağı çox xoşlayır.",
                    description_en=PETS_I18N["Luna"]["desc_en"], description_ru=PETS_I18N["Luna"]["desc_ru"],
                    personality="Mehriban, Gülərüz, Mehriban, Uşaqcanlı", personality_en=PETS_I18N["Luna"]["pers_en"], personality_ru=PETS_I18N["Luna"]["pers_ru"],
                    photo_url="/static/img/pets/luna.jpg", status="available", energy_level=5,
                    good_with_children=True, good_with_other_pets=True, house_trained=True,
                    microchip_id="AZ-982-100-8802", neutered=True, shelter_id=s1
                ),
                Pet(
                    name="Milo", species="dog", breed="Kokker Spaniel", gender="Male",
                    age_years=3, age_months=2, size="Medium", coat_color="Qəhvəyi-Boz",
                    description="İpək kimi qulaqları və kədərli baxışları olan Milo sakit mənzil mühitinə tam uyğundur. Park gəzintilərini səbirsizliklə gözləyir.",
                    description_en=PETS_I18N["Milo"]["desc_en"], description_ru=PETS_I18N["Milo"]["desc_ru"],
                    personality="Sakit, Həssas, Sadiq", personality_en=PETS_I18N["Milo"]["pers_en"], personality_ru=PETS_I18N["Milo"]["pers_ru"],
                    photo_url="/static/img/pets/milo.jpg", status="pending", energy_level=3,
                    good_with_children=True, good_with_other_pets=True, house_trained=True,
                    microchip_id="AZ-982-100-8803", neutered=True, shelter_id=s2
                ),
                Pet(
                    name="Qaytar", species="dog", breed="Azərbaycan Çoban İti (Qurdbasar)", gender="Male",
                    age_years=3, age_months=0, size="Large", coat_color="Krem, qara üzlü",
                    description="Həyətli ev və ya fermer təsərrüfatı üçün ideal seçimdir. Soyuğa dözümlüdür, güclü fiziki quruluşa və təmkinli xarakterə malikdir.",
                    description_en=PETS_I18N["Qaytar"]["desc_en"], description_ru=PETS_I18N["Qaytar"]["desc_ru"],
                    personality="Ciddi, Qoruyucu, Dözümlü", personality_en=PETS_I18N["Qaytar"]["pers_en"], personality_ru=PETS_I18N["Qaytar"]["pers_ru"],
                    photo_url="/static/img/pets/qaytar.jpg", status="available", energy_level=4,
                    good_with_children=True, good_with_other_pets=False, house_trained=False,
                    microchip_id="AZ-982-100-8804", neutered=False, shelter_id=s4
                ),
                Pet(
                    name="Bobi", species="dog", breed="Baqi (Beagle)", gender="Male",
                    age_years=1, age_months=2, size="Small", coat_color="Üçrəngli (Tri-color)",
                    description="Bobi kiçik ölçülü, lakin böyük ürəkli bir kəşfiyyatçıdır. Həmişə burnu yerdə yeni qoxular axtarışındadır.",
                    description_en=PETS_I18N["Bobi"]["desc_en"], description_ru=PETS_I18N["Bobi"]["desc_ru"],
                    personality="Maraqlı, Şən, Oynaq", personality_en=PETS_I18N["Bobi"]["pers_en"], personality_ru=PETS_I18N["Bobi"]["pers_ru"],
                    photo_url="/static/img/pets/bobi.jpg", status="available", energy_level=5,
                    good_with_children=True, good_with_other_pets=True, house_trained=True,
                    microchip_id="AZ-982-100-8805", neutered=True, shelter_id=s3
                ),
                Pet(
                    name="Bəyaz", species="dog", breed="Samoyed (Mix)", gender="Female",
                    age_years=2, age_months=1, size="Medium", coat_color="Qar kimi Ağ",
                    description="Təbəssümü ilə hər kəsin qəlbini fəth edən Bəyaz. Qalın tükləri var və gündəlik daramağı çox sevir.",
                    description_en=PETS_I18N["Bəyaz"]["desc_en"], description_ru=PETS_I18N["Bəyaz"]["desc_ru"],
                    personality="Sevimli, Canlı, Təmizkar", personality_en=PETS_I18N["Bəyaz"]["pers_en"], personality_ru=PETS_I18N["Bəyaz"]["pers_ru"],
                    photo_url="/static/img/pets/beyaz.jpg", status="available", energy_level=4,
                    good_with_children=True, good_with_other_pets=True, house_trained=True,
                    microchip_id="AZ-982-100-8806", neutered=True, shelter_id=s2
                ),
                Pet(
                    name="Reks", species="dog", breed="Cek Rassel Teryer", gender="Male",
                    age_years=1, age_months=6, size="Small", coat_color="Ağ, Qara və Qəhvəyi",
                    description="Yorulmaz enerji mənbəyi! Qaçmağı, tullanmağı və çeviklik oyunlarını çox sevir. Aktiv gənclər üçün idealdır.",
                    description_en=PETS_I18N["Reks"]["desc_en"], description_ru=PETS_I18N["Reks"]["desc_ru"],
                    personality="Enerjili, Cəld, Cəsur", personality_en=PETS_I18N["Reks"]["pers_en"], personality_ru=PETS_I18N["Reks"]["pers_ru"],
                    photo_url="/static/img/pets/reks.jpg", status="available", energy_level=5,
                    good_with_children=True, good_with_other_pets=True, house_trained=True,
                    microchip_id="AZ-982-100-8807", neutered=True, shelter_id=s1
                ),
                Pet(
                    name="Bella", species="dog", breed="Labrador Retriever", gender="Female",
                    age_years=4, age_months=0, size="Large", coat_color="Qara",
                    description="Bella təlim görmüş, çox sakit və mehriban xarakterli bir xanımdır. Su ilə oynamağı hədsiz dərəcədə sevir.",
                    description_en=PETS_I18N["Bella"]["desc_en"], description_ru=PETS_I18N["Bella"]["desc_ru"],
                    personality="Təmkinli, Dostcanlı, Ailəpərəst", personality_en=PETS_I18N["Bella"]["pers_en"], personality_ru=PETS_I18N["Bella"]["pers_ru"],
                    photo_url="/static/img/pets/bella.jpg", status="adopted", energy_level=3,
                    good_with_children=True, good_with_other_pets=True, house_trained=True,
                    microchip_id="AZ-982-100-8808", neutered=True, shelter_id=s1
                ),
                Pet(
                    name="Məstan", species="cat", breed="Britaniya Qısatüklüsü (Mix)", gender="Male",
                    age_years=1, age_months=5, size="Medium", coat_color="Dumanlı Boz",
                    description="Məstan kətə kimi tükləri və kəhrəba gözləri olan əsl zadəgan pişikdir. Mənzildə sakitcə pəncərədən baxmağı sevir.",
                    description_en=PETS_I18N["Məstan"]["desc_en"], description_ru=PETS_I18N["Məstan"]["desc_ru"],
                    personality="Zadəgan, Müstəqil, Təmizkar", personality_en=PETS_I18N["Məstan"]["pers_en"], personality_ru=PETS_I18N["Məstan"]["pers_ru"],
                    photo_url="/static/img/pets/mestan.jpg", status="available", energy_level=2,
                    good_with_children=True, good_with_other_pets=True, house_trained=True,
                    microchip_id="AZ-982-200-9901", neutered=True, shelter_id=s1
                ),
                Pet(
                    name="Pamıq", species="cat", breed="Fars Pişiyi (Mix)", gender="Female",
                    age_years=2, age_months=3, size="Small", coat_color="Ağ",
                    description="Pambıq kimi yumşaq və zərif bir qız. Sakit mühitləri sevir, qucaqda yatmağa və sığallanmağa heyran olur.",
                    description_en=PETS_I18N["Pamıq"]["desc_en"], description_ru=PETS_I18N["Pamıq"]["desc_ru"],
                    personality="Zərif, Sakit, Şirin", personality_en=PETS_I18N["Pamıq"]["pers_en"], personality_ru=PETS_I18N["Pamıq"]["pers_ru"],
                    photo_url="/static/img/pets/pamiq.jpg", status="available", energy_level=1,
                    good_with_children=True, good_with_other_pets=True, house_trained=True,
                    microchip_id="AZ-982-200-9902", neutered=True, shelter_id=s2
                ),
                Pet(
                    name="Simba", species="cat", breed="Yerli Qırmızı Təbii", gender="Male",
                    age_years=0, age_months=9, size="Small", coat_color="Narıncı zolaqlı",
                    description="Evə sevinc və hərəkət gətirən kiçik aslan balası! Hər şeylə maraqlanır və gün boyu topla oynayır.",
                    description_en=PETS_I18N["Simba"]["desc_en"], description_ru=PETS_I18N["Simba"]["desc_ru"],
                    personality="Oynağan, Maraqlı, Sosial", personality_en=PETS_I18N["Simba"]["pers_en"], personality_ru=PETS_I18N["Simba"]["pers_ru"],
                    photo_url="/static/img/pets/simba.jpg", status="available", energy_level=4,
                    good_with_children=True, good_with_other_pets=True, house_trained=True,
                    microchip_id="AZ-982-200-9903", neutered=True, shelter_id=s3
                ),
                Pet(
                    name="Qaraqulaq", species="cat", breed="Avropa Qısatüklüsü", gender="Male",
                    age_years=2, age_months=0, size="Medium", coat_color="Qapqara",
                    description="Gözəl qara tükləri və zümrüd yaşılı gözləri var. Çox müstəqil, eyni zamanda sədaqətlidir.",
                    description_en=PETS_I18N["Qaraqulaq"]["desc_en"], description_ru=PETS_I18N["Qaraqulaq"]["desc_ru"],
                    personality="Ağıllı, Təmizkar, Sevgi dolu", personality_en=PETS_I18N["Qaraqulaq"]["pers_en"], personality_ru=PETS_I18N["Qaraqulaq"]["pers_ru"],
                    photo_url="/static/img/pets/qaraqulaq.jpg", status="available", energy_level=3,
                    good_with_children=True, good_with_other_pets=True, house_trained=True,
                    microchip_id="AZ-982-200-9904", neutered=True, shelter_id=s1
                ),
                Pet(
                    name="Tarzan", species="cat", breed="Sibir Pişiyi (Mix)", gender="Male",
                    age_years=3, age_months=4, size="Large", coat_color="Boz Təbii",
                    description="İri cüssəli, tüklü quyruğu olan vəhşi təbiət gözəli. Hündür yerlərdən ətrafı müşahidə etməyi xoşlayır.",
                    description_en=PETS_I18N["Tarzan"]["desc_en"], description_ru=PETS_I18N["Tarzan"]["desc_ru"],
                    personality="Cəsur, Maraqlı, Sakit", personality_en=PETS_I18N["Tarzan"]["pers_en"], personality_ru=PETS_I18N["Tarzan"]["pers_ru"],
                    photo_url="/static/img/pets/tarzan.jpg", status="pending", energy_level=3,
                    good_with_children=True, good_with_other_pets=True, house_trained=True,
                    microchip_id="AZ-982-200-9905", neutered=True, shelter_id=s4
                ),
                Pet(
                    name="Boncuk", species="rabbit", breed="Hollandiya Lop-qulağı", gender="Male",
                    age_years=1, age_months=0, size="Small", coat_color="Açıq Boz",
                    description="Sakit, təmizkar və çox şirin dovşan. Qəfəsdən kənarda otaqda sərbəst gəzməyi və təzə yerkökü yeməyi sevir.",
                    description_en=PETS_I18N["Boncuk"]["desc_en"], description_ru=PETS_I18N["Boncuk"]["desc_ru"],
                    personality="Zərif, Sülhsevər, Sakit", personality_en=PETS_I18N["Boncuk"]["pers_en"], personality_ru=PETS_I18N["Boncuk"]["pers_ru"],
                    photo_url="/static/img/pets/boncuk.jpg", status="available", energy_level=2,
                    good_with_children=True, good_with_other_pets=False, house_trained=True,
                    microchip_id="AZ-982-300-1101", neutered=False, shelter_id=s2
                ),
                Pet(
                    name="Koko", species="bird", breed="Dalğalı Tutuquşu", gender="Male",
                    age_years=1, age_months=2, size="Small", coat_color="Yaşıl və Sarı",
                    description="Rəngarəng və şən tutuquşu. Səhərlər melodik səslə oxumağı çox sevir və asanlıqla ələ öyrəşir.",
                    description_en=PETS_I18N["Koko"]["desc_en"], description_ru=PETS_I18N["Koko"]["desc_ru"],
                    personality="Musiqisevər, Danışan, Şən", personality_en=PETS_I18N["Koko"]["pers_en"], personality_ru=PETS_I18N["Koko"]["pers_ru"],
                    photo_url="/static/img/pets/koko.jpg", status="available", energy_level=4,
                    good_with_children=True, good_with_other_pets=False, house_trained=False,
                    microchip_id="AZ-982-400-2201", neutered=False, shelter_id=s1
                )
            ]
            db.add_all(sample_pets)
            db.commit()

        # 3. Synchronize multilingual columns for existing pets if missing
        #    (also repairs EN/RU fields that were filled with a copy of the Azerbaijani text)
        existing_pets = db.query(Pet).all()
        for pet in existing_pets:
            data = PETS_I18N.get(pet.name)
            if data:
                if not pet.description_en or pet.description_en == pet.description:
                    pet.description_en = data["desc_en"]
                if not pet.description_ru or pet.description_ru == pet.description:
                    pet.description_ru = data["desc_ru"]
                if not pet.personality_en or pet.personality_en == pet.personality:
                    pet.personality_en = data["pers_en"]
                if not pet.personality_ru or pet.personality_ru == pet.personality:
                    pet.personality_ru = data["pers_ru"]
            else:
                if not pet.description_en:
                    pet.description_en = pet.description
                if not pet.description_ru:
                    pet.description_ru = pet.description
                if not pet.personality_en:
                    pet.personality_en = pet.personality
                if not pet.personality_ru:
                    pet.personality_ru = pet.personality
        db.commit()

        # 4. Ensure Users table has default admin and demo user
        admin_user = db.query(User).filter(User.email == "admin@pawconnect.az").first()
        if not admin_user:
            admin_user = User(
                name="Admin İdarəçi",
                email="admin@pawconnect.az",
                password_hash=hash_password("idschool"),
                role="admin"
            )
            db.add(admin_user)

        demo_user = db.query(User).filter(User.email == "user@pawconnect.az").first()
        if not demo_user:
            demo_user = User(
                name="Nuran Əliyev",
                email="user@pawconnect.az",
                password_hash=hash_password("user123456"),
                role="user"
            )
            db.add(demo_user)
        db.commit()

        # 5. Seed sample vaccines if none
        if db.query(VaccineRecord).count() == 0 and len(existing_pets) > 0:
            for p in existing_pets[:6]:
                v1 = VaccineRecord(
                    pet_id=p.id,
                    vaccine_name="Quduzluq (Rabies)",
                    administered_date=date.today() - timedelta(days=60),
                    next_due_date=date.today() + timedelta(days=305),
                    batch_number="RAB-2025-9981",
                    status="valid"
                )
                v2 = VaccineRecord(
                    pet_id=p.id,
                    vaccine_name="Kompleks DHPPi",
                    administered_date=date.today() - timedelta(days=400),
                    next_due_date=date.today() - timedelta(days=35),
                    batch_number="DHP-2024-1102",
                    status="overdue"
                )
                db.add_all([v1, v2])
            db.commit()

        # 6. Medical passport updates (late / overdue vaccines) + live status sync
        apply_vaccine_updates(db)

        print(f"Database successfully verified! Total Pets: {db.query(Pet).count()}, Shelters: {db.query(Shelter).count()}")

    except Exception as e:
        db.rollback()
        print(f"Seed error: {e}")
    finally:
        db.close()


if __name__ == "__main__":
    seed_database()
