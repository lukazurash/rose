"""Seed content for Rose. Loaded into the database on first run; after that the admin panel owns it.

TEXTS: every word on the public site, {key: (Georgian, English)}. New keys are added on start-up without
touching keys the admin already edited.
"""

TEXTS = {
    # head
    "meta_title": ("Rose: ყვავილების მაღაზია ვაკეში, თბილისი", "Rose: a flower shop in Vake, Tbilisi"),
    "meta_desc": ("ხელით აწყობილი ბუკეტები 45 ₾-დან. შეუკვეთე ონლაინ, მივიტანთ თბილისში იმავე დღეს.",
                  "Hand-tied bouquets from 45 ₾. Order online and we deliver across Tbilisi the same day."),
    "skip": ("გადასვლა შინაარსზე", "Skip to content"),
    # nav
    "nav_bouquets": ("ბუკეტები", "Bouquets"),
    "nav_custom": ("შენი ბუკეტი", "Your own"),
    "nav_events": ("ქორწილები", "Weddings"),
    "nav_visit": ("მისამართი", "Visit"),
    "nav_menu": ("მენიუ", "Menu"),
    "lang_switch": ("English", "ქართული"),
    "cta_order": ("შეუკვეთე ბუკეტი", "Order a bouquet"),
    "menu_all": ("ყველა ბუკეტი", "All bouquets"),
    "menu_all_line": ("სრული კატალოგი ფასებით", "The full range with prices"),
    # hero
    "hero_notice": ("შეუკვეთე {cutoff}-მდე და მივიტანთ დღესვე", "Order by {cutoff} for delivery today"),
    "hero_h1": ("ყვავილების მაღაზია ვაკეში, თბილისი", "Flower shop in Vake, Tbilisi"),
    "hero_lead": ("ხელით აწყობილი ბუკეტები {from} ₾-დან. ღიაა ყოველდღე 09:00–21:00.",
                  "Hand-tied bouquets from {from} ₾. Open every day, 9:00 to 21:00."),
    # visit
    "visit_h2": ("მაღაზია და მიტანა", "Shop and delivery"),
    "visit_label": ("მისამართი", "Address"),
    "visit_area": ("იხილე რუკაზე", "See the area"),
    "visit_dirs": ("მარშრუტი", "Get directions"),
    "visit_hours": ("სამუშაო საათები", "Opening hours"),
    "visit_delivery": ("მიტანა", "Delivery"),
    "visit_delivery_v": ("მთელ თბილისში {min} ₾-დან, 2 საათში", "All of Tbilisi from {min} ₾, within 2 hours"),
    "visit_events": ("ქორწილები", "Weddings"),
    "visit_events_v": ("უფასო კონსულტაცია", "Free consultation"),
    # bouquets
    "shop_h2": ("ბუკეტები და ფასები", "Bouquets and prices"),
    "shop_line": ("ყველა ბუკეტს თან ახლავს უფასო ბარათი.", "Every bouquet comes with a free card."),
    "shop_all": ("ყველა ბუკეტი", "See all bouquets"),
    "shop_order": ("შეკვეთა", "Order"),
    "tag_hit": ("ფავორიტი", "Bestseller"),
    "tag_vase": ("ვაზით", "With a vase"),
    "tag_premium": ("პრემიუმი", "Premium"),
    "cat_all": ("ყველა", "All"),
    "cat_love": ("სიყვარული", "Love"),
    "cat_birthday": ("დაბადების დღე", "Birthday"),
    "cat_wedding": ("ქორწილი", "Wedding"),
    "cat_vase": ("ვაზაში", "In a vase"),
    "catalogue_h1": ("ყველა ბუკეტი", "All bouquets"),
    "catalogue_line": ("ფასი მოიცავს შეფუთვას და ბარათს. მიტანა თბილისში {min} ₾-დან.",
                       "Prices include wrapping and a card. Delivery in Tbilisi from {min} ₾."),
    "catalogue_empty": ("ამ კატეგორიაში ჯერ ბუკეტი არ არის.", "No bouquets in this group yet."),
    "back_home": ("მთავარი გვერდი", "Home page"),
    # custom builder
    "c_h2": ("შექმენი შენი ბუკეტი", "Make your own bouquet"),
    "c_line": ("აირჩიე ბიუჯეტი და ფერები. ფლორისტი WhatsApp-ით მოგწერს და ერთად დააზუსტებთ.",
               "Pick a budget and colours. The florist writes to you on WhatsApp to agree the details."),
    "c_budget": ("ბიუჯეტი", "Budget"),
    "c_colors": ("ფერები", "Colours"),
    "c_note": ("რისთვის არის", "What it is for"),
    "c_note_hint": ("არასავალდებულო, მაგ. დედის დაბადების დღე", "Optional, e.g. Mum's birthday"),
    "c_name": ("შენი სახელი", "Your name"),
    "c_phone": ("ტელეფონი", "Phone"),
    "c_phone_hint": ("არასავალდებულო", "Optional"),
    "c_send": ("გაგზავნე იდეა", "Send your idea"),
    "c_sent": ("იდეა შენახულია, მოთხოვნა #{n}. WhatsApp იხსნება, რომ გაუგზავნო.",
               "Your idea is saved as request #{n}. WhatsApp opens so you can send it."),
    "c_preview": ("შენი ბუკეტის ესკიზი", "A sketch of your bouquet"),
    "col_pink": ("ვარდისფერი", "Pink"),
    "col_red": ("წითელი", "Red"),
    "col_white": ("თეთრი", "White"),
    "col_peach": ("ატმისფერი", "Peach"),
    "col_yellow": ("ყვითელი", "Yellow"),
    "col_blue": ("ცისფერი", "Blue"),
    # chapters (photo-chapters)
    "ch_h2": ("როგორ იქმნება შენი ბუკეტი", "How your bouquet is made"),
    "ch_lead": ("დილის მიწოდებიდან შენს კარამდე, ერთ დღეში.", "From the morning delivery to your door in one day."),
    "ch1_t": ("ახალი ყვავილები ყოველ დილით", "Fresh stems every morning"),
    "ch1_p": ("ყვავილები დილით შემოდის და მაღაზიის გახსნამდე სუფთა წყალში დგას.",
              "Flowers arrive in the morning and stand in fresh water before the shop opens."),
    "ch2_t": ("შერჩეული შენი შეკვეთისთვის", "Chosen for your order"),
    "ch2_p": ("ფლორისტი ღეროებს ფერისა და ზომის მიხედვით არჩევს და მაგიდაზე ალაგებს.",
              "The florist picks the stems for your bouquet by colour and size and lays them out on the bench."),
    "ch3_t": ("შეკრული, შეფუთული, გადაღებული", "Tied, wrapped and photographed"),
    "ch3_p": ("ბუკეტს ვჭრით, ვკრავთ და ვფუთავთ, შემდეგ კურიერის გასვლამდე ფოტოს გიგზავნით WhatsApp-ით.",
              "We trim, tie and wrap it, then send you a photo on WhatsApp before the courier leaves."),
    # events
    "ev_cta": ("მოითხოვე კონსულტაცია", "Request a consultation"),
    "ev_msg": ("გამარჯობა, Rose! მინდა კონსულტაცია ღონისძიებისთვის.", "Hello Rose! I'd like a consultation for an event."),
    # order
    "o_h2": ("ბუკეტის შეკვეთა", "Order a bouquet"),
    "o_line": ("შეუკვეთე {cutoff}-მდე და მივიტანთ დღესვე. {free} ₾-დან მიტანა უფასოა.",
               "Order by {cutoff} for delivery today. Delivery is free on orders from {free} ₾."),
    "o_bouquet": ("ბუკეტი", "Bouquet"),
    "o_date": ("მიტანის დღე", "Delivery day"),
    "o_zone": ("უბანი", "District"),
    "o_card": ("ბარათის ტექსტი", "Card message"),
    "o_card_hint": ("არასავალდებულო, მაგ. გილოცავ დაბადების დღეს, დე", "Optional, e.g. Happy birthday, Mum"),
    "o_name": ("შენი სახელი", "Your name"),
    "o_phone": ("ტელეფონი", "Phone"),
    "o_phone_hint": ("არასავალდებულო", "Optional"),
    "o_total": ("ჯამი", "Total"),
    "o_fee": ("მიტანა", "delivery"),
    "o_free": ("უფასო", "free"),
    "o_reply": ("შეკვეთა ინახება და WhatsApp იხსნება, რომ გაგვიგზავნო.",
                "Your order is saved and WhatsApp opens so you can send it to us."),
    "o_sent": ("შეკვეთა #{n} შენახულია. WhatsApp იხსნება, რომ გაგვიგზავნო.",
               "Order #{n} is saved. WhatsApp opens so you can send it to us."),
    "o_open_wa": ("გახსენი WhatsApp", "Open WhatsApp"),
    "o_sending": ("იგზავნება", "Sending"),
    "o_failed": ("ვერ გაიგზავნა, კავშირი გაწყდა. შენი ტექსტი შენახულია, სცადე თავიდან.",
                 "Not sent: the connection failed. Your words are still here, try again."),
    "o_fix": ("გასასწორებელი ველები: {n}", "{n} fields to fix."),
    # field errors
    "e_name": ("დაწერე სახელი, ვისი სახელითაც არის შეკვეთა.", "Write the name the order is under."),
    "e_phone": ("დაწერე ტელეფონი ციფრებით, მაგ. 5xx xx xx xx.", "Write the phone as digits, like 5xx xx xx xx."),
    "e_date": ("აირჩიე მიტანის დღე, დღეიდან 60 დღის ფარგლებში.", "Pick a delivery day within the next 60 days."),
    "e_late": ("დღევანდელი შეკვეთები {cutoff}-მდე მიიღება. აირჩიე ხვალინდელი დღე.", "Same-day orders close at {cutoff}. Pick tomorrow."),
    "e_bouquet": ("აირჩიე ბუკეტი სიიდან.", "Pick a bouquet from the list."),
    "e_zone": ("აირჩიე უბანი სიიდან.", "Pick a district from the list."),
    "e_card": ("ბარათის ტექსტი 200 სიმბოლომდე უნდა იყოს.", "Keep the card message under 200 characters."),
    "e_budget": ("ბიუჯეტი 50-დან 500 ₾-მდე.", "Pick a budget from 50 to 500 ₾."),
    "e_busy": ("ძალიან ბევრი მოთხოვნა. სცადე რამდენიმე წუთში.", "Too many requests. Try again in a few minutes."),
    # whatsapp message
    "m_hi": ("გამარჯობა, Rose! მინდა შევუკვეთო:", "Hello Rose! I'd like to order:"),
    "m_order": ("შეკვეთა", "Order"),
    "m_bouquet": ("ბუკეტი", "Bouquet"),
    "m_date": ("მიტანა", "Delivery"),
    "m_zone": ("უბანი", "District"),
    "m_card": ("ბარათი", "Card"),
    "m_name": ("სახელი", "Name"),
    "m_phone": ("ტელეფონი", "Phone"),
    "m_total": ("ჯამი", "Total"),
    "m_custom": ("გამარჯობა, Rose! მინდა ინდივიდუალური ბუკეტი.", "Hello Rose! I'd like a custom bouquet."),
    "m_request": ("მოთხოვნა", "Request"),
    "m_budget": ("ბიუჯეტი", "Budget"),
    "m_colors": ("ფერები", "Colours"),
    "m_for": ("რისთვის", "For"),
    "m_hello": ("გამარჯობა, Rose!", "Hello Rose!"),
    # close and footer
    "close_h2": ("ყვავილები დღესვე, მთელ თბილისში", "Flowers today, anywhere in Tbilisi"),
    "close_line": ("შეუკვეთე {cutoff}-მდე და ბუკეტი დღესვე მივა.", "Order by {cutoff} and the bouquet arrives today."),
    "foot_wa": ("მოგვწერე WhatsApp-ზე", "Message us on WhatsApp"),
    "foot_privacy": ("კონფიდენციალურობა", "Privacy"),
    "foot_by": ("საიტი: ლუკა", "Site by Luka"),
    "credits_line": ("ფოტოები: Unsplash და Wikimedia Commons", "Photographs via Unsplash and Wikimedia Commons"),
    "credits_h1": ("ფოტოების ავტორები", "Photograph credits"),
    "privacy_h1": ("კონფიდენციალურობა", "Privacy"),
    "privacy_body": ("შეკვეთისას ვინახავთ შენს სახელს, ტელეფონს (თუ მიუთითებ), მიტანის დღეს, უბანს და ბარათის ტექსტს, მხოლოდ შეკვეთის შესასრულებლად. მონაცემებს არავის ვუზიარებთ. წაშლა რომ გინდოდეს, მოგვწერე WhatsApp-ზე.",
                     "When you order we keep your name, your phone if you give it, the delivery day, the district and the card message, only to deliver the order. We share them with no one. To have them deleted, message us on WhatsApp."),
    "nf_h1": ("გვერდი ვერ მოიძებნა", "Page not found"),
    "nf_line": ("ეს ბმული აღარ მუშაობს. ბუკეტები მთავარ გვერდზეა.", "This link no longer works. The bouquets are on the home page."),
    # photo alt text
    "alt_hero": ("ფლორისტი მაკრატლით ჭრის ღეროებს სამუშაო მაგიდაზე, უკან ყვავილების ვედროები", "A florist trimming stems at the workbench, buckets of flowers behind"),
    "alt_visit": ("ატმისფერი ვარდების ბუკეტი მინის ვაზაში", "Peach roses arranged in a glass vase"),
    "alt_ch1": ("ახლად მოტანილი ყვავილები შავ ვედროში", "Fresh flower buds standing in a black bucket"),
    "alt_ch2": ("ღეროები და ფოთლები ფლორისტის მაგიდაზე", "Stems and leaves laid out on the florist's bench"),
    "alt_ch3": ("ფლორისტი ჭრის შეფუთული ბუკეტის ღეროებს", "A florist trimming the stems of a wrapped bouquet"),
}

