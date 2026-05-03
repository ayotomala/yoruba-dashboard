"""
Expanded Sample Data Generator for Yoruba Diaspora Learning Platform
Generates ~3500+ records across 9 tables spanning 2023-2026
100 users across 10 UK cities
"""
import sqlite3
import random
from datetime import datetime, timedelta

# Connect to existing database
conn = sqlite3.connect('yoruba_platform.db')
cursor = conn.cursor()

# Clear existing data (keep schema)
tables = ['cultural_content', 'community_posts', 'feedback', 'quiz_results', 'user_progress', 'lesson_content', 'lessons', 'categories', 'users']
for t in tables:
    cursor.execute(f"DELETE FROM {t}")
conn.commit()

# Reset autoincrement
cursor.execute("DELETE FROM sqlite_sequence")
conn.commit()

# ========== CONFIG ==========
LOCATIONS = ['London', 'Birmingham', 'Manchester', 'Leeds', 'Bristol', 'Nottingham', 'Sheffield', 'Liverpool', 'Coventry', 'Reading']
YORUBA_FIRST_NAMES = ['Ade', 'Bisi', 'Chidi', 'Damilola', 'Emeka', 'Funke', 'Grace', 'Hassan', 'Ifeoma', 'James', 'Kemi', 'Lola', 'Michael', 'Ngozi', 'Oluwaseun', 'Claire', 'Sarah', 'Yinka', 'Zainab', 'Tunde', 'Abiodun', 'Bolaji', 'Chidinma', 'Dayo', 'Ebun', 'Fola', 'Gbenga', 'Halima', 'Ife', 'Jide', 'Kehinde', 'Laide', 'Muyiwa', 'Nneka', 'Oladele', 'Peju', 'Rotimi', 'Sade', 'Taiwo', 'Uche', 'Victor', 'Wale', 'Yemi', 'Zara', 'Adaeze', 'Bunmi', 'Chiamaka', 'Dele', 'Eniola', 'Folasade', 'Gbemi', 'Habiba', 'Ifeanyi', 'Jumoke', 'Kunle', 'Lanre', 'Mosun', 'Nkem', 'Olu', 'Priye', 'Rebecca', 'Segun', 'Titi', 'Uzoma', 'Victoria', 'Wumi', 'Yetunde', 'Bukola', 'Ayomide', 'Temitope']
LAST_NAMES = ['Ogundimu', 'Afolabi', 'Okafor', 'Bakare', 'Nwosu', 'Adeyemi', 'Ojo', 'Ibrahim', 'Eze', 'Adebayo', 'Sowande', 'Fasanya', 'Obi', 'Amadi', 'Taiwo', 'Thompson', 'Johnson', 'Balogun', 'Mustapha', 'Akinola', 'Ogunleye', 'Ajayi', 'Oladipo', 'Alabi', 'Fashola', 'Ogunyemi', 'Adeniyi', 'Babajide', 'Coker', 'Davies', 'Ekwueme', 'Fatoyinbo', 'Garba', 'Hughes', 'Idowu', 'Jones', 'Kalu', 'Lawal', 'Mohammed', 'Nwachukwu', 'Olumide', 'Peters', 'Quadri', 'Rufai', 'Smith', 'Tayo', 'Usman', 'Williams', 'Yakubu', 'Zakariya']

# ========== USERS (100) ==========
print("Generating users...")
users_data = []

# 70 learners
for i in range(70):
    fn = random.choice(YORUBA_FIRST_NAMES)
    ln = random.choice(LAST_NAMES)
    loc = random.choices(LOCATIONS, weights=[25, 15, 12, 8, 8, 7, 7, 7, 6, 5])[0]  # London weighted higher
    dob_year = random.randint(1970, 2005)
    dob = f"{dob_year}-{random.randint(1,12):02d}-{random.randint(1,28):02d}"
    prof = random.choices(['beginner', 'intermediate', 'advanced'], weights=[50, 35, 15])[0]
    display = f"{fn}{ln[0]}{random.randint(1,99)}"
    email = f"{fn.lower()}.{ln.lower()}{i}@email.com"
    created = f"2023-{random.randint(1,12):02d}-{random.randint(1,28):02d}"
    users_data.append((fn, ln, email, f'hashed_pw{i+1}', 'learner', display, dob, loc, prof, created, None))

