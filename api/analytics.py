"""
Advanced Analytics System for RAGFlow Enterprise
Provides usage analytics, performance metrics, and custom reports
"""
from typing import List, Dict, Any, Optional
from datetime import datetime, timedelta
from collections import defaultdict
from dataclasses import dataclass, asdict
import json


@dataclass
class UsageMetric:
    """Usage metric data point"""
    timestamp: str
    tenant_id: str
    metric_name: str
    value: float
    metadata: Dict[str, Any]


@dataclass
class PerformanceMetric:
    """Performance metric data point"""
    timestamp: str
    service: str
    endpoint: str
    response_time_ms: float
    status_code: int
    error: Optional[str]


class AnalyticsEngine:
    """Core analytics engine"""
    
    def __init__(self):
        self.usage_metrics: List[UsageMetric] = []
        self.performance_metrics: List[PerformanceMetric] = []
        self.aggregations: Dict[str, Dict[str, Any]] = defaultdict(dict)
    
    def track_usage(
        self,
        tenant_id: str,
        metric_name: str,
        value: float,
        metadata: Optional[Dict[str, Any]] = None
    ):
        """Track usage metric"""
        metric = UsageMetric(
            timestamp=datetime.now().isoformat(),
            tenant_id=tenant_id,
            metric_name=metric_name,
            value=value,
            metadata=metadata or {}
        )
        self.usage_metrics.append(metric)
    
    def track_performance(
        self,
        service: str,
        endpoint: str,
        response_time_ms: float,
        status_code: int,
        error: Optional[str] = None
    ):
        """Track performance metric"""
        metric = PerformanceMetric(
            timestamp=datetime.now().isoformat(),
            service=service,
            endpoint=endpoint,
            response_time_ms=response_time_ms,
            status_code=status_code,
            error=error
        )
        self.performance_metrics.append(metric)
    
    def get_usage_summary(
        self,
        tenant_id: Optional[str] = None,
        start_date: Optional[str] = None,
        end_date: Optional[str] = None,
        metric_name: Optional[str] = None
    ) -> Dict[str, Any]:
        """Get usage summary"""
        metrics = self.usage_metrics
        
        # Filter by tenant
        if tenant_id:
            metrics = [m for m in metrics if m.tenant_id == tenant_id]
        
        # Filter by date range
        if start_date:
            start = datetime.fromisoformat(start_date)
            metrics = [m for m in metrics if datetime.fromisoformat(m.timestamp) >= start]
        
        if end_date:
            end = datetime.fromisoformat(end_date)
            metrics = [m for m in metrics if datetime.fromisoformat(m.timestamp) <= end]
        
        # Filter by metric name
        if metric_name:
            metrics = [m for m in metrics if m.metric_name == metric_name]
        
        # Calculate summary
        if not metrics:
            return {
                'total_metrics': 0,
                'unique_tenants': 0,
                'metric_types': [],
                'total_value': 0,
            }
        
        unique_tenants = set(m.tenant_id for m in metrics)
        metric_types = set(m.metric_name for m in metrics)
        total_value = sum(m.value for m in metrics)
        
        # Group by metric name
        by_metric = defaultdict(list)
        for m in metrics:
            by_metric[m.metric_name].append(m.value)
        
        metric_stats = {
            name: {
                'count': len(values),
                'sum': sum(values),
                'avg': sum(values) / len(values),
                'min': min(values),
                'max': max(values),
            }
            for name, values in by_metric.items()
        }
        
        return {
            'total_metrics': len(metrics),
            'unique_tenants': len(unique_tenants),
            'metric_types': list(metric_types),
            'total_value': total_value,
            'by_metric': metric_stats,
            'period': {
                'start': metrics[0].timestamp if metrics else None,
                'end': metrics[-1].timestamp if metrics else None,
            }
        }
    
    def get_performance_summary(
        self,
        service: Optional[str] = None,
        start_date: Optional[str] = None,
        end_date: Optional[str] = None
    ) -> Dict[str, Any]:
        """Get performance summary"""
        metrics = self.performance_metrics
        
        # Filter by service
        if service:
            metrics = [m for m in metrics if m.service == service]
        
        # Filter by date range
        if start_date:
            start = datetime.fromisoformat(start_date)
            metrics = [m for m in metrics if datetime.fromisoformat(m.timestamp) >= start]
        
        if end_date:
            end = datetime.fromisoformat(end_date)
            metrics = [m for m in metrics if datetime.fromisoformat(m.timestamp) <= end]
        
        if not metrics:
            return {
                'total_requests': 0,
                'avg_response_time': 0,
                'error_rate': 0,
            }
        
        # Calculate statistics
        response_times = [m.response_time_ms for m in metrics]
        errors = [m for m in metrics if m.error or m.status_code >= 400]
        
        # Group by endpoint
        by_endpoint = defaultdict(list)
        for m in metrics:
            by_endpoint[m.endpoint].append(m)
        
        endpoint_stats = {}
        for endpoint, endpoint_metrics in by_endpoint.items():
            times = [m.response_time_ms for m in endpoint_metrics]
            endpoint_errors = [m for m in endpoint_metrics if m.error or m.status_code >= 400]
            
            endpoint_stats[endpoint] = {
                'count': len(endpoint_metrics),
                'avg_response_time': sum(times) / len(times),
                'min_response_time': min(times),
                'max_response_time': max(times),
                'p95_response_time': sorted(times)[int(len(times) * 0.95)] if len(times) > 1 else times[0],
                'error_count': len(endpoint_errors),
                'error_rate': len(endpoint_errors) / len(endpoint_metrics) * 100,
            }
        
        return {
            'total_requests': len(metrics),
            'avg_response_time': sum(response_times) / len(response_times),
            'min_response_time': min(response_times),
            'max_response_time': max(response_times),
            'p95_response_time': sorted(response_times)[int(len(response_times) * 0.95)] if len(response_times) > 1 else response_times[0],
            'error_count': len(errors),
            'error_rate': len(errors) / len(metrics) * 100,
            'by_endpoint': endpoint_stats,
            'period': {
                'start': metrics[0].timestamp if metrics else None,
                'end': metrics[-1].timestamp if metrics else None,
            }
        }
    
    def get_time_series(
        self,
        tenant_id: Optional[str] = None,
        metric_name: Optional[str] = None,
        interval: str = 'hour',  # hour, day, week, month
        start_date: Optional[str] = None,
        end_date: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """Get time series data"""
        metrics = self.usage_metrics
        
        # Filter
        if tenant_id:
            metrics = [m for m in metrics if m.tenant_id == tenant_id]
        
        if metric_name:
            metrics = [m for m in metrics if m.metric_name == metric_name]
        
        if start_date:
            start = datetime.fromisoformat(start_date)
            metrics = [m for m in metrics if datetime.fromisoformat(m.timestamp) >= start]
        
        if end_date:
            end = datetime.fromisoformat(end_date)
            metrics = [m for m in metrics if datetime.fromisoformat(m.timestamp) <= end]
        
        # Group by interval
        interval_map = {
            'hour': lambda dt: dt.strftime('%Y-%m-%d %H:00'),
            'day': lambda dt: dt.strftime('%Y-%m-%d'),
            'week': lambda dt: dt.strftime('%Y-W%W'),
            'month': lambda dt: dt.strftime('%Y-%m'),
        }
        
        group_func = interval_map.get(interval, interval_map['day'])
        
        grouped = defaultdict(list)
        for m in metrics:
            dt = datetime.fromisoformat(m.timestamp)
            key = group_func(dt)
            grouped[key].append(m.value)
        
        # Calculate aggregations
        result = []
        for period, values in sorted(grouped.items()):
            result.append({
                'period': period,
                'count': len(values),
                'sum': sum(values),
                'avg': sum(values) / len(values),
                'min': min(values),
                'max': max(values),
            })
        
        return result


class ReportBuilder:
    """Custom report builder"""
    
    def __init__(self, analytics_engine: AnalyticsEngine):
        self.engine = analytics_engine
        self.templates: Dict[str, Dict[str, Any]] = {}
    
    def create_template(
        self,
        template_id: str,
        name: str,
        description: str,
        metrics: List[str],
        filters: Dict[str, Any],
        schedule: Optional[str] = None
    ):
        """Create report template"""
        self.templates[template_id] = {
            'template_id': template_id,
            'name': name,
            'description': description,
            'metrics': metrics,
            'filters': filters,
            'schedule': schedule,
            'created_at': datetime.now().isoformat(),
        }
    
    def generate_report(
        self,
        template_id: str,
        start_date: Optional[str] = None,
        end_date: Optional[str] = None,
        format: str = 'json'  # json, csv, pdf
    ) -> Dict[str, Any]:
        """Generate report from template"""
        template = self.templates.get(template_id)
        if not template:
            raise ValueError(f"Template {template_id} not found")
        
        # Get data for each metric
        report_data = {
            'report_id': f"report_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
            'template_id': template_id,
            'template_name': template['name'],
            'generated_at': datetime.now().isoformat(),
            'period': {
                'start': start_date,
                'end': end_date,
            },
            'sections': []
        }
        
        for metric_name in template['metrics']:
            # Get usage summary for this metric
            summary = self.engine.get_usage_summary(
                metric_name=metric_name,
                start_date=start_date,
                end_date=end_date,
                **template['filters']
            )
            
            # Get time series
            time_series = self.engine.get_time_series(
                metric_name=metric_name,
                start_date=start_date,
                end_date=end_date,
                **template['filters']
            )
            
            report_data['sections'].append({
                'metric': metric_name,
                'summary': summary,
                'time_series': time_series,
            })
        
        # Format based on output format
        if format == 'json':
            return report_data
        elif format == 'csv':
            return self._format_csv(report_data)
        elif format == 'pdf':
            return self._format_pdf(report_data)
        
        return report_data
    
    def _format_csv(self, report_data: Dict[str, Any]) -> str:
        """Format report as CSV"""
        lines = []
        lines.append(f"Report: {report_data['template_name']}")
        lines.append(f"Generated: {report_data['generated_at']}")
        lines.append(f"Period: {report_data['period']['start']} to {report_data['period']['end']}")
        lines.append("")
        
        for section in report_data['sections']:
            lines.append(f"Metric: {section['metric']}")
            lines.append("Period,Count,Sum,Avg,Min,Max")
            
            for data_point in section['time_series']:
                lines.append(
                    f"{data_point['period']},"
                    f"{data_point['count']},"
                    f"{data_point['sum']},"
                    f"{data_point['avg']:.2f},"
                    f"{data_point['min']},"
                    f"{data_point['max']}"
                )
            lines.append("")
        
        return "\n".join(lines)
    
    def _format_pdf(self, report_data: Dict[str, Any]) -> Dict[str, Any]:
        """Format report as PDF metadata (actual PDF generation would use library)"""
        return {
            'format': 'pdf',
            'title': report_data['template_name'],
            'data': report_data,
            'note': 'PDF generation requires additional library (e.g., ReportLab)'
        }
    
    def list_templates(self) -> List[Dict[str, Any]]:
        """List all report templates"""
        return list(self.templates.values())
    
    def delete_template(self, template_id: str) -> bool:
        """Delete report template"""
        if template_id in self.templates:
            del self.templates[template_id]
            return True
        return False


class DashboardBuilder:
    """Dashboard widget builder"""
    
    def __init__(self, analytics_engine: AnalyticsEngine):
        self.engine = analytics_engine
        self.dashboards: Dict[str, Dict[str, Any]] = {}
    
    def create_dashboard(
        self,
        dashboard_id: str,
        name: str,
        description: str,
        widgets: List[Dict[str, Any]],
        layout: Dict[str, Any],
        tenant_id: Optional[str] = None
    ):
        """Create custom dashboard"""
        self.dashboards[dashboard_id] = {
            'dashboard_id': dashboard_id,
            'name': name,
            'description': description,
            'widgets': widgets,
            'layout': layout,
            'tenant_id': tenant_id,
            'created_at': datetime.now().isoformat(),
        }
    
    def get_dashboard_data(
        self,
        dashboard_id: str,
        start_date: Optional[str] = None,
        end_date: Optional[str] = None
    ) -> Dict[str, Any]:
        """Get data for dashboard widgets"""
        dashboard = self.dashboards.get(dashboard_id)
        if not dashboard:
            raise ValueError(f"Dashboard {dashboard_id} not found")
        
        widget_data = []
        
        for widget in dashboard['widgets']:
            widget_type = widget['type']
            config = widget['config']
            
            if widget_type == 'metric':
                # Single metric widget
                data = self.engine.get_usage_summary(
                    tenant_id=dashboard.get('tenant_id'),
                    metric_name=config.get('metric_name'),
                    start_date=start_date,
                    end_date=end_date
                )
            
            elif widget_type == 'chart':
                # Time series chart
                data = self.engine.get_time_series(
                    tenant_id=dashboard.get('tenant_id'),
                    metric_name=config.get('metric_name'),
                    interval=config.get('interval', 'day'),
                    start_date=start_date,
                    end_date=end_date
                )
            
            elif widget_type == 'performance':
                # Performance widget
                data = self.engine.get_performance_summary(
                    service=config.get('service'),
                    start_date=start_date,
                    end_date=end_date
                )
            
            else:
                data = {'error': f'Unknown widget type: {widget_type}'}
            
            widget_data.append({
                'widget_id': widget['widget_id'],
                'title': widget['title'],
                'type': widget_type,
                'data': data,
            })
        
        return {
            'dashboard_id': dashboard_id,
            'name': dashboard['name'],
            'widgets': widget_data,
            'layout': dashboard['layout'],
        }
    
    def list_dashboards(self, tenant_id: Optional[str] = None) -> List[Dict[str, Any]]:
        """List dashboards"""
        dashboards = list(self.dashboards.values())
        
        if tenant_id:
            dashboards = [d for d in dashboards if d.get('tenant_id') == tenant_id]
        
        return dashboards
    
    def delete_dashboard(self, dashboard_id: str) -> bool:
        """Delete dashboard"""
        if dashboard_id in self.dashboards:
            del self.dashboards[dashboard_id]
            return True
        return False


# Global instances
analytics_engine = AnalyticsEngine()
report_builder = ReportBuilder(analytics_engine)
dashboard_builder = DashboardBuilder(analytics_engine)
