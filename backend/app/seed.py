"""Sample data, inserted on startup only when the employees table is empty."""
from datetime import date

from sqlalchemy.orm import Session

from app.models.employee import Employee

SAMPLE_EMPLOYEES = [
    # (name, email, department, designation, date_of_joining)
    ("Rahul Sharma", "rahul.sharma@company.com", "Engineering", "Staff Software Engineer", date(2021, 3, 15)),
    ("Priya Patel", "priya.patel@company.com", "Engineering", "Frontend Lead", date(2020, 8, 1)),
    ("Rahul Verma", "rahul.verma@company.com", "Product", "Principal Product Manager", date(2022, 1, 10)),
    ("Ananya Iyer", "ananya.iyer@company.com", "Engineering", "Backend Engineer", date(2023, 6, 20)),
    ("Amitabh Sen", "amitabh.sen@company.com", "Human Resources", "HR Director", date(2019, 11, 5)),
    ("Sneha Kulkarni", "sneha.kulkarni@company.com", "Human Resources", "Talent Acquisition Specialist", date(2022, 4, 18)),
    ("Vikram Malhotra", "vikram.malhotra@company.com", "Finance", "VP of Finance", date(2018, 5, 12)),
    ("Neha Gupta", "neha.gupta@company.com", "Finance", "Senior Financial Analyst", date(2021, 9, 30)),
    ("Rohan Mehra", "rohan.mehra@company.com", "Design", "Lead Product Designer", date(2021, 2, 14)),
    ("Kavita Rao", "kavita.rao@company.com", "Design", "UI/UX Designer", date(2023, 3, 22)),
    ("Arjun Nair", "arjun.nair@company.com", "Marketing", "Head of Growth Marketing", date(2020, 10, 1)),
    ("Pooja Deshmukh", "pooja.deshmukh@company.com", "Marketing", "Content Strategist", date(2022, 7, 15)),
    ("Siddharth Joshi", "siddharth.joshi@company.com", "Sales", "Enterprise Sales Director", date(2019, 2, 1)),
    ("Deepika Reddy", "deepika.reddy@company.com", "Sales", "Account Executive", date(2023, 1, 9)),
    ("Karan Singhania", "karan.singhania@company.com", "Operations", "Operations Lead", date(2021, 12, 1)),
    ("Tanvi Bhatia", "tanvi.bhatia@company.com", "Operations", "Customer Success Manager", date(2022, 11, 14)),
    ("Manoj Kumar", "manoj.kumar@company.com", "Engineering", "DevOps / SRE Specialist", date(2020, 4, 15)),
    ("Zoya Akhtar", "zoya.akhtar@company.com", "Engineering", "QA Automation Engineer", date(2023, 5, 2)),
    ("Aditya Roy", "aditya.roy@company.com", "Product", "Associate Product Manager", date(2024, 2, 1)),
    ("Simran Kaur", "simran.kaur@company.com", "Legal", "Corporate Legal Counsel", date(2021, 6, 10)),
]


def seed_database(db: Session) -> None:
    if db.query(Employee).count() > 0:
        return
    for name, email, department, designation, joined in SAMPLE_EMPLOYEES:
        db.add(Employee(name=name, email=email, department=department, designation=designation, date_of_joining=joined))
    db.commit()
