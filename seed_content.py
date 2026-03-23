import MySQLdb
import json
import os
import sys
from dotenv import load_dotenv

# Fix Windows console encoding for Hindi/Telugu characters
if sys.platform == 'win32':
    try:
        sys.stdout.reconfigure(encoding='utf-8', errors='replace')
        sys.stderr.reconfigure(encoding='utf-8', errors='replace')
    except:
        pass

load_dotenv()

DB_HOST = os.getenv("MYSQL_HOST", "localhost")
DB_USER = os.getenv("MYSQL_USER", "root")
DB_PASSWORD = os.getenv("MYSQL_PASSWORD", "")
DB_NAME = os.getenv("MYSQL_DB", "ruralquest_db")

def seed_data():
    try:
        db = MySQLdb.connect(host=DB_HOST, user=DB_USER, passwd=DB_PASSWORD, db=DB_NAME, charset='utf8mb4')
        cur = db.cursor()

        # Phase 1: Define Subjects and their counts
        # We define them here first to ensure subtitles match our lists
        CHAPTER_LISTS = {
            # Grade 8
            ("8", "Mathematics"): [
                "Rational Numbers", "Linear Equations in One Variable", "Understanding Quadrilaterals",
                "Practical Geometry", "Data Handling", "Squares and Square Roots", "Cubes and Cube Roots",
                "Comparing Quantities", "Algebraic Expressions and Identities", "Visualising Solid Shapes",
                "Mensuration", "Exponents and Powers", "Direct and Inverse Proportions", "Factorisation",
                "Introduction to Graphs",
            ],
            ("8", "Science"): [
                "Crop Production & Management", "Microorganisms", "Synthetic Fibres & Plastics",
                "Metals & Non-Metals", "Coal & Petroleum", "Combustion and Flame",
                "Conservation of Plants and Animals", "Cell - Structure and Functions",
                "Reproduction in Animals", "Reaching the Age of Adolescence",
                "Force and Pressure", "Friction", "Sound", "Chemical Effects of Electric Current",
                "Some Natural Phenomena", "Light", "Stars and the Solar System", "Pollution of Air and Water",
            ],
            ("8", "English"): [
                "The Best Christmas Present", "The Tsunami", "Glimpses of the Past",
                "Bepin Choudhury", "The Summit Within", "This is Jody's Fawn",
                "A Visit to Cambridge", "A Short Monsoon Diary", "The Great Stone Face I",
                "The Great Stone Face II",
            ],
            ("8", "Social Studies"): [
                "How, When and Where", "From Trade to Territory", "Ruling the Countryside",
                "Tribal Diku", "When People Rebel", "Weavers, Iron Smelters and Factory Owners",
                "Civilising the Native", "Women, Caste and Reform", "The Making of the National Movement",
                "India After Independence",
            ],
            ("8", "Hindi"): [
                "ध्वनि", "लाख की चूड़ियां", "बस की यात्रा", "दीवानों की हस्ती",
                "चिठ्ठियों की अनूठी दुनिया", "क्या निराश हुआ जाए", "भगवान के डाकिए",
                "यह सबसे कठिन समय नहीं", "कबीर की साखियाँ", "कामचोर",
                "जब सिनेमा ने बोलना सीखा", "सुदाమా चरित", "जहाँ पहिया है",
                "अकबरी लोटा", "सूरदास के पद", "पानी की कहानी",
                "बाज और साँप", "टोपी शुक्ला",
            ],
            ("8", "Telugu"): [
                "మాతృభూమి", "పల్లెటూరి పిల్లగాడు", "లోభి", "నాగభైరవ",
                "స్వాతంత్ర్య సమరం", "గురజాడ", "విద్య", "సంస్కృతి",
            ],
            # Grade 9
            ("9", "Mathematics"): [
                "Number Systems", "Polynomials", "Coordinate Geometry",
                "Linear Equations in Two Variables", "Introduction to Euclid's Geometry",
                "Lines and Angles", "Triangles", "Quadrilaterals", "Areas of Parallelograms and Triangles",
                "Circles", "Constructions", "Heron's Formula",
            ],
            ("9", "Science"): [
                "Matter in Our Surroundings", "Is Matter Around Us Pure?", "Atoms and Molecules",
                "Structure of the Atom", "The Fundamental Unit of Life", "Tissues",
                "Diversity in Living Organisms", "Motion", "Force and Laws of Motion",
                "Gravitation", "Work and Energy", "Sound",
                "Why Do We Fall Ill?", "Natural Resources", "Improvement in Food Resources",
            ],
            ("9", "English"): [
                "The Fun They Had", "The Sound of Music", "The Little Girl",
                "A Truly Beautiful Mind", "The Snake and the Mirror",
                "My Childhood", "Packing", "Reach for the Top", "The Bond of Love",
            ],
            ("9", "Social Studies"): [
                "The French Revolution", "Socialism in Europe", "Nazism and the Rise of Hitler",
                "Forest Society and Colonialism", "Pastoralists in the Modern World",
                "India - Size and Location", "Physical Features of India", "Drainage",
                "Climate", "Natural Vegetation and Wild Life", "Population",
                "What is Democracy? Why Democracy?", "Constitutional Design",
                "Electoral Politics", "Working of Institutions", "Democratic Rights",
                "The Story of Village Palampur",
            ],
            ("9", "Hindi"): [
                "दो बैलों की कथा", "ल्हासा की ओर", "उपभोक्तावाद की संस्कृति",
                "साँवले सपनों की याद", "नाना साहब की पुत्री", "प्रेमचंद के फटे जूते",
                "मेरे बचपन के दिन", "एक कुत्ता और एक मैना",
            ],
            ("9", "Telugu"): [
                "శివతాండవం", "చైతన్యదీప్తి", "ఉద్యమస్ఫూర్తి", "కవిత్వ పరిమళం",
                "సాహిత్య సౌరభం", "భాషా వైభవం", "నీతి శతకం", "దేశభక్తి",
            ],
            # Grade 10
            ("10", "Mathematics"): [
                "Real Numbers", "Polynomials", "Pair of Linear Equations in Two Variables",
                "Quadratic Equations", "Arithmetic Progressions", "Triangles",
                "Coordinate Geometry", "Introduction to Trigonometry", "Some Applications of Trigonometry",
                "Circles", "Constructions", "Areas Related to Circles",
                "Surface Areas and Volumes", "Statistics",
            ],
            ("10", "Science"): [
                "Chemical Reactions and Equations", "Acids, Bases and Salts", "Metals and Non-metals",
                "Carbon and its Compounds", "Periodic Classification of Elements",
                "Life Processes", "Control and Coordination", "How do Organisms Reproduce?",
                "Heredity and Evolution", "Light - Reflection and Refraction",
                "Human Eye and Colourful World", "Electricity", "Magnetic Effects of Electric Current",
                "Sources of Energy", "Our Environment", "Management of Natural Resources",
            ],
            ("10", "English"): [
                "A Letter to God", "Nelson Mandela: Long Walk to Freedom",
                "Two Stories about Flying", "From the Diary of Anne Frank",
                "The Hundred Dresses – I", "The Hundred Dresses – II",
                "Glimpses of India", "Mijbil the Otter", "Madam Rides the Bus",
                "The Sermon at Benares", "The Proposal",
                "Amanda!", "Animals",
            ],
            ("10", "Social Studies"): [
                "The Rise of Nationalism in Europe", "Nationalism in India",
                "The Making of a Global World", "Print Culture and the Modern World",
                "Resources and Development", "Forest and Wildlife Resources",
                "Water Resources", "Agriculture", "Minerals and Energy Resources",
                "Manufacturing Industries", "Lifelines of National Economy",
                "Power Sharing",
            ],
            ("10", "Hindi"): [
                "पद", "राम-लक्ष्मण-परशुराम संवाद", "सवैय्या और कवित्त", "आत्मकथ्य",
                "उत्साह", "यह दंतुरित मुस्कान", "फसल", "छाया मत छूना",
                "कन्यादान", "संगतकार",
            ],
            ("10", "Telugu"): [
                "మాతృభావన", "అమరావతి", "జానపదుని జాబు", "ధన్యజీవి",
                "సాహిత్యం", "విజ్ఞానం", "సంస్కృతి", "దేశప్రేమ",
                "కళాత్మకత", "జీవిత సత్యాలు",
            ],
        }

        # Subject metadata (visuals)
        SUBJECT_METADATA = {
            "Mathematics": ("ic_calculator", "#2196F3", "#E3F2FD"),
            "Science": ("ic_flask", "#4CAF50", "#E8F5E9"),
            "English": ("ic_book_icon", "#9C27B0", "#F3E5F5"),
            "Social Studies": ("ic_globe", "#FF9800", "#FFF3E0"),
            "Hindi": ("ic_language", "#F44336", "#FFEBEE"),
            "Telugu": ("ic_language", "#00BCD4", "#E0F7FA"),
        }

        print("--- Seeding Subjects (Aligning Subtitles) ---")
        for (grade, title), chapters in CHAPTER_LISTS.items():
            meta = SUBJECT_METADATA.get(title, ("ic_book_icon", "#555555", "#EEEEEE"))
            subtitle = f"{len(chapters)} Chapters"
            
            cur.execute("""
                INSERT INTO subjects (grade, title, subtitle, icon_res, tint_color, bg_color)
                VALUES (%s, %s, %s, %s, %s, %s)
                ON DUPLICATE KEY UPDATE subtitle=VALUES(subtitle)
            """, (grade, title, subtitle, meta[0], meta[1], meta[2]))
        db.commit()

        # Fetch subject IDs
        cur.execute("SELECT id, grade, title FROM subjects")
        subject_map = {(row[1], row[2]): row[0] for row in cur.fetchall()}

        print("--- Seeding ALL Chapters & PDF Links ---")
        for (grade, sub_title), titles in CHAPTER_LISTS.items():
            parent_id = subject_map.get((grade, sub_title))
            if not parent_id: continue
            
            for i, ch_title in enumerate(titles, 1):
                # Use descriptive chapter title for PDF filename (matches migrate_all_pdfs.py convention)
                import re
                san_sub = sub_title.lower().replace(' ', '_')
                san_ch = ch_title.lower().replace(' ', '_').replace('-', '_')
                san_ch = re.sub(r'[^a-z0-9_]', '', san_ch)
                pdf_file = f"{san_sub}_{grade}_{san_ch}.pdf"
                pdf_url = f"/api/pdfs/{pdf_file}"
                
                # Using INSERT ... ON DUPLICATE KEY UPDATE (if we have a unique constraint on subject_id, title)
                # But typically we search by title first
                cur.execute("SELECT id FROM chapters WHERE subject_id = %s AND title = %s", (parent_id, ch_title))
                row = cur.fetchone()
                if row:
                    cur.execute("UPDATE chapters SET chapter_number = %s, pdf_url = %s WHERE id = %s", (i, pdf_url, row[0]))
                else:
                    cur.execute("""
                        INSERT INTO chapters (subject_id, chapter_number, title, lessons_count, is_offline, pdf_url)
                        VALUES (%s, %s, %s, %s, %s, %s)
                    """, (parent_id, i, ch_title, 5, (i <= 5), pdf_url))
        db.commit()

        # Questions (Sampling first chapter of each)
        QUESTIONS = {
            "Rational Numbers": [
                ("What is the additive inverse of 2/8?", ["-2/8", "8/2", "0", "1"], 0, "The additive inverse of a/b is -a/b."),
                ("What is the multiplicative inverse of -13?", ["13", "1/-13", "-1", "0"], 1, "The multiplicative inverse of x is 1/x."),
                ("Which of the following is a rational number?", ["0", "√2", "π", "None"], 0, "0 is a rational number (0/1)."),
            ],
            "ध्वनि": [
                ("कवि का नाम क्या है?", ["सूर्यकांत त्रिपाठी 'निराला'", "सुमित्रानंदन पंत", "महादेवी वर्मा", "जयशंकर प्रसाद"], 0, "ध्वनि कविता के कवि सूर्यकांत त्रिपाठी 'निराला' हैं।"),
                ("अभी न होगा मेरा अंत - इस पंक्ति का क्या आशय है?", ["निराशा", "आत्मविश्वास", "क्रोध", "आलस्य"], 1, "यह कवि के आत्मविश्वास को दर्शाता है।"),
            ],
            "మాతృభూమి": [
                ("మాతృభూమి పాఠ్యభాగ రచయిత ఎవరు?", ["ముద్దురామకృష్ణయ్య", "సి.నారాయణరెడ్డి", "శ్రీశ్రీ", "గురజాడ"], 0, "మాతృభూమి పాఠ్యభాగ రచయిత ముద్దురామకృష్ణయ్య."),
                ("జన్మభూమి స్వర్గం కంటే మిన్న అని ఎవరు చెప్పారు?", ["శ్రీరాముడు", "శ్రీకృష్ణుడు", "అర్జునుడు", "భరతుడు"], 0, "జననీ జన్మభూమిశ్చ స్వర్గాదపి గరీయసి అని శ్రీరాముడు చెప్పారు."),
            ],
            "Number Systems": [
                ("Smallest natural number is?", ["0", "1", "-1", "None"], 1, "1 starts the natural numbers."),
                ("Which of these is irrational?", ["3", "1.5", "√2", "4/5"], 2, "√2 cannot be written as p/q."),
            ],
            "Real Numbers": [
                ("HCF of 6 and 20 is?", ["2", "4", "6", "10"], 0, "6=2x3, 20=2x2x5. HCF is 2."),
                ("LCM of 6 and 20 is?", ["20", "40", "60", "120"], 2, "LCM is 60."),
            ]
        }

        print("--- Seeding Sample Questions ---")
        cur.execute("SELECT id, title FROM chapters")
        id_map = {row[1].strip().lower(): row[0] for row in cur.fetchall()}

        for title, qs in QUESTIONS.items():
            ch_id = id_map.get(title.strip().lower())
            if ch_id:
                cur.execute("DELETE FROM questions WHERE chapter_id = %s", (ch_id,))
                for q_text, opts, corr, rev in qs:
                    cur.execute("INSERT INTO questions (chapter_id, question_text, options, correct_option_index, review_text) VALUES (%s, %s, %s, %s, %s)",
                              (ch_id, q_text, json.dumps(opts), corr, rev))
        
        db.commit()
        print("Done Seeding! ALL Subjects and Chapters aligned with PDFs.")
        cur.close()
        db.close()
    except Exception as e:
        print(f"Error seeding data: {e}")

if __name__ == "__main__":
    seed_data()