# 15 tutors
for i in range(15):
    fn = random.choice(YORUBA_FIRST_NAMES)
    ln = random.choice(LAST_NAMES)
    loc = random.choice(LOCATIONS[:5])
    dob_year = random.randint(1965, 1990)
    dob = f"{dob_year}-{random.randint(1,12):02d}-{random.randint(1,28):02d}"
    display = f"Tutor{fn}{i}"
    email = f"tutor.{fn.lower()}{i}@email.com"
    created = f"2023-{random.randint(1,6):02d}-{random.randint(1,28):02d}"
    users_data.append((fn, ln, email, f'hashed_pw_t{i+1}', 'tutor', display, dob, loc, 'advanced', created, None))

# 5 admins
for i in range(5):
    fn = random.choice(YORUBA_FIRST_NAMES)
    ln = random.choice(LAST_NAMES)
    display = f"Admin{fn}{i}"
    email = f"admin.{fn.lower()}{i}@yorubalearn.com"
    created = f"2023-01-{random.randint(1,28):02d}"
    users_data.append((fn, ln, email, f'hashed_pw_a{i+1}', 'admin', display, f"199{i}-05-15", 'London', None, created, None))

# 5 elders
for i in range(5):
    fn = random.choice(['Chief', 'Pa', 'Mama', 'Baba', 'Iya'])
    ln = random.choice(LAST_NAMES)
    loc = random.choice(LOCATIONS[:4])
    display = f"Elder{ln}{i}"
    email = f"elder.{ln.lower()}{i}@email.com"
    created = f"2023-{random.randint(1,6):02d}-{random.randint(1,28):02d}"
    users_data.append((fn, ln, email, f'hashed_pw_e{i+1}', 'elder', display, f"195{random.randint(0,9)}-{random.randint(1,12):02d}-15", loc, 'advanced', created, None))

# 5 institutions
institutions = [('Imole', 'Saturday School', 'London'), ('Heritage', 'Language Centre', 'Birmingham'), ('Eko', 'Academy', 'Manchester'), ('Adura', 'Learning Hub', 'Leeds'), ('Iwe', 'Community School', 'Bristol')]
for i, (fn, ln, loc) in enumerate(institutions):
    display = f"{fn}{ln.replace(' ','')}"
    email = f"info@{fn.lower()}{i}.org"
    created = f"2023-0{random.randint(1,6)}-{random.randint(1,28):02d}"
    users_data.append((fn, ln, email, f'hashed_pw_i{i+1}', 'institution', display, None, loc, None, created, None))

for u in users_data:
    cursor.execute("INSERT INTO users (first_name, last_name, email, password_hash, role, display_name, date_of_birth, location, proficiency_level, created_at, updated_at) VALUES (?,?,?,?,?,?,?,?,?,?,?)", u)
conn.commit()
print(f"  Users: {len(users_data)}")

# ========== CATEGORIES (6) ==========
print("Generating categories...")
categories = [
    ('Greetings', 'Basic and advanced Yoruba greetings for different times and occasions'),
    ('Grammar', 'Yoruba sentence structure, tenses, and grammatical rules'),
    ('Proverbs', 'Traditional Yoruba proverbs (owe) and their meanings'),
    ('Cultural Customs', 'Yoruba traditions, ceremonies, and cultural practices'),
    ('Vocabulary', 'Core Yoruba vocabulary organised by theme'),
    ('Conversations', 'Practical conversational Yoruba for everyday situations')
]
for c in categories:
    cursor.execute("INSERT INTO categories (category_name, description) VALUES (?,?)", c)
conn.commit()
print(f"  Categories: {len(categories)}")

