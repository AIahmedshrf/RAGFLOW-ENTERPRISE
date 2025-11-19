import { Table, Tag, Button, Space } from 'antd';
import { useQuery } from '@tanstack/react-query';
import { getBenchmarks } from '@/services/model-service';
import { Line } from '@ant-design/plots';

interface ModelBenchmarkProps {
  modelId: string;
}

export const ModelBenchmark: React.FC<ModelBenchmarkProps> = ({ modelId }) => {
  const { data, isLoading } = useQuery({
    queryKey: ['benchmarks', modelId],
    queryFn: () => getBenchmarks(modelId),
    refetchInterval: 5000, // Refresh every 5s
  });

  const benchmarks = data?.data?.benchmarks || [];

  const columns = [
    {
      title: 'Test Type',
      dataIndex: 'test_type',
      key: 'test_type',
      render: (type: string) => <Tag color="blue">{type}</Tag>,
    },
    {
      title: 'Status',
      dataIndex: 'status',
      key: 'status',
      render: (status: string) => {
        const colors: Record<string, string> = {
          running: 'processing',
          completed: 'success',
          failed: 'error',
        };
        return <Tag color={colors[status] || 'default'}>{status}</Tag>;
      },
    },
    {
      title: 'Results',
      dataIndex: 'results',
      key: 'results',
      render: (results: any, record: any) => {
        if (record.status !== 'completed' || !results) return '-';
        
        if (record.test_type === 'latency') {
          return `Avg: ${results.avg_latency_ms?.toFixed(2)}ms`;
        } else if (record.test_type === 'quality') {
          return `Score: ${(results.overall_score * 100)?.toFixed(1)}%`;
        } else if (record.test_type === 'throughput') {
          return `${results.requests_per_second?.toFixed(1)} req/s`;
        }
        return '-';
      },
    },
    {
      title: 'Timestamp',
      dataIndex: 'timestamp',
      key: 'timestamp',
      render: (date: string) => new Date(date).toLocaleString(),
    },
  ];

  // Chart data for latency trends
  const latencyData = benchmarks
    .filter((b: any) => b.test_type === 'latency' && b.status === 'completed')
    .map((b: any) => ({
      timestamp: new Date(b.timestamp).toLocaleTimeString(),
      latency: b.results?.avg_latency_ms || 0,
    }));

  return (
    <Space direction="vertical" style={{ width: '100%' }} size="large">
      <Table
        columns={columns}
        dataSource={benchmarks}
        rowKey="id"
        loading={isLoading}
        pagination={{ pageSize: 10 }}
      />

      {latencyData.length > 0 && (
        <div>
          <h4>Latency Trend</h4>
          <Line
            data={latencyData}
            xField="timestamp"
            yField="latency"
            height={300}
            smooth
          />
        </div>
      )}
    </Space>
  );
};
