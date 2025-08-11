import React from 'react';
import { ChevronDown, Users } from 'lucide-react';

const PageSelector = ({ pages, selectedPage, onPageSelect }) => {
  if (!pages || pages.length === 0) {
    return (
      <div className="text-sm text-gray-500">
        Aucune page disponible
      </div>
    );
  }

  return (
    <div className="relative">
      <select
        value={selectedPage?.id || ''}
        onChange={(e) => {
          const page = pages.find(p => p.id === e.target.value);
          onPageSelect(page);
        }}
        className="facebook-input pr-8 text-sm max-w-xs"
      >
        {pages.map((page) => (
          <option key={page.id} value={page.id}>
            {page.name}
          </option>
        ))}
      </select>
      
      <div className="absolute right-2 top-1/2 transform -translate-y-1/2 pointer-events-none">
        <ChevronDown className="w-4 h-4 text-gray-400" />
      </div>
    </div>
  );
};

export default PageSelector;