# ========== LESSONS (30) ==========
print("Generating lessons...")
lessons = [
    ('Morning Greetings', 'Learn essential morning greetings', 'beginner', 1, 15),
    ('Respectful Greetings for Elders', 'Greet elders properly', 'beginner', 1, 20),
    ('Evening and Night Greetings', 'Evening greeting customs', 'beginner', 1, 15),
    ('Basic Sentence Structure', 'SVO patterns in Yoruba', 'beginner', 2, 30),
    ('Yoruba Tenses', 'Past, present and future tense', 'intermediate', 2, 35),
    ('Complex Sentences', 'Combining clauses', 'advanced', 2, 40),
    ('Common Proverbs Part 1', 'Essential proverbs', 'intermediate', 3, 25),
    ('Common Proverbs Part 2', 'More essential proverbs', 'intermediate', 3, 25),
    ('Proverbs in Daily Life', 'Using proverbs naturally', 'advanced', 3, 30),
    ('Naming Ceremonies', 'Naming traditions', 'beginner', 4, 20),
    ('Wedding Traditions', 'Wedding customs', 'intermediate', 4, 25),
    ('Funeral Rites', 'Burial customs and respect', 'advanced', 4, 30),
    ('Family Members', 'Family vocabulary', 'beginner', 5, 15),
    ('Food and Cooking', 'Food terms', 'beginner', 5, 20),
    ('Numbers and Counting', 'Counting 1-100', 'beginner', 5, 15),
    ('Body Parts', 'Body vocabulary', 'beginner', 5, 15),
    ('Colours and Descriptions', 'Descriptive words', 'beginner', 5, 15),
    ('Days and Months', 'Time vocabulary', 'beginner', 5, 20),
    ('At the Market', 'Market conversations', 'intermediate', 6, 25),
    ('Meeting New People', 'Introductions', 'beginner', 6, 20),
    ('Telephone Conversations', 'Phone Yoruba', 'intermediate', 6, 25),
    ('Storytelling Basics', 'Traditional story structures', 'advanced', 6, 35),
    ('Expressing Emotions', 'Emotional vocabulary', 'intermediate', 6, 20),
    ('Asking Directions', 'Navigation language', 'intermediate', 6, 20),
    ('At the Hospital', 'Medical vocabulary', 'intermediate', 5, 25),
    ('Religious Expressions', 'Spiritual language', 'intermediate', 4, 20),
    ('Music and Dance', 'Arts vocabulary', 'beginner', 4, 20),
    ('Animals and Nature', 'Nature vocabulary', 'beginner', 5, 15),
    ('Yoruba Tongue Twisters', 'Pronunciation practice', 'advanced', 2, 30),
    ('Business Yoruba', 'Professional language', 'advanced', 6, 35),
]

tutor_ids = list(range(71, 86))  # tutor user_ids
for title, desc, diff, cat_id, duration in lessons:
    tutor = random.choice(tutor_ids)
    created = f"2023-{random.randint(1,12):02d}-{random.randint(1,28):02d}"
    cursor.execute("INSERT INTO lessons (title, description, difficulty_level, category_id, created_by, estimated_duration_mins, created_at) VALUES (?,?,?,?,?,?,?)",
                   (title, desc, diff, cat_id, tutor, duration, created))
conn.commit()
print(f"  Lessons: {len(lessons)}")

# ========== LESSON CONTENT (90) ==========
print("Generating lesson content...")
content_count = 0
for lesson_id in range(1, 31):
    num_items = random.randint(2, 5)
    for order in range(1, num_items + 1):
        ctype = random.choices(['text', 'audio', 'image'], weights=[70, 20, 10])[0]
        yoruba = f"Yoruba text for lesson {lesson_id}, item {order}" if ctype == 'text' else None
        english = f"English translation for lesson {lesson_id}, item {order}" if ctype == 'text' else f"Visual/audio aid for lesson {lesson_id}"
        pron = f"Pronunciation guide {lesson_id}-{order}" if ctype == 'text' else None
        context = f"Cultural context note for this content piece" if random.random() > 0.3 else None
        cursor.execute("INSERT INTO lesson_content (lesson_id, content_type, yoruba_text, english_translation, pronunciation_guide, cultural_context, display_order) VALUES (?,?,?,?,?,?,?)",
                       (lesson_id, ctype, yoruba, english, pron, context, order))
        content_count += 1
conn.commit()
print(f"  Lesson content: {content_count}")

# ========== USER PROGRESS (2000+) ==========
print("Generating user progress...")
progress_count = 0
learner_ids = list(range(1, 71))
lesson_ids = list(range(1, 31))

# Generate progress over 2023-2026
start_date = datetime(2023, 3, 1)
end_date = datetime(2026, 4, 30)