SETTINGS = {
    "shop_name": "Rose",
    "whatsapp": "995000000000",  # the shop's WhatsApp number, international format without +
    "street": "",                # empty: the site names the district only and links "See the area"
    "district_ka": "ვაკე",
    "district_en": "Vake",
    "city_ka": "თბილისი",
    "city_en": "Tbilisi",
    # one row per line: days for system.js (mon-sun, sat,sun ...) | Georgian label | English label | time
    "hours": "mon-sun|ყოველდღე|Every day|09:00–21:00",
    "hours_assumed": "1",        # 1 until the owner confirms the hours: no "open now" line is shown
    "cutoff": "18:00",           # same-day orders close at this time (Tbilisi time)
    "free_from": "300",          # free delivery from this order value, in GEL
    "days_ahead": "60",
    "site_by_url": "https://lukazurash.github.io",
}

# (Georgian name, English name, Georgian line, English line, price, categories, tag, photo source, featured)
BOUQUETS = [
    ("ვარდისფერი ღრუბელი", "Pink Cloud", "ვარდები, მატიოლა და ეუსტომა ჰაეროვან შეფუთვაში", "Roses, stock and lisianthus in airy wrapping", 120, "love,birthday", "hit", "pinkwhite.jpg", 1),
    ("ბაღის ვარდები", "Garden Roses", "ნაზი, უხვად გაშლილი ბაღის ვარდები", "Soft, full-bloom garden roses", 150, "love,wedding", "", "hero.jpg", 1),
    ("მზიანი დღე", "Sunny Day", "მზესუმზირა, ჰორტენზია და ნარინჯისფერი ვარდები", "Sunflowers, hydrangea and orange roses", 130, "birthday", "", "sunflower.jpg", 1),
    ("დიდი ბუკეტი", "The Grand", "ბაღის ვარდები, ევკალიპტი და ტყის კენკრა", "Garden roses, eucalyptus and wild berries", 220, "wedding,love", "premium", "roses.jpg", 1),
    ("წითელი ბუშ-ვარდები", "Red Spray Roses", "კლასიკა, რომელიც არასდროს ბერდება", "A classic that never gets old", 95, "love", "", "redroses.jpg", 0),
    ("ატმისფერი ვაზა", "Peach in a Vase", "ბუკეტი მინის ვაზით, მზადაა საჩუქრად", "Arranged in a glass vase, ready to give", 140, "birthday,vase", "vase", "vase.jpg", 0),
    ("მინდვრის ზღაპარი", "Meadow Tale", "ფერადი და ცოცხალი, ზაფხულის განწყობით", "Colourful and lively, a taste of summer", 110, "birthday", "", "colorful.jpg", 0),
    ("ტიტები ვაზაში", "Tulips in a Vase", "15 ვარდისფერი ტიტა მინის ვაზით", "15 pink tulips with a glass vase", 85, "vase,love", "vase", "pinkvase.jpg", 0),
    ("ცეცხლოვანი", "Ember", "ნარინჯისფერი და წითელი, მინის ქილაში", "Orange and red, in a glass jar", 105, "birthday,vase", "vase", "redtable.jpg", 0),
    ("თეთრი ნაზი", "Soft White", "თეთრი და კრემისფერი, ქორწილისთვის", "White and cream, made for weddings", 160, "wedding", "", "white.jpg", 0),
    ("პატარა სიურპრიზი", "Little Surprise", "მინი ბუკეტი მშრალი ყვავილებით", "A mini bouquet of dried flowers", 45, "love,birthday", "", "dried.jpg", 0),
]

