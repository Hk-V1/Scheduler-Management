import os
import logging
import uuid
from datetime import datetime
from typing import List, Dict, Any, Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update, delete, func, desc
from collections import defaultdict

from models import (
    SchedulerCreate, SchedulerTable, LogTable,
    MongoSchedulerDocument, MongoLogDocument
)

logger = logging.getLogger(__name__)

DATABASE_TYPE = os.getenv("DATABASE_TYPE", "postgresql")

# Scheduler CRUD operations

async def create_scheduler_db(db, scheduler_data: SchedulerCreate) -> Dict[str, Any]:
    """Create a new scheduler in database"""
    scheduler_id = str(uuid.uuid4())
    
    if DATABASE_TYPE == "mongodb":
        # MongoDB implementation
        collection = db["schedulers"]
        doc = MongoSchedulerDocument.create_document(
            id=scheduler_id,
            name=scheduler_data.name,
            job_type=scheduler_data.job_type,
            frequency=scheduler_data.frequency,
            frequency_config=scheduler_data.frequency_config,
            description=scheduler_data.description
        )
        await collection.insert_one(doc)
        return _mongo_doc_to_dict(doc)
    else:
        # SQL implementation
        new_scheduler = SchedulerTable(
            id=scheduler_id,
            name=scheduler_data.name,
            description=scheduler_data.description,
            job_type=scheduler_data.job_type,
            frequency=scheduler_data.frequency,
            frequency_config=scheduler_data.frequency_config
        )
        db.add(new_scheduler)
        await db.commit()
        await db.refresh(new_scheduler)
        return _sql_row_to_dict(new_scheduler)

async def get_schedulers_db(db) -> List[Dict[str, Any]]:
    """Get all schedulers from database"""
    if DATABASE_TYPE == "mongodb":
        # MongoDB implementation
        collection = db["schedulers"]
        cursor = collection.find({}).sort("created_at", -1)
        schedulers = await cursor.to_list(length=None)
        return [_mongo_doc_to_dict(doc) for doc in schedulers]
    else:
        # SQL implementation
        result = await db.execute(
            select(SchedulerTable).order_by(desc(SchedulerTable.created_at))
        )
        schedulers = result.scalars().all()
        return [_sql_row_to_dict(scheduler) for scheduler in schedulers]

async def get_scheduler_db(db, scheduler_id: str) -> Optional[Dict[str, Any]]:
    """Get a scheduler by ID from database"""
    if DATABASE_TYPE == "mongodb":
        # MongoDB implementation
        collection = db["schedulers"]
        doc = await collection.find_one({"_id": scheduler_id})
        return _mongo_doc_to_dict(doc) if doc else None
    else:
        # SQL implementation
        result = await db.execute(
            select(SchedulerTable).where(SchedulerTable.id == scheduler_id)
        )
        scheduler = result.scalar_one_or_none()
        return _sql_row_to_dict(scheduler) if scheduler else None

