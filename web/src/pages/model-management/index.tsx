import { Card, Table, Button, Tag, Space, Modal, Form, Input, Select, message, Tabs } from 'antd';
import { PlusOutlined, EditOutlined, DeleteOutlined, ExperimentOutlined, HistoryOutlined } from '@ant-design/icons';
import { useState } from 'react';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { getModels, registerModel, updateModel, deleteModel, runBenchmark } from '@/services/model-service';
import { ModelBenchmark } from './components/ModelBenchmark';
import { ModelVersions } from './components/ModelVersions';
import styles from './index.less';

const { TabPane } = Tabs;

const ModelManagement = () => {
  const [isModalVisible, setIsModalVisible] = useState(false);
  const [editingModel, setEditingModel] = useState<any>(null);
  const [selectedModel, setSelectedModel] = useState<any>(null);
  const [form] = Form.useForm();
  const queryClient = useQueryClient();

  const { data: modelsData, isLoading } = useQuery({
    queryKey: ['models'],
    queryFn: getModels,
  });

  const registerMutation = useMutation({
    mutationFn: registerModel,
    onSuccess: () => {
      message.success('Model registered successfully');
      queryClient.invalidateQueries({ queryKey: ['models'] });
      setIsModalVisible(false);
      form.resetFields();
    },
    onError: (error: any) => {
      message.error(`Failed to register model: ${error.message}`);
    },
  });

  const updateMutation = useMutation({
    mutationFn: ({ id, data }: { id: string; data: any }) => updateModel(id, data),
    onSuccess: () => {
      message.success('Model updated successfully');
      queryClient.invalidateQueries({ queryKey: ['models'] });
      setIsModalVisible(false);
      setEditingModel(null);
      form.resetFields();
    },
  });

  const deleteMutation = useMutation({
    mutationFn: deleteModel,
    onSuccess: () => {
      message.success('Model deleted successfully');
      queryClient.invalidateQueries({ queryKey: ['models'] });
    },
  });

  const benchmarkMutation = useMutation({
    mutationFn: ({ id, testType }: { id: string; testType: string }) => 
      runBenchmark(id, testType),
    onSuccess: () => {
      message.success('Benchmark started');
    },
  });

  const handleAdd = () => {
    setEditingModel(null);
    form.resetFields();
    setIsModalVisible(true);
  };

  const handleEdit = (model: any) => {
    setEditingModel(model);
    form.setFieldsValue(model);
    setIsModalVisible(true);
  };

  const handleDelete = (model: any) => {
    Modal.confirm({
      title: 'Delete Model',
      content: `Are you sure you want to delete ${model.name}?`,
      onOk: () => deleteMutation.mutate(model.id),
    });
  };

  const handleBenchmark = (model: any) => {
    Modal.confirm({
      title: 'Run Benchmark',
      content: (
        <div>
          <p>Select benchmark type for {model.name}:</p>
          <Select
            id="benchmark-type"
            defaultValue="latency"
            style={{ width: '100%', marginTop: 16 }}
          >
            <Select.Option value="latency">Latency Test</Select.Option>
            <Select.Option value="quality">Quality Test</Select.Option>
            <Select.Option value="throughput">Throughput Test</Select.Option>
          </Select>
        </div>
      ),
      onOk: () => {
        const testType = (document.getElementById('benchmark-type') as HTMLSelectElement)?.value || 'latency';
        benchmarkMutation.mutate({ id: model.id, testType });
      },
    });
  };

  const handleSubmit = async (values: any) => {
    if (editingModel) {
      updateMutation.mutate({ id: editingModel.id, data: values });
    } else {
      registerMutation.mutate(values);
    }
  };

  const columns = [
    {
      title: 'Name',
      dataIndex: 'name',
      key: 'name',
    },
    {
      title: 'Type',
      dataIndex: 'model_type',
      key: 'model_type',
      render: (type: string) => <Tag color="blue">{type}</Tag>,
    },
    {
      title: 'Factory',
      dataIndex: 'factory',
      key: 'factory',
    },
    {
      title: 'Status',
      dataIndex: 'status',
      key: 'status',
      render: (status: string) => (
        <Tag color={status === 'active' ? 'green' : 'red'}>
          {status}
        </Tag>
      ),
    },
    {
      title: 'Created',
      dataIndex: 'created_at',
      key: 'created_at',
      render: (date: string) => date ? new Date(date).toLocaleDateString() : '-',
    },
    {
      title: 'Actions',
      key: 'actions',
      render: (_: any, record: any) => (
        <Space>
          <Button
            icon={<EditOutlined />}
            size="small"
            onClick={() => handleEdit(record)}
          />
          <Button
            icon={<ExperimentOutlined />}
            size="small"
            onClick={() => handleBenchmark(record)}
          />
          <Button
            icon={<HistoryOutlined />}
            size="small"
            onClick={() => setSelectedModel(record)}
          />
          <Button
            icon={<DeleteOutlined />}
            size="small"
            danger
            onClick={() => handleDelete(record)}
          />
        </Space>
      ),
    },
  ];

  const models = modelsData?.data || {};
  const allModels = [
    ...(models.llm || []),
    ...(models.embedding || []),
    ...(models.rerank || []),
    ...(models.chat || []),
    ...(models.image || []),
  ];

  return (
    <div className={styles.modelManagement}>
      <Card
        title="Model Management"
        extra={
          <Button
            type="primary"
            icon={<PlusOutlined />}
            onClick={handleAdd}
          >
            Register Model
          </Button>
        }
      >
        <Tabs defaultActiveKey="all">
          <TabPane tab={`All (${allModels.length})`} key="all">
            <Table
              columns={columns}
              dataSource={allModels}
              rowKey="id"
              loading={isLoading}
            />
          </TabPane>
          <TabPane tab={`LLM (${models.llm?.length || 0})`} key="llm">
            <Table
              columns={columns}
              dataSource={models.llm || []}
              rowKey="id"
              loading={isLoading}
            />
          </TabPane>
          <TabPane tab={`Embedding (${models.embedding?.length || 0})`} key="embedding">
            <Table
              columns={columns}
              dataSource={models.embedding || []}
              rowKey="id"
              loading={isLoading}
            />
          </TabPane>
          <TabPane tab={`Rerank (${models.rerank?.length || 0})`} key="rerank">
            <Table
              columns={columns}
              dataSource={models.rerank || []}
              rowKey="id"
              loading={isLoading}
            />
          </TabPane>
        </Tabs>
      </Card>

      {/* Benchmark Panel */}
      {selectedModel && (
        <Card
          title={`Benchmark Results - ${selectedModel.name}`}
          style={{ marginTop: 16 }}
          extra={
            <Button onClick={() => setSelectedModel(null)}>Close</Button>
          }
        >
          <ModelBenchmark modelId={selectedModel.id} />
        </Card>
      )}

      {/* Version History */}
      {selectedModel && (
        <Card
          title={`Version History - ${selectedModel.name}`}
          style={{ marginTop: 16 }}
        >
          <ModelVersions modelId={selectedModel.id} />
        </Card>
      )}

      {/* Add/Edit Modal */}
      <Modal
        title={editingModel ? 'Edit Model' : 'Register Model'}
        open={isModalVisible}
        onCancel={() => {
          setIsModalVisible(false);
          setEditingModel(null);
          form.resetFields();
        }}
        footer={null}
      >
        <Form
          form={form}
          layout="vertical"
          onFinish={handleSubmit}
        >
          <Form.Item
            name="name"
            label="Model Name"
            rules={[{ required: true, message: 'Please enter model name' }]}
          >
            <Input placeholder="e.g., llama3:8b" />
          </Form.Item>

          <Form.Item
            name="model_type"
            label="Model Type"
            rules={[{ required: true, message: 'Please select model type' }]}
          >
            <Select placeholder="Select type">
              <Select.Option value="chat">Chat</Select.Option>
              <Select.Option value="embedding">Embedding</Select.Option>
              <Select.Option value="rerank">Rerank</Select.Option>
              <Select.Option value="image">Image</Select.Option>
            </Select>
          </Form.Item>

          <Form.Item
            name="factory"
            label="Factory"
            rules={[{ required: true, message: 'Please select factory' }]}
          >
            <Select placeholder="Select factory">
              <Select.Option value="Ollama">Ollama</Select.Option>
              <Select.Option value="OpenAI">OpenAI</Select.Option>
              <Select.Option value="Azure">Azure</Select.Option>
              <Select.Option value="HuggingFace">HuggingFace</Select.Option>
            </Select>
          </Form.Item>

          <Form.Item
            name="api_base"
            label="API Base URL"
          >
            <Input placeholder="https://api.example.com" />
          </Form.Item>

          <Form.Item
            name="api_key"
            label="API Key"
          >
            <Input.Password placeholder="Enter API key (optional)" />
          </Form.Item>

          <Form.Item>
            <Space>
              <Button type="primary" htmlType="submit" loading={registerMutation.isPending || updateMutation.isPending}>
                {editingModel ? 'Update' : 'Register'}
              </Button>
              <Button onClick={() => {
                setIsModalVisible(false);
                setEditingModel(null);
                form.resetFields();
              }}>
                Cancel
              </Button>
            </Space>
          </Form.Item>
        </Form>
      </Modal>
    </div>
  );
};

export default ModelManagement;
