import { Card, Col, Row, Statistic, Spin, List, Avatar, Tag } from 'antd';
import {
  UserOutlined,
  DatabaseOutlined,
  MessageOutlined,
  FileTextOutlined,
  RobotOutlined,
  CloudServerOutlined,
  UserAddOutlined,
  FileAddOutlined,
  SettingOutlined,
  DeleteOutlined,
} from '@ant-design/icons';
import { useQuery } from '@tanstack/react-query';
import { getDashboardMetrics } from '@/services/admin-service';
import styles from './index.less';

const Dashboard = () => {
  const { data: metrics, isLoading } = useQuery({
    queryKey: ['dashboardMetrics'],
    queryFn: getDashboardMetrics,
    refetchInterval: 30000, // Refresh every 30 seconds
  });

  if (isLoading) {
    return (
      <div className={styles.loadingContainer}>
        <Spin size="large" />
      </div>
    );
  }

  const metricsData: AdminService.DashboardMetrics = metrics?.data || {
    totalUsers: 0,
    activeUsers7d: 0,
    totalKnowledgeBases: 0,
    totalConversations: 0,
    activeConversations7d: 0,
    totalDocuments: 0,
    documentsProcessed7d: 0,
    activeAgents: 0,
    activeServices: 0,
    totalServices: 0,
    userActivity: [],
    apiUsage: [],
    storageUsage: [],
    recentActivities: [],
  };

  return (
    <div className={styles.dashboard}>
      <h1>Dashboard</h1>
      
      {/* Metrics Cards */}
      <Row gutter={[16, 16]}>
        <Col xs={24} sm={12} lg={8}>
          <Card>
            <Statistic
              title="Total Users"
              value={metricsData.totalUsers || 0}
              prefix={<UserOutlined />}
              valueStyle={{ color: '#3f8600' }}
            />
          </Card>
        </Col>
        
        <Col xs={24} sm={12} lg={8}>
          <Card>
            <Statistic
              title="Knowledge Bases"
              value={metricsData.totalKnowledgeBases || 0}
              prefix={<DatabaseOutlined />}
              valueStyle={{ color: '#1890ff' }}
            />
          </Card>
        </Col>
        
        <Col xs={24} sm={12} lg={8}>
          <Card>
            <Statistic
              title="Total Conversations"
              value={metricsData.totalConversations || 0}
              prefix={<MessageOutlined />}
              valueStyle={{ color: '#722ed1' }}
            />
          </Card>
        </Col>
        
        <Col xs={24} sm={12} lg={8}>
          <Card>
            <Statistic
              title="Documents Processed"
              value={metricsData.totalDocuments || 0}
              prefix={<FileTextOutlined />}
              valueStyle={{ color: '#fa8c16' }}
            />
          </Card>
        </Col>
        
        <Col xs={24} sm={12} lg={8}>
          <Card>
            <Statistic
              title="Active Agents"
              value={metricsData.activeAgents || 0}
              prefix={<RobotOutlined />}
              valueStyle={{ color: '#eb2f96' }}
            />
          </Card>
        </Col>
        
        <Col xs={24} sm={12} lg={8}>
          <Card>
            <Statistic
              title="Active Services"
              value={metricsData.activeServices || 0}
              suffix={`/ ${metricsData.totalServices || 0}`}
              prefix={<CloudServerOutlined />}
              valueStyle={{ color: metricsData.activeServices === metricsData.totalServices ? '#3f8600' : '#cf1322' }}
            />
          </Card>
        </Col>
      </Row>

      {/* Recent Activity */}
      <Row gutter={[16, 16]} style={{ marginTop: 24 }}>
        <Col xs={24}>
          <Card title="Recent Activity">
            {metricsData.recentActivities && metricsData.recentActivities.length > 0 ? (
              <List
                itemLayout="horizontal"
                dataSource={metricsData.recentActivities}
                renderItem={(activity: any) => (
                  <List.Item>
                    <List.Item.Meta
                      avatar={
                        <Avatar icon={
                          activity.type === 'user_created' ? <UserAddOutlined /> :
                          activity.type === 'document_uploaded' ? <FileAddOutlined /> :
                          activity.type === 'settings_changed' ? <SettingOutlined /> :
                          activity.type === 'user_deleted' ? <DeleteOutlined /> :
                          <MessageOutlined />
                        } />
                      }
                      title={
                        <div style={{ display: 'flex', justifyContent: 'space-between' }}>
                          <span>{activity.description}</span>
                          <Tag color={
                            activity.type === 'user_created' ? 'success' :
                            activity.type === 'document_uploaded' ? 'processing' :
                            activity.type === 'user_deleted' ? 'error' :
                            'default'
                          }>
                            {activity.type.replace('_', ' ')}
                          </Tag>
                        </div>
                      }
                      description={
                        <div style={{ display: 'flex', justifyContent: 'space-between' }}>
                          <span>{activity.user}</span>
                          <span style={{ color: '#999' }}>{activity.timestamp}</span>
                        </div>
                      }
                    />
                  </List.Item>
                )}
              />
            ) : (
              <div style={{ textAlign: 'center', padding: '40px 0', color: '#999' }}>
                No recent activities
              </div>
            )}
          </Card>
        </Col>
      </Row>
    </div>
  );
};

export default Dashboard;
