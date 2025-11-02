import json

def get_mails(since: str, until: str) -> str:
    """
    Get emails between two dates (mock implementation)
    
    Args:
        since: Start date
        until: End date
    """
    mock_emails = [
        {
            "from": "john.doe@company.com",
            "subject": "Project Status Update",
            "date": "2025-10-30 09:15",
            "summary": "Discussed Q4 deliverables and timeline adjustments"
        },
        {
            "from": "sarah.smith@company.com",
            "subject": "Code Review Request",
            "date": "2025-10-30 14:30",
            "summary": "Reviewed PR #123 for the new authentication feature"
        },
        {
            "from": "team@company.com",
            "subject": "Team Meeting Notes",
            "date": "2025-10-31 10:00",
            "summary": "Weekly sync - discussed sprint progress and blockers"
        }
    ]
    return json.dumps({"emails": mock_emails, "period": f"{since} to {until}"}, ensure_ascii=False)

def get_chats(since: str, until: str) -> str:
    """
    Get chat messages between two dates (mock implementation)
    
    Args:
        since: Start date
        until: End date
    """
    mock_chats = [
        {
            "channel": "Engineering",
            "date": "2025-10-30 11:00",
            "participants": ["Alice", "Bob"],
            "summary": "Discussed API design for new microservice"
        },
        {
            "channel": "Product",
            "date": "2025-10-30 15:45",
            "participants": ["Product Manager", "Design Team"],
            "summary": "Reviewed mockups for user dashboard redesign"
        },
        {
            "channel": "DevOps",
            "date": "2025-10-31 09:30",
            "participants": ["DevOps Team"],
            "summary": "Planned infrastructure upgrade for production environment"
        }
    ]
    return json.dumps({"chats": mock_chats, "period": f"{since} to {until}"}, ensure_ascii=False)

def get_notes(since: str, until: str) -> str:
    """
    Get personal notes between two dates (mock implementation)
    
    Args:
        since: Start date
        until: End date
    """
    mock_notes = [
        {
            "title": "Technical Research",
            "date": "2025-10-30 13:00",
            "content": "Explored OpenVINO optimization techniques for LLM inference"
        },
        {
            "title": "Meeting Action Items",
            "date": "2025-10-30 16:00",
            "content": "1. Update documentation 2. Schedule follow-up with stakeholders 3. Review test coverage"
        },
        {
            "title": "Ideas",
            "date": "2025-10-31 08:00",
            "content": "Consider implementing tool-calling feature with ReAct pattern for better LLM interactions"
        }
    ]
    return json.dumps({"notes": mock_notes, "period": f"{since} to {until}"}, ensure_ascii=False)
