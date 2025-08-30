import React, { useMemo } from 'react';
import { ResponsiveHeatMap } from '@nivo/heatmap';
import { AcousticIndex } from '../../data/mockData';

interface CorrelationMatrixProps {
  data: AcousticIndex[];
}

export function CorrelationMatrix({ data }: CorrelationMatrixProps) {
  const correlationData = useMemo(() => {
    const indices = ['aci', 'adi', 'aei', 'bi', 'ndsi'];
    const indexNames = {
      aci: 'ACI',
      adi: 'ADI', 
      aei: 'AEI',
      bi: 'BI',
      ndsi: 'NDSI'
    };

    // Calculate correlation matrix
    const matrix: { [key: string]: { [key: string]: number } } = {};
    
    indices.forEach(index1 => {
      matrix[index1] = {};
      indices.forEach(index2 => {
        if (index1 === index2) {
          matrix[index1][index2] = 1;
        } else {
          // Calculate Pearson correlation coefficient
          const values1 = data.map(d => d[index1 as keyof AcousticIndex] as number).filter(v => typeof v === 'number');
          const values2 = data.map(d => d[index2 as keyof AcousticIndex] as number).filter(v => typeof v === 'number');
          
          const mean1 = values1.reduce((sum, val) => sum + val, 0) / values1.length;
          const mean2 = values2.reduce((sum, val) => sum + val, 0) / values2.length;
          
          let numerator = 0;
          let sumSq1 = 0;
          let sumSq2 = 0;
          
          for (let i = 0; i < Math.min(values1.length, values2.length); i++) {
            const diff1 = values1[i] - mean1;
            const diff2 = values2[i] - mean2;
            numerator += diff1 * diff2;
            sumSq1 += diff1 * diff1;
            sumSq2 += diff2 * diff2;
          }
          
          const correlation = numerator / Math.sqrt(sumSq1 * sumSq2);
          matrix[index1][index2] = isNaN(correlation) ? 0 : correlation;
        }
      });
    });

    // Convert to Nivo format
    return indices.map(rowIndex => ({
      id: indexNames[rowIndex as keyof typeof indexNames],
      data: indices.map(colIndex => ({
        x: indexNames[colIndex as keyof typeof indexNames],
        y: matrix[rowIndex][colIndex]
      }))
    }));
  }, [data]);

  return (
    <div className="h-96">
      <ResponsiveHeatMap
        data={correlationData}
        margin={{ top: 60, right: 90, bottom: 60, left: 90 }}
        valueFormat=">-.2f"
        axisTop={{
          tickSize: 5,
          tickPadding: 5,
          tickRotation: -45,
          legend: '',
          legendOffset: 46
        }}
        axisRight={null}
        axisBottom={{
          tickSize: 5,
          tickPadding: 5,
          tickRotation: -45,
          legend: '',
          legendOffset: 46
        }}
        axisLeft={{
          tickSize: 5,
          tickPadding: 5,
          tickRotation: 0,
          legend: '',
          legendOffset: -72
        }}
        colors={{
          type: 'diverging',
          scheme: 'red_yellow_blue',
          divergeAt: 0.5,
          minValue: -1,
          maxValue: 1
        }}
        emptyColor="#555555"
        borderColor={{
          from: 'color',
          modifiers: [['darker', 0.4]]
        }}
        labelTextColor={{
          from: 'color',
          modifiers: [['darker', 1.8]]
        }}
        legends={[
          {
            anchor: 'bottom',
            translateX: 0,
            translateY: 30,
            length: 400,
            thickness: 8,
            direction: 'row',
            tickPosition: 'after',
            tickSize: 3,
            tickSpacing: 4,
            tickOverlap: false,
            title: 'Correlation Coefficient →',
            titleAlign: 'start',
            titleOffset: 4
          }
        ]}
        theme={{
          labels: {
            text: {
              fontSize: 12,
              fill: '#374151'
            }
          },
          legends: [
            {
              text: {
                fontSize: 12,
                fill: '#374151'
              }
            }
          ],
          tooltip: {
            container: {
              background: 'white',
              color: '#374151',
              fontSize: '12px',
              borderRadius: '8px',
              boxShadow: '0 4px 6px -1px rgba(0, 0, 0, 0.1)',
              border: '1px solid #e5e7eb'
            }
          }
        }}
        tooltip={({ cell }) => (
          <div className="bg-white p-3 border rounded-lg shadow-lg">
            <div className="font-semibold">Correlation Analysis</div>
            <div className="text-sm text-muted-foreground mt-1">
              {cell.serieId} ↔ {cell.data.x}
            </div>
            <div className="text-sm mt-1">
              Correlation: <span className={`font-semibold ${
                cell.value > 0.7 ? 'text-green-600' : 
                cell.value > 0.3 ? 'text-blue-600' :
                cell.value < -0.3 ? 'text-red-600' : 'text-gray-600'
              }`}>
                {cell.formattedValue}
              </span>
            </div>
            <div className="text-xs text-muted-foreground mt-1">
              {cell.value > 0.7 ? 'Strong positive correlation' :
               cell.value > 0.3 ? 'Moderate positive correlation' :
               cell.value < -0.7 ? 'Strong negative correlation' :
               cell.value < -0.3 ? 'Moderate negative correlation' :
               'Weak correlation'}
            </div>
          </div>
        )}
      />
    </div>
  );
}