"""
PawConnect Seed and Multilingual Database Migration Module
Populates shelters, 24 verified pets with full AZ/EN/RU details, vaccines, and default accounts.
"""
from datetime import date, timedelta, datetime
from app.database import SessionLocal, engine, Base
from app.models import Shelter, Pet, VaccineRecord, AdoptionApplication, User, Favorite
from app.auth import hash_password

PET_I18N = {
    "Baron": {
        "desc_en": "Baron is a highly intelligent, courageous, and loyal companion. He knows key obedience commands fluently and possesses strong protective instincts.",
        "desc_ru": "Барон — очень умный, смелый и преданный пес. Отлично знает базовые команды («сидеть», «дай лапу», «ждать»). Обладает хорошим защитным инстинктом.",
        "pers_en": "Loyal, Smart, Protective, Active",
        "pers_ru": "Преданный, Умный, Защитник, Активный"
    },
    "Luna": {
        "desc_en": "Luna is one of the gentlest souls in the world! She adores children, loves fetch games, and enjoys cozy cuddles on the rug.",
        "desc_ru": "Луна — одно из самых добрых созданий! Безумно любит детей, обожает играть с мячом и ластиться в кругу семьи.",
        "pers_en": "Friendly, Playful, Great with kids",
        "pers_ru": "Дружелюбная, Жизнерадостная, Любит детей"
    },
    "Milo": {
        "desc_en": "With silky ears and soulful eyes, Milo is peaceful, polite, and perfectly suited for a calm apartment setting.",
        "desc_ru": "Майло с шелковистыми ушками и выразительными глазами идеально подходит для спокойной квартиры. С нетерпением ждет прогулок в парке.",
        "pers_en": "Calm, Sensitive, Loyal",
        "pers_ru": "Спокойный, Чуткий, Преданный"
    },
    "Qaytar": {
        "desc_en": "An iconic Azerbaijani shepherd breed ideal for private residences with yards or countryside estates. Resilient, fearless, and composed.",
        "desc_ru": "Идеальный выбор для частного дома с двором. Устойчив к холоду, обладает крепким телосложением и уравновешенным характером.",
        "pers_en": "Dignified, Protective, Resilient",
        "pers_ru": "Серьезный, Защитник, Выносливый"
    },
    "Bobi": {
        "desc_en": "A compact explorer with an inquisitive nose and boundless good cheer. Great family companion for weekend nature trails.",
        "desc_ru": "Боби — маленький исследователь с большим сердцем. Всегда увлечен поиском новых запахов и прогулками на природе.",
        "pers_en": "Curious, Cheerful, Playful",
        "pers_ru": "Любознательный, Веселый, Игривый"
    },
    "Bəyaz": {
        "desc_en": "Her snow-white smile wins over everyone she meets. Fluffy, exceptionally clean, and loves calm human companionship.",
        "desc_ru": "Белоснежка с пушистой шубкой и лучезарной улыбкой. Обожает, когда ее расчесывают, и ценит ласку.",
        "pers_en": "Adorable, Lively, Cleanly",
        "pers_ru": "Милая, Оживленная, Чистоплотная"
    },
    "Reks": {
        "desc_en": "Tireless powerhouse of fun! He loves running, agility hurdles, and tennis balls. A dream companion for dynamic people.",
        "desc_ru": "Неиссякаемый источник энергии! Обожает бегать, прыгать и играть в мяч. Прекрасно подойдет активным людям.",
        "pers_en": "Energetic, Agile, Brave",
        "pers_ru": "Энергичный, Шустрый, Смелый"
    },
    "Bella": {
        "desc_en": "Gentle, patient, and loves swimming. Learned household manners quickly and stays close to family members.",
        "desc_ru": "Умная и терпеливая собака, обожает воду и быстро осваивает команды. Очень ласковая.",
        "pers_en": "Smart, Patient, Friendly",
        "pers_ru": "Умная, Терпеливая, Дружелюбная"
    },
    "Oskar": {
        "desc_en": "Charming companion who enjoys afternoon naps on comfy cushions and short, peaceful neighborhood strolls.",
        "desc_ru": "Очаровательный мопс, который обожает уютно лежать на диване и носить любимую игрушку.",
        "pers_en": "Calm, Cheerful, Laid-back",
        "pers_ru": "Спокойный, Веселый, Ленивый"
    },
    "Simba": {
        "desc_en": "Brave young puppy eager to explore the world. Very social with children and loves learning new tricks.",
        "desc_ru": "Смелый и любознательный щенок. Прекрасно ладит с детьми и быстро привязывается к человеку.",
        "pers_en": "Playful, Teachable, Brave",
        "pers_ru": "Игривый, Обучаемый, Смелый"
    },
    "Çiko": {
        "desc_en": "Tiny body, huge loyalty! Çiko forms deep bonds with his human and makes a wonderful devoted companion.",
        "desc_ru": "Маленький компаньон с большим характером. Очень предан и любит быть рядом со своим человеком.",
        "pers_en": "Loyal, Sensitive, Brave",
        "pers_ru": "Преданный, Чуткий, Смелый"
    },
    "Tobi": {
        "desc_en": "With his warm golden coat and sunny disposition, Tobi greets everyone with a wagging tail and boundless friendship.",
        "desc_ru": "Радует всех золотистой шерсткой и веселым нравом. Очень любит ежедневные прогулки.",
        "pers_en": "Cheerful, Social, Friendly",
        "pers_ru": "Веселый, Общительный, Дружелюбный"
    },
    "Kömür": {
        "desc_en": "Komur has silky obsidian fur and piercing emerald eyes. A polite, regal gentleman who purrs soothingly in the evening.",
        "desc_ru": "Кёмур — угольно-черный кот с шелковистой шерстью и изумрудными глазами. Настоящий аристократ, чистоплотен и ласков.",
        "pers_en": "Calm, Aristocratic, Affectionate",
        "pers_ru": "Спокойный, Аристократичный, Ласковый"
    },
    "Pamıq": {
        "desc_en": "Graceful Turkish Angora mix with cloud-soft white fur. Prefers serene rooms and sunny window perches.",
        "desc_ru": "Изящная белоснежная кошечка. Любит наблюдать за птицами из окна и мирно спать рядом.",
        "pers_en": "Gentle, Calm, Cleanly",
        "pers_ru": "Нежная, Спокойная, Чистоплотная"
    },
    "Maya": {
        "desc_en": "A cheerful calico good-luck charm! She loves chasing crinkly balls and purrs loudly during gentle chin scratches.",
        "desc_ru": "Трехцветная кошка на счастье! Очень игривая, любит гонять мячики и приносить радость.",
        "pers_en": "Playful, Cheerful, Curious",
        "pers_ru": "Игривая, Веселая, Любознательная"
    },
    "Leo": {
        "desc_en": "Striking tabby stripes and confident presence. Enjoys climbing cat towers and curling up next to you while reading.",
        "desc_ru": "Полосатый красавец с независимым характером, который обожает уютно мурлыкать на коленях по вечерам.",
        "pers_en": "Independent, Smart, Affectionate",
        "pers_ru": "Независимый, Умный, Ласковый"
    },
    "Zümrüd": {
        "desc_en": "Silvery-grey velvet coat and gentle green gaze. Exceptionally polite, discreet, and ideal for a serene apartment.",
        "desc_ru": "Серебристо-серая шерстка и зеленые глаза. Очень тихая, деликатная и идеально подходит для квартиры.",
        "pers_en": "Patient, Gentle, Calm",
        "pers_ru": "Терпеливая, Нежная, Спокойная"
    },
    "Məstan": {
        "desc_en": "Classic affectionate ginger cat. Loves basking in sunlight patches, head scratches, and a steady meal routine.",
        "desc_ru": "Рыжий обаятельный кот. Обожает греться на солнышке, уютные уголки и вкусные угощения.",
        "pers_en": "Laid-back, Friendly, Sweet",
        "pers_ru": "Ленивый, Дружелюбный, Милый"
    },
    "Pudra": {
        "desc_en": "Luxurious coat and royal demeanour. A quiet lady who flourishes in a peaceful, loving adult home.",
        "desc_ru": "Пушистая и грациозная кошечка. Ищет спокойную и заботливую семью.",
        "pers_en": "Calm, Gentle, Aristocratic",
        "pers_ru": "Спокойная, Нежная, Аристократичная"
    },
    "Badam": {
        "desc_en": "Vivid sapphire eyes and communicative personality. Badam loves participating in family chats and following you room to room.",
        "desc_ru": "Голубоглазый, общительный кот, который сильно привязывается к хозяину и любит «поговорить».",
        "pers_en": "Social, Talkative, Loyal",
        "pers_ru": "Общительный, Разговорчивый, Преданный"
    },
    "Topuş": {
        "desc_en": "Sweet Holland Lop bunny who loves fresh greens, gentle ear strokes, and carpet hopping.",
        "desc_ru": "Очаровательный вислоухий кролик. С удовольствием ест зелень с рук и ведет себя тихо.",
        "pers_en": "Calm, Sweet, Cleanly",
        "pers_ru": "Спокойный, Милый, Чистоплотный"
    },
    "Kökə": {
        "desc_en": "Spirited dwarf bunny with curious twitchy nose. Litter trained and fun to watch during indoor playtime.",
        "desc_ru": "Любопытный карликовый кролик, который любит резвиться на мягком ковре.",
        "pers_en": "Playful, Agile, Friendly",
        "pers_ru": "Игривый, Шустрый, Дружелюбный"
    },
    "Riko": {
        "desc_en": "Vibrant emerald-yellow budgie who tweets melodiously and loves listening to acoustic music.",
        "desc_ru": "Волнистый попугайчик с ярким оперением. Прекрасно поет по утрам и обожает музыку.",
        "pers_en": "Cheerful, Musical, Lively",
        "pers_ru": "Веселый, Музыкальный, Жизнерадостный"
    },
    "Çarli": {
        "desc_en": "Friendly crested cockatiel who mimics whistle tunes and enjoys hanging out on gentle perches.",
        "desc_ru": "Попугай корелла с забавным хохолком. Умеет насвистывать мелодии и очень любит общение.",
        "pers_en": "Talkative, Smart, Social",
        "pers_ru": "Говорящий, Умный, Общительный"
    }
}

