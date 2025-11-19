import { Input, Select, DatePicker, Button, Space } from 'antd';
import { SearchOutlined, FilterOutlined, ClearOutlined } from '@ant-design/icons';
import { useState } from 'react';
import styles from './UserFilters.less';

const { RangePicker } = DatePicker;

interface UserFiltersProps {
  onFilter: (filters: FilterValues) => void;
  onReset: () => void;
}

export interface FilterValues {
  search?: string;
  role?: string;
  status?: string;
  dateRange?: [string, string];
}

export const UserFilters: React.FC<UserFiltersProps> = ({ onFilter, onReset }) => {
  const [filters, setFilters] = useState<FilterValues>({});

  const handleFilterChange = (key: keyof FilterValues, value: any) => {
    const newFilters = { ...filters, [key]: value };
    setFilters(newFilters);
    onFilter(newFilters);
  };

  const handleReset = () => {
    setFilters({});
    onReset();
  };

  return (
    <div className={styles.userFilters}>
      <Space size="middle" wrap>
        <Input
          placeholder="Search by email or nickname"
          prefix={<SearchOutlined />}
          value={filters.search}
          onChange={(e) => handleFilterChange('search', e.target.value)}
          style={{ width: 250 }}
          allowClear
        />
        
        <Select
          placeholder="Filter by role"
          value={filters.role}
          onChange={(value) => handleFilterChange('role', value)}
          style={{ width: 150 }}
          allowClear
        >
          <Select.Option value="admin">Admin</Select.Option>
          <Select.Option value="user">User</Select.Option>
        </Select>
        
        <Select
          placeholder="Filter by status"
          value={filters.status}
          onChange={(value) => handleFilterChange('status', value)}
          style={{ width: 150 }}
          allowClear
        >
          <Select.Option value="active">Active</Select.Option>
          <Select.Option value="inactive">Inactive</Select.Option>
        </Select>
        
        <RangePicker
          onChange={(dates, dateStrings) => 
            handleFilterChange('dateRange', dateStrings)
          }
          style={{ width: 280 }}
        />
        
        <Button
          icon={<ClearOutlined />}
          onClick={handleReset}
        >
          Clear Filters
        </Button>
      </Space>
    </div>
  );
};
