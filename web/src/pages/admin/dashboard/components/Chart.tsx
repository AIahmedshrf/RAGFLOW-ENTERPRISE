import { Line, Pie } from '@ant-design/plots';

interface ChartProps {
  type: 'line' | 'pie';
  data: any[];
  xField?: string;
  yField?: string;
  angleField?: string;
  colorField?: string;
}

export const Chart: React.FC<ChartProps> = ({
  type,
  data,
  xField,
  yField,
  angleField,
  colorField,
}) => {
  if (type === 'line') {
    const config = {
      data,
      xField: xField || 'x',
      yField: yField || 'y',
      smooth: true,
      animation: {
        appear: {
          animation: 'path-in',
          duration: 1000,
        },
      },
      point: {
        size: 5,
        shape: 'circle',
      },
      xAxis: {
        label: {
          autoRotate: true,
        },
      },
    };

    return <Line {...config} />;
  }

  if (type === 'pie') {
    const config = {
      data,
      angleField: angleField || 'value',
      colorField: colorField || 'category',
      radius: 0.8,
      innerRadius: 0.6,
      label: {
        type: 'spider',
        labelHeight: 28,
        content: '{name}\n{percentage}',
      },
      interactions: [
        {
          type: 'element-selected',
        },
        {
          type: 'element-active',
        },
      ],
      statistic: {
        title: false,
        content: {
          style: {
            whiteSpace: 'pre-wrap',
            overflow: 'hidden',
            textOverflow: 'ellipsis',
          },
          content: 'Total',
        },
      },
    };

    return <Pie {...config} />;
  }

  return null;
};
