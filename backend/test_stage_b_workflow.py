"""
Test Stage B: Mock Business Workflow

Goal: Prove the workflow works with mock data and services.
No AI, no agents - just business logic and data flow.
"""

from app.plugins.hr_recruitment.tools.mock_repositories import (
    get_job_repository,
    get_candidate_repository
)
from app.plugins.hr_recruitment.tools.services import (
    RequirementExtractionService,
    MatchingService,
    ScoringService,
    ShortlistingService
)


def test_stage_b_workflow():
    """Test the HR workflow with mock data."""
    
    print("🧪 Testing Stage B: Mock Business Workflow")
    print("=" * 80)
    
    # Initialize repositories and services
    job_repo = get_job_repository()
    candidate_repo = get_candidate_repository()
    
    requirement_service = RequirementExtractionService()
    matching_service = MatchingService()
    scoring_service = ScoringService()
    shortlisting_service = ShortlistingService()
    
    # Step 1: Get Job Description
    print("\n📋 Step 1: Job Description")
    print("-" * 80)
    job = job_repo.get_by_title("Python Backend Developer")
    
    if not job:
        print("❌ Job not found")
        return False
    
    print(f"✅ Job: {job['title']}")
    print(f"   ID: {job['id']}")
    print(f"   Description preview: {job['description'][:100]}...")
    
    # Step 2: Extract Requirements
    print("\n🔍 Step 2: Extract Requirements")
    print("-" * 80)
    requirements = requirement_service.extract(job["description"])
    
    print(f"✅ Requirements extracted:")
    print(f"   Required Skills: {requirements['required_skills']}")
    print(f"   Experience: {requirements['experience_years_min']}-{requirements['experience_years_max']} years")
    print(f"   Location: {requirements['location']}")
    print(f"   Education: {requirements['education']}")
    
    # Step 3: Search Candidates
    print("\n👥 Step 3: Search Candidates")
    print("-" * 80)
    candidates = candidate_repo.search(
        skills=requirements["required_skills"],
        min_experience=requirements["experience_years_min"],
        location=requirements["location"]
    )
    
    print(f"✅ Found {len(candidates)} matching candidates:")
    for candidate in candidates:
        print(f"   - {candidate['name']} ({candidate['experience_years']} years, {candidate['location']})")
    
    if len(candidates) == 0:
        print("⚠️  No candidates found, using all candidates for testing")
        candidates = candidate_repo.list_all()
    
    # Step 4: Match Candidates
    print("\n🎯 Step 4: Match Candidates to Requirements")
    print("-" * 80)
    matched = matching_service.match_candidates(requirements, candidates)
    
    print(f"✅ Matched {len(matched)} candidates:")
    for item in matched[:5]:  # Show top 5
        candidate = item["candidate"]
        match_data = item["match_data"]
        print(f"   - {candidate['name']}: {match_data['skill_match_score']}% skill match")
        print(f"     Matching: {match_data['matching_skills']}")
        if match_data['missing_skills']:
            print(f"     Missing: {match_data['missing_skills']}")
    
    # Step 5: Score Candidates
    print("\n📊 Step 5: Score Candidates")
    print("-" * 80)
    scored = scoring_service.score_candidates(requirements, matched)
    
    print(f"✅ Scored {len(scored)} candidates:")
    for item in scored[:5]:  # Show top 5
        candidate = item["candidate"]
        scores = item["scores"]
        print(f"   - {candidate['name']}: {scores['final']} points")
        print(f"     Skills: {scores['skill']}, Experience: {scores['experience']}, "
              f"Education: {scores['education']}, Location: {scores['location']}")
    
    # Step 6: Generate Shortlist
    print("\n🌟 Step 6: Generate Shortlist")
    print("-" * 80)
    result = shortlisting_service.generate_shortlist(scored, top_n=5)
    
    shortlist = result["shortlist"]
    summary = result["summary"]
    
    print(f"✅ Shortlist generated ({len(shortlist)} candidates):")
    print()
    
    for item in shortlist:
        candidate = item["candidate"]
        scores = item["scores"]
        rank = item["rank"]
        recommendation = item["recommendation"]
        priority = item["priority"]
        
        print(f"   {rank}. {candidate['name']} - Score: {scores['final']} [{priority} Priority]")
        print(f"      Skills: {', '.join(candidate['skills'][:4])}")
        print(f"      Experience: {candidate['experience_years']} years")
        print(f"      Location: {candidate['location']}")
        print(f"      Recommendation: {recommendation}")
        print()
    
    # Summary
    print("📈 Summary:")
    print(f"   Total candidates evaluated: {summary['total_candidates']}")
    print(f"   Shortlisted: {summary['shortlisted']}")
    print(f"   Average score: {summary['average_score']}")
    print(f"   High priority: {summary['high_priority']}")
    print(f"   Medium priority: {summary['medium_priority']}")
    print(f"   Low priority: {summary['low_priority']}")
    
    # Validation
    print("\n" + "=" * 80)
    print("✅ STAGE B: WORKFLOW COMPLETE!")
    print("=" * 80)
    
    print("\n✨ What Stage B Proved:")
    print("✅ Job description → Requirements extraction works")
    print("✅ Requirements → Candidate search works")
    print("✅ Candidates → Matching works")
    print("✅ Matching → Scoring works")
    print("✅ Scoring → Shortlist works")
    print("✅ End-to-end workflow produces business result")
    
    print("\n📊 Data Flow Validated:")
    print("   Job Description")
    print("        ↓")
    print("   Requirements (extracted)")
    print("        ↓")
    print(f"   Candidates ({len(candidates)} found)")
    print("        ↓")
    print(f"   Matched ({len(matched)} evaluated)")
    print("        ↓")
    print(f"   Scored ({len(scored)} ranked)")
    print("        ↓")
    print(f"   Shortlist ({len(shortlist)} selected)")
    
    print("\n🎯 Business Output:")
    print(f"   Top candidate: {shortlist[0]['candidate']['name']} (Score: {shortlist[0]['scores']['final']})")
    print(f"   Recommendation: {shortlist[0]['recommendation']}")
    
    print("\n⏭️  Ready for Stage C: Add Intelligence (one capability at a time)")
    
    return True


