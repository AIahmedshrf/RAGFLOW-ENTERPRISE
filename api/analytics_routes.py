"""
Analytics API Routes
Provides endpoints for analytics, reporting, and dashboards
"""
from flask import Blueprint, request
from api.analytics import analytics_engine, report_builder, dashboard_builder
from api.security import require_api_key, rate_limit


analytics_bp = Blueprint('analytics', __name__, url_prefix='/api/v1/analytics')


# Usage Analytics
@analytics_bp.route('/usage/track', methods=['POST'])
@require_api_key
@rate_limit('basic')
def track_usage():
    """Track usage metric"""
    try:
        data = request.get_json()
        
        analytics_engine.track_usage(
            tenant_id=data['tenant_id'],
            metric_name=data['metric_name'],
            value=data['value'],
            metadata=data.get('metadata', {})
        )
        
        return {'success': True, 'message': 'Metric tracked'}
    except Exception as e:
        return {'error': str(e), 'code': 400}, 400


@analytics_bp.route('/usage/summary', methods=['GET'])
@require_api_key
@rate_limit('basic')
def get_usage_summary():
    """Get usage summary"""
    try:
        tenant_id = request.args.get('tenant_id')
        start_date = request.args.get('start_date')
        end_date = request.args.get('end_date')
        metric_name = request.args.get('metric_name')
        
        summary = analytics_engine.get_usage_summary(
            tenant_id=tenant_id,
            start_date=start_date,
            end_date=end_date,
            metric_name=metric_name
        )
        
        return {
            'success': True,
            'summary': summary
        }
    except Exception as e:
        return {'error': str(e), 'code': 400}, 400


@analytics_bp.route('/usage/timeseries', methods=['GET'])
@require_api_key
@rate_limit('basic')
def get_time_series():
    """Get time series data"""
    try:
        tenant_id = request.args.get('tenant_id')
        metric_name = request.args.get('metric_name')
        interval = request.args.get('interval', 'day')
        start_date = request.args.get('start_date')
        end_date = request.args.get('end_date')
        
        time_series = analytics_engine.get_time_series(
            tenant_id=tenant_id,
            metric_name=metric_name,
            interval=interval,
            start_date=start_date,
            end_date=end_date
        )
        
        return {
            'success': True,
            'time_series': time_series,
            'total_points': len(time_series)
        }
    except Exception as e:
        return {'error': str(e), 'code': 400}, 400


# Performance Analytics
@analytics_bp.route('/performance/track', methods=['POST'])
@require_api_key
@rate_limit('basic')
def track_performance():
    """Track performance metric"""
    try:
        data = request.get_json()
        
        analytics_engine.track_performance(
            service=data['service'],
            endpoint=data['endpoint'],
            response_time_ms=data['response_time_ms'],
            status_code=data['status_code'],
            error=data.get('error')
        )
        
        return {'success': True, 'message': 'Performance tracked'}
    except Exception as e:
        return {'error': str(e), 'code': 400}, 400


@analytics_bp.route('/performance/summary', methods=['GET'])
@require_api_key
@rate_limit('basic')
def get_performance_summary():
    """Get performance summary"""
    try:
        service = request.args.get('service')
        start_date = request.args.get('start_date')
        end_date = request.args.get('end_date')
        
        summary = analytics_engine.get_performance_summary(
            service=service,
            start_date=start_date,
            end_date=end_date
        )
        
        return {
            'success': True,
            'summary': summary
        }
    except Exception as e:
        return {'error': str(e), 'code': 400}, 400


# Report Management
@analytics_bp.route('/reports/templates', methods=['POST'])
@require_api_key
@rate_limit('professional')
def create_report_template():
    """Create report template"""
    try:
        data = request.get_json()
        
        report_builder.create_template(
            template_id=data['template_id'],
            name=data['name'],
            description=data['description'],
            metrics=data['metrics'],
            filters=data.get('filters', {}),
            schedule=data.get('schedule')
        )
        
        return {
            'success': True,
            'message': 'Report template created',
            'template_id': data['template_id']
        }, 201
    except Exception as e:
        return {'error': str(e), 'code': 400}, 400


@analytics_bp.route('/reports/templates', methods=['GET'])
@require_api_key
@rate_limit('basic')
def list_report_templates():
    """List report templates"""
    templates = report_builder.list_templates()
    
    return {
        'success': True,
        'templates': templates,
        'total': len(templates)
    }


