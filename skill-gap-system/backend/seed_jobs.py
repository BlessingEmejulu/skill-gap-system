from app.database import SessionLocal
from app.models.user import User
from app.models.employer import Employer, JobPosting, JobSkill
from app.models.skill import Skill
from app.models.common import UserRole

def seed_jobs():
    db = SessionLocal()
    try:
        # Create an employer user if not exists
        employer_user = db.query(User).filter(User.email == "techcorp@example.com").first()
        if not employer_user:
            employer_user = User(
                email="techcorp@example.com",
                hashed_password="hashedpassword123",  # Mock
                role=UserRole.EMPLOYER,
                full_name="TechCorp HR",
                is_active=True
            )
            db.add(employer_user)
            db.commit()
            db.refresh(employer_user)

        # Create employer profile
        employer = db.query(Employer).filter(Employer.user_id == employer_user.id).first()
        if not employer:
            employer = Employer(
                user_id=employer_user.id,
                company_name="TechCorp Global",
                industry="Information Technology",
                company_size="1000-5000",
                description="A leading software company building AI-powered solutions."
            )
            db.add(employer)
            db.commit()
            db.refresh(employer)

        # Check existing jobs
        existing_jobs = db.query(JobPosting).filter(JobPosting.employer_id == employer.id).count()
        if existing_jobs > 0:
            print("Jobs already exist. Skipping seed.")
            return

        # Fetch some technical skills
        all_skills = db.query(Skill).all()
        skill_map = {s.name.lower(): s for s in all_skills}
        
        # We need to map some common skill names, or just use any available skills
        # Just grab random skills if specific ones aren't found
        def get_skill(name, fallback_index=0):
            if name.lower() in skill_map:
                return skill_map[name.lower()]
            elif fallback_index < len(all_skills):
                return all_skills[fallback_index]
            return None

        # Job 1: Junior Frontend Developer
        job1 = JobPosting(
            employer_id=employer.id,
            title="Junior Frontend Developer",
            industry="Software Development",
            description="Looking for an energetic junior frontend developer familiar with React and modern CSS.",
            min_experience_years=1.0,
            location="Remote",
            is_active="active"
        )
        db.add(job1)
        db.flush()
        
        # Add required skills
        s1 = get_skill("javascript", 0)
        s2 = get_skill("react", 1)
        s3 = get_skill("html/css", 2)
        
        for idx, s in enumerate([s1, s2, s3]):
            if s:
                db.add(JobSkill(job_posting_id=job1.id, skill_id=s.id, importance=5.0 - idx))

        # Job 2: Data Analyst
        job2 = JobPosting(
            employer_id=employer.id,
            title="Data Analyst",
            industry="Data Science",
            description="Analyze large datasets to extract meaningful insights.",
            min_experience_years=2.0,
            location="Lagos, Nigeria",
            is_active="active"
        )
        db.add(job2)
        db.flush()
        
        db.add(JobSkill(job_posting_id=job2.id, skill_id=get_skill("python", 3).id, importance=5.0))
        db.add(JobSkill(job_posting_id=job2.id, skill_id=get_skill("sql", 4).id, importance=4.0))
        db.add(JobSkill(job_posting_id=job2.id, skill_id=get_skill("data analysis", 5).id, importance=5.0))

        # Job 3: Product Manager
        job3 = JobPosting(
            employer_id=employer.id,
            title="Product Manager",
            industry="Product Management",
            description="Lead the product lifecycle from ideation to launch.",
            min_experience_years=3.0,
            location="Hybrid",
            is_active="active"
        )
        db.add(job3)
        db.flush()
        
        db.add(JobSkill(job_posting_id=job3.id, skill_id=get_skill("agile", 6).id, importance=5.0))
        db.add(JobSkill(job_posting_id=job3.id, skill_id=get_skill("leadership", 7).id, importance=4.0))
        db.add(JobSkill(job_posting_id=job3.id, skill_id=get_skill("communication", 8).id, importance=5.0))

        db.commit()
        print("Successfully seeded 3 jobs!")

    finally:
        db.close()

if __name__ == "__main__":
    seed_jobs()