for user_id in learner_ids:
    # Each learner attempts 5-20 lessons
    num_lessons = random.randint(5, 20)
    attempted_lessons = random.sample(lesson_ids, min(num_lessons, len(lesson_ids)))
    
    for lesson_id in attempted_lessons:
        # Random date within range
        days_offset = random.randint(0, (end_date - start_date).days)
        started = start_date + timedelta(days=days_offset)
        
        status = random.choices(['completed', 'in_progress', 'not_started'], weights=[65, 25, 10])[0]
        score = round(random.uniform(45, 100), 2) if status == 'completed' else None
        time_spent = random.randint(5, 45) if status != 'not_started' else 0
        completed_at = (started + timedelta(days=random.randint(0, 3))).strftime('%Y-%m-%d') if status == 'completed' else None
        
        cursor.execute("INSERT INTO user_progress (user_id, lesson_id, status, score_percentage, time_spent_mins, started_at, completed_at) VALUES (?,?,?,?,?,?,?)",
                       (user_id, lesson_id, status, score, time_spent, started.strftime('%Y-%m-%d'), completed_at))
        progress_count += 1

conn.commit()
print(f"  User progress: {progress_count}")

# ========== QUIZ RESULTS (800+) ==========
print("Generating quiz results...")
quiz_count = 0
# Only for completed lessons
cursor.execute("SELECT user_id, lesson_id FROM user_progress WHERE status = 'completed'")
completed = cursor.fetchall()

for user_id, lesson_id in random.sample(completed, min(800, len(completed))):
    total_q = 10
    correct = random.randint(3, 10)
    score = round((correct / total_q) * 100, 2)
    days_offset = random.randint(0, (end_date - start_date).days)
    attempted = (start_date + timedelta(days=days_offset)).strftime('%Y-%m-%d')
    
    cursor.execute("INSERT INTO quiz_results (user_id, lesson_id, total_questions, correct_answers, score_percentage, attempted_at) VALUES (?,?,?,?,?,?)",
                   (user_id, lesson_id, total_q, correct, score, attempted))
    quiz_count += 1

conn.commit()
print(f"  Quiz results: {quiz_count}")

# ========== FEEDBACK (200) ==========
print("Generating feedback...")
feedback_count = 0
comments = [
    'Excellent lesson, very clear!', 'Good content but needs more audio.',
    'Struggled with tonal marks.', 'This connected me to my heritage.',
    'Perfect for beginners!', 'Would love more examples.',
    'The cultural context notes are brilliant.', 'Could be more challenging.',
    'Best Yoruba resource online.', 'My children enjoyed this too.',
    'Very practical vocabulary.', 'Helped me talk to my grandmother!',
    'Need more pronunciation guides.', 'Well structured and clear.',
    'The proverbs are beautiful.', 'Too short, wanted more depth.',
    'Great refresher for intermediate learners.', 'Interactive elements would help.',
    'Used this at the market last week!', 'Challenging but rewarding.'
]

for _ in range(200):
    user_id = random.choice(learner_ids)
    lesson_id = random.choice(lesson_ids)
    rating = random.choices([3, 4, 5], weights=[15, 40, 45])[0]
    comment = random.choice(comments)
    days_offset = random.randint(0, (end_date - start_date).days)
    submitted = (start_date + timedelta(days=days_offset)).strftime('%Y-%m-%d')
    
    cursor.execute("INSERT INTO feedback (user_id, lesson_id, rating, comment, submitted_at) VALUES (?,?,?,?,?)",
                   (user_id, lesson_id, rating, comment, submitted))
    feedback_count += 1

conn.commit()
print(f"  Feedback: {feedback_count}")

# ========== COMMUNITY POSTS (150) ==========
print("Generating community posts...")
post_count = 0
post_titles = [
    'Struggling with tones', 'My Yoruba journey', 'Teaching my children',
    'Birmingham learners?', 'Manchester meetup', 'Proverb from my father',
    'Learning as non-Nigerian', 'Music recommendations', 'Advanced practice partner needed',
    'Best way to learn tenses?', 'Yoruba vs French difficulty', 'Leeds community',
    'Saturday school experience', 'Greetings practice', 'Cultural tips needed',
    'London study group', 'Bristol learners unite', 'Pronunciation help',
    'My motivation', 'Sheffield Yoruba speakers', 'Wedding vocabulary help',
    'Naming ceremony advice', 'Market bargaining tips', 'Storytelling tradition',
    'Cooking vocabulary', 'Family reunion prep', 'Church Yoruba expressions'
]
post_types = ['discussion', 'cultural_contribution', 'question', 'other']

