import { Button, Dropdown, message } from 'antd';
import { DownloadOutlined, FileExcelOutlined, FilePdfOutlined } from '@ant-design/icons';
import type { MenuProps } from 'antd';

interface UserExportProps {
  users: any[];
  selectedUsers?: string[];
}

export const UserExport: React.FC<UserExportProps> = ({ users, selectedUsers }) => {
  const exportToCSV = (data: any[]) => {
    const headers = ['Email', 'Nickname', 'Role', 'Status', 'Created Date', 'Last Login'];
    const csvContent = [
      headers.join(','),
      ...data.map(user => [
        user.email,
        user.nickname || '',
        user.is_superuser ? 'Admin' : 'User',
        user.is_active ? 'Active' : 'Inactive',
        user.create_date || '',
        user.last_login_time || '',
      ].join(','))
    ].join('\n');

    const blob = new Blob([csvContent], { type: 'text/csv;charset=utf-8;' });
    const link = document.createElement('a');
    link.href = URL.createObjectURL(blob);
    link.download = `users_export_${new Date().toISOString().split('T')[0]}.csv`;
    link.click();
    message.success('Users exported to CSV successfully');
  };

  const exportToJSON = (data: any[]) => {
    const jsonContent = JSON.stringify(data, null, 2);
    const blob = new Blob([jsonContent], { type: 'application/json' });
    const link = document.createElement('a');
    link.href = URL.createObjectURL(blob);
    link.download = `users_export_${new Date().toISOString().split('T')[0]}.json`;
    link.click();
    message.success('Users exported to JSON successfully');
  };

  const handleExport = (format: 'csv' | 'json') => {
    const dataToExport = selectedUsers && selectedUsers.length > 0
      ? users.filter(user => selectedUsers.includes(user.email))
      : users;

    if (dataToExport.length === 0) {
      message.warning('No users to export');
      return;
    }

    if (format === 'csv') {
      exportToCSV(dataToExport);
    } else {
      exportToJSON(dataToExport);
    }
  };

  const items: MenuProps['items'] = [
    {
      key: 'csv',
      label: 'Export as CSV',
      icon: <FileExcelOutlined />,
      onClick: () => handleExport('csv'),
    },
    {
      key: 'json',
      label: 'Export as JSON',
      icon: <FilePdfOutlined />,
      onClick: () => handleExport('json'),
    },
  ];

  return (
    <Dropdown menu={{ items }}>
      <Button icon={<DownloadOutlined />}>
        Export
      </Button>
    </Dropdown>
  );
};
