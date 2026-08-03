from app.database.session import SessionLocal
from app.models.skill import Skill

db = SessionLocal()

skills = [
    {"name": "Python", "category": "technical"},
    {"name": "Java", "category": "technical"},
    {"name": "JavaScript", "category": "technical"},
    {"name": "React", "category": "technical"},
    {"name": "SQL", "category": "technical"},
    {"name": "Machine Learning", "category": "technical"},
    {"name": "Data Analysis", "category": "technical"},
    
    {"name": "Communication", "category": "soft"},
    {"name": "Teamwork", "category": "soft"},
    {"name": "Problem Solving", "category": "soft"},
    {"name": "Time Management", "category": "soft"},
    {"name": "Adaptability", "category": "soft"},
    
    {"name": "Microsoft Office", "category": "digital_literacy"},
    {"name": "Google Workspace", "category": "digital_literacy"},
    {"name": "Cloud Computing Basics", "category": "digital_literacy"},
    {"name": "Cybersecurity Basics", "category": "digital_literacy"},
    
    {"name": "Project Management", "category": "industry_readiness"},
    {"name": "Agile Methodologies", "category": "industry_readiness"},
    {"name": "Business Etiquette", "category": "industry_readiness"},
    {"name": "Resume Writing", "category": "industry_readiness"},
    {"name": "Interview Preparation", "category": "industry_readiness"},
]

for s in skills:
    # check if exists
    if not db.query(Skill).filter(Skill.name == s["name"]).first():
        db.add(Skill(name=s["name"], category=s["category"]))

db.commit()
print("Skills seeded successfully!")
