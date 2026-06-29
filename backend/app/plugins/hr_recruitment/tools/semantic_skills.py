"""
Semantic Skills Mapping - Iteration 2

This module provides semantic understanding of skill relationships.
Helps the algorithm recognize related skills for partial credit scoring.
"""

from typing import List, Dict, Set, Optional


# Semantic skills mapping - skills that are related/similar
SEMANTIC_SKILLS = {
    # Backend frameworks
    "FastAPI": ["Flask", "Django", "Starlette", "Bottle"],
    "Flask": ["FastAPI", "Django", "Bottle", "Pyramid"],
    "Django": ["FastAPI", "Flask", "Rails", "Spring"],
    "Express": ["Fastify", "Koa", "Hapi"],
    
    # Frontend frameworks
    "React": ["Vue.js", "Angular", "Svelte", "Preact"],
    "Vue.js": ["React", "Angular", "Svelte"],
    "Angular": ["React", "Vue.js", "Ember"],
    "Svelte": ["React", "Vue.js"],
    
    # Databases - NoSQL
    "MongoDB": ["PostgreSQL", "MySQL", "DynamoDB", "CouchDB"],
    "DynamoDB": ["MongoDB", "CouchDB", "Cassandra"],
    "Redis": ["Memcached", "Elasticsearch"],
    
    # Databases - SQL
    "PostgreSQL": ["MySQL", "MongoDB", "Oracle", "SQL Server"],
    "MySQL": ["PostgreSQL", "MongoDB", "MariaDB", "SQL Server"],
    "SQL Server": ["PostgreSQL", "MySQL", "Oracle"],
    "Oracle": ["PostgreSQL", "MySQL", "SQL Server"],
    
    # Cloud platforms
    "AWS": ["Azure", "Google Cloud", "DigitalOcean"],
    "Azure": ["AWS", "Google Cloud"],
    "Google Cloud": ["AWS", "Azure"],
    "GCP": ["AWS", "Azure"],  # Alias
    
    # Programming languages
    "Python": ["Django", "Flask", "FastAPI"],
    "JavaScript": ["TypeScript", "Node.js"],
    "TypeScript": ["JavaScript"],
    "Java": ["Kotlin", "Scala"],
    "C#": [".NET", "ASP.NET"],
    
    # DevOps & Containers
    "Docker": ["Kubernetes", "Podman", "containerd"],
    "Kubernetes": ["Docker", "OpenShift", "Nomad"],
    "Jenkins": ["GitLab CI", "GitHub Actions", "CircleCI"],
    "GitLab CI": ["Jenkins", "GitHub Actions", "CircleCI"],
    "GitHub Actions": ["Jenkins", "GitLab CI", "CircleCI"],
    
    # Testing
    "Jest": ["Mocha", "Jasmine", "Vitest"],
    "Pytest": ["unittest", "nose"],
    "JUnit": ["TestNG", "Spock"],
    
    # Web servers
    "Nginx": ["Apache", "Caddy"],
    "Apache": ["Nginx", "Caddy"],
    
    # Message queues
    "RabbitMQ": ["Kafka", "Redis", "AWS SQS"],
    "Kafka": ["RabbitMQ", "Pulsar", "AWS Kinesis"],
    
    # Monitoring
    "Prometheus": ["Grafana", "Datadog", "New Relic"],
    "Grafana": ["Prometheus", "Kibana", "Datadog"],
}


def get_related_skills(skill: str) -> List[str]:
    """
    Get semantically related skills.
    
    Args:
        skill: The skill to find relationships for
    
    Returns:
        List of related skills
    
    Example:
        >>> get_related_skills("FastAPI")
        ["Flask", "Django", "Starlette", "Bottle"]
    """
    # Case-insensitive lookup
    for key, values in SEMANTIC_SKILLS.items():
        if key.lower() == skill.lower():
            return values
    
    return []


def find_skill_relationships(
    required_skills: List[str],
    candidate_skills: List[str]
) -> Dict[str, Dict[str, str]]:
    """
    Find relationships between required and candidate skills.
    
    This helps identify when a candidate has related experience
    even if they don't have the exact skill match.
    
    Args:
        required_skills: Skills required by the job
        candidate_skills: Skills the candidate has
    
    Returns:
        Dictionary mapping required skills to related candidate skills
    
    Example:
        >>> find_skill_relationships(
        ...     ["FastAPI", "MongoDB"],
        ...     ["Flask", "PostgreSQL"]
        ... )
        {
            "FastAPI": {
                "candidate_has": "Flask",
                "relationship": "related_backend_framework"
            },
            "MongoDB": {
                "candidate_has": "PostgreSQL",
                "relationship": "related_database"
            }
        }
    """
    relationships = {}
    
    # Normalize for comparison
    required_lower = [s.lower() for s in required_skills]
    candidate_lower = [s.lower() for s in candidate_skills]
    
    for req_skill in required_skills:
        related = get_related_skills(req_skill)
        related_lower = [s.lower() for s in related]
        
        # Check if candidate has any related skill
        for i, cand_skill_lower in enumerate(candidate_lower):
            if cand_skill_lower in related_lower:
                # Determine relationship type
                relationship_type = _infer_relationship_type(req_skill, candidate_skills[i])
                
                relationships[req_skill] = {
                    "candidate_has": candidate_skills[i],
                    "relationship": relationship_type
                }
                break  # Only map first related skill found
    
    return relationships