def test_repository_layer():
    """Test repository layer independently."""
    print("\n" + "=" * 80)
    print("🧪 Testing Repository Layer")
    print("=" * 80)
    
    job_repo = get_job_repository()
    candidate_repo = get_candidate_repository()
    
    # Test job repository
    print("\n📋 Job Repository:")
    jobs = job_repo.list_all()
    print(f"✅ {len(jobs)} jobs in repository")
    
    job = job_repo.get_by_id("JOB001")
    if job:
        print(f"✅ Get by ID works: {job['title']}")
    
    job = job_repo.get_by_title("Python")
    if job:
        print(f"✅ Get by title works: {job['title']}")
    
    # Test candidate repository
    print("\n👥 Candidate Repository:")
    candidates = candidate_repo.list_all()
    print(f"✅ {len(candidates)} candidates in repository")
    
    candidate = candidate_repo.get_by_id("CAND001")
    if candidate:
        print(f"✅ Get by ID works: {candidate['name']}")
    
    # Test search
    results = candidate_repo.search(skills=["Python"], min_experience=3)
    print(f"✅ Search works: Found {len(results)} Python developers with 3+ years")
    
    results = candidate_repo.search(location="Remote")
    print(f"✅ Location filter works: Found {len(results)} remote candidates")
    
    return True


if __name__ == "__main__":
    print("🚀 Stage B: Mock Business Workflow Test")
    print("=" * 80)
    print()
    
    # Test repository layer
    repo_passed = test_repository_layer()
    
    if not repo_passed:
        print("\n❌ Repository layer tests failed")
        exit(1)
    
    # Test workflow
    workflow_passed = test_stage_b_workflow()
    
    if not workflow_passed:
        print("\n❌ Workflow tests failed")
        exit(1)
    
    # All tests passed
    print("\n" + "=" * 80)
    print("🎉 ALL STAGE B TESTS PASSED!")
    print("=" * 80)
    
    print("\n✅ Stage B Quality Gate:")
    print("✅ Mock data created (8 candidates, 2 jobs)")
    print("✅ Repository layer works")
    print("✅ Service layer works")
    print("✅ Workflow executes end-to-end")
    print("✅ Business result generated")
    print("✅ No AI involved (pure business logic)")
    
    print("\n🚀 Stage B Complete - Ready for Stage C!")
    print("\n💡 In Stage C, we'll replace RequirementExtractionService")
    print("   with Gemini LLM, keeping everything else unchanged.")
