from datetime import datetime
from typing import List, Dict, Optional, Any, Union

class HistoryEntry:
    """Model for a browser history entry"""
    def __init__(
        self, 
        id: int,
        url: str,
        title: Optional[str] = None,
        visit_time: Optional[str] = None,
        visit_count: int = 0,
        domain: Optional[str] = None
    ):
        self.id = id
        self.url = url
        self.title = title
        self.visit_time = visit_time
        self.visit_count = visit_count
        self.domain = domain
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        return {
            'id': self.id,
            'url': self.url,
            'title': self.title or '',
            'visit_time': self.visit_time or '',
            'visit_count': self.visit_count,
            'domain': self.domain or ''
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'HistoryEntry':
        """Create from dictionary"""
        return cls(
            id=data.get('id', 0),
            url=data.get('url', ''),
            title=data.get('title', ''),
            visit_time=data.get('visit_time', ''),
            visit_count=data.get('visit_count', 0),
            domain=data.get('domain', '')
        )

class DownloadItem:
    """Model for a browser download item"""
    def __init__(
        self,
        filename: str,
        url: str,
        download_time: Optional[str] = None,
        referrer: Optional[str] = None,
        file_size: Union[int, str] = 0,
        mime_type: Optional[str] = None,
        status: str = 'completed'
    ):
        self.filename = filename
        self.url = url
        self.download_time = download_time
        self.referrer = referrer
        self.file_size = file_size
        self.mime_type = mime_type
        self.status = status
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        return {
            'filename': self.filename,
            'url': self.url,
            'download_time': self.download_time or '',
            'referrer': self.referrer or '',
            'file_size': self.file_size or 0,
            'mime_type': self.mime_type or '',
            'status': self.status or 'unknown'
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'DownloadItem':
        """Create from dictionary"""
        return cls(
            filename=data.get('filename', ''),
            url=data.get('url', ''),
            download_time=data.get('download_time', ''),
            referrer=data.get('referrer', ''),
            file_size=data.get('file_size', 0),
            mime_type=data.get('mime_type', ''),
            status=data.get('status', 'completed')
        )

class DownloadSource:
    """Model for a source of a download"""
    def __init__(
        self,
        url: str,
        title: Optional[str] = None,
        time: Optional[str] = None,
        match_type: str = 'temporal'
    ):
        self.url = url
        self.title = title
        self.time = time
        self.match_type = match_type
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        return {
            'url': self.url,
            'title': self.title or '',
            'time': self.time or '',
            'match_type': self.match_type
        }

class DownloadSourceGroup:
    """Model for a group of sources for a download"""
    def __init__(
        self,
        filename: str,
        download_url: str,
        download_time: str,
        sources: List[DownloadSource] = None
    ):
        self.filename = filename
        self.download_url = download_url
        self.download_time = download_time
        self.sources = sources or []
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        return {
            'filename': self.filename,
            'download_url': self.download_url,
            'download_time': self.download_time,
            'sources': [source.to_dict() for source in self.sources]
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'DownloadSourceGroup':
        """Create from dictionary"""
        sources = []
        for source_data in data.get('sources', []):
            source = DownloadSource(
                url=source_data.get('url', ''),
                title=source_data.get('title', ''),
                time=source_data.get('time', ''),
                match_type=source_data.get('match_type', 'temporal')
            )
            sources.append(source)
        
        return cls(
            filename=data.get('filename', ''),
            download_url=data.get('download_url', ''),
            download_time=data.get('download_time', ''),
            sources=sources
        )

class SyncVisit:
    """Model for a synchronized visit"""
    def __init__(
        self,
        url: str,
        title: Optional[str] = None,
        visit_time: Optional[str] = None,
        source: Optional[int] = None,
        source_desc: Optional[str] = None
    ):
        self.url = url
        self.title = title
        self.visit_time = visit_time
        self.source = source
        self.source_desc = source_desc
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        return {
            'url': self.url,
            'title': self.title or '',
            'visit_time': self.visit_time or '',
            'source': self.source,
            'source_desc': self.source_desc or ''
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'SyncVisit':
        """Create from dictionary"""
        return cls(
            url=data.get('url', ''),
            title=data.get('title', ''),
            visit_time=data.get('visit_time', ''),
            source=data.get('source'),
            source_desc=data.get('source_desc', '')
        )

class SyncDataType:
    """Model for a synchronized data type"""
    def __init__(
        self,
        name: str,
        enabled: bool = False
    ):
        self.name = name
        self.enabled = enabled
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        return {
            'name': self.name,
            'enabled': self.enabled
        }

class SyncSettings:
    """Model for browser sync settings"""
    def __init__(
        self,
        enabled: bool = False,
        first_sync_time: Optional[str] = None,
        last_sync_time: Optional[str] = None,
        data_types: List[SyncDataType] = None
    ):
        self.enabled = enabled
        self.first_sync_time = first_sync_time
        self.last_sync_time = last_sync_time
        self.data_types = data_types or []
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        return {
            'enabled': self.enabled,
            'first_sync_time': self.first_sync_time or '',
            'last_sync_time': self.last_sync_time or '',
            'data_types': [data_type.to_dict() for data_type in self.data_types]
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'SyncSettings':
        """Create from dictionary"""
        data_types = []
        for dt_data in data.get('data_types', []):
            dt = SyncDataType(
                name=dt_data.get('name', ''),
                enabled=dt_data.get('enabled', False)
            )
            data_types.append(dt)
        
        return cls(
            enabled=data.get('enabled', False),
            first_sync_time=data.get('first_sync_time', ''),
            last_sync_time=data.get('last_sync_time', ''),
            data_types=data_types
        )

class AccountInfo:
    """Model for sync account information"""
    def __init__(
        self,
        email: Optional[str] = None,
        name: Optional[str] = None,
        account_type: Optional[str] = None,
        last_sync_time: Optional[str] = None
    ):
        self.email = email
        self.name = name
        self.account_type = account_type
        self.last_sync_time = last_sync_time
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        return {
            'email': self.email or '',
            'name': self.name or '',
            'account_type': self.account_type or '',
            'last_sync_time': self.last_sync_time or ''
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'AccountInfo':
        """Create from dictionary"""
        return cls(
            email=data.get('email', ''),
            name=data.get('name', ''),
            account_type=data.get('account_type', ''),
            last_sync_time=data.get('last_sync_time', '')
        )

class SyncInfo:
    """Model for browser synchronization information"""
    def __init__(
        self,
        account_info: Optional[AccountInfo] = None,
        sync_settings: Optional[SyncSettings] = None,
        synced_visits: List[SyncVisit] = None
    ):
        self.account_info = account_info
        self.sync_settings = sync_settings
        self.synced_visits = synced_visits or []
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        result = {}
        if self.account_info:
            result['account_info'] = self.account_info.to_dict()
        if self.sync_settings:
            result['sync_settings'] = self.sync_settings.to_dict()
        if self.synced_visits:
            result['synced_visits'] = [visit.to_dict() for visit in self.synced_visits]
        return result
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'SyncInfo':
        """Create from dictionary"""
        account_info = None
        if 'account_info' in data:
            account_info = AccountInfo.from_dict(data['account_info'])
        
        sync_settings = None
        if 'sync_settings' in data:
            sync_settings = SyncSettings.from_dict(data['sync_settings'])
        
        synced_visits = []
        for visit_data in data.get('synced_visits', []):
            visit = SyncVisit.from_dict(visit_data)
            synced_visits.append(visit)
        
        return cls(
            account_info=account_info,
            sync_settings=sync_settings,
            synced_visits=synced_visits
        )