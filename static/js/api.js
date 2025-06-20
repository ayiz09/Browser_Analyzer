// State variables
let currentFileId = null;
let currentPage = 1;
let totalPages = 1;
let pageSize = 1000;
let currentData = null;

// Load data from server
function loadData(fileId) {
    if (!fileId) return;
    
    // Show loader
    showLoader();
    
    // Send request
    fetch(`/get_page?file_id=${fileId}&page=1&page_size=${pageSize}`)
    .then(response => {
        if (!response.ok) {
            throw new Error('Failed to load data');
        }
        return response.json();
    })
    .then(data => {
        // Store current data
        currentData = data;
        currentFileId = data.file_id;
        currentPage = data.page;
        totalPages = data.total_pages;
        
        // Save file ID to localStorage
        localStorage.setItem('currentFileId', currentFileId);
        
        // Process and display data
        processData(data);
        
        // Hide loader, show results
        hideLoader();
        showResults();
    })
    .catch(error => {
        console.error('Error loading data:', error);
        hideLoader();
        
        // Clear saved file ID if it's invalid
        localStorage.removeItem('currentFileId');
        currentFileId = null;
    });
}

// Upload and process file
function uploadFile() {
    console.log("uploadFile function called");
    
    const fileInput = document.getElementById('fileInput');
    
    if (!fileInput) {
        console.error("File input element not found!");
        return;
    }
    
    const file = fileInput.files[0];
    if (!file) {
        alert('Please select a file first');
        return;
    }
    
    console.log("File selected:", file.name, "Size:", file.size, "bytes");
    
    // Reset state
    currentPage = 1;
    
    // Show loader
    console.log("Showing loader");
    const loader = document.getElementById('loader');
    const resultsContainer = document.getElementById('resultsContainer');
    
    if (loader) loader.classList.remove('hidden');
    if (resultsContainer) resultsContainer.classList.add('hidden');
    
    // Create form data
    const formData = new FormData();
    formData.append('file', file);
    formData.append('page', currentPage);
    formData.append('page_size', pageSize);
    
    console.log("Sending POST request to /upload");
    
    // Send request with detailed logging
    fetch('/upload', {
        method: 'POST',
        body: formData
    })
    .then(response => {
        console.log("Received response:", response.status, response.statusText);
        if (!response.ok) {
            throw new Error(`Server responded with status: ${response.status}`);
        }
        return response.json();
    })
    .then(data => {
        console.log("Parsed response data:", data);
        
        if (data.error) {
            console.error("Server returned error:", data.error);
            alert('Error: ' + data.error);
            if (loader) loader.classList.add('hidden');
            return;
        }
        
        // Store current data and file ID
        currentData = data;
        currentFileId = data.file_id;
        totalPages = data.total_pages || 1;
        
        // Save file ID to localStorage for persistence
        localStorage.setItem('currentFileId', currentFileId);
        console.log('Saved file ID to localStorage:', currentFileId);
        
        // Process and display data
        processData(data);
        
        // Hide loader, show results
        if (loader) loader.classList.add('hidden');
        if (resultsContainer) resultsContainer.classList.remove('hidden');
    })
    .catch(error => {
        console.error('Upload error:', error);
        alert('Error uploading file: ' + error.message);
        if (loader) loader.classList.add('hidden');
    });
}

// Fetch sync information
function fetchSyncInfo(fileId) {
    if (!fileId) return;
    
    fetch(`/get_sync_info?file_id=${fileId}`)
    .then(response => {
        if (!response.ok) {
            throw new Error('Failed to load sync data');
        }
        return response.json();
    })
    .then(data => {
        if (data.sync_info) {
            displaySyncInfo(data.sync_info);
        }
    })
    .catch(error => {
        console.error('Error loading sync data:', error);
        syncContainer.innerHTML = `
            <div class="alert alert-warning" role="alert">
                Failed to load synchronization information: ${error.message}
            </div>
        `;
    });
}

// Load a specific page
function loadPage(page) {
    if (!currentFileId) return;
    
    // Show loader
    showLoader();
    
    // Send request
    fetch(`/get_page?file_id=${currentFileId}&page=${page}&page_size=${pageSize}`)
    .then(response => response.json())
    .then(data => {
        if (data.error) {
            alert('Error: ' + data.error);
            hideLoader();
            return;
        }
        
        // Update current data and page
        currentData = data;
        currentPage = data.page;
        totalPages = data.total_pages;
        
        // Display results
        displayResults(data);
        
        // Update pagination
        generatePagination();
        
        // Hide loader
        hideLoader();
    })
    .catch(error => {
        console.error('Error:', error);
        alert('Error loading page: ' + error.message);
        hideLoader();
    });

// static/js/api.js - Add these functions to your existing code

/**
 * Export data with the specified format and type
 * @param {string} fileId - The file ID to export
 * @param {string} format - Export format (csv, json, excel)
 * @param {string} dataType - Data type to export (history, domains, downloads, timeline)
 * @param {Object} filters - Optional filters to apply
 * @returns {Promise} - Promise that resolves when export completes
 */
function exportData(fileId, format, dataType, filters = {}) {
    return fetch('/api/export', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify({
            file_id: fileId,
            format: format,
            data_type: dataType,
            filters: filters
        })
    })
    .then(response => {
        if (!response.ok) {
            if (response.headers.get('content-type')?.includes('application/json')) {
                return response.json().then(data => {
                    throw new Error(data.error || 'Export failed');
                });
            }
            throw new Error(`Export failed with status ${response.status}`);
        }
        return response.blob();
    })
    .then(blob => {
        // Create a download link and trigger it
        const url = window.URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.style.display = 'none';
        a.href = url;
        a.download = `browser_${dataType}_${fileId}.${format}`;
        document.body.appendChild(a);
        a.click();
        window.URL.revokeObjectURL(url);
        document.body.removeChild(a);
        return { success: true };
    });
}

}