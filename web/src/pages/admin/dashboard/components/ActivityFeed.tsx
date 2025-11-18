import { List, Avatar, Tag } from 'antd';
import {
  UserAddOutlined,
  FileAddOutlined,
  MessageOutlined,
  SettingOutlined,
  DeleteOutlined,
} from '@ant-design/icons';
import { formatDistanceToNow } from 'date-fns';
import styles from './ActivityFeed.less';

interface Activity {
  id: string;
  type: 'user_created' | 'document_uploaded' | 'conversation' | 'settings_changed' | 'user_deleted';
  user: string;
  description: string;
  timestamp: string;
}

interface ActivityFeedProps {
  activities: Activity[];
}

const getActivityIcon = (type: string) => {
  const iconMap: Record<string, React.ReactNode> = {
    user_created: <UserAddOutlined style={{ color: '#52c41a' }} />,
    document_uploaded: <FileAddOutlined style={{ color: '#1890ff' }} />,
    conversation: <MessageOutlined style={{ color: '#722ed1' }} />,
    settings_changed: <SettingOutlined style={{ color: '#fa8c16' }} />,
    user_deleted: <DeleteOutlined style={{ color: '#ff4d4f' }} />,
  };
  return iconMap[type] || <SettingOutlined />;
};

const getActivityColor = (type: string) => {
  const colorMap: Record<string, string> = {
    user_created: 'success',
    document_uploaded: 'processing',
    conversation: 'purple',
    settings_changed: 'warning',
    user_deleted: 'error',
  };
  return colorMap[type] || 'default';
};

export const ActivityFeed: React.FC<ActivityFeedProps> = ({ activities }) => {
  if (!activities || activities.length === 0) {
    return (
      <div className={styles.emptyState}>
        <p>No recent activities</p>
      </div>
    );
  }

  return (
    <List
      className={styles.activityFeed}
      itemLayout="horizontal"
      dataSource={activities}
      renderItem={(activity) => (
        <List.Item>
          <List.Item.Meta
            avatar={
              <Avatar icon={getActivityIcon(activity.type)} />
            }
            title={
              <div className={styles.activityTitle}>
                <span>{activity.description}</span>
                <Tag color={getActivityColor(activity.type)}>
                  {activity.type.replace('_', ' ')}
                </Tag>
              </div>
            }
            description={
              <div className={styles.activityMeta}>
                <span className={styles.user}>{activity.user}</span>
                <span className={styles.timestamp}>
                  {formatDistanceToNow(new Date(activity.timestamp), { addSuffix: true })}
                </span>
              </div>
            }
          />
        </List.Item>
      )}
    />
  );
};
