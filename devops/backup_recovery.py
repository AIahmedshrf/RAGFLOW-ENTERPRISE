"""
Automated Backup and Recovery System for RAGFlow Enterprise
Handles database, file storage, and configuration backups
"""
import subprocess
import shutil
import os
import tarfile
from datetime import datetime, timedelta
from typing import List, Dict, Any, Optional
import json
import logging


logger = logging.getLogger(__name__)


class BackupManager:
    """Manages backup operations"""
    
    def __init__(
        self,
        backup_dir: str = "/backups",
        retention_days: int = 30
    ):
        self.backup_dir = backup_dir
        self.retention_days = retention_days
        self.backups: Dict[str, Dict[str, Any]] = {}
        
        os.makedirs(backup_dir, exist_ok=True)
    
    def create_mysql_backup(
        self,
        host: str = "localhost",
        port: int = 3306,
        user: str = "root",
        password: str = "infini_rag_flow",
        database: str = "rag_flow"
    ) -> str:
        """Create MySQL database backup"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        backup_file = os.path.join(
            self.backup_dir,
            f"mysql_backup_{timestamp}.sql.gz"
        )
        
        # Create mysqldump command
        cmd = [
            "mysqldump",
            f"--host={host}",
            f"--port={port}",
            f"--user={user}",
            f"--password={password}",
            "--single-transaction",
            "--routines",
            "--triggers",
            "--events",
            database
        ]
        
        try:
            # Execute mysqldump and compress
            with open(backup_file, 'wb') as f:
                dump_process = subprocess.Popen(
                    cmd,
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE
                )
                
                gzip_process = subprocess.Popen(
                    ["gzip"],
                    stdin=dump_process.stdout,
                    stdout=f,
                    stderr=subprocess.PIPE
                )
                
                dump_process.stdout.close()
                gzip_process.communicate()
            
            # Get file size
            size = os.path.getsize(backup_file)
            
            # Record backup
            backup_id = f"mysql_{timestamp}"
            self.backups[backup_id] = {
                'backup_id': backup_id,
                'type': 'mysql',
                'file': backup_file,
                'size': size,
                'timestamp': timestamp,
                'status': 'completed'
            }
            
            logger.info(f"MySQL backup created: {backup_file} ({size} bytes)")
            return backup_id
        
        except Exception as e:
            logger.error(f"MySQL backup failed: {e}")
            raise
    
    def create_minio_backup(
        self,
        endpoint: str = "localhost:9000",
        access_key: str = "minioadmin",
        secret_key: str = "minioadmin",
        bucket: str = "ragflow"
    ) -> str:
        """Create MinIO file storage backup"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        backup_dir = os.path.join(
            self.backup_dir,
            f"minio_backup_{timestamp}"
        )
        backup_file = f"{backup_dir}.tar.gz"
        
        try:
            # Create temporary directory for backup
            os.makedirs(backup_dir, exist_ok=True)
            
            # Use mc (MinIO client) to mirror bucket
            cmd = [
                "mc",
                "mirror",
                f"{endpoint}/{bucket}",
                backup_dir
            ]
            
            env = os.environ.copy()
            env['MC_HOST_local'] = f"http://{access_key}:{secret_key}@{endpoint}"
            
            subprocess.run(cmd, check=True, env=env)
            
            # Create tar.gz archive
            with tarfile.open(backup_file, "w:gz") as tar:
                tar.add(backup_dir, arcname=os.path.basename(backup_dir))
            
            # Remove temporary directory
            shutil.rmtree(backup_dir)
            
            # Get file size
            size = os.path.getsize(backup_file)
            
            # Record backup
            backup_id = f"minio_{timestamp}"
            self.backups[backup_id] = {
                'backup_id': backup_id,
                'type': 'minio',
                'file': backup_file,
                'size': size,
                'timestamp': timestamp,
                'status': 'completed'
            }
            
            logger.info(f"MinIO backup created: {backup_file} ({size} bytes)")
            return backup_id
        
        except Exception as e:
            logger.error(f"MinIO backup failed: {e}")
            raise
    
    def create_elasticsearch_backup(
        self,
        host: str = "localhost",
        port: int = 9200,
        index: str = "ragflow"
    ) -> str:
        """Create Elasticsearch index backup"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        backup_file = os.path.join(
            self.backup_dir,
            f"elasticsearch_backup_{timestamp}.json"
        )
        
        try:
            # Use elasticdump to backup index
            cmd = [
                "elasticdump",
                f"--input=http://{host}:{port}/{index}",
                f"--output={backup_file}",
                "--type=data"
            ]
            
            subprocess.run(cmd, check=True)
            
            # Get file size
            size = os.path.getsize(backup_file)
            
            # Record backup
            backup_id = f"elasticsearch_{timestamp}"
            self.backups[backup_id] = {
                'backup_id': backup_id,
                'type': 'elasticsearch',
                'file': backup_file,
                'size': size,
                'timestamp': timestamp,
                'status': 'completed'
            }
            
            logger.info(f"Elasticsearch backup created: {backup_file} ({size} bytes)")
            return backup_id
        
        except Exception as e:
            logger.error(f"Elasticsearch backup failed: {e}")
            raise
    
    def create_full_backup(self) -> Dict[str, str]:
        """Create full system backup"""
        logger.info("Starting full backup...")
        
        backup_ids = {
            'mysql': self.create_mysql_backup(),
            'minio': self.create_minio_backup(),
            'elasticsearch': self.create_elasticsearch_backup()
        }
        
        logger.info(f"Full backup completed: {backup_ids}")
        return backup_ids
    
    def restore_mysql_backup(
        self,
        backup_id: str,
        host: str = "localhost",
        port: int = 3306,
        user: str = "root",
        password: str = "infini_rag_flow",
        database: str = "rag_flow"
    ):
        """Restore MySQL database from backup"""
        backup = self.backups.get(backup_id)
        if not backup or backup['type'] != 'mysql':
            raise ValueError(f"MySQL backup {backup_id} not found")
        
        backup_file = backup['file']
        
        try:
            # Decompress and restore
            cmd = f"gunzip < {backup_file} | mysql -h {host} -P {port} -u {user} -p{password} {database}"
            
            subprocess.run(cmd, shell=True, check=True)
            
            logger.info(f"MySQL backup restored: {backup_id}")
        
        except Exception as e:
            logger.error(f"MySQL restore failed: {e}")
            raise
    
    def restore_minio_backup(
        self,
        backup_id: str,
        endpoint: str = "localhost:9000",
        access_key: str = "minioadmin",
        secret_key: str = "minioadmin",
        bucket: str = "ragflow"
    ):
        """Restore MinIO file storage from backup"""
        backup = self.backups.get(backup_id)
        if not backup or backup['type'] != 'minio':
            raise ValueError(f"MinIO backup {backup_id} not found")
        
        backup_file = backup['file']
        restore_dir = os.path.join(self.backup_dir, "restore_temp")
        
        try:
            # Extract archive
            with tarfile.open(backup_file, "r:gz") as tar:
                tar.extractall(restore_dir)
            
            # Use mc to restore
            cmd = [
                "mc",
                "mirror",
                restore_dir,
                f"{endpoint}/{bucket}"
            ]
            
            env = os.environ.copy()
            env['MC_HOST_local'] = f"http://{access_key}:{secret_key}@{endpoint}"
            
            subprocess.run(cmd, check=True, env=env)
            
            # Cleanup
            shutil.rmtree(restore_dir)
            
            logger.info(f"MinIO backup restored: {backup_id}")
        
        except Exception as e:
            logger.error(f"MinIO restore failed: {e}")
            raise
    
    def restore_elasticsearch_backup(
        self,
        backup_id: str,
        host: str = "localhost",
        port: int = 9200,
        index: str = "ragflow"
    ):
        """Restore Elasticsearch index from backup"""
        backup = self.backups.get(backup_id)
        if not backup or backup['type'] != 'elasticsearch':
            raise ValueError(f"Elasticsearch backup {backup_id} not found")
        
        backup_file = backup['file']
        
        try:
            # Use elasticdump to restore
            cmd = [
                "elasticdump",
                f"--input={backup_file}",
                f"--output=http://{host}:{port}/{index}",
                "--type=data"
            ]
            
            subprocess.run(cmd, check=True)
            
            logger.info(f"Elasticsearch backup restored: {backup_id}")
        
        except Exception as e:
            logger.error(f"Elasticsearch restore failed: {e}")
            raise
    
    def cleanup_old_backups(self):
        """Remove backups older than retention period"""
        cutoff_date = datetime.now() - timedelta(days=self.retention_days)
        
        removed_count = 0
        for backup_id, backup in list(self.backups.items()):
            backup_date = datetime.strptime(backup['timestamp'], "%Y%m%d_%H%M%S")
            
            if backup_date < cutoff_date:
                # Remove file
                if os.path.exists(backup['file']):
                    os.remove(backup['file'])
                
                # Remove from registry
                del self.backups[backup_id]
                removed_count += 1
                
                logger.info(f"Removed old backup: {backup_id}")
        
        logger.info(f"Cleanup completed: {removed_count} backups removed")
        return removed_count
    
    def list_backups(
        self,
        backup_type: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """List available backups"""
        backups = list(self.backups.values())
        
        if backup_type:
            backups = [b for b in backups if b['type'] == backup_type]
        
        return sorted(backups, key=lambda x: x['timestamp'], reverse=True)
    
    def get_backup_info(self, backup_id: str) -> Optional[Dict[str, Any]]:
        """Get backup information"""
        return self.backups.get(backup_id)


class ScheduledBackup:
    """Scheduled backup execution"""
    
    def __init__(self, backup_manager: BackupManager):
        self.backup_manager = backup_manager
        self.schedules: Dict[str, Dict[str, Any]] = {}
    
    def create_schedule(
        self,
        schedule_id: str,
        backup_type: str,  # full, mysql, minio, elasticsearch
        cron_expression: str,  # e.g., "0 2 * * *" for 2 AM daily
        retention_days: int = 30
    ):
        """Create backup schedule"""
        self.schedules[schedule_id] = {
            'schedule_id': schedule_id,
            'backup_type': backup_type,
            'cron_expression': cron_expression,
            'retention_days': retention_days,
            'last_run': None,
            'next_run': None,
            'enabled': True
        }
    
    def execute_scheduled_backup(self, schedule_id: str):
        """Execute scheduled backup"""
        schedule = self.schedules.get(schedule_id)
        if not schedule or not schedule['enabled']:
            return
        
        backup_type = schedule['backup_type']
        
        try:
            if backup_type == 'full':
                backup_ids = self.backup_manager.create_full_backup()
            elif backup_type == 'mysql':
                backup_ids = {'mysql': self.backup_manager.create_mysql_backup()}
            elif backup_type == 'minio':
                backup_ids = {'minio': self.backup_manager.create_minio_backup()}
            elif backup_type == 'elasticsearch':
                backup_ids = {'elasticsearch': self.backup_manager.create_elasticsearch_backup()}
            else:
                raise ValueError(f"Unknown backup type: {backup_type}")
            
            schedule['last_run'] = datetime.now().isoformat()
            
            logger.info(f"Scheduled backup completed: {schedule_id} -> {backup_ids}")
            
            # Cleanup old backups
            self.backup_manager.cleanup_old_backups()
        
        except Exception as e:
            logger.error(f"Scheduled backup failed: {schedule_id} - {e}")
    
    def list_schedules(self) -> List[Dict[str, Any]]:
        """List backup schedules"""
        return list(self.schedules.values())


# Global instance
backup_manager = BackupManager()
scheduled_backup = ScheduledBackup(backup_manager)
