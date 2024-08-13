from pydantic import BaseSettings

class Settings(BaseSettings):
    app_name: str = "My FastAPI Application"  # 애플리케이션 이름 설정
    admin_email: str = "admin@example.com"    # 관리자 이메일 설정
    items_per_user: int = 50                  # 사용자당 처리할 항목 수 기본값 설정

settings = Settings()
