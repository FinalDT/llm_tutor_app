import os
import json
from typing import Optional


class Settings:
    """환경변수 중앙 관리 클래스"""

    def __init__(self):
        self._load_local_settings()
        self._validate_required_env_vars()

    def _load_local_settings(self):
        """local.settings.json에서 환경변수 로드"""
        try:
            local_settings_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'local.settings.json')
            if os.path.exists(local_settings_path):
                with open(local_settings_path, 'r', encoding='utf-8') as f:
                    settings_data = json.load(f)
                    values = settings_data.get('Values', {})

                    # 환경변수가 없는 경우에만 local.settings.json 값 사용
                    for key, value in values.items():
                        if not os.environ.get(key):
                            os.environ[key] = value
        except Exception as e:
            # local.settings.json 로드 실패해도 계속 진행
            pass

    @property
    def sql_connection_string(self) -> str:
        """SQL Server 연결 문자열"""
        return os.environ.get("SqlConnectionString", "")

    @property
    def openai_api_key(self) -> str:
        """OpenAI API 키"""
        return os.environ.get("OpenApiKey", "")

    @property
    def openai_endpoint(self) -> str:
        """OpenAI 엔드포인트"""
        return os.environ.get("OpenAIEndpoint", "")

    @property
    def openai_api_version(self) -> str:
        """OpenAI API 버전"""
        return "2023-05-15"

    @property
    def openai_model(self) -> str:
        """OpenAI 모델명"""
        return "gpt-4o-mini"

    def _validate_required_env_vars(self) -> None:
        """필수 환경변수 검증"""
        required_vars = [
            "SqlConnectionString",
            "OpenApiKey",
            "OpenAIEndpoint"
        ]

        missing_vars = []
        for var in required_vars:
            if not os.environ.get(var):
                missing_vars.append(var)

        if missing_vars:
            raise ValueError(f"Required environment variables are missing: {', '.join(missing_vars)}")


# 싱글톤 인스턴스
settings = Settings()