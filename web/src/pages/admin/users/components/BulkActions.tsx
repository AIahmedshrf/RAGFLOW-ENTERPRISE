import { Button, Dropdown, Modal, message, Space } from 'antd';
import { DownOutlined, DeleteOutlined, CheckCircleOutlined, StopOutlined } from '@ant-design/icons';
import type { MenuProps } from 'antd';
import { useState } from 'react';

interface BulkActionsProps {
  selectedUsers: string[];
  onBulkAction: (action: string, users: string[]) => Promise<void>;
  onClearSelection: () => void;
}

export const BulkActions: React.FC<BulkActionsProps> = ({
  selectedUsers,
  onBulkAction,
  onClearSelection,
}) => {
  const [isLoading, setIsLoading] = useState(false);

  const handleAction = async (action: string) => {
    const actionNames: Record<string, string> = {
      activate: 'activate',
      deactivate: 'deactivate',
      delete: 'delete',
    };

    Modal.confirm({
      title: `Confirm ${actionNames[action]}`,
      content: `Are you sure you want to ${actionNames[action]} ${selectedUsers.length} user(s)?`,
      onOk: async () => {
        setIsLoading(true);
        try {
          await onBulkAction(action, selectedUsers);
          message.success(`Successfully ${actionNames[action]}d ${selectedUsers.length} user(s)`);
          onClearSelection();
        } catch (error) {
          message.error(`Failed to ${actionNames[action]} users: ${error}`);
        } finally {
          setIsLoading(false);
        }
      },
    });
  };

  const items: MenuProps['items'] = [
    {
      key: 'activate',
      label: 'Activate Users',
      icon: <CheckCircleOutlined />,
      onClick: () => handleAction('activate'),
    },
    {
      key: 'deactivate',
      label: 'Deactivate Users',
      icon: <StopOutlined />,
      onClick: () => handleAction('deactivate'),
    },
    {
      type: 'divider',
    },
    {
      key: 'delete',
      label: 'Delete Users',
      icon: <DeleteOutlined />,
      danger: true,
      onClick: () => handleAction('delete'),
    },
  ];

  if (selectedUsers.length === 0) {
    return null;
  }

  return (
    <Space>
      <span>{selectedUsers.length} user(s) selected</span>
      <Dropdown menu={{ items }} disabled={isLoading}>
        <Button>
          Bulk Actions <DownOutlined />
        </Button>
      </Dropdown>
      <Button onClick={onClearSelection}>Clear Selection</Button>
    </Space>
  );
};
