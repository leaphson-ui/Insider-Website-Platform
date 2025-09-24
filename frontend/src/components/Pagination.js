import React from 'react';

const Pagination = ({ 
  currentPage, 
  totalPages, 
  onPageChange, 
  itemsPerPage, 
  totalItems,
  loading = false 
}) => {
  const startItem = (currentPage - 1) * itemsPerPage + 1;
  const endItem = Math.min(currentPage * itemsPerPage, totalItems);

  const handlePrevious = () => {
    if (currentPage > 1 && !loading) {
      onPageChange(currentPage - 1);
    }
  };

  const handleNext = () => {
    if (currentPage < totalPages && !loading) {
      onPageChange(currentPage + 1);
    }
  };

  if (totalPages <= 1) return null;

  return (
    <div className="pagination-container">
      <div className="pagination-info">
        Showing {startItem}-{endItem} of {totalItems} transactions
      </div>
      
      <div className="pagination-controls">
        <button 
          className={`pagination-btn ${currentPage === 1 || loading ? 'disabled' : ''}`}
          onClick={handlePrevious}
          disabled={currentPage === 1 || loading}
          aria-label="Previous page"
        >
          <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
            <path d="M15 18L9 12L15 6"/>
          </svg>
          Previous
        </button>
        
        <div className="pagination-page-info">
          Page {currentPage} of {totalPages}
        </div>
        
        <button 
          className={`pagination-btn ${currentPage === totalPages || loading ? 'disabled' : ''}`}
          onClick={handleNext}
          disabled={currentPage === totalPages || loading}
          aria-label="Next page"
        >
          Next
          <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
            <path d="M9 18L15 12L9 6"/>
          </svg>
        </button>
      </div>
    </div>
  );
};

export default Pagination;
