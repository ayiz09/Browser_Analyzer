// DOM Elements - Function to safely get elements
function getElementSafely(id, fallback = null) {
    const element = document.getElementById(id);
    if (!element) {
        console.warn(`Element with ID '${id}' not found in the DOM`);
    }
    return element || fallback;
}

// Show/hide UI elements
// Show/hide UI elements
function showLoader() {
    console.log("Showing loader");
    const loader = document.getElementById('loader');
    const resultsContainer = document.getElementById('resultsContainer');
    
    if (loader) {
        loader.classList.remove('hidden');
    } else {
        console.error("Loader element not found");
    }
    
    if (resultsContainer) {
        resultsContainer.classList.add('hidden');
    } else {
        console.error("Results container element not found");
    }
}

function hideLoader() {
    console.log("Hiding loader");
    const loader = document.getElementById('loader');
    
    if (loader) {
        loader.classList.add('hidden');
    } else {
        console.error("Loader element not found");
    }
}

function showResults() {
    console.log("Showing results");
    const resultsContainer = document.getElementById('resultsContainer');
    
    if (resultsContainer) {
        resultsContainer.classList.remove('hidden');
    } else {
        console.error("Results container element not found");
    }
}

function hideLoader() {
    console.log("Hiding loader");
    const loader = getElementSafely('loader');
    
    if (loader) {
        loader.classList.add('hidden');
    } else {
        console.error("Loader element not found");
    }
}

function showResults() {
    console.log("Showing results");
    const resultsContainer = getElementSafely('resultsContainer');
    
    if (resultsContainer) {
        resultsContainer.classList.remove('hidden');
    } else {
        console.error("Results container element not found");
    }
}

// Process data from API response
function processData(data) {
    console.log("Processing data:", data);
    
    try {
        // Display results
        displayResults(data);
        
        // Generate pagination
        generatePagination();
        
        // Calculate domain statistics
        calculateDomainStats(data.entries);
        
        // Display downloads
        displayDownloads(data.downloads, data.download_sources);
        
        // Display sync information
        if (data.sync_info) {
            displaySyncInfo(data.sync_info);
        } else {
            // If no sync info in the current data, fetch it separately
            fetchSyncInfo(currentFileId);
        }
        console.log("Data processing complete");
    } catch (error) {
        console.error("Error processing data:", error);
        alert("Error displaying results: " + error.message);
    }
}

// Display results in the UI with error handling
// Display results in the UI with error handling
function displayResults(data) {
    console.log("Displaying results");
    
    // Update summary
    const browserTypeElement = document.getElementById('browserType');
    const totalEntriesElement = document.getElementById('totalEntries');
    const historyTableBody = document.getElementById('historyTableBody');
    
    if (!browserTypeElement || !totalEntriesElement || !historyTableBody) {
        console.error("Required DOM elements not found for displayResults");
        return;
    }
    
    // Update summary
    browserTypeElement.textContent = data.browser_type === 'firefox' ? 'Firefox' : 'Chrome/Edge';
    totalEntriesElement.textContent = data.total_entries.toLocaleString();
    
    // Clear table
    historyTableBody.innerHTML = '';
    
    // Add entries to table
    if (Array.isArray(data.entries)) {
        data.entries.forEach(entry => {
            const row = document.createElement('tr');
            
            row.innerHTML = `
                <td>${entry.title || 'Unknown'}</td>
                <td><a href="#" title="${entry.url}">${truncateText(entry.url, 50)}</a></td>
                <td>${entry.visit_time}</td>
                <td>${entry.domain}</td>
            `;
            
            historyTableBody.appendChild(row);
        });
    } else {
        console.error("No entries array in data:", data);
    }
}

