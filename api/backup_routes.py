"""
Backup and Recovery API Routes
"""
from flask import Blueprint, request
from devops.backup_recovery import backup_manager, scheduled_backup
from api.security import require_api_key, rate_limit


backup_bp = Blueprint('backup', __name__, url_prefix='/api/v1/backup')


@backup_bp.route('/create', methods=['POST'])
@require_api_key
@rate_limit('professional')
def create_backup():
    """Create backup"""
    try:
        data = request.get_json()
        backup_type = data.get('type', 'full')
        
        if backup_type == 'full':
            backup_ids = backup_manager.create_full_backup()
        elif backup_type == 'mysql':
            backup_ids = {'mysql': backup_manager.create_mysql_backup()}
        elif backup_type == 'minio':
            backup_ids = {'minio': backup_manager.create_minio_backup()}
        elif backup_type == 'elasticsearch':
            backup_ids = {'elasticsearch': backup_manager.create_elasticsearch_backup()}
        else:
            return {'error': f'Unknown backup type: {backup_type}', 'code': 400}, 400
        
        return {
            'success': True,
            'backup_ids': backup_ids,
            'type': backup_type
        }, 201
    except Exception as e:
        return {'error': str(e), 'code': 500}, 500


@backup_bp.route('/list', methods=['GET'])
@require_api_key
@rate_limit('basic')
def list_backups():
    """List backups"""
    backup_type = request.args.get('type')
    
    backups = backup_manager.list_backups(backup_type)
    
    return {
        'success': True,
        'backups': backups,
        'total': len(backups)
    }


@backup_bp.route('/<backup_id>', methods=['GET'])
@require_api_key
@rate_limit('basic')
def get_backup_info(backup_id):
    """Get backup information"""
    backup = backup_manager.get_backup_info(backup_id)
    
    if not backup:
        return {'error': 'Backup not found', 'code': 404}, 404
    
    return {
        'success': True,
        'backup': backup
    }


@backup_bp.route('/restore', methods=['POST'])
@require_api_key
@rate_limit('professional')
def restore_backup():
    """Restore from backup"""
    try:
        data = request.get_json()
        backup_id = data['backup_id']
        backup_type = data.get('type')
        
        backup = backup_manager.get_backup_info(backup_id)
        if not backup:
            return {'error': 'Backup not found', 'code': 404}, 404
        
        if not backup_type:
            backup_type = backup['type']
        
        if backup_type == 'mysql':
            backup_manager.restore_mysql_backup(backup_id)
        elif backup_type == 'minio':
            backup_manager.restore_minio_backup(backup_id)
        elif backup_type == 'elasticsearch':
            backup_manager.restore_elasticsearch_backup(backup_id)
        else:
            return {'error': f'Unknown backup type: {backup_type}', 'code': 400}, 400
        
        return {
            'success': True,
            'message': 'Backup restored successfully',
            'backup_id': backup_id
        }
    except Exception as e:
        return {'error': str(e), 'code': 500}, 500


@backup_bp.route('/cleanup', methods=['POST'])
@require_api_key
@rate_limit('professional')
def cleanup_old_backups():
    """Cleanup old backups"""
    try:
        removed_count = backup_manager.cleanup_old_backups()
        
        return {
            'success': True,
            'removed_count': removed_count
        }
    except Exception as e:
        return {'error': str(e), 'code': 500}, 500


@backup_bp.route('/schedules', methods=['POST'])
@require_api_key
@rate_limit('professional')
def create_backup_schedule():
    """Create backup schedule"""
    try:
        data = request.get_json()
        
        scheduled_backup.create_schedule(
            schedule_id=data['schedule_id'],
            backup_type=data['backup_type'],
            cron_expression=data['cron_expression'],
            retention_days=data.get('retention_days', 30)
        )
        
        return {
            'success': True,
            'message': 'Backup schedule created',
            'schedule_id': data['schedule_id']
        }, 201
    except Exception as e:
        return {'error': str(e), 'code': 400}, 400


@backup_bp.route('/schedules', methods=['GET'])
@require_api_key
@rate_limit('basic')
def list_backup_schedules():
    """List backup schedules"""
    schedules = scheduled_backup.list_schedules()
    
    return {
        'success': True,
        'schedules': schedules,
        'total': len(schedules)
    }


@backup_bp.route('/schedules/<schedule_id>/execute', methods=['POST'])
@require_api_key
@rate_limit('professional')
def execute_backup_schedule(schedule_id):
    """Execute backup schedule manually"""
    try:
        scheduled_backup.execute_scheduled_backup(schedule_id)
        
        return {
            'success': True,
            'message': 'Backup schedule executed'
        }
    except Exception as e:
        return {'error': str(e), 'code': 500}, 500