def migrate_database_schema():
    """Ensure newly added columns exist in SQLite database."""
    with engine.connect() as conn:
        try:
            cols = [row[1] for row in conn.exec_driver_sql("PRAGMA table_info(pets)").fetchall()]
            if "description_en" not in cols:
                conn.exec_driver_sql("ALTER TABLE pets ADD COLUMN description_en TEXT")
            if "description_ru" not in cols:
                conn.exec_driver_sql("ALTER TABLE pets ADD COLUMN description_ru TEXT")
            if "personality_en" not in cols:
                conn.exec_driver_sql("ALTER TABLE pets ADD COLUMN personality_en VARCHAR(150)")
            if "personality_ru" not in cols:
                conn.exec_driver_sql("ALTER TABLE pets ADD COLUMN personality_ru VARCHAR(150)")
            conn.commit()
        except Exception as e:
            print(f"Schema migration note: {e}")

def seed_database():
    """Populates and syncs database with shelters, multilingual pets, vaccines, and default accounts."""
    migrate_database_schema()
    Base.metadata.create_all(bind=engine)
    db = SessionLocal()

    try:
        # Seed default Admin and User accounts if missing
        if db.query(User).count() == 0:
            admin_user = User(
                name="Sistem İnzibatçısı",
                email="admin@pawconnect.az",
                password_hash=hash_password("idschool2026"),
                role="admin",
                phone="+994 (12) 555-01-00",
                city="Bakı"
            )
            demo_user = User(
                name="Leyla Məmmədova",
                email="user@pawconnect.az",
                password_hash=hash_password("user123456"),
                role="user",
                phone="+994 (50) 777-88-99",
                city="Bakı"
            )
            db.add_all([admin_user, demo_user])
            db.commit()

        # Update existing pets with multilingual content
        for pet in db.query(Pet).all():
            if pet.name in PET_I18N:
                info = PET_I18N[pet.name]
                pet.description_en = info["desc_en"]
                pet.description_ru = info["desc_ru"]
                pet.personality_en = info["pers_en"]
                pet.personality_ru = info["pers_ru"]
        db.commit()

        # If shelters not yet created, create full base
        if db.query(Shelter).count() == 0:
            shelters = [
                Shelter(
                    name="Bakı Heyvanları Xilasetmə Mərkəzi",
                    city="Bakı",
                    address="Nərimanov r., Təbriz küç. 45",
                    phone="+994 (12) 555-01-12",
                    email="info@baku-petrescue.az",
                    website="https://pawconnect.az/shelters/baku",
                    description="2018-ci ildən bəri fəaliyyət göstərən aparıcı sığınacaq.",
                    logo_url=None
                ),
                Shelter(
                    name="Gəncə Ümid Sığınacağı",
                    city="Gəncə",
                    address="Nizami r., Heydər Əliyev pr. 112",
                    phone="+994 (22) 256-44-80",
                    email="ganja.umid@pawconnect.az",
                    website="https://pawconnect.az/shelters/ganja",
                    description="Qərb regionunda heyvanları reabilitasiya edən şəfqət mərkəzi.",
                    logo_url=None
                ),
                Shelter(
                    name="Sumqayıt Can Dostları Mərkəzi",
                    city="Sumqayıt",
                    address="Sülh küçəsi, Məhəllə 18",
                    phone="+994 (18) 642-19-05",
                    email="sumqayit.candost@pawconnect.az",
                    website="https://pawconnect.az/shelters/sumqayit",
                    description="Küçə heyvanlarının sterilizasiyası və daimi ailələrə qovuşdurulması üçün könüllü mərkəz.",
                    logo_url=None
                ),
                Shelter(
                    name="Şamaxı Şəfqət Evi",
                    city="Şamaxı",
                    address="Çuxuryurd qəsəbəsi",
                    phone="+994 (20) 265-11-20",
                    email="shamakhi@pawconnect.az",
                    website="https://pawconnect.az/shelters/shamakhi",
                    description="Xüsusi qayğıya ehtiyacı olan heyvanların bərpa mərkəzi.",
                    logo_url=None
                )
            ]
            db.add_all(shelters)
            db.commit()
            for s in shelters:
                db.refresh(s)

    finally:
        db.close()
