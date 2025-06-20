// Helper function to truncate text
function truncateText(text, maxLength) {
    if (!text) return '';
    return text.length > maxLength ? text.substring(0, maxLength) + '...' : text;
}

// Get badge color for match type
function getBadgeColorForMatchType(matchType) {
    switch (matchType) {
        case 'same_domain': return 'success';
        case 'file_pattern': return 'warning';
        case 'temporal': return 'secondary';
        default: return 'primary';
    }
}

// Format match type for display
function formatMatchType(matchType) {
    switch (matchType) {
        case 'same_domain': return 'Same Domain';
        case 'file_pattern': return 'File Pattern';
        case 'temporal': return 'Temporal';
        default: return matchType;
    }
}

// Format file size
function formatFileSize(bytes) {
    if (!bytes || isNaN(bytes)) return 'Unknown size';
    
    const units = ['B', 'KB', 'MB', 'GB', 'TB'];
    let size = parseInt(bytes, 10);
    let unitIndex = 0;
    
    while (size >= 1024 && unitIndex < units.length - 1) {
        size /= 1024;
        unitIndex++;
    }
    
    return `${size.toFixed(1)} ${units[unitIndex]}`;
}