@analytics_bp.route('/reports/templates/<template_id>', methods=['DELETE'])
@require_api_key
@rate_limit('professional')
def delete_report_template(template_id):
    """Delete report template"""
    success = report_builder.delete_template(template_id)
    
    if not success:
        return {'error': 'Template not found', 'code': 404}, 404
    
    return {'success': True, 'message': 'Template deleted'}


@analytics_bp.route('/reports/generate', methods=['POST'])
@require_api_key
@rate_limit('professional')
def generate_report():
    """Generate report from template"""
    try:
        data = request.get_json()
        
        report = report_builder.generate_report(
            template_id=data['template_id'],
            start_date=data.get('start_date'),
            end_date=data.get('end_date'),
            format=data.get('format', 'json')
        )
        
        return {
            'success': True,
            'report': report
        }
    except Exception as e:
        return {'error': str(e), 'code': 400}, 400


# Dashboard Management
@analytics_bp.route('/dashboards', methods=['POST'])
@require_api_key
@rate_limit('professional')
def create_dashboard():
    """Create custom dashboard"""
    try:
        data = request.get_json()
        
        dashboard_builder.create_dashboard(
            dashboard_id=data['dashboard_id'],
            name=data['name'],
            description=data['description'],
            widgets=data['widgets'],
            layout=data['layout'],
            tenant_id=data.get('tenant_id')
        )
        
        return {
            'success': True,
            'message': 'Dashboard created',
            'dashboard_id': data['dashboard_id']
        }, 201
    except Exception as e:
        return {'error': str(e), 'code': 400}, 400


@analytics_bp.route('/dashboards', methods=['GET'])
@require_api_key
@rate_limit('basic')
def list_dashboards():
    """List dashboards"""
    tenant_id = request.args.get('tenant_id')
    
    dashboards = dashboard_builder.list_dashboards(tenant_id)
    
    return {
        'success': True,
        'dashboards': dashboards,
        'total': len(dashboards)
    }


@analytics_bp.route('/dashboards/<dashboard_id>', methods=['GET'])
@require_api_key
@rate_limit('basic')
def get_dashboard_data(dashboard_id):
    """Get dashboard data"""
    try:
        start_date = request.args.get('start_date')
        end_date = request.args.get('end_date')
        
        data = dashboard_builder.get_dashboard_data(
            dashboard_id=dashboard_id,
            start_date=start_date,
            end_date=end_date
        )
        
        return {
            'success': True,
            'dashboard': data
        }
    except Exception as e:
        return {'error': str(e), 'code': 400}, 400


@analytics_bp.route('/dashboards/<dashboard_id>', methods=['DELETE'])
@require_api_key
@rate_limit('professional')
def delete_dashboard(dashboard_id):
    """Delete dashboard"""
    success = dashboard_builder.delete_dashboard(dashboard_id)
    
    if not success:
        return {'error': 'Dashboard not found', 'code': 404}, 404
    
    return {'success': True, 'message': 'Dashboard deleted'}


# Export functionality
@analytics_bp.route('/export/usage', methods=['POST'])
@require_api_key
@rate_limit('professional')
def export_usage_data():
    """Export usage data"""
    try:
        data = request.get_json()
        
        summary = analytics_engine.get_usage_summary(
            tenant_id=data.get('tenant_id'),
            start_date=data.get('start_date'),
            end_date=data.get('end_date'),
            metric_name=data.get('metric_name')
        )
        
        time_series = analytics_engine.get_time_series(
            tenant_id=data.get('tenant_id'),
            metric_name=data.get('metric_name'),
            interval=data.get('interval', 'day'),
            start_date=data.get('start_date'),
            end_date=data.get('end_date')
        )
        
        export_format = data.get('format', 'json')
        
        if export_format == 'csv':
            # Format as CSV
            lines = ['Period,Count,Sum,Average,Min,Max']
            for point in time_series:
                lines.append(
                    f"{point['period']},"
                    f"{point['count']},"
                    f"{point['sum']},"
                    f"{point['avg']:.2f},"
                    f"{point['min']},"
                    f"{point['max']}"
                )
            
            return {
                'success': True,
                'format': 'csv',
                'data': '\n'.join(lines)
            }
        
        else:
            # JSON format
            return {
                'success': True,
                'format': 'json',
                'summary': summary,
                'time_series': time_series
            }
    
    except Exception as e:
        return {'error': str(e), 'code': 400}, 400
