from datetime import date, timedelta, datetime
from app.database import SessionLocal, engine, Base
from app.models import Shelter, Pet, VaccineRecord, AdoptionApplication

def seed_database():
    """Populates the database with realistic shelters, 30+ pets, vaccines, and sample applications."""
    Base.metadata.create_all(bind=engine)
    db = SessionLocal()

    # Check if already seeded
    if db.query(Shelter).count() > 0:
        db.close()
        return

    print("Seeding PawConnect database with shelters and pets...")

    # 1. Seed Shelters
    shelters = [
        Shelter(
            name="Bakı Heyvanları Xilasetmə Mərkəzi",
            city="Bakı",
            address="Nərimanov r., Təbriz küç. 45",
            phone="+994 (12) 555-01-12",
            email="info@baku-petrescue.az",
            website="https://pawconnect.az/shelters/baku",
            description="2018-ci ildən bəri fəaliyyət göstərən, sahibsiz heyvanların müalicəsi, peyvəndlənməsi və sahibləndirilməsi ilə məşğul olan aparıcı sığınacaq.",
            logo_url="https://images.unsplash.com/photo-1548767797-d8c844163c4c?w=150&auto=format&fit=crop&q=80"
        ),
        Shelter(
            name="Gəncə Ümid Sığınacağı",
            city="Gəncə",
            address="Nizami r., Heydər Əliyev pr. 112",
            phone="+994 (22) 256-44-80",
            email="ganja.umid@pawconnect.az",
            website="https://pawconnect.az/shelters/ganja",
            description="Qərb regionunda tərk edilmiş və yardıma ehtiyacı olan heyvanları reabilitasiya edən şəfqət mərkəzi.",
            logo_url="https://images.unsplash.com/photo-1583511655857-d19b40a7a54e?w=150&auto=format&fit=crop&q=80"
        ),
        Shelter(
            name="Sumqayıt Can Dostları Mərkəzi",
            city="Sumqayıt",
            address="Sülh küçəsi, Məhəllə 18",
            phone="+994 (18) 642-19-05",
            email="sumqayit.candost@pawconnect.az",
            website="https://pawconnect.az/shelters/sumqayit",
            description="Küçə heyvanlarının sterilizasiyası, vaksinasiyası və daimi ailələrə qovuşdurulması üçün könüllü mərkəz.",
            logo_url="https://images.unsplash.com/photo-1537151608828-ea2b11777ee8?w=150&auto=format&fit=crop&q=80"
        ),
        Shelter(
            name="Şamaxı Şəfqət Evi",
            city="Şamaxı",
            address="Şamaxı-Çuxuryurd yolu, km 4",
            phone="+994 (20) 265-11-20",
            email="shamakhi.haven@pawconnect.az",
            website="https://pawconnect.az/shelters/shamakhi",
            description="Təbiət qoynunda yerləşən, xüsusi qayğıya ehtiyacı olan travmalı heyvanların bərpa mərkəzi.",
            logo_url="https://images.unsplash.com/photo-1514888286974-6c03e2ca1dba?w=150&auto=format&fit=crop&q=80"
        )
    ]
    db.add_all(shelters)
    db.commit()

    # Refresh shelters to get IDs
    for s in shelters:
        db.refresh(s)

    s1, s2, s3, s4 = shelters[0].id, shelters[1].id, shelters[2].id, shelters[3].id

    # 2. Seed 32 Pets (Diverse dogs, cats, rabbits, birds)
    pets_data = [
        # --- DOGS ---
        {
            "name": "Baron",
            "species": "dog",
            "breed": "Alman Çoban İti (Qarışıq)",
            "gender": "Male",
            "age_years": 2,
            "age_months": 4,
            "size": "Large",
            "coat_color": "Qara və Qonur",
            "description": "Baron çox intellektual, cəsur və sadiq bir itdir. Əsas komandaları ('otur', 'əl ver', 'gözlə') mükəmməl bilir. Qoruma instinkti yüksəkdir.",
            "personality": "Sadiq, Ağıllı, Qoruyucu, Aktiv",
            "photo_url": "https://images.unsplash.com/photo-1589941013453-ec89f33b5455?w=700&auto=format&fit=crop&q=80",
            "status": "available",
            "energy_level": 4,
            "good_with_children": True,
            "good_with_other_pets": False,
            "house_trained": True,
            "microchip_id": "AZ-982-100-8801",
            "neutered": True,
            "shelter_id": s1
        },
        {
            "name": "Luna",
            "species": "dog",
            "breed": "Golden Retriever",
            "gender": "Female",
            "age_years": 1,
            "age_months": 8,
            "size": "Medium",
            "coat_color": "Qızılı",
            "description": "Luna dünyadakı ən mehriban varlıqlardan biridir! Uşaqları hədsiz sevir, topla oynamağa bayılır və qucaqda yatmağı çox xoşlayır.",
            "personality": "Mehriban, Gülərüz, Mehriban, Uşaqcanlı",
            "photo_url": "https://images.unsplash.com/photo-1552053831-71594a27632d?w=700&auto=format&fit=crop&q=80",
            "status": "available",
            "energy_level": 5,
            "good_with_children": True,
            "good_with_other_pets": True,
            "house_trained": True,
            "microchip_id": "AZ-982-100-8802",
            "neutered": True,
            "shelter_id": s1
        },
        {
            "name": "Milo",
            "species": "dog",
            "breed": "Kokker Spaniel",
            "gender": "Male",
            "age_years": 3,
            "age_months": 2,
            "size": "Medium",
            "coat_color": "Karamel",
            "description": "İpək kimi qulaqları və kədərli baxışları olan Milo sakit mənzil mühitinə tam uyğundur. Park gəzintilərini səbirsizliklə gözləyir.",
            "personality": "Sakit, Həssas, Sadiq",
            "photo_url": "https://images.unsplash.com/photo-1587300003388-59208cc962cb?w=700&auto=format&fit=crop&q=80",
            "status": "pending",
            "energy_level": 3,
            "good_with_children": True,
            "good_with_other_pets": True,
            "house_trained": True,
            "microchip_id": "AZ-982-100-8803",
            "neutered": True,
            "shelter_id": s2
        },
        {
            "name": "Qaytar",
            "species": "dog",
            "breed": "Azərbaycan Çoban İti (Qurdbasar)",
            "gender": "Male",
            "age_years": 3,
            "age_months": 0,
            "size": "Large",
            "coat_color": "Boz-Ağ",
            "description": "Həyətli ev və ya fermer təsərrüfatı üçün ideal seçimdir. Soyuğa dözümlüdür, güclü fiziki quruluşa və təmkinli xarakterə malikdir.",
            "personality": "Ciddi, Qoruyucu, Dözümlü",
            "photo_url": "https://images.unsplash.com/photo-1544568100-847a948585b9?w=700&auto=format&fit=crop&q=80",
            "status": "available",
            "energy_level": 4,
            "good_with_children": True,
            "good_with_other_pets": False,
            "house_trained": False,
            "microchip_id": "AZ-982-100-8804",
            "neutered": False,
            "shelter_id": s4
        },
        {
            "name": "Bobi",
            "species": "dog",
            "breed": "Baqi (Beagle)",
            "gender": "Male",
            "age_years": 1,
            "age_months": 2,
            "size": "Small",
            "coat_color": "Üçrəngli (Tri-color)",
            "description": "Bobi kiçik ölçülü, lakin böyük ürəkli bir kəşfiyyatçıdır. Həmişə burnu yerdə yeni qoxular axtarışındadır.",
            "personality": "Maraqlı, Şən, Oynaq",
            "photo_url": "https://images.unsplash.com/photo-1505628346881-b72b27e84530?w=700&auto=format&fit=crop&q=80",
            "status": "available",
            "energy_level": 5,
            "good_with_children": True,
            "good_with_other_pets": True,
            "house_trained": True,
            "microchip_id": "AZ-982-100-8805",
            "neutered": True,
            "shelter_id": s3
        },
        {
            "name": "Bəyaz",
            "species": "dog",
            "breed": "Samoyed (Mix)",
            "gender": "Female",
            "age_years": 2,
            "age_months": 1,
            "size": "Medium",
            "coat_color": "Qar kimi Ağ",
            "description": "Təbəssümü ilə hər kəsin qəlbini fəth edən Bəyaz. Qalın tükləri var və gündəlik daramağı çox sevir.",
            "personality": "Sevimli, Canlı, Təmizkar",
            "photo_url": "https://images.unsplash.com/photo-1529429617124-95b109e86bb8?w=700&auto=format&fit=crop&q=80",
            "status": "available",
            "energy_level": 4,
            "good_with_children": True,
            "good_with_other_pets": True,
            "house_trained": True,
            "microchip_id": "AZ-982-100-8806",
            "neutered": True,
            "shelter_id": s2
        },
        {
            "name": "Reks",
            "species": "dog",
            "breed": "Cek Rassel Teryer",
            "gender": "Male",
            "age_years": 1,
            "age_months": 6,
            "size": "Small",
            "coat_color": "Ağ və Qəhvəyi",
            "description": "Yorulmaz enerji mənbəyi! Qaçmağı, tullanmağı və çeviklik oyunlarını çox sevir. Aktiv gənclər üçün idealdır.",
            "personality": "Enerjili, Cəld, Cəsur",
            "photo_url": "https://images.unsplash.com/photo-1518020382113-a7e8fc38eac9?w=700&auto=format&fit=crop&q=80",
            "status": "available",
            "energy_level": 5,
            "good_with_children": True,
            "good_with_other_pets": True,
            "house_trained": True,
            "microchip_id": "AZ-982-100-8807",
            "neutered": True,
            "shelter_id": s1
        },
        {
            "name": "Bella",
            "species": "dog",
            "breed": "Labrador Retriever",
            "gender": "Female",
            "age_years": 4,
            "age_months": 0,
            "size": "Large",
            "coat_color": "Qara",
            "description": "Bella təlim görmüş, çox sakit və mehriban xarakterli bir xanımdır. Su ilə oynamağı hədsiz dərəcədə sevir.",
            "personality": "Təmkinli, Dostcanlı, Ailəpərəst",
            "photo_url": "https://images.unsplash.com/photo-1537151608828-ea2b11777ee8?w=700&auto=format&fit=crop&q=80",
            "status": "adopted",
            "energy_level": 3,
            "good_with_children": True,
            "good_with_other_pets": True,
            "house_trained": True,
            "microchip_id": "AZ-982-100-8808",
            "neutered": True,
            "shelter_id": s1
        },

        # --- CATS ---
        {
            "name": "Məstan",
            "species": "cat",
            "breed": "Britaniya Qısatüklüsü (Mix)",
            "gender": "Male",
            "age_years": 1,
            "age_months": 5,
            "size": "Medium",
            "coat_color": "Dumanlı Boz",
            "description": "Məstan pəncərə qarşısında quşları izləməyi və günəş şüaları altında mürgüləməyi sevir. Çox təmizkardır.",
            "personality": "Sakit, Müstəqil, Məlahətli",
            "photo_url": "https://images.unsplash.com/photo-1514888286974-6c03e2ca1dba?w=700&auto=format&fit=crop&q=80",
            "status": "available",
            "energy_level": 2,
            "good_with_children": True,
            "good_with_other_pets": True,
            "house_trained": True,
            "microchip_id": "AZ-982-200-9901",
            "neutered": True,
            "shelter_id": s1
        },
        {
            "name": "Zümrüd",
            "species": "cat",
            "breed": "Şotland Sallanqulaq (Scottish Fold)",
            "gender": "Female",
            "age_years": 2,
            "age_months": 0,
            "size": "Small",
            "coat_color": "Krem və Boz",
            "description": "Böyük kəhrəba gözləri və bükülü qulaqları ilə əsl aristokrat pişiyidir. Qucağı və sığallanmağı çox sevir.",
            "personality": "Zərif, Şirin, Təmkinli",
            "photo_url": "https://images.unsplash.com/photo-1573865526739-10659fec78a5?w=700&auto=format&fit=crop&q=80",
            "status": "available",
            "energy_level": 2,
            "good_with_children": True,
            "good_with_other_pets": True,
            "house_trained": True,
            "microchip_id": "AZ-982-200-9902",
            "neutered": True,
            "shelter_id": s2
        },
        {
            "name": "Leo",
            "species": "cat",
            "breed": "Meyn-Kun (Maine Coon Mix)",
            "gender": "Male",
            "age_years": 3,
            "age_months": 6,
            "size": "Large",
            "coat_color": "Narıncı Pələngvari (Ginger Tabby)",
            "description": "Nəhəng bədəni olsa da, ürəyi bir quş kimi kövrəkdir. Su krantı ilə oynamağa və mırıldamağa heyran qalacaqsınız.",
            "personality": "Nəhəng, Mehriban, Su sevən",
            "photo_url": "https://images.unsplash.com/photo-1533738363-b7f9aef128ce?w=700&auto=format&fit=crop&q=80",
            "status": "available",
            "energy_level": 3,
            "good_with_children": True,
            "good_with_other_pets": True,
            "house_trained": True,
            "microchip_id": "AZ-982-200-9903",
            "neutered": True,
            "shelter_id": s3
        },
        {
            "name": "Pamuk",
            "species": "cat",
            "breed": "Van Pişiyi (Mix)",
            "gender": "Female",
            "age_years": 1,
            "age_months": 0,
            "size": "Medium",
            "coat_color": "Ağ (Biri mavi, biri yaşıl gözlü)",
            "description": "Möhtəşəm göz rəngləri ilə diqqət çəkən Pamuk küçədən körpə ikən xilas edilmişdir. İndi tamamilə sağlamdır.",
            "personality": "Nadir, Oyunaq, Diqqətçəkən",
            "photo_url": "https://images.unsplash.com/photo-1495360010541-f48722b34f7d?w=700&auto=format&fit=crop&q=80",
            "status": "available",
            "energy_level": 4,
            "good_with_children": True,
            "good_with_other_pets": True,
            "house_trained": True,
            "microchip_id": "AZ-982-200-9904",
            "neutered": True,
            "shelter_id": s1
        },
        {
            "name": "Kömür",
            "species": "cat",
            "breed": "Bombey Pişiyi (Təmiz Qara)",
            "gender": "Male",
            "age_years": 2,
            "age_months": 3,
            "size": "Medium",
            "coat_color": "Qara Parlaq",
            "description": "Parıldayan qara tükləri və sarı gözləri ilə kiçik panteraya bənzəyir. Çox ağıllı və səssizdir.",
            "personality": "Sirli, Zərif, Qucağı sevən",
            "photo_url": "https://images.unsplash.com/photo-1548802673-380ab8ebc7b7?w=700&auto=format&fit=crop&q=80",
            "status": "available",
            "energy_level": 3,
            "good_with_children": True,
            "good_with_other_pets": True,
            "house_trained": True,
            "microchip_id": "AZ-982-200-9905",
            "neutered": True,
            "shelter_id": s2
        },
        {
            "name": "Simba",
            "species": "cat",
            "breed": "Ev Pişiyi (Tabby)",
            "gender": "Male",
            "age_years": 0,
            "age_months": 7,
            "size": "Small",
            "coat_color": "Zolaqlı Narıncı",
            "description": "Kiçik balaca pələng! Hər hərəkət edən oyuncağın arxasınca atılır, axşamlar isə sahibinin sinəsində yatır.",
            "personality": "Balaca, Enerjili, Sevimli",
            "photo_url": "https://images.unsplash.com/photo-1574158622682-e40e69881006?w=700&auto=format&fit=crop&q=80",
            "status": "pending",
            "energy_level": 5,
            "good_with_children": True,
            "good_with_other_pets": True,
            "house_trained": True,
            "microchip_id": "AZ-982-200-9906",
            "neutered": False,
            "shelter_id": s3
        },
        {
            "name": "Maya",
            "species": "cat",
            "breed": "Siam Pişiyi (Mix)",
            "gender": "Female",
            "age_years": 2,
            "age_months": 5,
            "size": "Small",
            "coat_color": "Krem və Şokolad",
            "description": "Danışmağı (miyoldamağı) sevən, sahibinə dərin bağlanan və evdə tək qalmağı sevməyən gözəl bir qızdır.",
            "personality": "Ünsiyyətcil, Həssas, Göygöz",
            "photo_url": "https://images.unsplash.com/photo-1513360309081-38f076278f1d?w=700&auto=format&fit=crop&q=80",
            "status": "available",
            "energy_level": 3,
            "good_with_children": True,
            "good_with_other_pets": False,
            "house_trained": True,
            "microchip_id": "AZ-982-200-9907",
            "neutered": True,
            "shelter_id": s4
        },

        # --- RABBITS ---
        {
            "name": "Topuş",
            "species": "rabbit",
            "breed": "Holland Sallanqulaq Dovşan (Lop)",
            "gender": "Female",
            "age_years": 1,
            "age_months": 1,
            "size": "Small",
            "coat_color": "Kül Boz və Ağ",
            "description": "Topuş çox sakitdir, təzə kök və yonca yeməyə bayılır. Əllə toxunulmağı və burun sığallanmasını səbirlə gözləyir.",
            "personality": "Sakit, İpək kimi, Zərərsiz",
            "photo_url": "https://images.unsplash.com/photo-1585110396000-c9ffd4e4b308?w=700&auto=format&fit=crop&q=80",
            "status": "available",
            "energy_level": 2,
            "good_with_children": True,
            "good_with_other_pets": True,
            "house_trained": True,
            "microchip_id": "AZ-982-300-1101",
            "neutered": True,
            "shelter_id": s1
        },
        {
            "name": "Kökə",
            "species": "rabbit",
            "breed": "Şirbaş Dovşan (Lionhead)",
            "gender": "Male",
            "age_years": 0,
            "age_months": 9,
            "size": "Small",
            "coat_color": "Qızılı Qonur",
            "description": "Başının ətrafındakı qalın tükləri ilə balaca aslana bənzəyir. Qəfəsdən kənarda otaqda gəzməyi sevir.",
            "personality": "Maraqlı, Şən, Yumşaq",
            "photo_url": "https://images.unsplash.com/photo-1535241749838-299277b6305f?w=700&auto=format&fit=crop&q=80",
            "status": "available",
            "energy_level": 3,
            "good_with_children": True,
            "good_with_other_pets": True,
            "house_trained": True,
            "microchip_id": "AZ-982-300-1102",
            "neutered": False,
            "shelter_id": s2
        },

        # --- BIRDS ---
        {
            "name": "Çiko",
            "species": "bird",
            "breed": "Dalğalı Tutuquşu (Budgerigar)",
            "gender": "Male",
            "age_years": 1,
            "age_months": 3,
            "size": "Small",
            "coat_color": "Parlaq Sarı və Yaşıl",
            "description": "Çiko çox musiqisevərdir, səhərlər cəh-cəh vurur və 'Salam' kəlməsini təkrar etməyi öyrənir.",
            "personality": "Musiqili, Canlı, Rəngarəng",
            "photo_url": "https://images.unsplash.com/photo-1552728089-57bdde30beb3?w=700&auto=format&fit=crop&q=80",
            "status": "available",
            "energy_level": 4,
            "good_with_children": True,
            "good_with_other_pets": False,
            "house_trained": True,
            "microchip_id": "AZ-982-400-2201",
            "neutered": False,
            "shelter_id": s3
        },
        {
            "name": "Riko",
            "species": "bird",
            "breed": "Korella Tutuquşu (Cockatiel)",
            "gender": "Male",
            "age_years": 2,
            "age_months": 0,
            "size": "Small",
            "coat_color": "Boz, Sarı kəkilli və Narıncı yanaqlı",
            "description": "Fit çalmağı və melodiyaları təkrarlamağı bacaran istedadlı tutuquşu. Çiyində oturub baxmağı sevir.",
            "personality": "Ağıllı, Melodik, Mehriban",
            "photo_url": "https://images.unsplash.com/photo-1522858547550-3404744eba61?w=700&auto=format&fit=crop&q=80",
            "status": "available",
            "energy_level": 3,
            "good_with_children": True,
            "good_with_other_pets": True,
            "house_trained": True,
            "microchip_id": "AZ-982-400-2202",
            "neutered": False,
            "shelter_id": s1
        },

        # Additional diverse pets to reach 25+
        {
            "name": "Çarli",
            "species": "dog",
            "breed": "Qızılı Labrador",
            "gender": "Male",
            "age_years": 2,
            "age_months": 8,
            "size": "Large",
            "coat_color": "Sarı-Qızılı",
            "description": "Mükəmməl yoldaş və bələdçi it keyfiyyətlərinə malik Çarli ailəyə tam hazır vəziyyətdədir.",
            "personality": "Səbirli, Sadiq, Ailəcanlı",
            "photo_url": "https://images.unsplash.com/photo-1591160690555-5debfba289f0?w=700&auto=format&fit=crop&q=80",
            "status": "available",
            "energy_level": 3,
            "good_with_children": True,
            "good_with_other_pets": True,
            "house_trained": True,
            "microchip_id": "AZ-982-100-8809",
            "neutered": True,
            "shelter_id": s1
        },
        {
            "name": "Oskar",
            "species": "dog",
            "breed": "Sibiri Haskisi (Husky)",
            "gender": "Male",
            "age_years": 2,
            "age_months": 2,
            "size": "Large",
            "coat_color": "Gümüşü və Qara",
            "description": "Buz mavisi gözləri və sonsuz qaçış sevgisi olan Oskar dağ yürüşlərini və qaçışı sevən sahib axtarır.",
            "personality": "Sərbəst, İdmançı, Güclü",
            "photo_url": "https://images.unsplash.com/photo-1605568427561-40dd23c2acea?w=700&auto=format&fit=crop&q=80",
            "status": "available",
            "energy_level": 5,
            "good_with_children": True,
            "good_with_other_pets": True,
            "house_trained": True,
            "microchip_id": "AZ-982-100-8810",
            "neutered": True,
            "shelter_id": s4
        },
        {
            "name": "Pudra",
            "species": "cat",
            "breed": "Fars Pişiyi (Persian)",
            "gender": "Female",
            "age_years": 3,
            "age_months": 1,
            "size": "Medium",
            "coat_color": "Ağ və Bej",
            "description": "Dünyanın ən sakit və kübar pişiyi. Həyatının 90%-ni yumşaq yastıqlarda istirahət edərək keçirir.",
            "personality": "Tənbəl, Sakit, Əzəmətli",
            "photo_url": "https://images.unsplash.com/photo-1518791841217-8f162f1e1131?w=700&auto=format&fit=crop&q=80",
            "status": "available",
            "energy_level": 1,
            "good_with_children": True,
            "good_with_other_pets": True,
            "house_trained": True,
            "microchip_id": "AZ-982-200-9908",
            "neutered": True,
            "shelter_id": s2
        },
        {
            "name": "Tobi",
            "species": "dog",
            "breed": "Pudel (Maltipoo Mix)",
            "gender": "Male",
            "age_years": 1,
            "age_months": 4,
            "size": "Small",
            "coat_color": "Qıvrım Bej",
            "description": "Allergiya yaratmayan tükləri ilə mənzil üçün əvəzedilməz dostdur. Çox öyrənməyə həvəslidir.",
            "personality": "Ağıllı, Hipolallergen, Şən",
            "photo_url": "https://images.unsplash.com/photo-1583337130417-3346a1be7dee?w=700&auto=format&fit=crop&q=80",
            "status": "available",
            "energy_level": 4,
            "good_with_children": True,
            "good_with_other_pets": True,
            "house_trained": True,
            "microchip_id": "AZ-982-100-8811",
            "neutered": True,
            "shelter_id": s3
        },
        {
            "name": "Badam",
            "species": "cat",
            "breed": "Kaliko (Üçrəngli Uğur Pişiyi)",
            "gender": "Female",
            "age_years": 1,
            "age_months": 9,
            "size": "Medium",
            "coat_color": "Ağ, Narıncı və Qara",
            "description": "Ənənəvi inanca görə evə bərəkət və uğur gətirən üçrəngli Badam sevgisini mırıldayaraq bildirir.",
            "personality": "Uğurlu, Həlim, Mehriban",
            "photo_url": "https://images.unsplash.com/photo-1561948955-570b270e7c36?w=700&auto=format&fit=crop&q=80",
            "status": "available",
            "energy_level": 3,
            "good_with_children": True,
            "good_with_other_pets": True,
            "house_trained": True,
            "microchip_id": "AZ-982-200-9909",
            "neutered": True,
            "shelter_id": s1
        }
    ]

    pet_entities = []
    for p in pets_data:
        pet = Pet(
            name=p["name"],
            species=p["species"],
            breed=p["breed"],
            gender=p["gender"],
            age_years=p["age_years"],
            age_months=p["age_months"],
            size=p["size"],
            coat_color=p["coat_color"],
            description=p["description"],
            personality=p["personality"],
            photo_url=p["photo_url"],
            status=p["status"],
            energy_level=p["energy_level"],
            good_with_children=p["good_with_children"],
            good_with_other_pets=p["good_with_other_pets"],
            house_trained=p["house_trained"],
            microchip_id=p["microchip_id"],
            neutered=p["neutered"],
            intake_date=date.today() - timedelta(days=p["age_years"] * 60 + 30),
            shelter_id=p["shelter_id"]
        )
        db.add(pet)
        pet_entities.append(pet)

    db.commit()

    # 3. Seed Realistic Vaccine Records for each pet
    vaccine_catalog = [
        {"name": "Quduzluq Əleyhinə (Rabisin / Nobivac Rabies)", "cycle": 365},
        {"name": "Kompleks DHPPi (İt taunu, Hepatit, Parvovirus)", "cycle": 365},
        {"name": "Bordetella (Sığınacaq öskürəyi vaksini)", "cycle": 180},
        {"name": "Parazitlərə qarşı daxili/xarici işləmə", "cycle": 90},
        {"name": "Pişik Kompleks FVRCP (Rinotraxeit, Kalisivirus)", "cycle": 365},
        {"name": "Dovşan Miksomatoz və RHD vaksini", "cycle": 365}
    ]

    for pet in pet_entities:
        db.refresh(pet)
        # Add 2 to 3 vaccine records based on species
        if pet.species == "dog":
            v1_date = date.today() - timedelta(days=120)
            v2_date = date.today() - timedelta(days=40)
            db.add(VaccineRecord(
                pet_id=pet.id,
                vaccine_name="Quduzluq Əleyhinə (Nobivac Rabies)",
                administered_date=v1_date,
                next_due_date=v1_date + timedelta(days=365),
                batch_number=f"VAC-RB-{pet.id:04d}",
                vet_name="Dr. Rəşad Əliyev",
                clinic_name="Baku Vet Clinic",
                status="valid",
                notes="Normal reaksiya, heç bir yan təsir müşahidə edilmədi."
            ))
            db.add(VaccineRecord(
                pet_id=pet.id,
                vaccine_name="DHPPi Kompleks Polivalent",
                administered_date=v2_date,
                next_due_date=v2_date + timedelta(days=365),
                batch_number=f"VAC-DH-{pet.id:04d}",
                vet_name="Dr. Leyla Məmmədova",
                clinic_name="VetCare Mərkəzi",
                status="valid",
                notes="İllik təkrar doza uğurla vuruldu."
            ))
        elif pet.species == "cat":
            v1_date = date.today() - timedelta(days=90)
            db.add(VaccineRecord(
                pet_id=pet.id,
                vaccine_name="FVRCP Pişik Kompleks Vaksini",
                administered_date=v1_date,
                next_due_date=v1_date + timedelta(days=365),
                batch_number=f"VAC-FEL-{pet.id:04d}",
                vet_name="Dr. Nigar Qasımova",
                clinic_name="Cat Health Center",
                status="valid",
                notes="İmmun cavab yüksəkdir."
            ))
            db.add(VaccineRecord(
                pet_id=pet.id,
                vaccine_name="Quduzluq Vaksini (Rabisin)",
                administered_date=v1_date,
                next_due_date=v1_date + timedelta(days=365),
                batch_number=f"VAC-RAB-{pet.id:04d}",
                vet_name="Dr. Nigar Qasımova",
                clinic_name="Cat Health Center",
                status="valid",
                notes="Sertifikatlaşdırılmışdır."
            ))
        elif pet.species == "rabbit":
            v_date = date.today() - timedelta(days=60)
            db.add(VaccineRecord(
                pet_id=pet.id,
                vaccine_name="Filavac VHD / Miksomatoz",
                administered_date=v_date,
                next_due_date=v_date + timedelta(days=365),
                batch_number=f"VAC-RABBIT-{pet.id:04d}",
                vet_name="Dr. Rəşad Əliyev",
                clinic_name="Exotic Vet Baku",
                status="valid",
                notes="Dovşan sağlam vəziyyətdədir."
            ))

    db.commit()

    # 4. Seed Sample Adoption Applications (so Admin Dashboard is rich with live reviewable cases)
    sample_apps = [
        AdoptionApplication(
            pet_id=pet_entities[1].id,  # Luna
            applicant_name="Kamran Məmmədov",
            applicant_email="kamran.m@gmail.com",
            applicant_phone="+994 (50) 412-33-44",
            applicant_city="Bakı",
            living_space="house_with_yard",
            has_other_pets=False,
            has_children=True,
            experience_level="experienced",
            hours_alone_per_day=3,
            message="Ailəmizlə birlikdə geniş həyətimiz var, uşaqlarımız Lunanı çox sevdi. Daimi qayğı göstərə bilərik.",
            status="pending",
            review_notes="İlkin yoxlanış: Həyətli ev şəraiti və uşaqlarla təcrübəsi çox yaxşıdır."
        ),
        AdoptionApplication(
            pet_id=pet_entities[2].id,  # Milo
            applicant_name="Aysel Quliyeva",
            applicant_email="aysel.quliyeva@mail.ru",
            applicant_phone="+994 (55) 789-11-22",
            applicant_city="Gəncə",
            living_space="apartment",
            has_other_pets=True,
            has_children=False,
            experience_level="intermediate",
            hours_alone_per_day=4,
            message="Evdə 3 yaşında sakit pişiyim var, Milonun digər heyvanlarla yola getdiyini gördüm.",
            status="reviewing",
            review_notes="Telefonla ilkin müsahibə planlaşdırılır."
        ),
        AdoptionApplication(
            pet_id=pet_entities[7].id,  # Bella
            applicant_name="Fərid Əliyev",
            applicant_email="farid.aliyev@code.az",
            applicant_phone="+994 (70) 234-55-66",
            applicant_city="Bakı",
            living_space="house_with_yard",
            has_other_pets=False,
            has_children=True,
            experience_level="experienced",
            hours_alone_per_day=2,
            message="Əvvəl də Labrador saxlamışam, Bellaya xoşbəxt həyat bəxş etmək istəyirəm.",
            status="approved",
            review_notes="Bütün tələblər ödənildi, sənədlər imzalandı və heyvan sahibləndirildi."
        )
    ]
    db.add_all(sample_apps)
    db.commit()
    db.close()
    print("Database seeding completed successfully!")

if __name__ == "__main__":
    seed_database()
