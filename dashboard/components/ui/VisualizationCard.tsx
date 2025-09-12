import React from 'react';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { LucideIcon, Loader2 } from 'lucide-react';

interface VisualizationCardProps {
  title: string;
  description: string;
  icon: LucideIcon;
  loading?: boolean;
  error?: Error | null;
  children: React.ReactNode;
  className?: string;
  iconColor?: string;
}

export default function VisualizationCard({
  title,
  description,
  icon: Icon,
  loading = false,
  error = null,
  children,
  className = '',
  iconColor = 'text-primary'
}: VisualizationCardProps) {
  return (
    <Card className={className}>
      <CardHeader>
        <div className="flex items-center gap-3">
          <div className="p-2 bg-primary/10 rounded-lg">
            <Icon className={`h-6 w-6 ${iconColor}`} />
          </div>
          <div>
            <CardTitle>{title}</CardTitle>
            <CardDescription>{description}</CardDescription>
          </div>
        </div>
      </CardHeader>
      <CardContent>
        {loading && (
          <div className="flex items-center justify-center py-12">
            <Loader2 className="h-8 w-8 animate-spin text-primary" />
            <span className="ml-2 text-muted-foreground">Loading data...</span>
          </div>
        )}
        
        {error && (
          <div className="text-center py-12">
            <div className="text-red-600 mb-2">Error loading data</div>
            <div className="text-sm text-muted-foreground">{error.message}</div>
          </div>
        )}
        
        {!loading && !error && children}
        
        {!loading && !error && !children && (
          <div className="text-center py-12 text-muted-foreground">
            No data available
          </div>
        )}
      </CardContent>
    </Card>
  );
}