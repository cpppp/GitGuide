from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey
from sqlalchemy.orm import relationship, declarative_base
from datetime import datetime

Base = declarative_base()

class Repository(Base):
    __tablename__ = "repositories"

    id = Column(Integer, primary_key=True, index=True)
    url = Column(String(500), unique=True, nullable=False)
    name = Column(String(200))
    description = Column(Text)
    language = Column(String(50))
    stars = Column(Integer, default=0)

    # V3.0 文档
    quick_start = Column(Text)
    overview_doc = Column(Text)
    architecture_doc = Column(Text)
    install_guide = Column(Text)

    # V3.1 文档
    usage_tutorial = Column(Text)
    dev_guide = Column(Text)
    troubleshooting = Column(Text)

    # V3.1 代码图谱数据
    code_graph = Column(Text)  # JSON格式存储代码图谱
    examples = Column(Text)    # JSON格式存储示例代码

    # V2.x 旧字段（兼容）
    learning_doc = Column(Text)
    setup_guide = Column(Text)

    analysis_result = Column(Text)
    quality_score = Column(Integer, default=0)

    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    chat_messages = relationship("ChatMessage", back_populates="repository", cascade="all, delete-orphan")
    favorites = relationship("Favorite", back_populates="repository", cascade="all, delete-orphan")

class ChatMessage(Base):
    __tablename__ = "chat_messages"
    
    id = Column(Integer, primary_key=True, index=True)
    repo_id = Column(Integer, ForeignKey("repositories.id", ondelete="CASCADE"))
    role = Column(String(20), nullable=False)
    content = Column(Text, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    repository = relationship("Repository", back_populates="chat_messages")

class Favorite(Base):
    __tablename__ = "favorites"
    
    id = Column(Integer, primary_key=True, index=True)
    repo_id = Column(Integer, ForeignKey("repositories.id", ondelete="CASCADE"))
    created_at = Column(DateTime, default=datetime.utcnow)
    
    repository = relationship("Repository", back_populates="favorites")

class AnalysisHistory(Base):
    __tablename__ = "analysis_history"
    
    id = Column(Integer, primary_key=True, index=True)
    repo_id = Column(Integer, ForeignKey("repositories.id", ondelete="CASCADE"))
    analyzed_at = Column(DateTime, default=datetime.utcnow)
