from fastapi import FastAPI, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
import os
import logging
from typing import List

from scheduler import SchedulerManager
from database import get_db, init_db
from models import SchedulerCreate, SchedulerResponse, LogResponse, StatisticsResponse
from crud import (
    create_scheduler_db, get_schedulers_db, get_scheduler_db,
    update_scheduler_db, delete_scheduler_db,
    get_logs_db, get_scheduler_logs_db, get_statistics_db,
    create_log_db, update_log_db
)

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Global scheduler manager
scheduler_manager = None

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan manager"""
    global scheduler_manager
    
    # Startup
    logger.info("Starting scheduler application...")
    
    # Initialize database
    await init_db()
    
    # Initialize scheduler manager
    scheduler_manager = SchedulerManager()
    scheduler_manager.start()
    
    # Restore existing schedulers from database
    try:
        db = await get_db().__anext__()
        schedulers = await get_schedulers_db(db)
        for scheduler in schedulers:
            if scheduler.get('is_active', True):
                await scheduler_manager.restore_scheduler(scheduler)
        logger.info(f"Restored {len([s for s in schedulers if s.get('is_active')])} active schedulers")
    except Exception as e:
        logger.error(f"Failed to restore schedulers: {e}")
    
    yield
    
    # Shutdown
    logger.info("Shutting down scheduler...")
    if scheduler_manager:
        scheduler_manager.shutdown()
    logger.info("Scheduler shut down successfully")

app = FastAPI(
    title="Scheduler Management API",
    description="API for managing scheduled jobs with APScheduler",
    version="1.0.0",
    lifespan=lifespan
)

# CORS configuration
allowed_origins = os.getenv("ALLOWED_ORIGINS", "http://localhost:3000").split(",")
app.add_middleware(
    CORSMiddleware,
    allow_origins=allowed_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
async def root():
    """Health check endpoint"""
    return {
        "status": "ok", 
        "message": "Scheduler Management API is running",
        "version": "1.0.0"
    }

@app.get("/schedulers", response_model=List[SchedulerResponse])
async def list_schedulers(db = Depends(get_db)):
    """List all schedulers"""
    try:
        return await get_schedulers_db(db)
    except Exception as e:
        logger.error(f"Error listing schedulers: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/schedulers", response_model=SchedulerResponse)
async def create_scheduler(
    scheduler_data: SchedulerCreate,
    db = Depends(get_db)
):
    """Create a new scheduler"""
    try:
        # Create scheduler in database
        scheduler = await create_scheduler_db(db, scheduler_data)
        
        # Add to APScheduler
        await scheduler_manager.add_scheduler(scheduler)
        
        return scheduler
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"Error creating scheduler: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/schedulers/{scheduler_id}", response_model=SchedulerResponse)
async def get_scheduler(scheduler_id: str, db = Depends(get_db)):
    """Get a specific scheduler by ID"""
    try:
        scheduler = await get_scheduler_db(db, scheduler_id)
        if not scheduler:
            raise HTTPException(status_code=404, detail="Scheduler not found")
        return scheduler
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting scheduler: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.put("/schedulers/{scheduler_id}", response_model=SchedulerResponse)
async def update_scheduler(
    scheduler_id: str,
    scheduler_data: dict,
    db = Depends(get_db)
):
    """Update a scheduler"""
    try:
        # Update in database
        scheduler = await update_scheduler_db(db, scheduler_id, scheduler_data)
        if not scheduler:
            raise HTTPException(status_code=404, detail="Scheduler not found")
        
        # Update in APScheduler
        await scheduler_manager.update_scheduler(scheduler)
        
        return scheduler
    except HTTPException:
        raise
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"Error updating scheduler: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/schedulers/{scheduler_id}/pause")
async def pause_scheduler(scheduler_id: str, db = Depends(get_db)):
    """Pause a scheduler"""
    try:
        # Update in database
        scheduler = await update_scheduler_db(db, scheduler_id, {"is_active": False})
        if not scheduler:
            raise HTTPException(status_code=404, detail="Scheduler not found")
        
        # Pause in APScheduler
        scheduler_manager.pause_scheduler(scheduler_id)
        
        return {"status": "paused", "scheduler_id": scheduler_id}
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error pausing scheduler: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/schedulers/{scheduler_id}/resume")
async def resume_scheduler(scheduler_id: str, db = Depends(get_db)):
    """Resume a scheduler"""
    try:
        # Update in database
        scheduler = await update_scheduler_db(db, scheduler_id, {"is_active": True})
        if not scheduler:
            raise HTTPException(status_code=404, detail="Scheduler not found")
        
        # Resume in APScheduler
        scheduler_manager.resume_scheduler(scheduler_id)
        
        return {"status": "resumed", "scheduler_id": scheduler_id}
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error resuming scheduler: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.delete("/schedulers/{scheduler_id}")
async def delete_scheduler(scheduler_id: str, db = Depends(get_db)):
    """Delete a scheduler"""
    try:
        # Remove from APScheduler
        scheduler_manager.remove_scheduler(scheduler_id)
        
        # Delete from database
        success = await delete_scheduler_db(db, scheduler_id)
        if not success:
            raise HTTPException(status_code=404, detail="Scheduler not found")
        
        return {"status": "deleted", "scheduler_id": scheduler_id}
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error deleting scheduler: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/schedulers/{scheduler_id}/logs", response_model=List[LogResponse])
async def get_scheduler_logs(
    scheduler_id: str,
    limit: int = 100,
    db = Depends(get_db)
):
    """Get execution logs for a scheduler"""
    try:
        return await get_scheduler_logs_db(db, scheduler_id, limit)
    except Exception as e:
        logger.error(f"Error getting scheduler logs: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/logs", response_model=List[LogResponse])
async def get_all_logs(limit: int = 100, db = Depends(get_db)):
    """Get all execution logs"""
    try:
        return await get_logs_db(db, limit)
    except Exception as e:
        logger.error(f"Error getting logs: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/stats", response_model=StatisticsResponse)
async def get_statistics(db = Depends(get_db)):
    """Get job execution statistics"""
    try:
        return await get_statistics_db(db)
    except Exception as e:
        logger.error(f"Error getting statistics: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# Job execution callback
async def job_execution_callback(scheduler_id: str, job_type: str, status: str, message: str = None, duration: int = None):
    """Callback for job execution logging"""
    try:
        db = await get_db().__anext__()
        await create_log_db(db, scheduler_id, job_type, status, message, duration)
    except Exception as e:
        logger.error(f"Failed to log job execution: {e}")

# Set the callback in scheduler manager
if scheduler_manager:
    scheduler_manager.set_log_callback(job_execution_callback)

if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("PORT", 8000))
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=port,
        reload=os.getenv("ENV") == "development"
    )
