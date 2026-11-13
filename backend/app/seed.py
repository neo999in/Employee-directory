from datetime import date
import logging
from sqlalchemy.orm import Session
from app.models.employee import Employee
from app.core.database import SessionLocal, Base, engine

logger = logging.getLogger(__name__)

INITIAL_EMPLOYEES = [
    {
        "name": "Rahul Sharma",
        "email": "rahul.sharma@company.com",
        "department": "Engineering",
        "designation": "Staff Software Engineer",
        "date_of_joining": date(2021, 3, 15)
    },
    {
        "name": "Priya Patel",
        "email": "priya.patel@company.com",
        "department": "Engineering",
        "designation": "Frontend Lead",
        "date_of_joining": date(2020, 8, 1)
    },
    {
        "name": "Rahul Verma",
        "email": "rahul.verma@company.com",
        "department": "Product",
        "designation": "Principal Product Manager",
        "date_of_joining": date(2022, 1, 10)
    },
    {
        "name": "Ananya Iyer",
        "email": "ananya.iyer@company.com",
        "department": "Engineering",
        "designation": "Backend Engineer",
        "date_of_joining": date(2023, 6, 20)
    },
    {
        "name": "Amitabh Sen",
        "email": "amitabh.sen@company.com",
        "department": "Human Resources",
        "designation": "HR Director",
        "date_of_joining": date(2019, 11, 5)
    },
    {
        "name": "Sneha Kulkarni",
        "email": "sneha.kulkarni@company.com",
        "department": "Human Resources",
        "designation": "Talent Acquisition Specialist",
        "date_of_joining": date(2022, 4, 18)
    },
    {
        "name": "Vikram Malhotra",
        "email": "vikram.malhotra@company.com",
        "department": "Finance",
        "designation": "VP of Finance",
        "date_of_joining": date(2018, 5, 12)
    },
    {
        "name": "Neha Gupta",
        "email": "neha.gupta@company.com",
        "department": "Finance",
        "designation": "Senior Financial Analyst",
        "date_of_joining": date(2021, 9, 30)
    },
    {
        "name": "Rohan Mehra",
        "email": "rohan.mehra@company.com",
        "department": "Design",
        "designation": "Lead Product Designer",
        "date_of_joining": date(2021, 2, 14)
    },
    {
        "name": "Kavita Rao",
        "email": "kavita.rao@company.com",
        "department": "Design",
        "designation": "UI/UX Designer",
        "date_of_joining": date(2023, 3, 22)
    },
    {
        "name": "Arjun Nair",
        "email": "arjun.nair@company.com",
        "department": "Marketing",
        "designation": "Head of Growth Marketing",
        "date_of_joining": date(2020, 10, 1)
    },
    {
        "name": "Pooja Deshmukh",
        "email": "pooja.deshmukh@company.com",
        "department": "Marketing",
        "designation": "Content Strategist",
        "date_of_joining": date(2022, 7, 15)
    },
    {
        "name": "Siddharth Joshi",
        "email": "siddharth.joshi@company.com",
        "department": "Sales",
        "designation": "Enterprise Sales Director",
        "date_of_joining": date(2019, 2, 1)
    },
    {
        "name": "Deepika Reddy",
        "email": "deepika.reddy@company.com",
        "department": "Sales",
        "designation": "Account Executive",
        "date_of_joining": date(2023, 1, 9)
    },
    {
        "name": "Karan Singhania",
        "email": "karan.singhania@company.com",
        "department": "Operations",
        "designation": "Operations Lead",
        "date_of_joining": date(2021, 12, 1)
    },
    {
        "name": "Tanvi Bhatia",
        "email": "tanvi.bhatia@company.com",
        "department": "Operations",
        "designation": "Customer Success Manager",
        "date_of_joining": date(2022, 11, 14)
    },
    {
        "name": "Manoj Kumar",
        "email": "manoj.kumar@company.com",
        "department": "Engineering",
        "designation": "DevOps / SRE Specialist",
        "date_of_joining": date(2020, 4, 15)
    },
    {
        "name": "Zoya Akhtar",
        "email": "zoya.akhtar@company.com",
        "department": "Engineering",
        "designation": "QA Automation Engineer",
        "date_of_joining": date(2023, 5, 2)
    },
    {
        "name": "Aditya Roy",
        "email": "aditya.roy@company.com",
        "department": "Product",
        "designation": "Associate Product Manager",
        "date_of_joining": date(2024, 2, 1)
    },
    {
        "name": "Simran Kaur",
        "email": "simran.kaur@company.com",
        "department": "Legal",
        "designation": "Corporate Legal Counsel",
        "date_of_joining": date(2021, 6, 10)
    }
]

def seed_database(db: Session):
    existing_count = db.query(Employee).count()
    if existing_count == 0:
        logger.info("Database is empty. Seeding initial employee records...")
        for data in INITIAL_EMPLOYEES:
            emp = Employee(**data)
            db.add(emp)
        db.commit()
        logger.info(f"Successfully seeded {len(INITIAL_EMPLOYEES)} employee records.")
    else:
        logger.info(f"Database already contains {existing_count} records. Skipping seed.")

if __name__ == "__main__":
    Base.metadata.create_all(bind=engine)
    session = SessionLocal()
    try:
        seed_database(session)
    finally:
        session.close()