// Generate pagination links
function generatePagination() {
    console.log("Generating pagination");
    const pagination = getElementSafely('pagination');
    
    if (!pagination) {
        console.error("Pagination element not found");
        return;
    }
    
    pagination.innerHTML = '';
    
    // Previous button
    const prevLi = document.createElement('li');
    prevLi.className = `page-item ${currentPage === 1 ? 'disabled' : ''}`;
    const prevLink = document.createElement('a');
    prevLink.className = 'page-link';
    prevLink.href = '#';
    prevLink.innerHTML = '&laquo;';
    prevLink.addEventListener('click', function(e) {
        e.preventDefault();
        if (currentPage > 1) {
            loadPage(currentPage - 1);
        }
    });
    prevLi.appendChild(prevLink);
    pagination.appendChild(prevLi);
    
    // Page numbers
    const maxVisiblePages = 5;
    let startPage = Math.max(1, currentPage - Math.floor(maxVisiblePages / 2));
    let endPage = Math.min(totalPages, startPage + maxVisiblePages - 1);
    
    if (endPage - startPage + 1 < maxVisiblePages) {
        startPage = Math.max(1, endPage - maxVisiblePages + 1);
    }
    
    // First page
    if (startPage > 1) {
        const firstLi = document.createElement('li');
        firstLi.className = 'page-item';
        const firstLink = document.createElement('a');
        firstLink.className = 'page-link';
        firstLink.href = '#';
        firstLink.textContent = '1';
        firstLink.addEventListener('click', function(e) {
            e.preventDefault();
            loadPage(1);
        });
        firstLi.appendChild(firstLink);
        pagination.appendChild(firstLi);
        
        if (startPage > 2) {
            const ellipsisLi = document.createElement('li');
            ellipsisLi.className = 'page-item disabled';
            const ellipsisSpan = document.createElement('span');
            ellipsisSpan.className = 'page-link';
            ellipsisSpan.innerHTML = '...';
            ellipsisLi.appendChild(ellipsisSpan);
            pagination.appendChild(ellipsisLi);
        }
    }
    
    // Page numbers
    for (let i = startPage; i <= endPage; i++) {
        const pageLi = document.createElement('li');
        pageLi.className = `page-item ${i === currentPage ? 'active' : ''}`;
        const pageLink = document.createElement('a');
        pageLink.className = 'page-link';
        pageLink.href = '#';
        pageLink.textContent = i;
        pageLink.addEventListener('click', function(e) {
            e.preventDefault();
            loadPage(i);
        });
        pageLi.appendChild(pageLink);
        pagination.appendChild(pageLi);
    }
    
    // Last page
    if (endPage < totalPages) {
        if (endPage < totalPages - 1) {
            const ellipsisLi = document.createElement('li');
            ellipsisLi.className = 'page-item disabled';
            const ellipsisSpan = document.createElement('span');
            ellipsisSpan.className = 'page-link';
            ellipsisSpan.innerHTML = '...';
            ellipsisLi.appendChild(ellipsisSpan);
            pagination.appendChild(ellipsisLi);
        }
        
        const lastLi = document.createElement('li');
        lastLi.className = 'page-item';
        const lastLink = document.createElement('a');
        lastLink.className = 'page-link';
        lastLink.href = '#';
        lastLink.textContent = totalPages;
        lastLink.addEventListener('click', function(e) {
            e.preventDefault();
            loadPage(totalPages);
        });
        lastLi.appendChild(lastLink);
        pagination.appendChild(lastLi);
    }
    
    // Next button
    const nextLi = document.createElement('li');
    nextLi.className = `page-item ${currentPage === totalPages ? 'disabled' : ''}`;
    const nextLink = document.createElement('a');
    nextLink.className = 'page-link';
    nextLink.href = '#';
    nextLink.innerHTML = '&raquo;';
    nextLink.addEventListener('click', function(e) {
        e.preventDefault();
        if (currentPage < totalPages) {
            loadPage(currentPage + 1);
        }
    });
    nextLi.appendChild(nextLink);
    pagination.appendChild(nextLi);
}

