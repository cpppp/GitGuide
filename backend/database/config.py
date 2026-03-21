from sqlalchemy import create_engine, inspect, text
from sqlalchemy.orm import sessionmaker
from backend.models.database import Base
import os

DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./gitguide.db")

engine = create_engine(
    DATABASE_URL,
    connect_args={"check_same_thread": False} if "sqlite" in DATABASE_URL else {}
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def init_db():
    """初始化数据库并执行迁移"""
    Base.metadata.create_all(bind=engine)
    migrate_database()

def migrate_database():
    """数据库迁移 - 添加新列"""
    if "sqlite" not in DATABASE_URL:
        return

    inspector = inspect(engine)
    existing_columns = [col["name"] for col in inspector.get_columns("repositories")]

    # 需要添加的新列
    new_columns = {
        "quick_start": "TEXT",
        "overview_doc": "TEXT",
        "architecture_doc": "TEXT",
        "install_guide": "TEXT",
        "usage_tutorial": "TEXT",
        "dev_guide": "TEXT",
        "troubleshooting": "TEXT",
        "quality_score": "INTEGER DEFAULT 0",
        # V3.1.2 新增字段
        "code_graph": "TEXT",
        "examples": "TEXT"
    }

    with engine.connect() as conn:
        for col_name, col_type in new_columns.items():
            if col_name not in existing_columns:
                try:
                    # SQLite 迁移：使用 ALTER TABLE ADD COLUMN
                    conn.execute(text(f"ALTER TABLE repositories ADD COLUMN {col_name} {col_type}"))
                    conn.commit()
                    print(f"[Migration] Added column: {col_name}")
                except Exception as e:
                    print(f"[Migration] Column {col_name} already exists or error: {e}")

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
