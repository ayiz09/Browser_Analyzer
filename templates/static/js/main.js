// Main entry point for the application
document.addEventListener('DOMContentLoaded', function() {
    // Initialize event listeners
    initEventListeners();
    
    // Check for saved file ID and load data if exists
    const savedFileId = localStorage.getItem('currentFileId');
    if (savedFileId) {
        console.log('Found saved file ID:', savedFileId);
        currentFileId = savedFileId;
        loadData(savedFileId);
    }
});

// Initialize event listeners
function initEventListeners() {
    // Upload form submission
    uploadForm.addEventListener('submit', function(e) {
        e.preventDefault();
        uploadFile();
    });
    
    // Search inputs
    searchInput.addEventListener('input', filterTable);
    downloadSearchInput.addEventListener('input', filterDownloads);
    
    // Export buttons
    exportButton.addEventListener('click', function() {
        if (currentFileId) {
            console.log('Exporting file with ID:', currentFileId);
            window.location.href = `/export/${currentFileId}`;
        } else {
            alert('No data available to export. Please upload a history file first.');
        }
    });
    
    exportDownloadsButton.addEventListener('click', function() {
        if (currentFileId) {
            console.log('Exporting downloads with ID:', currentFileId);
            window.location.href = `/export_downloads/${currentFileId}`;
        } else {
            alert('No data available to export. Please upload a history file first.');
        }
    });
}