ZONES = [
    ("ვაკე", "Vake", 10), ("საბურთალო", "Saburtalo", 10), ("მთაწმინდა", "Mtatsminda", 12),
    ("ძველი თბილისი", "Old Tbilisi", 12), ("ვერე", "Vere", 12), ("დიდუბე", "Didube", 15),
    ("ჩუღურეთი", "Chugureti", 15), ("ნაძალადევი", "Nadzaladevi", 18), ("ისანი", "Isani", 18),
    ("დიღომი", "Dighomi", 20), ("გლდანი", "Gldani", 20), ("სამგორი", "Samgori", 20), ("ვარკეთილი", "Varketili", 20),
]

# site photo slots: slot -> (source file, make a 4:5 phone crop, focus x, focus y)
PHOTOS = {
    "hero": ("m138226685-2400.webp", True, 0.45, 0.5),
    "visit": ("vase.jpg", False, 0.5, 0.45),
    "ch1": ("m183016636-2400.webp", False, 0.4, 0.4),
    "ch2": ("f138226682.jpg", False, 0.5, 0.5),
    "ch3": ("m138226686-2400.webp", False, 0.6, 0.6),
}

# credits for the stand-in photographs, by source file (shown on /credits while the photograph is on the site)
CREDITS = {
    "m138226685-2400.webp": "direct2Florist, CC BY 2.0, Wikimedia Commons|https://commons.wikimedia.org/wiki/File:Florist_cutting_stems_with_floristry_scissors.jpg",
    "m138226686-2400.webp": "direct2Florist, CC BY 2.0, Wikimedia Commons|https://commons.wikimedia.org/wiki/File:Florist_cutting_flower_stems.jpg",
    "m183016636-2400.webp": "Leo219, CC BY-SA 4.0, Wikimedia Commons|https://commons.wikimedia.org/wiki/File:Buds_and_flowers_of_Leucadendron_Plumosum_in_a_black_bucket.jpg",
    "f138226682.jpg": "direct2Florist, CC BY 2.0, Wikimedia Commons|https://commons.wikimedia.org/wiki/File:Flowers_ready_to_be_prepared_by_florist.jpg",
}
UNSPLASH = "Unsplash, Unsplash License|https://unsplash.com/license"