all_user_ids = list(range(1, 96))  # learners + tutors + elders
for _ in range(150):
    user_id = random.choice(all_user_ids)
    lesson_id = random.choice(lesson_ids) if random.random() > 0.4 else None
    title = random.choice(post_titles)
    content = f"Post content for: {title}. This is a community discussion."
    ptype = random.choices(post_types, weights=[40, 25, 25, 10])[0]
    days_offset = random.randint(0, (end_date - start_date).days)
    created = (start_date + timedelta(days=days_offset)).strftime('%Y-%m-%d')
    
    cursor.execute("INSERT INTO community_posts (user_id, lesson_id, title, content, post_type, created_at) VALUES (?,?,?,?,?,?)",
                   (user_id, lesson_id, title, content, ptype, created))
    post_count += 1

conn.commit()
print(f"  Community posts: {post_count}")

# ========== CULTURAL CONTENT (80) ==========
print("Generating cultural content...")
cultural_count = 0
content_types = ['proverb', 'folktale', 'idiom', 'song', 'custom']
proverbs = [
    ('Owe lesin oro', 'Proverbs are the horses of speech'),
    ('Bi a ba n la aso, a kii gbe ebi re sori aga', 'When spreading cloth, we do not place its enemy on the chair'),
    ('Eni ti o ba fowo kan igi odan', 'Whoever climbs the baobab tree will see everywhere'),
    ('Ti a ba ji ko ri eni foore se', 'If you wake and find no one to be kind to, go back to sleep'),
    ('Agba ki wa loja ki ori omo titun wo', 'An elder does not stay in the market while a child goes astray'),
    ('Bi ojo ba n ro, a maa n ro sori gbogbo ile', 'When it rains, it rains on every roof'),
    ('Ohun ti a ko ba fi oju kan', 'What one has not seen, one does not follow'),
    ('Ise agbe ni ise ile wa', 'Farming is our native work'),
    ('Iwa lewa', 'Character is beauty'),
    ('Suuru ni baba iwa', 'Patience is the father of character'),
]

elder_ids = list(range(91, 96)) # user_ids 91-95 (5 elders)
admin_ids = list(range(86, 91)) # user_ids 86-90 (5 admins)

for _ in range(80):
    contributor = random.choice(elder_ids + learner_ids[:10])
    ctype = random.choices(content_types, weights=[40, 20, 20, 10, 10])[0]
    
    if ctype == 'proverb' and proverbs:
        yoruba, english = random.choice(proverbs)
    else:
        yoruba = f"Yoruba {ctype} content #{random.randint(1,100)}"
        english = f"English translation of {ctype} #{random.randint(1,100)}"
    
    significance = f"Cultural significance note for this {ctype}"
    approved = random.choices([0, 1], weights=[30, 70])[0]
    approver = random.choice(admin_ids) if approved else None
    days_offset = random.randint(0, (end_date - start_date).days)
    created = (start_date + timedelta(days=days_offset)).strftime('%Y-%m-%d')
    
    cursor.execute("INSERT INTO cultural_content (contributed_by, content_type, yoruba_text, english_translation, cultural_significance, approved, approved_by, created_at) VALUES (?,?,?,?,?,?,?,?)",
                   (contributor, ctype, yoruba, english, significance, approved, approver, created))
    cultural_count += 1

conn.commit()
print(f"  Cultural content: {cultural_count}")

# ========== FINAL COUNT ==========
print("\n========== FINAL RECORD COUNTS ==========")
for table in ['users', 'categories', 'lessons', 'lesson_content', 'user_progress', 'quiz_results', 'feedback', 'community_posts', 'cultural_content']:
    cursor.execute(f"SELECT COUNT(*) FROM {table}")
    count = cursor.fetchone()[0]
    print(f"  {table}: {count}")

cursor.execute("SELECT (SELECT COUNT(*) FROM users) + (SELECT COUNT(*) FROM categories) + (SELECT COUNT(*) FROM lessons) + (SELECT COUNT(*) FROM lesson_content) + (SELECT COUNT(*) FROM user_progress) + (SELECT COUNT(*) FROM quiz_results) + (SELECT COUNT(*) FROM feedback) + (SELECT COUNT(*) FROM community_posts) + (SELECT COUNT(*) FROM cultural_content)")
total = cursor.fetchone()[0]
print(f"\n  TOTAL RECORDS: {total}")

conn.close()
print("\nDone! Database expanded successfully.")
