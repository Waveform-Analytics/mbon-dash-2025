'use client';

import { useState } from 'react';
import { motion } from 'framer-motion';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { useViewData } from '@/lib/data/useViewData';
import { Search, FileText, Filter, Waves } from 'lucide-react';

interface AcousticIndex {
  id: string;
  name: string;
  full_name: string;
  category: string;
  description: string;
  domain: string;
  unit?: string;
  interpretation: string;
  calculation_method?: string;
}

interface IndicesData {
  metadata: {
    generated_at: string;
    version: string;
    description: string;
  };
  summary: {
    total_indices: number;
    categories: {
      count: number;
      list: string[];
    } | string[];  // Support both old and new format
    domains?: string[];
  };
  indices: AcousticIndex[];
}

export default function IndicesPage() {
  const { data: indicesData, loading, error } = useViewData<IndicesData>('indices_reference.json');
  const [searchTerm, setSearchTerm] = useState('');
  const [selectedCategory, setSelectedCategory] = useState('all');

  if (loading) {
    return (
      <div className="min-h-screen bg-background pt-8 flex items-center justify-center">
        <motion.div 
          className="text-center"
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
        >
          <Waves className="h-12 w-12 text-primary mx-auto mb-4 animate-pulse" />
          <p className="text-muted-foreground">Loading acoustic indices reference...</p>
        </motion.div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="min-h-screen bg-background pt-8 flex items-center justify-center">
        <Card className="max-w-md">
          <CardHeader>
            <CardTitle className="text-destructive">Error Loading Data</CardTitle>
          </CardHeader>
          <CardContent>
            <p className="text-muted-foreground">Failed to load acoustic indices reference data.</p>
          </CardContent>
        </Card>
      </div>
    );
  }

  const filteredIndices = indicesData?.indices.filter(index => {
    const matchesSearch = (index.prefix?.toLowerCase() || '').includes(searchTerm.toLowerCase()) ||
                         (index.full_name?.toLowerCase() || '').includes(searchTerm.toLowerCase()) ||
                         (index.description?.toLowerCase() || '').includes(searchTerm.toLowerCase()) ||
                         (index.subcategory?.toLowerCase() || '').includes(searchTerm.toLowerCase());
    const matchesCategory = selectedCategory === 'all' || index.category === selectedCategory;
    return matchesSearch && matchesCategory;
  }) || [];

  const categories = Array.isArray(indicesData?.summary.categories) 
    ? indicesData.summary.categories 
    : indicesData?.summary.categories?.list || [];

  return (
    <div className="min-h-screen bg-background pt-8">
      <div className="container mx-auto px-4 py-8">
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.6 }}
          className="text-center mb-12"
        >
          <h1 className="text-4xl font-medium mb-4">Acoustic Indices Reference</h1>
          <p className="text-xl text-muted-foreground max-w-3xl mx-auto mb-6">
            Comprehensive guide to acoustic indices used in marine soundscape analysis and biodiversity assessment
          </p>
          <div className="w-24 h-1 bg-gradient-to-r from-primary to-accent-foreground mx-auto"></div>
          
          {indicesData && (
            <motion.div
              initial={{ opacity: 0 }}
              animate={{ opacity: 1 }}
              transition={{ delay: 0.3 }}
              className="mt-8 text-center"
            >
              <div className="flex items-center justify-center gap-6 text-sm text-muted-foreground">
                <div className="flex items-center gap-2">
                  <FileText className="h-4 w-4" />
                  <span>{indicesData.summary.total_indices} indices</span>
                </div>
                <div className="flex items-center gap-2">
                  <Filter className="h-4 w-4" />
                  <span>{categories.length || indicesData.summary.categories?.count || 0} categories</span>
                </div>
              </div>
            </motion.div>
          )}
        </motion.div>

        {/* Search and Filter Controls */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.6, delay: 0.2 }}
          className="mb-8"
        >
          <Card>
            <CardContent className="p-6">
              <div className="flex flex-col md:flex-row gap-4">
                <div className="flex-1 relative">
                  <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 h-4 w-4 text-muted-foreground" />
                  <input
                    type="text"
                    placeholder="Search indices by name or description..."
                    value={searchTerm}
                    onChange={(e) => setSearchTerm(e.target.value)}
                    className="w-full pl-10 pr-4 py-2 bg-background border border-input rounded-lg focus:outline-none focus:ring-2 focus:ring-ring"
                  />
                </div>
                <select
                  value={selectedCategory}
                  onChange={(e) => setSelectedCategory(e.target.value)}
                  className="px-4 py-2 bg-background border border-input rounded-lg focus:outline-none focus:ring-2 focus:ring-ring"
                >
                  <option value="all">All Categories</option>
                  {categories.map(category => (
                    <option key={category} value={category}>
                      {category.replace('_', ' ')}
                    </option>
                  ))}
                </select>
              </div>
            </CardContent>
          </Card>
        </motion.div>

        {/* Indices Grid */}
        <motion.div
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          transition={{ duration: 0.6, delay: 0.4 }}
        >
          {filteredIndices.length === 0 ? (
            <Card className="text-center py-12">
              <CardContent>
                <Search className="h-12 w-12 text-muted-foreground mx-auto mb-4" />
                <h3 className="font-medium mb-2">No indices found</h3>
                <p className="text-muted-foreground">
                  Try adjusting your search terms or category filter
                </p>
              </CardContent>
            </Card>
          ) : (
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-4">
              {filteredIndices.map((index, i) => {
                // Define colors for each category
                const categoryColors: Record<string, { bg: string; border: string; header: string; badge: string }> = {
                  'Complexity Indices': { 
                    bg: 'bg-gradient-to-br from-chart-1/5 to-chart-1/10', 
                    border: 'border-chart-1/30', 
                    header: 'bg-gradient-to-r from-chart-1/20 to-chart-1/10',
                    badge: 'bg-chart-1/20 text-chart-1 border-chart-1/30'
                  },
                  'Temporal Indices': { 
                    bg: 'bg-gradient-to-br from-chart-2/5 to-chart-2/10', 
                    border: 'border-chart-2/30', 
                    header: 'bg-gradient-to-r from-chart-2/20 to-chart-2/10',
                    badge: 'bg-chart-2/20 text-chart-2 border-chart-2/30'
                  },
                  'Diversity Indices': { 
                    bg: 'bg-gradient-to-br from-chart-3/5 to-chart-3/10', 
                    border: 'border-chart-3/30', 
                    header: 'bg-gradient-to-r from-chart-3/20 to-chart-3/10',
                    badge: 'bg-chart-3/20 text-chart-3 border-chart-3/30'
                  },
                  'Spectral Indices': { 
                    bg: 'bg-gradient-to-br from-chart-4/5 to-chart-4/10', 
                    border: 'border-chart-4/30', 
                    header: 'bg-gradient-to-r from-chart-4/20 to-chart-4/10',
                    badge: 'bg-chart-4/20 text-chart-4 border-chart-4/30'
                  },
                  'Amplitude Indices': { 
                    bg: 'bg-gradient-to-br from-chart-5/5 to-chart-5/10', 
                    border: 'border-chart-5/30', 
                    header: 'bg-gradient-to-r from-chart-5/20 to-chart-5/10',
                    badge: 'bg-chart-5/20 text-chart-5 border-chart-5/30'
                  }
                };
                const colors = categoryColors[index.category] || { 
                  bg: 'bg-gradient-to-br from-muted/50 to-muted', 
                  border: 'border-border', 
                  header: 'bg-muted',
                  badge: 'bg-muted text-foreground border-border'
                };
                
                return (
                  <motion.div
                    key={index.prefix || `index-${i}`}
                    initial={{ opacity: 0, scale: 0.95 }}
                    animate={{ opacity: 1, scale: 1 }}
                    transition={{ duration: 0.3, delay: Math.min(i * 0.02, 0.3) }}
                    whileHover={{ y: -4 }}
                  >
                    <Card className={`h-full hover:shadow-xl transition-all duration-300 ${colors.bg} ${colors.border} border-2 overflow-hidden`}>
                      <CardHeader className={`${colors.header} pb-3`}>
                        <div className="space-y-1">
                          <CardTitle className="text-2xl font-mono font-black tracking-tight">
                            {index.prefix}
                          </CardTitle>
                          <CardDescription className="text-sm font-medium text-foreground/80">
                            {index.full_name || index.prefix}
                          </CardDescription>
                        </div>
                      </CardHeader>
                      <CardContent className="pt-4">
                        <div className="space-y-3">
                          {index.subcategory && (
                            <div className="flex items-center gap-2">
                              <span className={`text-xs font-medium px-2 py-1 rounded-full border ${colors.badge}`}>
                                {index.subcategory}
                              </span>
                            </div>
                          )}
                          
                          {index.description && (
                            <p className="text-sm text-muted-foreground leading-relaxed line-clamp-3 hover:line-clamp-none transition-all">
                              {index.description}
                            </p>
                          )}
                          
                          {index.computational_type && (
                            <div className="pt-2 border-t border-border/50">
                              <span className="text-xs font-mono text-muted-foreground">
                                {index.computational_type}
                              </span>
                            </div>
                          )}
                        </div>
                      </CardContent>
                    </Card>
                  </motion.div>
                );
              })}
            </div>
          )}
        </motion.div>

        {/* Summary Footer */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.6, delay: 0.6 }}
          className="mt-12 text-center text-muted-foreground"
        >
          <p>
            Showing {filteredIndices.length} of {indicesData?.summary.total_indices || 0} acoustic indices
            {selectedCategory !== 'all' && ` in ${selectedCategory.replace('_', ' ')} category`}
          </p>
        </motion.div>
      </div>
    </div>
  );
}