// Calculate and display domain statistics with enhanced logging
function calculateDomainStats(entries) {
    console.log("Calculating domain stats", {
        entriesCount: entries ? entries.length : 0,
        entriesType: entries ? typeof entries : 'undefined'
    });
    
    const domainStats = getElementSafely('domainStats');
    
    if (!domainStats) {
        console.error("Domain stats element not found. Selector: #domainStats");
        // List all divs in the document to help debug
        const allDivs = document.querySelectorAll('div[id]');
        console.log("Available div IDs:", Array.from(allDivs).map(div => div.id));
        return;
    }
    
    // Rest of the function remains the same
    // ...
    
    // Count domain occurrences
    const domainCounts = {};
    
    entries.forEach(entry => {
        const domain = entry.domain;
        if (domain) {
            domainCounts[domain] = (domainCounts[domain] || 0) + 1;
        }
    });
    
    // Convert to array and sort
    const domainArray = Object.entries(domainCounts)
        .map(([domain, count]) => ({ domain, count }))
        .sort((a, b) => b.count - a.count);
    
    // Display top domains
    domainStats.innerHTML = '<h6>Top Domains</h6>';
    
    // Take top 20 domains
    const topDomains = domainArray.slice(0, 20);
    
    if (topDomains.length === 0) {
        domainStats.innerHTML += '<div class="alert alert-info">No domain statistics available</div>';
        return;
    }
    
    topDomains.forEach(item => {
        const domainItem = document.createElement('div');
        domainItem.className = 'domain-item';
        domainItem.innerHTML = `
            <span>${item.domain}</span>
            <span class="domain-count">${item.count}</span>
        `;
        domainStats.appendChild(domainItem);
    });
}

