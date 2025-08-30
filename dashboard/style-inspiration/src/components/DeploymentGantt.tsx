import React, { useState } from 'react';
import { deploymentSchedule, DeploymentSchedule } from '../data/mockData';
import { Badge } from './ui/badge';

export function DeploymentGantt() {
  const [hoveredDeployment, setHoveredDeployment] = useState<string | null>(null);

  // Calculate date range for the chart
  const allDates = deploymentSchedule.flatMap(d => [new Date(d.startDate), new Date(d.endDate)]);
  const minDate = new Date(Math.min(...allDates.map(d => d.getTime())));
  const maxDate = new Date(Math.max(...allDates.map(d => d.getTime())));
  
  // Extend the range slightly for better visualization
  minDate.setMonth(minDate.getMonth() - 1);
  maxDate.setMonth(maxDate.getMonth() + 1);

  const totalDays = Math.ceil((maxDate.getTime() - minDate.getTime()) / (1000 * 60 * 60 * 24));

  const dateToPosition = (date: Date) => {
    const days = Math.ceil((date.getTime() - minDate.getTime()) / (1000 * 60 * 60 * 24));
    return (days / totalDays) * 100;
  };

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'completed': return 'bg-blue-500';
      case 'active': return 'bg-green-500';
      case 'planned': return 'bg-gray-400';
      default: return 'bg-gray-400';
    }
  };

  const formatDate = (dateString: string) => {
    return new Date(dateString).toLocaleDateString('en-US', { 
      month: 'short', 
      day: 'numeric',
      year: '2-digit'
    });
  };

  // Generate month markers
  const generateMonthMarkers = () => {
    const markers = [];
    const current = new Date(minDate);
    current.setDate(1); // First day of month
    
    while (current <= maxDate) {
      const position = dateToPosition(current);
      markers.push({
        date: new Date(current),
        position,
        label: current.toLocaleDateString('en-US', { month: 'short', year: '2-digit' })
      });
      current.setMonth(current.getMonth() + 1);
    }
    
    return markers;
  };

  const monthMarkers = generateMonthMarkers();

  return (
    <div className="space-y-4">
      {/* Timeline header */}
      <div className="relative">
        <div className="flex text-xs text-muted-foreground border-b pb-2">
          {monthMarkers.map((marker, index) => (
            <div
              key={index}
              className="absolute transform -translate-x-1/2"
              style={{ left: `${marker.position}%` }}
            >
              {marker.label}
            </div>
          ))}
        </div>
      </div>

      {/* Gantt bars */}
      <div className="space-y-3 pt-4">
        {deploymentSchedule.map((deployment) => {
          const startPos = dateToPosition(new Date(deployment.startDate));
          const endPos = dateToPosition(new Date(deployment.endDate));
          const width = endPos - startPos;
          const isHovered = hoveredDeployment === deployment.id;

          return (
            <div key={deployment.id} className="relative">
              {/* Instrument label */}
              <div className="flex items-center mb-1">
                <div className="w-32 text-sm font-medium truncate">
                  {deployment.instrumentName}
                </div>
                <div className="text-xs text-muted-foreground ml-2">
                  {deployment.instrumentId}
                </div>
              </div>

              {/* Timeline track */}
              <div className="relative h-8 bg-gray-100 rounded">
                {/* Month grid lines */}
                {monthMarkers.map((marker, index) => (
                  <div
                    key={index}
                    className="absolute top-0 bottom-0 w-px bg-gray-300 opacity-30"
                    style={{ left: `${marker.position}%` }}
                  />
                ))}

                {/* Deployment bar */}
                <div
                  className={`absolute top-1 bottom-1 rounded transition-all duration-200 cursor-pointer ${
                    getStatusColor(deployment.status)
                  } ${isHovered ? 'opacity-90 shadow-md' : 'opacity-80'}`}
                  style={{
                    left: `${startPos}%`,
                    width: `${width}%`,
                    minWidth: '2px'
                  }}
                  onMouseEnter={() => setHoveredDeployment(deployment.id)}
                  onMouseLeave={() => setHoveredDeployment(null)}
                >
                  {/* Status badge on the bar */}
                  {width > 15 && ( // Only show if bar is wide enough
                    <div className="absolute inset-0 flex items-center justify-center">
                      <Badge 
                        variant="secondary" 
                        className="text-xs bg-white/20 text-white border-white/30 hover:bg-white/20"
                      >
                        {deployment.status}
                      </Badge>
                    </div>
                  )}
                </div>

                {/* Hover tooltip */}
                {isHovered && (
                  <div className="absolute -top-20 left-1/2 transform -translate-x-1/2 bg-white p-3 rounded-lg shadow-lg border text-xs z-10">
                    <div className="font-semibold">{deployment.purpose}</div>
                    <div className="text-muted-foreground space-y-1 mt-1">
                      <div>Start: {formatDate(deployment.startDate)}</div>
                      <div>End: {formatDate(deployment.endDate)}</div>
                      <div>Data: {deployment.dataCollected} MB</div>
                      <div>Status: <span className="capitalize">{deployment.status}</span></div>
                    </div>
                  </div>
                )}
              </div>

              {/* Deployment info */}
              <div className="flex justify-between items-center mt-1 text-xs text-muted-foreground">
                <span>{formatDate(deployment.startDate)}</span>
                <span className="truncate max-w-32 mx-2">{deployment.purpose}</span>
                <span>{formatDate(deployment.endDate)}</span>
              </div>
            </div>
          );
        })}
      </div>

      {/* Legend */}
      <div className="flex gap-4 pt-4 border-t text-xs">
        <div className="flex items-center gap-2">
          <div className="w-3 h-3 bg-blue-500 rounded"></div>
          <span>Completed</span>
        </div>
        <div className="flex items-center gap-2">
          <div className="w-3 h-3 bg-green-500 rounded"></div>
          <span>Active</span>
        </div>
        <div className="flex items-center gap-2">
          <div className="w-3 h-3 bg-gray-400 rounded"></div>
          <span>Planned</span>
        </div>
      </div>
    </div>
  );
}