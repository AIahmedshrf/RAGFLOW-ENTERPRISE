import { Table, Tag, Button, Space, Modal, Form, Input, message } from 'antd';
import { PlusOutlined, CheckCircleOutlined, RollbackOutlined } from '@ant-design/icons';
import { useState } from 'react';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { getModelVersions, createModelVersion, activateVersion, rollbackVersion } from '@/services/model-service';

interface ModelVersionsProps {
  modelId: string;
}

export const ModelVersions: React.FC<ModelVersionsProps> = ({ modelId }) => {
  const [isModalVisible, setIsModalVisible] = useState(false);
  const [form] = Form.useForm();
  const queryClient = useQueryClient();

  const { data, isLoading } = useQuery({
    queryKey: ['model-versions', modelId],
    queryFn: () => getModelVersions(modelId),
  });

  const createMutation = useMutation({
    mutationFn: (versionData: any) => createModelVersion(modelId, versionData),
    onSuccess: () => {
      message.success('Version created successfully');
      queryClient.invalidateQueries({ queryKey: ['model-versions', modelId] });
      setIsModalVisible(false);
      form.resetFields();
    },
  });

  const activateMutation = useMutation({
    mutationFn: (versionId: number) => activateVersion(modelId, versionId),
    onSuccess: () => {
      message.success('Version activated');
      queryClient.invalidateQueries({ queryKey: ['model-versions', modelId] });
    },
  });

  const rollbackMutation = useMutation({
    mutationFn: () => rollbackVersion(modelId),
    onSuccess: () => {
      message.success('Rolled back to previous version');
      queryClient.invalidateQueries({ queryKey: ['model-versions', modelId] });
    },
  });

  const columns = [
    {
      title: 'Version',
      dataIndex: 'version',
      key: 'version',
    },
    {
      title: 'Description',
      dataIndex: 'description',
      key: 'description',
    },
    {
      title: 'Status',
      dataIndex: 'is_active',
      key: 'is_active',
      render: (isActive: boolean) => (
        <Tag color={isActive ? 'green' : 'default'}>
          {isActive ? 'Active' : 'Inactive'}
        </Tag>
      ),
    },
    {
      title: 'Created',
      dataIndex: 'created_at',
      key: 'created_at',
      render: (date: string) => new Date(date).toLocaleString(),
    },
    {
      title: 'Created By',
      dataIndex: 'created_by',
      key: 'created_by',
    },
    {
      title: 'Actions',
      key: 'actions',
      render: (_: any, record: any) => (
        <Space>
          {!record.is_active && (
            <Button
              icon={<CheckCircleOutlined />}
              size="small"
              onClick={() => activateMutation.mutate(record.id)}
            >
              Activate
            </Button>
          )}
        </Space>
      ),
    },
  ];

  const versions = data?.data?.versions || [];

  return (
    <Space direction="vertical" style={{ width: '100%' }} size="large">
      <Space>
        <Button
          type="primary"
          icon={<PlusOutlined />}
          onClick={() => setIsModalVisible(true)}
        >
          Create Version
        </Button>
        <Button
          icon={<RollbackOutlined />}
          onClick={() => rollbackMutation.mutate()}
          disabled={versions.length < 2}
        >
          Rollback
        </Button>
      </Space>

      <Table
        columns={columns}
        dataSource={versions}
        rowKey="id"
        loading={isLoading}
        pagination={false}
      />

      <Modal
        title="Create New Version"
        open={isModalVisible}
        onCancel={() => {
          setIsModalVisible(false);
          form.resetFields();
        }}
        footer={null}
      >
        <Form
          form={form}
          layout="vertical"
          onFinish={(values) => createMutation.mutate(values)}
        >
          <Form.Item
            name="version"
            label="Version"
            rules={[{ required: true, message: 'Please enter version' }]}
          >
            <Input placeholder="e.g., 1.0.0" />
          </Form.Item>

          <Form.Item
            name="description"
            label="Description"
            rules={[{ required: true, message: 'Please enter description' }]}
          >
            <Input.TextArea rows={3} placeholder="What changed in this version?" />
          </Form.Item>

          <Form.Item
            name="created_by"
            label="Created By"
            initialValue="admin"
          >
            <Input />
          </Form.Item>

          <Form.Item>
            <Space>
              <Button type="primary" htmlType="submit" loading={createMutation.isPending}>
                Create
              </Button>
              <Button onClick={() => {
                setIsModalVisible(false);
                form.resetFields();
              }}>
                Cancel
              </Button>
            </Space>
          </Form.Item>
        </Form>
      </Modal>
    </Space>
  );
};