// Display downloads with error handling
function displayDownloads(downloads, downloadSources) {
    console.log("Displaying downloads", {
        downloadsCount: downloads ? downloads.length : 0,
        downloadSourcesCount: downloadSources ? downloadSources.length : 0
    });
    
    const downloadsContainer = getElementSafely('downloadsContainer');
    
    if (!downloadsContainer) {
        console.error("Downloads container element not found. Selector: #downloadsContainer");
        // List all divs in the document to help debug
        const allDivs = document.querySelectorAll('div[id]');
        console.log("Available div IDs:", Array.from(allDivs).map(div => div.id));
        return;
    }
    
    downloadsContainer.innerHTML = '';
    
    if (!downloads || downloads.length === 0) {
        downloadsContainer.innerHTML = `
            <div class="empty-state">
                <p>📥</p>
                <p>No download history found</p>
            </div>
        `;
        return;
    }
    
    // Enable export button
    const exportDownloadsButton = getElementSafely('exportDownloadsButton');
    if (exportDownloadsButton) {
        exportDownloadsButton.disabled = false;
    }
    
    // Group download sources by filename for easy lookup
    const sourcesByFilename = {};
    if (downloadSources && downloadSources.length > 0) {
        downloadSources.forEach(source => {
            sourcesByFilename[source.filename] = source;
        });
    }
    
    // Create download items
    downloads.forEach(download => {
        const downloadItem = document.createElement('div');
        downloadItem.className = 'download-item';
        downloadItem.setAttribute('data-filename', download.filename || '');
        downloadItem.setAttribute('data-url', download.url || '');
        
        // Determine file type icon based on file extension
        const fileExtension = download.filename ? download.filename.split('.').pop().toLowerCase() : '';
        let fileTypeIcon = '📄'; // Default document icon
        
        if (['jpg', 'jpeg', 'png', 'gif', 'bmp', 'webp', 'svg'].includes(fileExtension)) {
            fileTypeIcon = '🖼️'; // Image
        } else if (['mp4', 'avi', 'mov', 'wmv', 'flv', 'webm'].includes(fileExtension)) {
            fileTypeIcon = '🎬'; // Video
        } else if (['mp3', 'wav', 'ogg', 'flac', 'm4a'].includes(fileExtension)) {
            fileTypeIcon = '🎵'; // Audio
        } else if (['zip', 'rar', '7z', 'tar', 'gz'].includes(fileExtension)) {
            fileTypeIcon = '🗜️'; // Archive
        } else if (['pdf'].includes(fileExtension)) {
            fileTypeIcon = '📕'; // PDF
        } else if (['doc', 'docx', 'ppt', 'pptx', 'xls', 'xlsx'].includes(fileExtension)) {
            fileTypeIcon = '📊'; // Office document
        } else if (['exe', 'msi', 'app'].includes(fileExtension)) {
            fileTypeIcon = '⚙️'; // Executable
        }
        
        // Get download status badge
        let statusBadge = '';
        if (download.status) {
            let badgeClass = 'bg-secondary';
            
            if (download.status === 'completed') {
                badgeClass = 'bg-success';
            } else if (download.status === 'failed' || download.status === 'interrupted') {
                badgeClass = 'bg-danger';
            } else if (download.status === 'in_progress') {
                badgeClass = 'bg-primary';
            } else if (download.status === 'canceled') {
                badgeClass = 'bg-warning';
            }
            
            statusBadge = `<span class="badge ${badgeClass}">${download.status}</span>`;
        }
        
        // Create download item content
        downloadItem.innerHTML = `
            <h5>
                <span class="file-type-icon">${fileTypeIcon}</span>
                ${download.filename || 'Unknown file'}
                ${statusBadge}
            </h5>
            <div class="download-meta">
                <span>
                    <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" fill="currentColor" class="bi bi-clock" viewBox="0 0 16 16">
                        <path d="M8 3.5a.5.5 0 0 0-1 0V9a.5.5 0 0 0 .252.434l3.5 2a.5.5 0 0 0 .496-.868L8 8.71V3.5z"/>
                        <path d="M8 16A8 8 0 1 0 8 0a8 8 0 0 0 0 16zm7-8A7 7 0 1 1 1 8a7 7 0 0 1 14 0z"/>
                    </svg>
                    ${download.download_time || 'Unknown time'}
                </span>
                ${download.file_size ? 
                    `<span>
                        <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" fill="currentColor" class="bi bi-file-earmark" viewBox="0 0 16 16">
                            <path d="M14 4.5V14a2 2 0 0 1-2 2H4a2 2 0 0 1-2-2V2a2 2 0 0 1 2-2h5.5L14 4.5zm-3 0A1.5 1.5 0 0 1 9.5 3V1H4a1 1 0 0 0-1 1v12a1 1 0 0 0 1 1h8a1 1 0 0 0 1-1V4.5h-2z"/>
                        </svg>
                        ${formatFileSize(download.file_size)}
                    </span>` 
                    : ''
                }
                ${download.mime_type ? 
                    `<span>
                        <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" fill="currentColor" class="bi bi-file-earmark-text" viewBox="0 0 16 16">
                            <path d="M5.5 7a.5.5 0 0 0 0 1h5a.5.5 0 0 0 0-1h-5zM5 9.5a.5.5 0 0 1 .5-.5h5a.5.5 0 0 1 0 1h-5a.5.5 0 0 1-.5-.5zm0 2a.5.5 0 0 1 .5-.5h2a.5.5 0 0 1 0 1h-2a.5.5 0 0 1-.5-.5z"/>
                            <path d="M9.5 0H4a2 2 0 0 0-2 2v12a2 2 0 0 0 2 2h8a2 2 0 0 0 2-2V4.5L9.5 0zm0 1v2A1.5 1.5 0 0 0 11 4.5h2V14a1 1 0 0 1-1 1H4a1 1 0 0 1-1-1V2a1 1 0 0 1 1-1h5.5z"/>
                        </svg>
                        ${download.mime_type}
                    </span>` 
                    : ''
                }
            </div>
            <div>
                <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" fill="currentColor" class="bi bi-link-45deg" viewBox="0 0 16 16">
                    <path d="M4.715 6.542 3.343 7.914a3 3 0 1 0 4.243 4.243l1.828-1.829A3 3 0 0 0 8.586 5.5L8 6.086a1.002 1.002 0 0 0-.154.199 2 2 0 0 1 .861 3.337L6.88 11.45a2 2 0 1 1-2.83-2.83l.793-.792a4.018 4.018 0 0 1-.128-1.287z"/>
                    <path d="M6.586 4.672A3 3 0 0 0 7.414 9.5l.775-.776a2 2 0 0 1-.896-3.346L9.12 3.55a2 2 0 1 1 2.83 2.83l-.793.792c.112.42.155.855.128 1.287l1.372-1.372a3 3 0 1 0-4.243-4.243L6.586 4.672z"/>
                </svg>
                <a href="#" title="${download.url}">${truncateText(download.url, 80)}</a>
            </div>
        `;
        
        // Add source references if available
        const sourceInfo = sourcesByFilename[download.filename];
        if (sourceInfo && sourceInfo.sources && sourceInfo.sources.length > 0) {
            try {
                addDownloadSources(downloadItem, sourceInfo);
            } catch (error) {
                console.error("Error adding download sources:", error);
            }
        }
        
        downloadsContainer.appendChild(downloadItem);
    });
}