def _infer_relationship_type(required_skill: str, candidate_skill: str) -> str:
    """
    Infer the type of relationship between two skills.
    
    Args:
        required_skill: Required skill
        candidate_skill: Candidate's skill
    
    Returns:
        Relationship type description
    """
    required_lower = required_skill.lower()
    candidate_lower = candidate_skill.lower()
    
    # Framework relationships
    frameworks = ["fastapi", "flask", "django", "react", "vue", "angular", "express"]
    if any(fw in required_lower for fw in frameworks) and any(fw in candidate_lower for fw in frameworks):
        return "related_framework"
    
    # Database relationships
    databases = ["mongodb", "postgresql", "mysql", "redis", "dynamodb"]
    if any(db in required_lower for db in databases) and any(db in candidate_lower for db in databases):
        return "related_database"
    
    # Cloud relationships
    cloud = ["aws", "azure", "gcp", "google cloud"]
    if any(c in required_lower for c in cloud) and any(c in candidate_lower for c in cloud):
        return "related_cloud_platform"
    
    # DevOps relationships
    devops = ["docker", "kubernetes", "jenkins", "gitlab"]
    if any(d in required_lower for d in devops) and any(d in candidate_lower for d in devops):
        return "related_devops_tool"
    
    # Language relationships
    languages = ["python", "javascript", "typescript", "java", "c#"]
    if any(lang in required_lower for lang in languages) and any(lang in candidate_lower for lang in languages):
        return "related_language"
    
    # Default
    return "related_technology"


def calculate_skill_similarity(skill1: str, skill2: str) -> float:
    """
    Calculate similarity score between two skills (0.0 to 1.0).
    
    Args:
        skill1: First skill
        skill2: Second skill
    
    Returns:
        Similarity score (1.0 = exact match, 0.5-0.8 = related, 0.0 = unrelated)
    
    Example:
        >>> calculate_skill_similarity("FastAPI", "Flask")
        0.75  # Related backend frameworks
        >>> calculate_skill_similarity("Python", "Python")
        1.0  # Exact match
    """
    skill1_lower = skill1.lower()
    skill2_lower = skill2.lower()
    
    # Exact match
    if skill1_lower == skill2_lower:
        return 1.0
    
    # Check if they're related
    related1 = [s.lower() for s in get_related_skills(skill1)]
    related2 = [s.lower() for s in get_related_skills(skill2)]
    
    # Bidirectional check
    if skill2_lower in related1 or skill1_lower in related2:
        # Determine similarity based on relationship type
        rel_type = _infer_relationship_type(skill1, skill2)
        
        if rel_type == "related_framework":
            return 0.75  # High similarity for frameworks
        elif rel_type == "related_database":
            return 0.70  # Good similarity for databases
        elif rel_type == "related_cloud_platform":
            return 0.70  # Good similarity for cloud
        elif rel_type == "related_language":
            return 0.60  # Medium similarity for languages
        else:
            return 0.65  # Default related similarity
    
    # No relationship found
    return 0.0


def get_skill_category(skill: str) -> str:
    """
    Get the category of a skill.
    
    Args:
        skill: The skill to categorize
    
    Returns:
        Category name
    """
    skill_lower = skill.lower()
    
    frameworks = ["fastapi", "flask", "django", "react", "vue", "angular", "express", "spring"]
    databases = ["mongodb", "postgresql", "mysql", "redis", "dynamodb", "oracle"]
    cloud = ["aws", "azure", "gcp", "google cloud"]
    devops = ["docker", "kubernetes", "jenkins", "gitlab", "github actions"]
    languages = ["python", "javascript", "typescript", "java", "c#", "go", "rust"]
    
    if any(fw in skill_lower for fw in frameworks):
        return "framework"
    elif any(db in skill_lower for db in databases):
        return "database"
    elif any(c in skill_lower for c in cloud):
        return "cloud_platform"
    elif any(d in skill_lower for d in devops):
        return "devops"
    elif any(lang in skill_lower for lang in languages):
        return "language"
    else:
        return "other"


# Export main functions
__all__ = [
    "SEMANTIC_SKILLS",
    "get_related_skills",
    "find_skill_relationships",
    "calculate_skill_similarity",
    "get_skill_category"
]