async def update_scheduler_db(db, scheduler_id: str, update_data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
    """Update a scheduler in database"""
    if DATABASE_TYPE == "mongodb":
        # MongoDB implementation
        collection = db["schedulers"]
        update_doc = {"updated_at": datetime.utcnow()}
        update_doc.update(update_data)
        
        result = await collection.update_one(
            {"_id": scheduler_id},
            {"$set": update_doc}
        )
        
        if result.modified_count > 0:
            updated_doc = await collection.find_one({"_id": scheduler_id})
            return _mongo_doc_to_dict(updated_doc)
        return None
    else:
        # SQL implementation
        update_values = {"updated_at": datetime.utcnow()}
        update_values.update(update_data)
        
        result = await db.execute(
            update(SchedulerTable)
            .where(SchedulerTable.id == scheduler_id)
            .values(**update_values)
        )
        
        if result.rowcount > 0:
            await db.commit()
            return await get_scheduler_db(db, scheduler_id)
        return None

async def delete_scheduler_db(db, scheduler_id: str) -> bool:
    """Delete a scheduler from database"""
    if DATABASE_TYPE == "mongodb":
        # MongoDB implementation
        collection = db["schedulers"]
        result = await collection.delete_one({"_id": scheduler_id})
        return result.deleted_count > 0
    else:
        # SQL implementation
        result = await db.execute(
            delete(SchedulerTable).where(SchedulerTable.id == scheduler_id)
        )
        if result.rowcount > 0:
            await db.commit()
            return True
        return False

# Log CRUD operations

async def create_log_db(
    db, 
    scheduler_id: str, 
    job_type: str, 
    status: str, 
    message: str = None, 
    duration: int = None
) -> Dict[str, Any]:
    """Create a log entry in database"""
    log_id = str(uuid.uuid4())
    
    if DATABASE_TYPE == "mongodb":
        # MongoDB implementation
        collection = db["logs"]
        doc = MongoLogDocument.create_document(
            id=log_id,
            scheduler_id=scheduler_id,
            job_type=job_type,
            status=status,
            message=message,
            duration=duration
        )
        if status != "running":
            doc["completed_at"] = datetime.utcnow()
        
        await collection.insert_one(doc)
        return _mongo_doc_to_dict(doc)
    else:
        # SQL implementation
        new_log = LogTable(
            id=log_id,
            scheduler_id=scheduler_id,
            job_type=job_type,
            status=status,
            message=message,
            duration=duration
        )
        if status != "running":
            new_log.completed_at = datetime.utcnow()
        
        db.add(new_log)
        await db.commit()
        await db.refresh(new_log)
        return _sql_row_to_dict(new_log)

async def update_log_db(
    db,
    log_id: str,
    status: str,
    message: str = None,
    duration: int = None
):
    """Update a log entry in database"""
    if DATABASE_TYPE == "mongodb":
        # MongoDB implementation
        collection = db["logs"]
        update_doc = {
            "status": status,
            "completed_at": datetime.utcnow()
        }
        if message:
            update_doc["message"] = message
        if duration:
            update_doc["duration"] = duration
        
        await collection.update_one({"_id": log_id}, {"$set": update_doc})
    else:
        # SQL implementation
        update_values = {
            "status": status,
            "completed_at": datetime.utcnow()
        }
        if message:
            update_values["message"] = message
        if duration:
            update_values["duration"] = duration
        
        await db.execute(
            update(LogTable)
            .where(LogTable.id == log_id)
            .values(**update_values)
        )
        await db.commit()

async def get_logs_db(db, limit: int = 100) -> List[Dict[str, Any]]:
    """Get all logs from database"""
    if DATABASE_TYPE == "mongodb":
        # MongoDB implementation
        collection = db["logs"]
        cursor = collection.find({}).sort("started_at", -1).limit(limit)
        logs = await cursor.to_list(length=None)
        return [_mongo_doc_to_dict(doc) for doc in logs]
    else:
        # SQL implementation
        result = await db.execute(
            select(LogTable).order_by(desc(LogTable.started_at)).limit(limit)
        )
        logs = result.scalars().all()
        return [_sql_row_to_dict(log) for log in logs]

async def get_scheduler_logs_db(db, scheduler_id: str, limit: int = 100) -> List[Dict[str, Any]]:
    """Get logs for a specific scheduler"""
    if DATABASE_TYPE == "mongodb":
        # MongoDB implementation
        collection = db["logs"]
        cursor = collection.find({"scheduler_id": scheduler_id}).sort("started_at", -1).limit(limit)
        logs = await cursor.to_list(length=None)
        return [_mongo_doc_to_dict(doc) for doc in logs]
    else:
        # SQL implementation
        result = await db.execute(
            select(LogTable)
            .where(LogTable.scheduler_id == scheduler_id)
            .order_by(desc(LogTable.started_at))
            .limit(limit)
        )
        logs = result.scalars().all()
        return [_sql_row_to_dict(log) for log in logs]

async def get_statistics_db(db) -> Dict[str, Any]:
    """Get statistics from database"""
    if DATABASE_TYPE == "mongodb":
        return await _get_mongodb_statistics(db)
    else:
        return await _get_sql_statistics(db)

# Helper functions

def _sql_row_to_dict(row) -> Dict[str, Any]:
    """Convert SQLAlchemy row to dictionary"""
    if not row:
        return None
    
    result = {}
    for column in row.__table__.columns:
        value = getattr(row, column.name)
        if isinstance(value, datetime):
            result[column.name] = value.isoformat()
        else:
            result[column.name] = value
    return result

def _mongo_doc_to_dict(doc) -> Dict[str, Any]:
    """Convert MongoDB document to dictionary"""
    if not doc:
        return None
    
    result = {}
    for key, value in doc.items():
        if key == "_id":
            result["id"] = value
        elif isinstance(value, datetime):
            result[key] = value.isoformat()
        else:
            result[key] = value
    return result

async def _get_sql_statistics(db) -> Dict[str, Any]:
    """Get statistics from SQL database"""
    # Basic counts
    total_schedulers = await db.scalar(select(func.count(SchedulerTable.id)))
    active_schedulers = await db.scalar(
        select(func.count(SchedulerTable.id)).where(SchedulerTable.is_active == True)
    )
    paused_schedulers = total_schedulers - active_schedulers
    
    total_executions = await db.scalar(select(func.count(LogTable.id)))
    successful_executions = await db.scalar(
        select(func.count(LogTable.id)).where(LogTable.status == "success")
    )
    failed_executions = await db.scalar(
        select(func.count(LogTable.id)).where(LogTable.status == "error")
    )
    
    # Average duration
    avg_duration = await db.scalar(
        select(func.avg(LogTable.duration)).where(LogTable.duration.isnot(None))
    )
    
    return {
        "total_schedulers": total_schedulers or 0,
        "active_schedulers": active_schedulers or 0,
        "paused_schedulers": paused_schedulers or 0,
        "total_executions": total_executions or 0,
        "successful_executions": successful_executions or 0,
        "failed_executions": failed_executions or 0,
        "executions_by_job_type": {},
        "executions_by_date": {},
        "average_execution_duration": float(avg_duration) if avg_duration else None
    }

async def _get_mongodb_statistics(db) -> Dict[str, Any]:
    """Get statistics from MongoDB"""
    schedulers_collection = db["schedulers"]
    logs_collection = db["logs"]
    
    # Basic counts
    total_schedulers = await schedulers_collection.count_documents({})
    active_schedulers = await schedulers_collection.count_documents({"is_active": True})
    paused_schedulers = total_schedulers - active_schedulers
    
    total_executions = await logs_collection.count_documents({})
    successful_executions = await logs_collection.count_documents({"status": "success"})
    failed_executions = await logs_collection.count_documents({"status": "error"})
    
    # Average duration
    pipeline = [
        {"$match": {"duration": {"$ne": None}}},
        {"$group": {"_id": None, "avg_duration": {"$avg": "$duration"}}}
    ]
    avg_result = await logs_collection.aggregate(pipeline).to_list(length=1)
    avg_duration = avg_result[0]["avg_duration"] if avg_result else None
    
    return {
        "total_schedulers": total_schedulers,
        "active_schedulers": active_schedulers,
        "paused_schedulers": paused_schedulers,
        "total_executions": total_executions,
        "successful_executions": successful_executions,
        "failed_executions": failed_executions,
        "executions_by_job_type": {},
        "executions_by_date": {},
        "average_execution_duration": avg_duration
    }
