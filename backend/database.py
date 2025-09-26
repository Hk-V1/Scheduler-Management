import os
import logging
from typing import AsyncGenerator, Any
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from sqlalchemy.orm import declarative_base
from motor.motor_asyncio import AsyncIOMotorClient

logger = logging.getLogger(__name__)

# Database configuration
DATABASE_TYPE = os.getenv("DATABASE_TYPE", "postgresql")
DATABASE_URL = os.getenv("DATABASE_URL")

# SQL Database setup
Base = declarative_base()
engine = None
SessionLocal = None

# MongoDB setup
mongo_client = None
mongo_db = None

async def init_db():
    """Initialize database connection"""
    global engine, SessionLocal, mongo_client, mongo_db
    
    if DATABASE_TYPE == "mongodb":
        await init_mongodb()
    else:
        await init_sql_database()

async def init_sql_database():
    """Initialize SQL database (PostgreSQL, MySQL, MSSQL)"""
    global engine, SessionLocal
    
    try:
        # Build database URL if not provided
        if not DATABASE_URL:
            if DATABASE_TYPE == "postgresql":
                db_url = f"postgresql+asyncpg://{os.getenv('POSTGRES_USER', 'postgres')}:{os.getenv('POSTGRES_PASSWORD', 'password')}@{os.getenv('POSTGRES_HOST', 'localhost')}:{os.getenv('POSTGRES_PORT', 5432)}/{os.getenv('POSTGRES_DB', 'scheduler_db')}"
            elif DATABASE_TYPE == "mysql":
                db_url = f"mysql+pymysql://{os.getenv('MYSQL_USER', 'root')}:{os.getenv('MYSQL_PASSWORD', 'password')}@{os.getenv('MYSQL_HOST', 'localhost')}:{os.getenv('MYSQL_PORT', 3306)}/{os.getenv('MYSQL_DB', 'scheduler_db')}"
            elif DATABASE_TYPE == "mssql":
                db_url = f"mssql+pyodbc://{os.getenv('MSSQL_USER', 'sa')}:{os.getenv('MSSQL_PASSWORD', 'Password123!')}@{os.getenv('MSSQL_HOST', 'localhost')}:{os.getenv('MSSQL_PORT', 1433)}/{os.getenv('MSSQL_DB', 'scheduler_db')}?driver=ODBC+Driver+17+for+SQL+Server"
            else:
                raise ValueError(f"Unsupported database type: {DATABASE_TYPE}")
        else:
            db_url = DATABASE_URL
        
        engine = create_async_engine(
            db_url,
            echo=os.getenv("ENV") == "development",
            pool_pre_ping=True,
            pool_recycle=300,
        )
        
        SessionLocal = async_sessionmaker(
            bind=engine,
            class_=AsyncSession,
            expire_on_commit=False
        )
        
        # Create tables
        from models import SchedulerTable, LogTable
        async with engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)
        
        logger.info(f"SQL database initialized: {DATABASE_TYPE}")
        
    except Exception as e:
        logger.error(f"Failed to initialize SQL database: {e}")
        raise

async def init_mongodb():
    """Initialize MongoDB connection"""
    global mongo_client, mongo_db
    
    try:
        # Build MongoDB URL if not provided
        if not DATABASE_URL:
            mongo_host = os.getenv("MONGODB_HOST", "localhost")
            mongo_port = int(os.getenv("MONGODB_PORT", 27017))
            mongo_user = os.getenv("MONGODB_USER")
            mongo_password = os.getenv("MONGODB_PASSWORD")
            mongo_db_name = os.getenv("MONGODB_DB", "scheduler_db")
            
            if mongo_user and mongo_password:
                db_url = f"mongodb://{mongo_user}:{mongo_password}@{mongo_host}:{mongo_port}/{mongo_db_name}"
            else:
                db_url = f"mongodb://{mongo_host}:{mongo_port}/{mongo_db_name}"
        else:
            db_url = DATABASE_URL
            mongo_db_name = os.getenv("MONGODB_DB", "scheduler_db")
        
        mongo_client = AsyncIOMotorClient(db_url)
        mongo_db = mongo_client[mongo_db_name]
        
        # Test connection
        await mongo_client.admin.command('ping')
        
        logger.info("MongoDB database initialized")
        
    except Exception as e:
        logger.error(f"Failed to initialize MongoDB: {e}")
        raise

async def get_db() -> AsyncGenerator[Any, None]:
    """Get database session/connection"""
    if DATABASE_TYPE == "mongodb":
        yield mongo_db
    else:
        async with SessionLocal() as session:
            try:
                yield session
            except Exception:
                await session.rollback()
                raise
            finally:
                await session.close()

async def close_db():
    """Close database connections"""
    global engine, mongo_client
    
    if engine:
        await engine.dispose()
    if mongo_client:
        mongo_client.close()
