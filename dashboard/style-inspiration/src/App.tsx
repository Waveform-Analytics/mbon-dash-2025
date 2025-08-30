import React, { useState } from 'react';
import { SidebarProvider, SidebarTrigger } from './components/ui/sidebar';
import { LandingPage } from './components/LandingPage';
import { DataTypesPage } from './components/DataTypesPage';
import { AnalysisPage } from './components/AnalysisPage';
import { AppSidebar } from './components/AppSidebar';

export default function App() {
  const [currentPage, setCurrentPage] = useState('landing');

  const renderPage = () => {
    const pages = {
      'landing': <LandingPage />,
      'data-types': <DataTypesPage />,
      'analysis': <AnalysisPage />
    };
    
    return pages[currentPage] || pages['landing'];
  };

  return (
    <SidebarProvider>
      <div className="flex h-screen w-full">
        <AppSidebar currentPage={currentPage} setCurrentPage={setCurrentPage} />
        <main className="flex-1 overflow-auto">
          <div className="p-6">
            <div className="mb-4">
              <SidebarTrigger />
            </div>
            {renderPage()}
          </div>
        </main>
      </div>
    </SidebarProvider>
  );
}