"""
Bulk operations API endpoints for user management
"""
from flask import request
from admin.server.routes import admin_bp
from admin.server.auth import check_admin_auth
from admin.server.responses import success_response, error_response
from admin.server.services import UserMgr
from api.common.exceptions import AdminException


@admin_bp.route('/users/bulk/create', methods=['POST'])
@check_admin_auth
def bulk_create_users():
    """Create multiple users at once"""
    try:
        if not request.json or 'users' not in request.json:
            return error_response('Users list is required', 400)
        
        users_data = request.json['users']
        results = {
            'success': [],
            'failed': [],
        }
        
        for user_data in users_data:
            try:
                email = user_data.get('email')
                password = user_data.get('password')
                role = user_data.get('role', 'user')
                
                if not email or not password:
                    results['failed'].append({
                        'email': email or 'unknown',
                        'error': 'Email and password are required'
                    })
                    continue
                
                UserMgr.create_user(email, password, role)
                results['success'].append(email)
                
            except AdminException as e:
                results['failed'].append({
                    'email': email,
                    'error': str(e)
                })
            except Exception as e:
                results['failed'].append({
                    'email': email,
                    'error': str(e)
                })
        
        return success_response(results)
        
    except Exception as e:
        return error_response(str(e), 500)


@admin_bp.route('/users/bulk/delete', methods=['POST'])
@check_admin_auth
def bulk_delete_users():
    """Delete multiple users at once"""
    try:
        if not request.json or 'emails' not in request.json:
            return error_response('Emails list is required', 400)
        
        emails = request.json['emails']
        results = {
            'success': [],
            'failed': [],
        }
        
        for email in emails:
            try:
                UserMgr.delete_user(email)
                results['success'].append(email)
            except Exception as e:
                results['failed'].append({
                    'email': email,
                    'error': str(e)
                })
        
        return success_response(results)
        
    except Exception as e:
        return error_response(str(e), 500)


@admin_bp.route('/users/bulk/activate', methods=['POST'])
@check_admin_auth
def bulk_activate_users():
    """Activate/deactivate multiple users at once"""
    try:
        if not request.json or 'emails' not in request.json or 'status' not in request.json:
            return error_response('Emails list and status are required', 400)
        
        emails = request.json['emails']
        status = request.json['status']  # 'on' or 'off'
        
        if status not in ['on', 'off']:
            return error_response('Status must be "on" or "off"', 400)
        
        results = {
            'success': [],
            'failed': [],
        }
        
        for email in emails:
            try:
                UserMgr.update_user_status(email, status)
                results['success'].append(email)
            except Exception as e:
                results['failed'].append({
                    'email': email,
                    'error': str(e)
                })
        
        return success_response(results)
        
    except Exception as e:
        return error_response(str(e), 500)


@admin_bp.route('/users/export', methods=['GET'])
@check_admin_auth
def export_users():
    """Export users list as CSV"""
    try:
        import csv
        import io
        from flask import make_response
        
        users = UserMgr.get_all_users()
        
        # Create CSV in memory
        output = io.StringIO()
        writer = csv.writer(output)
        
        # Write header
        writer.writerow(['Email', 'Nickname', 'Is Active', 'Is Superuser', 'Create Date'])
        
        # Write data
        for user in users:
            writer.writerow([
                user['email'],
                user.get('nickname', ''),
                'Yes' if user.get('is_active') else 'No',
                'Yes' if user.get('is_superuser') else 'No',
                user.get('create_date', ''),
            ])
        
        # Create response
        output.seek(0)
        response = make_response(output.getvalue())
        response.headers['Content-Type'] = 'text/csv'
        response.headers['Content-Disposition'] = 'attachment; filename=users_export.csv'
        
        return response
        
    except Exception as e:
        return error_response(str(e), 500)


@admin_bp.route('/users/import', methods=['POST'])
@check_admin_auth
def import_users():
    """Import users from CSV file"""
    try:
        if 'file' not in request.files:
            return error_response('No file provided', 400)
        
        file = request.files['file']
        
        if file.filename == '':
            return error_response('No file selected', 400)
        
        if not file.filename.endswith('.csv'):
            return error_response('File must be a CSV', 400)
        
        # Read CSV
        import csv
        import io
        
        stream = io.StringIO(file.stream.read().decode("UTF8"), newline=None)
        csv_reader = csv.DictReader(stream)
        
        results = {
            'success': [],
            'failed': [],
        }
        
        for row in csv_reader:
            try:
                email = row.get('Email', '').strip()
                password = row.get('Password', '').strip()
                role = row.get('Role', 'user').strip().lower()
                
                if not email or not password:
                    results['failed'].append({
                        'email': email or 'unknown',
                        'error': 'Email and password are required'
                    })
                    continue
                
                UserMgr.create_user(email, password, role)
                results['success'].append(email)
                
            except AdminException as e:
                results['failed'].append({
                    'email': email,
                    'error': str(e)
                })
            except Exception as e:
                results['failed'].append({
                    'email': email,
                    'error': str(e)
                })
        
        return success_response(results)
        
    except Exception as e:
        return error_response(str(e), 500)
