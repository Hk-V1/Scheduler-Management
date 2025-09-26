from pydantic import BaseModel, Field, validator
from sqlalchemy import Column, String, DateTime, Boolean, Text, Integer, JSON
from sqlalchemy.sql import func
from datetime import datetime
from typing import Dict, Any, Optional
from enum import Enum
import uuid

from database import Base

# Pydantic models for API
class JobType(str, Enum):
    EMAIL_NOTIFICATION = "email_notification"
    DATA_BACKUP = "data_backup"
    REPORT_GENERATION = "report_generation"
    API_CALL = "api_call"
    FILE_CLEANUP = "file_cleanup"
    CUSTOM = "custom"

class FrequencyType(str, Enum):
    CRON = "cron"
    INTERVAL = "interval"
    DATE = "date"

class LogStatus(str, Enum):
    SUCCESS = "success"
    ERROR = "error"
    RUNNING = "running"

class SchedulerCreate(BaseModel):
    name: str = Field(..., min_length=1, max_length=200)
    description: Optional[str] = Field(default=None, max_length=1000)
    job_type = Column(String(100), nullable=False)
    status = Column(String(20), nullable=False)
    message = Column(Text, nullable=True)
    started_at = Column(DateTime(timezone=True), server_default=func.now())
    completed_at = Column(DateTime(timezone=True), nullable=True)
    duration = Column(Integer, nullable=True)

# MongoDB document structures
class MongoSchedulerDocument:
    @staticmethod
    def create_document(
        id: str,
        name: str,
        job_type: str,
        frequency: str,
        frequency_config: Dict[str, Any],
        description: Optional[str] = None,
        is_active: bool = True
    ) -> Dict[str, Any]:
        return {
            "_id": id,
            "name": name,
            "description": description,
            "job_type": job_type,
            "frequency": frequency,
            "frequency_config": frequency_config,
            "is_active": is_active,
            "created_at": datetime.utcnow(),
            "updated_at": datetime.utcnow(),
            "last_run": None,
            "next_run": None
        }

class MongoLogDocument:
    @staticmethod
    def create_document(
        id: str,
        scheduler_id: str,
        job_type: str,
        status: str,
        message: Optional[str] = None,
        started_at: Optional[datetime] = None,
        completed_at: Optional[datetime] = None,
        duration: Optional[int] = None
    ) -> Dict[str, Any]:
        return {
            "_id": id,
            "scheduler_id": scheduler_id,
            "job_type": job_type,
            "status": status,
            "message": message,
            "started_at": started_at or datetime.utcnow(),
            "completed_at": completed_at,
            "duration": duration
        }: JobType
    frequency: FrequencyType
    frequency_config: Dict[str, Any]
    
    @validator('frequency_config')
    def validate_frequency_config(cls, v, values):
        frequency_type = values.get('frequency')
        if not frequency_type:
            return v
        
        if frequency_type == FrequencyType.CRON:
            if 'cron_expression' not in v:
                raise ValueError('cron_expression is required for cron frequency')
        elif frequency_type == FrequencyType.INTERVAL:
            valid_keys = {'seconds', 'minutes', 'hours', 'days'}
            if not any(key in v for key in valid_keys):
                raise ValueError('At least one interval (seconds, minutes, hours, days) must be specified')
        elif frequency_type == FrequencyType.DATE:
            if 'run_date' not in v:
                raise ValueError('run_date is required for date frequency')
        
        return v

class SchedulerResponse(BaseModel):
    id: str
    name: str
    description: Optional[str]
    job_type: str
    frequency: str
    frequency_config: Dict[str, Any]
    is_active: bool
    created_at: datetime
    updated_at: Optional[datetime]
    last_run: Optional[datetime]
    next_run: Optional[datetime]
    
    class Config:
        from_attributes = True

class LogResponse(BaseModel):
    id: str
    scheduler_id: str
    job_type: str
    status: str
    message: Optional[str]
    started_at: datetime
    completed_at: Optional[datetime]
    duration: Optional[int]
    
    class Config:
        from_attributes = True

class StatisticsResponse(BaseModel):
    total_schedulers: int
    active_schedulers: int
    paused_schedulers: int
    total_executions: int
    successful_executions: int
    failed_executions: int
    executions_by_job_type: Dict[str, int]
    executions_by_date: Dict[str, int]
    average_execution_duration: Optional[float]

# SQLAlchemy models for SQL databases
class SchedulerTable(Base):
    __tablename__ = "schedulers"
    
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    name = Column(String(200), nullable=False)
    description = Column(Text, nullable=True)
    job_type = Column(String(100), nullable=False)
    frequency = Column(String(50), nullable=False)
    frequency_config = Column(JSON, nullable=False)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    last_run = Column(DateTime(timezone=True), nullable=True)
    next_run = Column(DateTime(timezone=True), nullable=True)

class LogTable(Base):
    __tablename__ = "logs"
    
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    scheduler_id = Column(String, nullable=False)
    job_type
