from pydantic_settings import BaseSettings

class Settings(BaseSettings):

    #App settings
    secret_key: str

    #Database settings
    db_host: str
    db_port: int
    db_user: str 
    db_password: str
    db_name: str

    #Admin user settings
    admin_email: str
    admin_password: str
    admin_first_name: str
    admin_last_name: str

    #JWT settings
    jwt_algorithm: str
    access_token_expire_minutes: int
    refresh_token_expire_days: int

    #Redis settings
    redis_db:int
    redis_host:str
    redis_port:int
    redis_password:str

    #Email settings
    email_host: str
    email_port: str
    email_host_user: str
    email_host_password: str
    email_from: str
    email_use_tls: bool
    email_verification_token_expire_days: int

    #Fronend settings
    front_end_url: str

    @property
    def database_url(self) -> str:
        return f"postgresql+psycopg://{self.db_user}:{self.db_password}@{self.db_host}:{self.db_port}/{self.db_name}"

    @property
    def redis_url(self) -> str:
        return f"redis://:{self.redis_password}@{self.redis_host}:{self.redis_port}/{self.redis_db}"
    
    @property
    def celery_broker_url(self) -> str:
        return self.redis_url
    
    @property
    def celery_result_backend(self) -> str:
        return self.redis_url

settings = Settings()