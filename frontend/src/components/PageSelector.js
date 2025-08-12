import React from 'react';
import { ChevronDown, Building2, User } from 'lucide-react';

const PageSelector = ({ pages, businessPages, selectedPage, onPageSelect, selectedBusinessManager }) => {
  // Combine personal and business pages
  const allPages = [];
  
  // Add personal pages if available
  if (pages && pages.length > 0) {
    allPages.push({
      type: 'group',
      label: 'Pages personnelles',
      pages: pages
    });
  }
  
  // Add business pages if available and a business manager is selected
  if (businessPages && businessPages.length > 0) {
    allPages.push({
      type: 'group',
      label: selectedBusinessManager ? `Pages - ${selectedBusinessManager.name}` : 'Pages Business Manager',
      pages: businessPages
    });
  }

  if (allPages.length === 0) {
    return (
      <div className="text-sm text-gray-500 flex items-center space-x-2">
        <Building2 className="w-4 h-4" />
        <span>Aucune page disponible</span>
      </div>
    );
  }

  const handlePageSelect = (pageId, sourceType = 'personal') => {
    let page = null;
    
    if (sourceType === 'business') {
      page = businessPages?.find(p => p.id === pageId);
    } else {
      page = pages?.find(p => p.id === pageId);
    }
    
    if (page) {
      // Mark the page source type
      page._sourceType = sourceType;
      onPageSelect(page);
    }
  };

  return (
    <div className="relative">
      <select
        value={selectedPage?.id || ''}
        onChange={(e) => {
          const value = e.target.value;
          if (!value) return;
          
          // Parse the value to get page ID and source type
          const [pageId, sourceType] = value.split('|');
          handlePageSelect(pageId, sourceType);
        }}
        className="facebook-input pr-8 text-sm max-w-xs"
      >
        <option value="">Sélectionnez une page</option>
        
        {allPages.map((group, groupIndex) => (
          <optgroup key={groupIndex} label={group.label}>
            {group.pages.map((page) => (
              <option 
                key={`${page.id}-${group.type === 'group' && group.label.includes('Business') ? 'business' : 'personal'}`} 
                value={`${page.id}|${group.type === 'group' && group.label.includes('Business') ? 'business' : 'personal'}`}
              >
                {page.name}
                {page.category && ` (${page.category})`}
              </option>
            ))}
          </optgroup>
        ))}
      </select>
      
      <div className="absolute right-2 top-1/2 transform -translate-y-1/2 pointer-events-none">
        <ChevronDown className="w-4 h-4 text-gray-400" />
      </div>
      
      {selectedPage && (
        <div className="absolute left-0 top-full mt-1 text-xs text-gray-500 flex items-center space-x-1">
          {selectedPage._sourceType === 'business' ? (
            <>
              <Building2 className="w-3 h-3" />
              <span>Business Manager</span>
            </>
          ) : (
            <>
              <User className="w-3 h-3" />
              <span>Personnel</span>
            </>
          )}
        </div>
      )}
    </div>
  );
};

export default PageSelector;