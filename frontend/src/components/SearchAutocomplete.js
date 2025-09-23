import React, { useState, useEffect, useRef } from 'react';
import { Link } from 'react-router-dom';
import { MagnifyingGlassIcon, UserIcon, BuildingOfficeIcon } from '@heroicons/react/24/outline';
import { searchSuggestions } from '../utils/api';

const SearchAutocomplete = ({ placeholder = "Search traders, companies, or tickers..." }) => {
 const [query, setQuery] = useState('');
 const [suggestions, setSuggestions] = useState([]);
 const [isOpen, setIsOpen] = useState(false);
 const [isLoading, setIsLoading] = useState(false);
 const [selectedIndex, setSelectedIndex] = useState(-1);
 
 const inputRef = useRef(null);
 const dropdownRef = useRef(null);
 const debounceRef = useRef(null);

 // Debounced search
 useEffect(() => {
  if (debounceRef.current) {
   clearTimeout(debounceRef.current);
  }

  if (query.length < 2) {
   setSuggestions([]);
   setIsOpen(false);
   return;
  }

  setIsLoading(true);
  debounceRef.current = setTimeout(async () => {
   try {
    const results = await searchSuggestions(query, 8);
    setSuggestions(results);
    setIsOpen(true);
    setSelectedIndex(-1);
   } catch (error) {
    console.error('Search error:', error);
    setSuggestions([]);
   } finally {
    setIsLoading(false);
   }
  }, 300);
 }, [query]);

 // Handle keyboard navigation
 const handleKeyDown = (e) => {
  if (!isOpen || suggestions.length === 0) return;

  switch (e.key) {
   case 'ArrowDown':
    e.preventDefault();
    setSelectedIndex(prev => 
     prev < suggestions.length - 1 ? prev + 1 : 0
    );
    break;
   case 'ArrowUp':
    e.preventDefault();
    setSelectedIndex(prev => 
     prev > 0 ? prev - 1 : suggestions.length - 1
    );
    break;
   case 'Enter':
    e.preventDefault();
    if (selectedIndex >= 0 && selectedIndex < suggestions.length) {
     handleSuggestionClick(suggestions[selectedIndex]);
    }
    break;
   case 'Escape':
    setIsOpen(false);
    setSelectedIndex(-1);
    break;
  }
 };

 const handleSuggestionClick = (suggestion) => {
  if (suggestion.type === 'trader') {
   // Navigate to trader profile
   window.location.href = `/traders/${suggestion.id}`;
  } else {
   // Navigate to dashboard with ticker filter
   window.location.href = `/dashboard?ticker=${suggestion.ticker}`;
  }
  setIsOpen(false);
  setQuery('');
 };

 const handleInputChange = (e) => {
  setQuery(e.target.value);
 };

 const handleInputFocus = () => {
  if (suggestions.length > 0) {
   setIsOpen(true);
  }
 };

 const handleInputBlur = () => {
  // Delay closing to allow clicks on suggestions
  setTimeout(() => {
   setIsOpen(false);
   setSelectedIndex(-1);
  }, 150);
 };

 return (
  <div className="relative w-full max-w-md">
   {/* Search Input */}
   <div className="relative">
    <div className="absolute inset-y-0 left-0 pl-4 flex items-center pointer-events-none">
     <MagnifyingGlassIcon className="h-5 w-5 text-secondary" />
    </div>
    <input
     ref={inputRef}
     type="text"
     value={query}
     onChange={handleInputChange}
     onFocus={handleInputFocus}
     onBlur={handleInputBlur}
     onKeyDown={handleKeyDown}
     placeholder={placeholder}
     className="w-full pl-12 pr-4 py-3 bg-primary border border-tertiary rounded-full text-primary placeholder-secondary focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent transition-all duration-200"
    />
    {isLoading && (
     <div className="absolute inset-y-0 right-0 pr-4 flex items-center">
      <div className="animate-spin rounded-full h-4 w-4 border-2 border-blue-500 border-t-transparent"></div>
     </div>
    )}
   </div>

   {/* Suggestions Dropdown */}
   {isOpen && suggestions.length > 0 && (
    <div
     ref={dropdownRef}
     className="absolute z-50 w-full mt-2 bg-primary border border-tertiary rounded-xl shadow-xl max-h-80 overflow-y-auto"
    >
     {suggestions.map((suggestion, index) => (
      <div
       key={`${suggestion.type}-${suggestion.id || suggestion.ticker}`}
       onClick={() => handleSuggestionClick(suggestion)}
       className={`flex items-center px-4 py-3 cursor-pointer transition-colors ${
        index === selectedIndex 
         ? 'bg-blue-500/20 text-blue-400' 
         : ' text-primary'
       }`}
      >
       <div className="flex-shrink-0 mr-3">
        {suggestion.type === 'trader' ? (
         <UserIcon className="h-5 w-5 text-blue-400" />
        ) : (
         <BuildingOfficeIcon className="h-5 w-5 text-green-400" />
        )}
       </div>
       <div className="flex-1 min-w-0">
        <div className="text-sm font-medium truncate">
         {suggestion.name}
        </div>
        <div className="text-xs text-secondary truncate">
         {suggestion.type === 'trader' 
          ? `${suggestion.title} - ${suggestion.ticker}`
          : `${suggestion.ticker} - ${suggestion.company}`
         }
        </div>
       </div>
       <div className="flex-shrink-0 ml-2">
        <span className={`text-xs px-2 py-1 rounded-full ${
         suggestion.type === 'trader' 
          ? 'bg-blue-500/20 text-blue-400' 
          : 'bg-green-500/20 text-green-400'
        }`}>
         {suggestion.type === 'trader' ? 'Trader' : 'Company'}
        </span>
       </div>
      </div>
     ))}
    </div>
   )}

   {/* No Results */}
   {isOpen && query.length >= 2 && !isLoading && suggestions.length === 0 && (
    <div className="absolute z-50 w-full mt-2 bg-primary border border-tertiary rounded-xl shadow-xl">
     <div className="px-4 py-3 text-center text-secondary">
      <MagnifyingGlassIcon className="h-8 w-8 mx-auto mb-2 opacity-50" />
      <p>No results found for "{query}"</p>
     </div>
    </div>
   )}
  </div>
 );
};

export default SearchAutocomplete;
