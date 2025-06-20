// Main entry point for the application
document.addEventListener('DOMContentLoaded', function() {
    console.log("Document loaded, initializing event listeners");
    
    // Initialize event listeners
    initEventListeners();
    
    // Initialize tabs
    initializeTabs();

    // Initialize export functionality
    initExportForm();
    
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
    console.log("Setting up event listeners");
    
    const uploadForm = document.getElementById('uploadForm');
    const analyzeButton = document.getElementById('analyzeButton');
    const analyzeHistoryButton = document.getElementById('analyzeHistory');
    
    // Try different button IDs since the HTML might have either
    const actualAnalyzeButton = analyzeButton || analyzeHistoryButton;
    
    if (uploadForm) {
        console.log("Found upload form");
        
        // Handle form submission
        uploadForm.addEventListener('submit', function(e) {
            console.log("Form submit event triggered");
            e.preventDefault();
            uploadFile();
        });
    } else {
        console.error("Upload form not found!");
    }
    
    if (actualAnalyzeButton) {
        console.log("Found analyze button with ID:", actualAnalyzeButton.id);
        
        // Handle button click
        actualAnalyzeButton.addEventListener('click', function() {
            console.log("Analyze button clicked");
            uploadFile();
        });
    } else {
        console.error("Analyze button not found! Checked IDs: 'analyzeButton', 'analyzeHistory'");
    }
    
    // Set up tab event listeners
    setupTabListeners();
    
    // Other event listeners
    setupOtherListeners();
}

// Set up tab event listeners
function setupTabListeners() {
    const tabLinks = document.querySelectorAll('[data-bs-toggle="tab"]');
    
    console.log("Found", tabLinks.length, "tab links");
    
    tabLinks.forEach(tabLink => {
        tabLink.addEventListener('click', function(event) {
            console.log("Tab clicked:", this.textContent, "Target:", this.getAttribute('data-bs-target'));
            
            // Check if target panel exists
            const targetId = this.getAttribute('data-bs-target');
            const targetPanel = document.querySelector(targetId);
            console.log("Target panel exists:", !!targetPanel);
            
            // Additional logging for debugging
            if (targetPanel) {
                const containerIds = {
                    '#downloads-content': 'downloadsContainer',
                    '#domains-content': 'domainStats',
                    '#sync-content': 'syncContainer',
                    '#timeline-content': 'historyTableBody'
                };
                
                const containerId = containerIds[targetId];
                if (containerId) {
                    const container = document.getElementById(containerId);
                    console.log(`Container '${containerId}' exists:`, !!container);
                    if (container) {
                        const content = container.innerHTML;
                        console.log(`Container has content:`, content.length > 0);
                    }
                }
            }
        });
    });
}

// Set up other event listeners
function setupOtherListeners() {
    const searchInput = document.getElementById('searchInput');
    if (searchInput) {
        searchInput.addEventListener('input', filterTable);
    }
    
    const downloadSearchInput = document.getElementById('downloadSearchInput');
    if (downloadSearchInput) {
        downloadSearchInput.addEventListener('input', filterDownloads);
    }
    
    const exportButton = document.getElementById('exportButton');
    if (exportButton) {
        exportButton.addEventListener('click', function() {
            if (currentFileId) {
                console.log('Exporting file with ID:', currentFileId);
                window.location.href = `/export/${currentFileId}`;
            } else {
                alert('No data available to export. Please upload a history file first.');
            }
        });
    }
    
    const exportDownloadsButton = document.getElementById('exportDownloadsButton');
    if (exportDownloadsButton) {
        exportDownloadsButton.addEventListener('click', function() {
            if (currentFileId) {
                console.log('Exporting downloads with ID:', currentFileId);
                window.location.href = `/export_downloads/${currentFileId}`;
            } else {
                alert('No data available to export. Please upload a history file first.');
            }
        });
    }
}

// Helper function to manually initialize tabs if Bootstrap isn't doing it
function initializeTabs() {
    console.log("Initializing tabs manually");
    
    const tabLinks = document.querySelectorAll('[data-bs-toggle="tab"]');
    
    if (tabLinks.length === 0) {
        console.error("No tab links found with [data-bs-toggle='tab']");
        return;
    }
    
    console.log("Found tabs:", Array.from(tabLinks).map(tab => tab.textContent.trim()));
    
    tabLinks.forEach(tabLink => {
        tabLink.addEventListener('click', function(event) {
            event.preventDefault();
            
            // Hide all tab panes
            const tabPanes = document.querySelectorAll('.tab-pane');
            tabPanes.forEach(pane => {
                pane.classList.remove('show', 'active');
            });
            
            // Remove active class from all tabs
            tabLinks.forEach(link => {
                link.classList.remove('active');
            });
            
            // Activate clicked tab
            this.classList.add('active');
            
            // Show the target pane
            const targetId = this.getAttribute('data-bs-target');
            const targetPane = document.querySelector(targetId);
            if (targetPane) {
                targetPane.classList.add('show', 'active');
                console.log(`Activated tab pane: ${targetId}`);
                
                // Force redraw if needed
                if (targetId === '#downloads-content' && window.currentData && window.currentData.downloads) {
                    console.log("Forcing redraw of downloads");
                    displayDownloads(window.currentData.downloads, window.currentData.download_sources);
                }
                else if (targetId === '#domains-content' && window.currentData && window.currentData.entries) {
                    console.log("Forcing redraw of domain stats");
                    calculateDomainStats(window.currentData.entries);
                }
            } else {
                console.error(`Tab pane not found: ${targetId}`);
            }
        });
    });
    
    // Ensure proper Bootstrap initialization
    try {
        if (typeof bootstrap !== 'undefined' && bootstrap.Tab) {
            console.log("Bootstrap Tab component detected, initializing");
            tabLinks.forEach(tabLink => {
                new bootstrap.Tab(tabLink);
            });
        } else {
            console.log("Bootstrap Tab component not found, using manual handling");
        }
    } catch(e) {
        console.error("Error initializing Bootstrap tabs:", e);
    }
}

function initExportForm() {
    const exportButton = document.getElementById('exportButton');
    const exportContainer = document.getElementById('exportContainer');
    
    if (!exportButton || !exportContainer) return;
    
    // Show/hide export form based on results visibility
    const resultsContainer = document.getElementById('resultsContainer');
    if (resultsContainer) {
        // Initially sync export visibility with results visibility
        const observer = new MutationObserver(function(mutations) {
            mutations.forEach(function(mutation) {
                if (mutation.attributeName === 'class') {
                    const isHidden = resultsContainer.classList.contains('hidden');
                    exportContainer.style.display = isHidden ? 'none' : 'block';
                }
            });
        });
        
        observer.observe(resultsContainer, { attributes: true });
        
        // Set initial state
        exportContainer.style.display = resultsContainer.classList.contains('hidden') ? 'none' : 'block';
    }
    
    // Handle export button click
    exportButton.addEventListener('click', function() {
        // Get active file ID from the data attribute or URL
        const fileId = getActiveFileId();
        
        if (!fileId) {
            showExportStatus('No browser history data available for export. Please upload a file first.', 'danger');
            return;
        }
        
        const format = document.getElementById('exportFormat').value;
        const dataType = document.getElementById('dataType').value;
        
        // Get active filters if any
        const filters = getCurrentFilters();
        
        // Show loading status
        showExportStatus('Exporting data, please wait...', 'info');
        
        // Show loader
        const loader = document.querySelector('.loader-container');
        if (loader) loader.style.display = 'flex';
        
        // Call export API
        exportData(fileId, format, dataType, filters)
            .then(() => {
                showExportStatus('Export completed successfully! Your download should begin automatically.', 'success');
            })
            .catch(error => {
                console.error('Export error:', error);
                showExportStatus(`Export failed: ${error.message}`, 'danger');
            })
            .finally(() => {
                // Hide loader
                if (loader) loader.style.display = 'none';
            });
    });
}

function getActiveFileId() {
    // First check URL parameters
    const urlParams = new URLSearchParams(window.location.search);
    const fileIdParam = urlParams.get('file_id');
    if (fileIdParam) return fileIdParam;
    
    // Then check for data attribute on the results container
    const resultsContainer = document.getElementById('resultsContainer');
    if (resultsContainer && resultsContainer.dataset.fileId) {
        return resultsContainer.dataset.fileId;
    }
    
    // Finally check summary element which might have the file ID
    const summaryElement = document.querySelector('.summary-content');
    if (summaryElement && summaryElement.dataset.fileId) {
        return summaryElement.dataset.fileId;
    }
    
    // If we can't find it, log a message and return null
    console.warn('Could not find active file ID');
    return null;
}

function getCurrentFilters() {
    const filters = {};
    
    // Get date range filters if present
    const startDate = document.getElementById('startDateFilter')?.value;
    const endDate = document.getElementById('endDateFilter')?.value;
    
    if (startDate) filters.start_date = startDate;
    if (endDate) filters.end_date = endDate;
    
    // Get domain filter if present
    const domainFilter = document.getElementById('domainFilter')?.value;
    if (domainFilter) filters.domain = domainFilter;
    
    // Get search filter if present
    const searchInput = document.querySelector('input[type="search"]')?.value;
    if (searchInput) filters.search = searchInput;
    
    return filters;
}

function showExportStatus(message, type = 'info') {
    const statusElement = document.getElementById('exportStatus');
    if (!statusElement) return;
    
    statusElement.textContent = message;
    statusElement.className = `alert alert-${type}`;
    statusElement.style.display = 'block';
    
    // Auto-hide success messages after 5 seconds
    if (type === 'success') {
        setTimeout(() => {
            statusElement.style.display = 'none';
        }, 5000);
    }
}

// Expose current data globally for debugging
window.debugTabs = function() {
    const tabLinks = document.querySelectorAll('[data-bs-toggle="tab"]');
    const tabPanes = document.querySelectorAll('.tab-pane');
    
    console.log("Tab links:", Array.from(tabLinks).map(t => ({
        id: t.id,
        text: t.textContent,
        target: t.getAttribute('data-bs-target'),
        active: t.classList.contains('active')
    })));
    
    console.log("Tab panes:", Array.from(tabPanes).map(p => ({
        id: p.id,
        active: p.classList.contains('active'),
        visible: p.classList.contains('show'),
        empty: p.innerHTML.trim() === ''
    })));
    
    return {
        tabLinks,
        tabPanes,
        currentData
    };

// static/js/main.js - Add this to your existing code

// Initialize export functionality when DOM is loaded
document.addEventListener('DOMContentLoaded', function() {
    initExportForm();
    
    // Other initialization code...
});

function initExportForm() {
    const exportButton = document.getElementById('exportButton');
    if (!exportButton) return;
    
    exportButton.addEventListener('click', function() {
        // Get active file ID from the current view
        const fileId = getActiveFileId();
        if (!fileId) {
            showExportStatus('No file selected. Please upload or select a history file first.', 'error');
            return;
        }
        
        const format = document.getElementById('exportFormat').value;
        const dataType = document.getElementById('dataType').value;
        
        // Get current filters
        const filters = getCurrentFilters();
        
        // Show loading
        showLoading(true);
        showExportStatus('Exporting data...', 'info');
        
        // Perform export
        exportData(fileId, format, dataType, filters)
            .then(() => {
                showExportStatus('Export completed successfully!', 'success');
            })
            .catch(error => {
                console.error('Export error:', error);
                showExportStatus(`Export failed: ${error.message}`, 'error');
            })
            .finally(() => {
                showLoading(false);
            });
    });
}

function showExportStatus(message, type = 'info') {
    const statusElem = document.getElementById('exportStatus');
    if (!statusElem) return;
    
    statusElem.textContent = message;
    statusElem.className = 'export-status';
    
    if (type) {
        statusElem.classList.add(type);
    }
    
    // Auto-hide success messages after a delay
    if (type === 'success') {
        setTimeout(() => {
            statusElem.style.display = 'none';
        }, 5000);
    }
}

function getActiveFileId() {
    // This function should return the currently active file ID
    // Implementation depends on how you track the active file in your app
    
    // Check if there's an active file ID in URL params
    const urlParams = new URLSearchParams(window.location.search);
    const fileIdParam = urlParams.get('file_id');
    if (fileIdParam) return fileIdParam;
    
    // Or check a data attribute on a container element
    const container = document.querySelector('.main-container');
    if (container && container.dataset.fileId) {
        return container.dataset.fileId;
    }
    
    // Or check if it's stored in sessionStorage
    return sessionStorage.getItem('activeFileId');
}

function getCurrentFilters() {
    const filters = {};
    
    // Example: Check for date range filters
    const startDateInput = document.getElementById('startDate');
    const endDateInput = document.getElementById('endDate');
    
    if (startDateInput && startDateInput.value) {
        filters.start_date = startDateInput.value;
    }
    
    if (endDateInput && endDateInput.value) {
        filters.end_date = endDateInput.value;
    }
    
    // Example: Check for domain filter
    const domainInput = document.getElementById('domainFilter');
    if (domainInput && domainInput.value) {
        filters.domain = domainInput.value;
    }
    
    // Example: Check for search input
    const searchInput = document.getElementById('searchInput');
    if (searchInput && searchInput.value) {
        filters.search = searchInput.value;
    }
    
    return filters;
}

function showLoading(show) {
    // Show or hide loading indicator
    const loader = document.querySelector('.loader-container');
    if (loader) {
        loader.style.display = show ? 'flex' : 'none';
    }
}

};