// Add download sources to download item
function addDownloadSources(downloadItem, sourceInfo) {
    const sourcesContainer = document.createElement('div');
    sourcesContainer.className = 'mt-3';
    
    // Add toggle button for sources
    const toggleButton = document.createElement('button');
    toggleButton.className = 'toggle-sources';
    toggleButton.textContent = 'Show download sources';
    toggleButton.addEventListener('click', function() {
        const content = this.nextElementSibling;
        if (content.style.display === 'none') {
            content.style.display = 'block';
            this.textContent = 'Hide download sources';
        } else {
            content.style.display = 'none';
            this.textContent = 'Show download sources';
        }
    });
    
    sourcesContainer.appendChild(toggleButton);
    
    // Container for source items
    const sourcesContent = document.createElement('div');
    sourcesContent.style.display = 'none';
    
    // Add heading
    const heading = document.createElement('h6');
    heading.className = 'mt-2 mb-2';
    heading.textContent = 'Source Pages';
    sourcesContent.appendChild(heading);
    
    // Add source items
    sourceInfo.sources.forEach(source => {
        const sourceItem = document.createElement('div');
        sourceItem.className = `download-source ${source.match_type}`;
        
        sourceItem.innerHTML = `
            <div class="download-source-title">
                ${source.title || 'Unknown Page'}
                <span class="badge bg-${getBadgeColorForMatchType(source.match_type)}">${formatMatchType(source.match_type)}</span>
            </div>
            <div class="download-source-url">${truncateText(source.url, 80)}</div>
            <div class="download-source-time">${source.time}</div>
        `;
        
        sourcesContent.appendChild(sourceItem);
    });
    
    sourcesContainer.appendChild(sourcesContent);
    downloadItem.appendChild(sourcesContainer);
}

// Display sync information
function displaySyncInfo(syncInfo) {
    console.log("Displaying sync info");
    const syncContainer = getElementSafely('syncContainer');
    
    if (!syncContainer) {
        console.error("Sync container element not found");
        return;
    }
    
    syncContainer.innerHTML = '';
    
    if (!syncInfo || (Object.keys(syncInfo).length === 0)) {
        syncContainer.innerHTML = `
            <div class="empty-state">
                <p>🔄</p>
                <p>No synchronization information found</p>
                <p class="small text-muted">Browser synchronization data not detected in the analyzed file</p>
            </div>
        `;
        return;
    }
    
    // Display account information if available
    if (syncInfo.account_info) {
        try {
            displayAccountInfo(syncInfo.account_info, syncContainer);
        } catch (error) {
            console.error("Error displaying account info:", error);
        }
    }
    
    // Display sync settings if available
    if (syncInfo.sync_settings) {
        try {
            displaySyncSettings(syncInfo.sync_settings, syncContainer);
        } catch (error) {
            console.error("Error displaying sync settings:", error);
        }
    }
    
    // Display synced visits if available
    if (syncInfo.synced_visits && syncInfo.synced_visits.length > 0) {
        try {
            displaySyncedVisits(syncInfo.synced_visits, syncContainer);
        } catch (error) {
            console.error("Error displaying synced visits:", error);
        }
    }
}

// Display account information
function displayAccountInfo(accountInfo, container) {
    const accountCard = document.createElement('div');
    accountCard.className = 'card sync-info-card mb-4';
    
    accountCard.innerHTML = `
        <div class="card-header">
            <h5 class="mb-0">Sync Account Information</h5>
        </div>
        <div class="card-body">
            <div class="sync-account-info">
                <h6>Account Details</h6>
                <div><strong>Email:</strong> ${accountInfo.email || 'Not available'}</div>
                <div><strong>Account Name:</strong> ${accountInfo.name || 'Not available'}</div>
                <div><strong>Account Type:</strong> ${accountInfo.account_type || 'Not available'}</div>
                <div class="sync-timestamp"><strong>Last Sync Time:</strong> ${accountInfo.last_sync_time || 'Not available'}</div>
            </div>
        </div>
    `;
    
    container.appendChild(accountCard);
}

