import asyncio
import logging
import time
from datetime import datetime
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.cron import CronTrigger
from apscheduler.triggers.interval import IntervalTrigger
from apscheduler.triggers.date import DateTrigger
from apscheduler.jobstores.memory import MemoryJobStore
from apscheduler.executors.asyncio import AsyncIOExecutor
from typing import Dict, Any, Callable, Optional
import httpx

logger = logging.getLogger(__name__)

class SchedulerManager:
    """Manages APScheduler and job execution"""
    
    def __init__(self):
        # Configure APScheduler
        jobstores = {
            'default': MemoryJobStore()
        }
        executors = {
            'default': AsyncIOExecutor()
        }
        job_defaults = {
            'coalesce': False,
            'max_instances': 3
        }
        
        self.scheduler = AsyncIOScheduler(
            jobstores=jobstores,
            executors=executors,
            job_defaults=job_defaults
        )
        
        self.log_callback: Optional[Callable] = None
    
    def start(self):
        """Start the scheduler"""
        self.scheduler.start()
        logger.info("APScheduler started")
    
    def shutdown(self):
        """Shutdown the scheduler"""
        if self.scheduler.running:
            self.scheduler.shutdown()
            logger.info("APScheduler shutdown")
    
    def set_log_callback(self, callback: Callable):
        """Set the logging callback function"""
        self.log_callback = callback
    
    async def add_scheduler(self, scheduler_data: Dict[str, Any]):
        """Add a new scheduler to APScheduler"""
        try:
            scheduler_id = scheduler_data['id']
            job_type = scheduler_data['job_type']
            frequency = scheduler_data['frequency']
            frequency_config = scheduler_data['frequency_config']
            
            # Create trigger based on frequency type
            trigger = self._create_trigger(frequency, frequency_config)
            
            # Add job to scheduler
            self.scheduler.add_job(
                func=self._execute_job,
                trigger=trigger,
                id=scheduler_id,
                args=[scheduler_id, job_type],
                replace_existing=True,
                max_instances=1
            )
            
            logger.info(f"Added scheduler {scheduler_id} with job type {job_type}")
            
        except Exception as e:
            logger.error(f"Failed to add scheduler {scheduler_data.get('id')}: {e}")
            raise
    
    async def update_scheduler(self, scheduler_data: Dict[str, Any]):
        """Update an existing scheduler"""
        try:
            scheduler_id = scheduler_data['id']
            frequency = scheduler_data['frequency']
            frequency_config = scheduler_data['frequency_config']
            
            # Create new trigger
            trigger = self._create_trigger(frequency, frequency_config)
            
            # Modify existing job
            self.scheduler.modify_job(scheduler_id, trigger=trigger)
            
            logger.info(f"Updated scheduler {scheduler_id}")
            
        except Exception as e:
            logger.error(f"Failed to update scheduler {scheduler_data.get('id')}: {e}")
            raise
    
    async def restore_scheduler(self, scheduler_data: Dict[str, Any]):
        """Restore a scheduler from database on startup"""
        try:
            await self.add_scheduler(scheduler_data)
            logger.info(f"Restored scheduler {scheduler_data['id']}")
        except Exception as e:
            logger.error(f"Failed to restore scheduler {scheduler_data.get('id')}: {e}")
    
    def pause_scheduler(self, scheduler_id: str):
        """Pause a scheduler"""
        try:
            self.scheduler.pause_job(scheduler_id)
            logger.info(f"Paused scheduler {scheduler_id}")
        except Exception as e:
            logger.error(f"Failed to pause scheduler {scheduler_id}: {e}")
            raise
    
    def resume_scheduler(self, scheduler_id: str):
        """Resume a scheduler"""
        try:
            self.scheduler.resume_job(scheduler_id)
            logger.info(f"Resumed scheduler {scheduler_id}")
        except Exception as e:
            logger.error(f"Failed to resume scheduler {scheduler_id}: {e}")
            raise
    
    def remove_scheduler(self, scheduler_id: str):
        """Remove a scheduler"""
        try:
            self.scheduler.remove_job(scheduler_id)
            logger.info(f"Removed scheduler {scheduler_id}")
        except Exception as e:
            logger.error(f"Failed to remove scheduler {scheduler_id}: {e}")
            raise
    
    def _create_trigger(self, frequency: str, frequency_config: Dict[str, Any]):
        """Create APScheduler trigger from frequency configuration"""
        if frequency == "cron":
            return CronTrigger.from_crontab(
                frequency_config["cron_expression"],
                timezone=frequency_config.get("timezone", "UTC")
            )
        elif frequency == "interval":
            return IntervalTrigger(**frequency_config)
        elif frequency == "date":
            return DateTrigger(run_date=frequency_config["run_date"])
        else:
            raise ValueError(f"Unsupported frequency type: {frequency}")
    
    async def _execute_job(self, scheduler_id: str, job_type: str):
        """Execute a scheduled job"""
        start_time = time.time()
        
        try:
            # Log job start
            if self.log_callback:
                await self.log_callback(scheduler_id, job_type, "running", "Job execution started")
            
            logger.info(f"Starting job execution: {scheduler_id} ({job_type})")
            
            # Execute the actual job based on type
            await self._execute_job_by_type(job_type, scheduler_id)
            
            # Calculate duration
            duration = int(time.time() - start_time)
            
            # Log success
            if self.log_callback:
                await self.log_callback(
                    scheduler_id, 
                    job_type, 
                    "success", 
                    "Job completed successfully", 
                    duration
                )
            
            logger.info(f"Job completed successfully: {scheduler_id} ({job_type}) in {duration}s")
            
        except Exception as e:
            duration = int(time.time() - start_time)
            error_message = f"Job failed: {str(e)}"
            
            # Log error
            if self.log_callback:
                await self.log_callback(
                    scheduler_id, 
                    job_type, 
                    "error", 
                    error_message, 
                    duration
                )
            
            logger.error(f"Job failed: {scheduler_id} ({job_type}) - {error_message}")
            raise
    
    async def _execute_job_by_type(self, job_type: str, scheduler_id: str):
        """Execute job based on its type"""
        if job_type == "email_notification":
            await self._execute_email_notification(scheduler_id)
        elif job_type == "data_backup":
            await self._execute_data_backup(scheduler_id)
        elif job_type == "report_generation":
            await self._execute_report_generation(scheduler_id)
        elif job_type == "api_call":
            await self._execute_api_call(scheduler_id)
        elif job_type == "file_cleanup":
            await self._execute_file_cleanup(scheduler_id)
        elif job_type == "custom":
            await self._execute_custom_job(scheduler_id)
        else:
            raise ValueError(f"Unknown job type: {job_type}")
    
    async def _execute_email_notification(self, scheduler_id: str):
        """Execute email notification job"""
        # Simulate email sending
        await asyncio.sleep(2)
        logger.info(f"Email notification sent for scheduler {scheduler_id}")
    
    async def _execute_data_backup(self, scheduler_id: str):
        """Execute data backup job"""
        # Simulate data backup process
        await asyncio.sleep(5)
        logger.info(f"Data backup completed for scheduler {scheduler_id}")
    
    async def _execute_report_generation(self, scheduler_id: str):
        """Execute report generation job"""
        # Simulate report generation
        await asyncio.sleep(10)
        logger.info(f"Report generated for scheduler {scheduler_id}")
    
    async def _execute_api_call(self, scheduler_id: str):
        """Execute API call job"""
        # Simulate API call
        try:
            async with httpx.AsyncClient() as client:
                response = await client.get("https://httpbin.org/uuid", timeout=30)
                response.raise_for_status()
                logger.info(f"API call successful for scheduler {scheduler_id}: {response.json()}")
        except Exception as e:
            logger.error(f"API call failed for scheduler {scheduler_id}: {e}")
            raise
    
    async def _execute_file_cleanup(self, scheduler_id: str):
        """Execute file cleanup job"""
        # Simulate file cleanup
        await asyncio.sleep(3)
        logger.info(f"File cleanup completed for scheduler {scheduler_id}")
    
    async def _execute_custom_job(self, scheduler_id: str):
        """Execute custom job"""
        # Simulate custom job execution
        await asyncio.sleep(1)
        logger.info(f"Custom job executed for scheduler {scheduler_id}")
