import { useState } from 'react';
import { Button, Table, Modal, Form, Input, Select, Tag, Space, Popconfirm, message } from 'antd';
import { UserAddOutlined, DeleteOutlined, EditOutlined, KeyOutlined, LockOutlined, UnlockOutlined } from '@ant-design/icons';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { listUsers, createUser, updateUserStatus, updateUserPassword, deleteUser } from '@/services/admin-service';
import type { ColumnsType } from 'antd/es/table';
import styles from './index.less';

interface User {
  email: string;
  nickname: string;
  create_date: string;
  is_active: boolean;
  is_superuser: boolean;
}

const UsersManagementEnhanced = () => {
  const queryClient = useQueryClient();
  const [isCreateModalOpen, setIsCreateModalOpen] = useState(false);
  const [isEditModalOpen, setIsEditModalOpen] = useState(false);
  const [selectedUser, setSelectedUser] = useState<User | null>(null);
  const [form] = Form.useForm();
  const [editForm] = Form.useForm();

  // Fetch users
  const { data: usersData, isLoading } = useQuery({
    queryKey: ['users'],
    queryFn: async () => (await listUsers())?.data?.data || [],
    refetchInterval: 10000,
  });

  // Create user mutation
  const createMutation = useMutation({
    mutationFn: ({ email, password }: { email: string; password: string }) => 
      createUser(email, password),
    onSuccess: () => {
      message.success('User created successfully');
      queryClient.invalidateQueries({ queryKey: ['users'] });
      setIsCreateModalOpen(false);
      form.resetFields();
    },
    onError: (error: any) => {
      message.error(error.response?.data?.message || 'Failed to create user');
    },
  });

  // Update status mutation
  const updateStatusMutation = useMutation({
    mutationFn: ({ email, status }: { email: string; status: 'on' | 'off' }) => 
      updateUserStatus(email, status),
    onSuccess: () => {
      message.success('User status updated');
      queryClient.invalidateQueries({ queryKey: ['users'] });
    },
    onError: (error: any) => {
      message.error(error.response?.data?.message || 'Failed to update status');
    },
  });

  // Update password mutation
  const updatePasswordMutation = useMutation({
    mutationFn: ({ email, password }: { email: string; password: string }) => 
      updateUserPassword(email, password),
    onSuccess: () => {
      message.success('Password updated successfully');
      setIsEditModalOpen(false);
      editForm.resetFields();
    },
    onError: (error: any) => {
      message.error(error.response?.data?.message || 'Failed to update password');
    },
  });

  // Delete user mutation
  const deleteMutation = useMutation({
    mutationFn: (email: string) => deleteUser(email),
    onSuccess: () => {
      message.success('User deleted successfully');
      queryClient.invalidateQueries({ queryKey: ['users'] });
    },
    onError: (error: any) => {
      message.error(error.response?.data?.message || 'Failed to delete user');
    },
  });

  const columns: ColumnsType<User> = [
    {
      title: 'Email',
      dataIndex: 'email',
      key: 'email',
      sorter: (a, b) => a.email.localeCompare(b.email),
      filterSearch: true,
    },
    {
      title: 'Nickname',
      dataIndex: 'nickname',
      key: 'nickname',
    },
    {
      title: 'Role',
      dataIndex: 'is_superuser',
      key: 'is_superuser',
      render: (is_superuser: boolean) => (
        <Tag color={is_superuser ? 'red' : 'blue'}>
          {is_superuser ? 'Admin' : 'User'}
        </Tag>
      ),
      filters: [
        { text: 'Admin', value: true },
        { text: 'User', value: false },
      ],
      onFilter: (value, record) => record.is_superuser === value,
    },
    {
      title: 'Status',
      dataIndex: 'is_active',
      key: 'is_active',
      render: (is_active: boolean) => (
        <Tag color={is_active ? 'success' : 'error'}>
          {is_active ? 'Active' : 'Inactive'}
        </Tag>
      ),
      filters: [
        { text: 'Active', value: true },
        { text: 'Inactive', value: false },
      ],
      onFilter: (value, record) => record.is_active === value,
    },
    {
      title: 'Created Date',
      dataIndex: 'create_date',
      key: 'create_date',
      sorter: (a, b) => new Date(a.create_date).getTime() - new Date(b.create_date).getTime(),
      render: (date: string) => new Date(date).toLocaleDateString(),
    },
    {
      title: 'Actions',
      key: 'actions',
      render: (_: any, record: User) => (
        <Space size="small">
          <Button
            size="small"
            icon={<KeyOutlined />}
            onClick={() => {
              setSelectedUser(record);
              setIsEditModalOpen(true);
            }}
            title="Change Password"
          />
          <Button
            size="small"
            icon={record.is_active ? <LockOutlined /> : <UnlockOutlined />}
            onClick={() => updateStatusMutation.mutate({
              email: record.email,
              status: record.is_active ? 'off' : 'on',
            })}
            title={record.is_active ? 'Deactivate' : 'Activate'}
          />
          <Popconfirm
            title="Delete User"
            description="Are you sure you want to delete this user? This action cannot be undone."
            onConfirm={() => deleteMutation.mutate(record.email)}
            okText="Yes"
            cancelText="No"
            okButtonProps={{ danger: true }}
          >
            <Button
              size="small"
              danger
              icon={<DeleteOutlined />}
              title="Delete User"
            />
          </Popconfirm>
        </Space>
      ),
    },
  ];

  return (
    <div className={styles.userManagement}>
      <div className={styles.header}>
        <h1>User Management</h1>
        <Button
          type="primary"
          icon={<UserAddOutlined />}
          onClick={() => setIsCreateModalOpen(true)}
        >
          Create User
        </Button>
      </div>

      <Table
        columns={columns}
        dataSource={usersData}
        loading={isLoading}
        rowKey="email"
        pagination={{
          pageSize: 10,
          showSizeChanger: true,
          showTotal: (total) => `Total ${total} users`,
        }}
      />

      {/* Create User Modal */}
      <Modal
        title="Create New User"
        open={isCreateModalOpen}
        onOk={() => form.submit()}
        onCancel={() => {
          setIsCreateModalOpen(false);
          form.resetFields();
        }}
        confirmLoading={createMutation.isPending}
      >
        <Form
          form={form}
          layout="vertical"
          onFinish={(values) => createMutation.mutate(values)}
        >
          <Form.Item
            name="email"
            label="Email"
            rules={[
              { required: true, message: 'Please input email' },
              { type: 'email', message: 'Please input valid email' },
            ]}
          >
            <Input placeholder="user@example.com" />
          </Form.Item>

          <Form.Item
            name="password"
            label="Password"
            rules={[
              { required: true, message: 'Please input password' },
              { min: 6, message: 'Password must be at least 6 characters' },
            ]}
          >
            <Input.Password placeholder="Enter password" />
          </Form.Item>

          <Form.Item
            name="confirmPassword"
            label="Confirm Password"
            dependencies={['password']}
            rules={[
              { required: true, message: 'Please confirm password' },
              ({ getFieldValue }) => ({
                validator(_, value) {
                  if (!value || getFieldValue('password') === value) {
                    return Promise.resolve();
                  }
                  return Promise.reject(new Error('Passwords do not match'));
                },
              }),
            ]}
          >
            <Input.Password placeholder="Confirm password" />
          </Form.Item>
        </Form>
      </Modal>

      {/* Change Password Modal */}
      <Modal
        title={`Change Password for ${selectedUser?.email}`}
        open={isEditModalOpen}
        onOk={() => editForm.submit()}
        onCancel={() => {
          setIsEditModalOpen(false);
          editForm.resetFields();
          setSelectedUser(null);
        }}
        confirmLoading={updatePasswordMutation.isPending}
      >
        <Form
          form={editForm}
          layout="vertical"
          onFinish={(values) => {
            if (selectedUser) {
              updatePasswordMutation.mutate({
                email: selectedUser.email,
                password: values.password,
              });
            }
          }}
        >
          <Form.Item
            name="password"
            label="New Password"
            rules={[
              { required: true, message: 'Please input new password' },
              { min: 6, message: 'Password must be at least 6 characters' },
            ]}
          >
            <Input.Password placeholder="Enter new password" />
          </Form.Item>

          <Form.Item
            name="confirmPassword"
            label="Confirm Password"
            dependencies={['password']}
            rules={[
              { required: true, message: 'Please confirm password' },
              ({ getFieldValue }) => ({
                validator(_, value) {
                  if (!value || getFieldValue('password') === value) {
                    return Promise.resolve();
                  }
                  return Promise.reject(new Error('Passwords do not match'));
                },
              }),
            ]}
          >
            <Input.Password placeholder="Confirm new password" />
          </Form.Item>
        </Form>
      </Modal>
    </div>
  );
};

export default UsersManagementEnhanced;