// Display sync settings
function displaySyncSettings(syncSettings, container) {
    const settingsCard = document.createElement('div');
    settingsCard.className = 'card sync-info-card mb-4';
    
    let dataTypesHTML = '';
    if (syncSettings.data_types && syncSettings.data_types.length > 0) {
        dataTypesHTML = `
            <h6>Synchronized Data Types</h6>
            <div class="sync-data-types">
        `;
        
        syncSettings.data_types.forEach(type => {
            const statusClass = type.enabled ? 'enabled' : 'disabled';
            dataTypesHTML += `
                <div class="sync-data-type ${statusClass}">
                    ${type.name} ${type.enabled ? '✓' : '✗'}
                </div>
            `;
        });
        
        dataTypesHTML += '</div>';
    }
    
    settingsCard.innerHTML = `
        <div class="card-header">
            <h5 class="mb-0">Sync Settings</h5>
        </div>
        <div class="card-body">
            <div><strong>Sync Enabled:</strong> ${syncSettings.enabled ? 'Yes' : 'No'}</div>
            <div><strong>First Sync Time:</strong> ${syncSettings.first_sync_time || 'Not available'}</div>
            <div><strong>Last Sync Time:</strong> ${syncSettings.last_sync_time || 'Not available'}</div>
            ${dataTypesHTML}
        </div>
    `;
    
    container.appendChild(settingsCard);
}

// Display synced visits
function displaySyncedVisits(syncedVisits, container) {
    const visitsCard = document.createElement('div');
    visitsCard.className = 'card sync-info-card';
    
    let visitsHTML = `
        <div class="card-header">
            <h5 class="mb-0">Synchronized Visits</h5>
        </div>
        <div class="card-body">
            <div class="table-container sync-visit-table">
                <table class="table table-striped table-hover">
                    <thead>
                        <tr>
                            <th>Title</th>
                            <th>URL</th>
                            <th>Visit Time</th>
                            <th>Source</th>
                        </tr>
                    </thead>
                    <tbody>
    `;
    
    syncedVisits.forEach(visit => {
        // Determine source badge class
        let sourceClass = '';
        let sourceText = visit.source_desc || '';
        
        if (sourceText.includes('Synchronised')) {
            sourceClass = 'source-synced';
        } else if (sourceText.includes('User browsed')) {
            sourceClass = 'source-browsed';
        } else if (sourceText.includes('Extension')) {
            sourceClass = 'source-extension';
        } else if (sourceText.includes('Imported')) {
            sourceClass = 'source-imported';
        }
        
        visitsHTML += `
            <tr>
                <td>${visit.title || 'Unknown'}</td>
                <td><a href="#" title="${visit.url}">${truncateText(visit.url, 50)}</a></td>
                <td>${visit.visit_time}</td>
                <td><span class="visit-source-badge ${sourceClass}">${sourceText}</span></td>
            </tr>
        `;
    });
    
    visitsHTML += `
                </tbody>
            </table>
        </div>
    </div>
    `;
    
    visitsCard.innerHTML = visitsHTML;
    container.appendChild(visitsCard);
}

// Filter table based on search input
function filterTable() {
    const searchInput = getElementSafely('searchInput');
    const historyTableBody = getElementSafely('historyTableBody');
    
    if (!searchInput || !historyTableBody) {
        console.error("Search input or history table body not found");
        return;
    }
    
    const searchTerm = searchInput.value.toLowerCase();
    const rows = historyTableBody.querySelectorAll('tr');
    
    rows.forEach(row => {
        const text = row.textContent.toLowerCase();
        if (text.includes(searchTerm)) {
            row.style.display = '';
        } else {
            row.style.display = 'none';
        }
    });
}

// Filter downloads based on search input
function filterDownloads() {
    const downloadSearchInput = getElementSafely('downloadSearchInput');
    const downloadsContainer = getElementSafely('downloadsContainer');
    
    if (!downloadSearchInput || !downloadsContainer) {
        console.error("Download search input or downloads container not found");
        return;
    }
    
    const searchTerm = downloadSearchInput.value.toLowerCase();
    const downloadItems = downloadsContainer.querySelectorAll('.download-item');
    
    downloadItems.forEach(item => {
        const filename = item.getAttribute('data-filename').toLowerCase();
        const url = item.getAttribute('data-url').toLowerCase();
        const text = item.textContent.toLowerCase();
        
        if (filename.includes(searchTerm) || url.includes(searchTerm) || text.includes(searchTerm)) {
            item.style.display = '';
        } else {
            item.style.display = 'none';
        }
    });
}