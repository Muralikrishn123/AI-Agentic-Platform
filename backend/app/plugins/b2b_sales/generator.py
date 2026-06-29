"""
Dynamic Mock Data Generator for B2B Sales.
Generates 100+ highly realistic companies, triggers, and decision-makers
to provide a robust dataset for the dashboard search.
"""
import random
from datetime import datetime, timedelta

COMPANY_NAMES = [
    "Apex", "Nexus", "CloudPeak", "DataStream", "Quantum", "Veritas", "Cognitive", "Meridian", "PayFlow", "LearnUp",
    "Delta", "Alpha", "Omega", "Zeta", "Sigma", "Helix", "Nova", "Vortex", "Sentry", "Aegis",
    "Vertex", "Starlight", "Core", "Vanguard", "Prism", "Beacon", "Summit", "Zenith", "Pinnacle", "Ridge",
    "Crest", "Valence", "Vector", "Matrix", "Tensor", "Catalyst", "Empower", "Elevate", "Velocity", "Aero",
    "Hydra", "Titan", "Spectra", "Lumina", "Aurora", "Solstice", "Equinox", "Synergy", "Fusion", "Orbit"
]

COMPANY_SUFFIXES = ["Technologies", "Solutions", "AI", "SaaS", "Analytics", "Labs", "Systems", "Software", "Digital", "Networks"]

SECTORS = ["SaaS", "Cloud Infrastructure", "AI/ML", "FinTech", "Analytics", "Enterprise SaaS", "HealthTech", "EdTech", "PropTech", "CleanTech"]
STAGES = ["Seed", "Series A", "Series B", "Series C", "Series D", "Public"]
TECH_STACKS = ["Python", "FastAPI", "React", "Node.js", "Go", "Java", "Spring Boot", "Kubernetes", "PostgreSQL", "MongoDB", "AWS", "GCP", "Azure"]
CITIES = ["Bangalore", "Mumbai", "Delhi", "Hyderabad", "Pune", "Chennai", "Gurgaon", "Noida"]

NAMES = [
    "Arjun", "Deepak", "Amit", "Rajiv", "Vikram", "Siddharth", "Karthik", "Rohan", "Suresh", "Vijay",
    "Priya", "Meera", "Divya", "Kavitha", "Preeti", "Nandini", "Neha", "Anjali", "Swati", "Ritu",
    "Rahul", "Sanjay", "Anil", "Sunil", "Manish", "Alok", "Harish", "Sandesh", "Gaurav", "Nitin",
    "Aisha", "Pooja", "Kiran", "Shalini", "Tanvi", "Jyoti", "Aditi", "Ridhi", "Sneha", "Kriti"
]
SURNAMES = [
    "Sharma", "Mehta", "Iyer", "Nair", "Gupta", "Sen", "Menon", "Balasubramanian", "Rathore", "Malhotra",
    "Krishnamurthy", "Shankar", "Desai", "Narayanan", "Pillai", "Rajan", "Gupta", "Sharma", "Verma", "Kapoor"
]

TRIGGER_TYPES = ["rapid_hiring", "funding_round", "leadership_change", "product_launch"]
SOURCES = ["LinkedIn Jobs", "TechCrunch", "Crunchbase", "Indeed", "Product Hunt"]


def generate_mock_companies(count: int = 100) -> list:
    companies = []
    
    # Generate unique names
    unique_names = set()
    while len(unique_names) < count:
        name = f"{random.choice(COMPANY_NAMES)} {random.choice(COMPANY_SUFFIXES)}"
        unique_names.add(name)
        
    for name in sorted(list(unique_names)):
        # Generate attributes
        sector = random.choice(SECTORS)
        stage = random.choice(STAGES)
        employee_count = random.randint(20, 4500)
        
        # Funding calculation
        funding_stages_usd = {
            "Seed": random.randint(500_000, 3_000_000),
            "Series A": random.randint(5_000_000, 12_000_000),
            "Series B": random.randint(15_000_000, 35_000_000),
            "Series C": random.randint(40_000_000, 80_000_000),
            "Series D": random.randint(90_000_000, 200_000_000),
            "Public": random.randint(250_000_000, 1_000_000_000)
        }
        total_funding = funding_stages_usd[stage]
        
        # Tech stack selection (3 to 6 random tech items)
        tech_stack = list(set(random.sample(TECH_STACKS, random.randint(3, 6))))
        
        hq = f"{random.choice(CITIES)}, India"
        website = f"https://{name.lower().replace(' ', '').replace('&', '')}.io"
        linkedin = f"https://linkedin.com/company/{name.lower().replace(' ', '-')}"
        
        # Trigger event
        trigger_type = random.choice(TRIGGER_TYPES)
        trigger_strength = random.choice(["low", "medium", "high"])
        
        trigger_templates = {
            "rapid_hiring": f"Posted {random.randint(5, 20)} engineering roles in the last 30 days",
            "funding_round": f"Raised ${total_funding//1_000_000}M {stage} funding round",
            "leadership_change": f"New CTO joined — restructuring engineering team",
            "product_launch": f"Launched new AI-powered platform version"
        }
        
        trigger = {
            "company": name,
            "signal_type": trigger_type,
            "signal": trigger_templates[trigger_type],
            "source": random.choice(SOURCES),
            "date": (datetime.utcnow() - timedelta(days=random.randint(1, 14))).isoformat(),
            "strength": trigger_strength
        }
        
        # Generate contacts (1 to 3)
        contacts = []
        titles = [
            ("Chief Technology Officer", "C-Suite", "Engineering"),
            ("VP Engineering", "VP", "Engineering"),
            ("Director of Technology", "Director", "Engineering"),
            ("Head of Talent Acquisition", "Director", "HR"),
            ("Co-Founder & CEO", "C-Suite", "Leadership"),
            ("Engineering Manager", "Manager", "Engineering")
        ]
        
        selected_titles = random.sample(titles, random.randint(1, 3))
        for priority, (title, seniority, dept) in enumerate(selected_titles):
            contact_name = f"{random.choice(NAMES)} {random.choice(SURNAMES)}"
            contacts.append({
                "name": contact_name,
                "title": title,
                "department": dept,
                "seniority": seniority,
                "linkedin_id": f"{contact_name.lower().replace(' ', '-')}-{random.randint(100, 999)}",
                "tenure_years": round(random.uniform(0.5, 6.0), 1),
                "priority": priority + 1
            })
            
        companies.append({
            "name": name,
            "sector": sector,
            "employee_count": employee_count,
            "funding_stage": stage,
            "total_funding_usd": total_funding,
            "hq": hq,
            "tech_stack": tech_stack,
            "annual_revenue_est": f"${total_funding//5_000_000}M - ${total_funding//2_000_000}M",
            "founded": random.randint(2012, 2023),
            "growth_rate": f"{random.randint(10, 150)}% YoY",
            "website": website,
            "linkedin_url": linkedin,
            "glassdoor_rating": round(random.uniform(3.2, 4.8), 1),
            "recent_news": [
                f"{name} announces integration with key cloud partners",
                f"{name} highlighted in TechCircle's list of emerging startups"
            ],
            "open_roles_count": random.randint(1, 15),
            "verified_tech_stack": tech_stack,
            "hiring_velocity": random.choice(["Low", "Medium", "High"]),
            "company_type": "Private" if stage != "Public" else "Public",
            "trigger": trigger,
            "contacts": contacts
        })
        
    return companies
