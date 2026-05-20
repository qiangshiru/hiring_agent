def get_resume_parser_service():
    from src.services.resume_parser.service import ResumeParserService
    return ResumeParserService

__all__ = ["get_resume_parser_service"]
