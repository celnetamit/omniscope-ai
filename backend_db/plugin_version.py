"""
Plugin Version Management for OmniScope AI
Handles semantic versioning, updates, and rollbacks
"""

from sqlalchemy.orm import Session
from sqlalchemy import Column, String, Text, DateTime, Boolean, ForeignKey, Integer
from sqlalchemy.sql import func
from typing import List, Dict, Any, Optional, Tuple
from datetime import datetime
import uuid
import re
import shutil
import os

from .models import Base


class PluginVersion(Base):
    """Model for plugin versions"""
    __tablename__ = "plugin_versions"
    
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    plugin_id = Column(String, nullable=False, index=True)
    version = Column(String(50), nullable=False)
    changelog = Column(Text)
    release_notes = Column(Text)
    
    # Version metadata
    major = Column(Integer, nullable=False)
    minor = Column(Integer, nullable=False)
    patch = Column(Integer, nullable=False)
    prerelease = Column(String(50))
    build = Column(String(50))
    
    # Status
    is_stable = Column(Boolean, default=True)
    is_deprecated = Column(Boolean, default=False)
    deprecation_message = Column(Text)
    
    # Files
    install_path = Column(String(500))
    checksum = Column(String(64))  # SHA-256 checksum
    
    # Compatibility
    min_platform_version = Column(String(50))
    max_platform_version = Column(String(50))
    breaking_changes = Column(Text)
    
    created_at = Column(DateTime, default=func.now())
    published_at = Column(DateTime)


class PluginUpdate(Base):
    """Model for plugin update history"""
    __tablename__ = "plugin_updates"
    
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    plugin_id = Column(String, nullable=False, index=True)
    from_version = Column(String(50), nullable=False)
    to_version = Column(String(50), nullable=False)
    user_id = Column(String)
    status = Column(String(50), nullable=False)  # success, failed, rolled_back
    error_message = Column(Text)
    updated_at = Column(DateTime, default=func.now())


class PluginRollback(Base):
    """Model for plugin rollback history"""
    __tablename__ = "plugin_rollbacks"
    
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    plugin_id = Column(String, nullable=False, index=True)
    from_version = Column(String(50), nullable=False)
    to_version = Column(String(50), nullable=False)
    user_id = Column(String)
    reason = Column(Text)
    rolled_back_at = Column(DateTime, default=func.now())


class SemanticVersion:
    """Semantic version parser and comparator"""
    
    VERSION_PATTERN = re.compile(
        r'^(?P<major>0|[1-9]\d*)\.(?P<minor>0|[1-9]\d*)\.(?P<patch>0|[1-9]\d*)'
        r'(?:-(?P<prerelease>(?:0|[1-9]\d*|\d*[a-zA-Z-][0-9a-zA-Z-]*)'
        r'(?:\.(?:0|[1-9]\d*|\d*[a-zA-Z-][0-9a-zA-Z-]*))*))?'
        r'(?:\+(?P<build>[0-9a-zA-Z-]+(?:\.[0-9a-zA-Z-]+)*))?$'
    )
    
    def __init__(self, version_string: str):
        """
        Parse semantic version string
        
        Args:
            version_string: Version string (e.g., "1.2.3-alpha.1+build.123")
        """
        match = self.VERSION_PATTERN.match(version_string)
        if not match:
            raise ValueError(f"Invalid semantic version: {version_string}")
        
        self.major = int(match.group('major'))
        self.minor = int(match.group('minor'))
        self.patch = int(match.group('patch'))
        self.prerelease = match.group('prerelease')
        self.build = match.group('build')
        self.version_string = version_string
    
    def __str__(self) -> str:
        return self.version_string
    
    def __eq__(self, other: 'SemanticVersion') -> bool:
        return self._compare(other) == 0
    
    def __lt__(self, other: 'SemanticVersion') -> bool:
        return self._compare(other) < 0
    
    def __le__(self, other: 'SemanticVersion') -> bool:
        return self._compare(other) <= 0
    
    def __gt__(self, other: 'SemanticVersion') -> bool:
        return self._compare(other) > 0
    
    def __ge__(self, other: 'SemanticVersion') -> bool:
        return self._compare(other) >= 0
    
    def _compare(self, other: 'SemanticVersion') -> int:
        """Compare versions"""
        # Compare major, minor, patch
        if self.major != other.major:
            return self.major - other.major
        if self.minor != other.minor:
            return self.minor - other.minor
        if self.patch != other.patch:
            return self.patch - other.patch
        
        # Compare prerelease
        if self.prerelease is None and other.prerelease is None:
            return 0
        if self.prerelease is None:
            return 1  # Release version > prerelease
        if other.prerelease is None:
            return -1
        
        # Compare prerelease identifiers
        self_parts = self.prerelease.split('.')
        other_parts = other.prerelease.split('.')
        
        for i in range(max(len(self_parts), len(other_parts))):
            if i >= len(self_parts):
                return -1
            if i >= len(other_parts):
                return 1
            
            self_part = self_parts[i]
            other_part = other_parts[i]
            
            # Try numeric comparison
            try:
                self_num = int(self_part)
                other_num = int(other_part)
                if self_num != other_num:
                    return self_num - other_num
            except ValueError:
                # Lexical comparison
                if self_part != other_part:
                    return -1 if self_part < other_part else 1
        
        return 0
    
    def is_compatible_with(self, other: 'SemanticVersion') -> bool:
        """
        Check if versions are compatible (same major version)
        
        Args:
            other: Other version
        
        Returns:
            bool: True if compatible
        """
        return self.major == other.major


class PluginVersionManager:
    """Service for plugin version management"""
    
    @staticmethod
    def add_version(
        db: Session,
        plugin_id: str,
        version: str,
        install_path: str,
        changelog: Optional[str] = None,
        release_notes: Optional[str] = None,
        min_platform_version: Optional[str] = None,
        max_platform_version: Optional[str] = None,
        breaking_changes: Optional[str] = None,
        is_stable: bool = True
    ) -> PluginVersion:
        """
        Add a new plugin version
        
        Args:
            db: Database session
            plugin_id: Plugin ID
            version: Version string
            install_path: Installation path
            changelog: Changelog
            release_notes: Release notes
            min_platform_version: Minimum platform version
            max_platform_version: Maximum platform version
            breaking_changes: Breaking changes description
            is_stable: Whether this is a stable release
        
        Returns:
            PluginVersion: Version record
        """
        # Parse version
        sem_ver = SemanticVersion(version)
        
        # Check if version already exists
        existing = db.query(PluginVersion).filter(
            PluginVersion.plugin_id == plugin_id,
            PluginVersion.version == version
        ).first()
        
        if existing:
            raise ValueError(f"Version {version} already exists for this plugin")
        
        # Calculate checksum
        checksum = PluginVersionManager._calculate_checksum(install_path)
        
        plugin_version = PluginVersion(
            plugin_id=plugin_id,
            version=version,
            major=sem_ver.major,
            minor=sem_ver.minor,
            patch=sem_ver.patch,
            prerelease=sem_ver.prerelease,
            build=sem_ver.build,
            changelog=changelog,
            release_notes=release_notes,
            install_path=install_path,
            checksum=checksum,
            min_platform_version=min_platform_version,
            max_platform_version=max_platform_version,
            breaking_changes=breaking_changes,
            is_stable=is_stable,
            published_at=datetime.utcnow()
        )
        
        db.add(plugin_version)
        db.commit()
        db.refresh(plugin_version)
        
        return plugin_version
    
    @staticmethod
    def get_latest_version(
        db: Session,
        plugin_id: str,
        stable_only: bool = True
    ) -> Optional[PluginVersion]:
        """
        Get latest version of a plugin
        
        Args:
            db: Database session
            plugin_id: Plugin ID
            stable_only: Only consider stable versions
        
        Returns:
            PluginVersion: Latest version or None
        """
        query = db.query(PluginVersion).filter(
            PluginVersion.plugin_id == plugin_id,
            PluginVersion.is_deprecated == False
        )
        
        if stable_only:
            query = query.filter(PluginVersion.is_stable == True)
        
        versions = query.all()
        
        if not versions:
            return None
        
        # Sort by semantic version
        sorted_versions = sorted(
            versions,
            key=lambda v: SemanticVersion(v.version),
            reverse=True
        )
        
        return sorted_versions[0]
    
    @staticmethod
    def list_versions(
        db: Session,
        plugin_id: str,
        include_deprecated: bool = False
    ) -> List[PluginVersion]:
        """
        List all versions of a plugin
        
        Args:
            db: Database session
            plugin_id: Plugin ID
            include_deprecated: Include deprecated versions
        
        Returns:
            List[PluginVersion]: List of versions
        """
        query = db.query(PluginVersion).filter(
            PluginVersion.plugin_id == plugin_id
        )
        
        if not include_deprecated:
            query = query.filter(PluginVersion.is_deprecated == False)
        
        versions = query.all()
        
        # Sort by semantic version (newest first)
        return sorted(
            versions,
            key=lambda v: SemanticVersion(v.version),
            reverse=True
        )
    
    @staticmethod
    def update_plugin(
        db: Session,
        plugin_id: str,
        current_version: str,
        target_version: str,
        user_id: Optional[str] = None
    ) -> Tuple[bool, str]:
        """
        Update plugin to a new version
        
        Args:
            db: Database session
            plugin_id: Plugin ID
            current_version: Current version
            target_version: Target version
            user_id: User ID
        
        Returns:
            Tuple[bool, str]: (success, message)
        """
        # Get version records
        current = db.query(PluginVersion).filter(
            PluginVersion.plugin_id == plugin_id,
            PluginVersion.version == current_version
        ).first()
        
        target = db.query(PluginVersion).filter(
            PluginVersion.plugin_id == plugin_id,
            PluginVersion.version == target_version
        ).first()
        
        if not current:
            return False, f"Current version {current_version} not found"
        
        if not target:
            return False, f"Target version {target_version} not found"
        
        # Check compatibility
        current_sem = SemanticVersion(current_version)
        target_sem = SemanticVersion(target_version)
        
        if not current_sem.is_compatible_with(target_sem):
            if target.breaking_changes:
                message = f"Breaking changes in {target_version}: {target.breaking_changes}"
            else:
                message = f"Major version change from {current_version} to {target_version}"
        else:
            message = f"Updated from {current_version} to {target_version}"
        
        # Record update
        update_record = PluginUpdate(
            plugin_id=plugin_id,
            from_version=current_version,
            to_version=target_version,
            user_id=user_id,
            status='success'
        )
        
        db.add(update_record)
        db.commit()
        
        return True, message
    
    @staticmethod
    def rollback_plugin(
        db: Session,
        plugin_id: str,
        current_version: str,
        target_version: str,
        user_id: Optional[str] = None,
        reason: Optional[str] = None
    ) -> Tuple[bool, str]:
        """
        Rollback plugin to a previous version
        
        Args:
            db: Database session
            plugin_id: Plugin ID
            current_version: Current version
            target_version: Target version to rollback to
            user_id: User ID
            reason: Rollback reason
        
        Returns:
            Tuple[bool, str]: (success, message)
        """
        # Verify versions exist
        current = db.query(PluginVersion).filter(
            PluginVersion.plugin_id == plugin_id,
            PluginVersion.version == current_version
        ).first()
        
        target = db.query(PluginVersion).filter(
            PluginVersion.plugin_id == plugin_id,
            PluginVersion.version == target_version
        ).first()
        
        if not current:
            return False, f"Current version {current_version} not found"
        
        if not target:
            return False, f"Target version {target_version} not found"
        
        # Verify target is older
        current_sem = SemanticVersion(current_version)
        target_sem = SemanticVersion(target_version)
        
        if target_sem >= current_sem:
            return False, "Target version must be older than current version"
        
        # Record rollback
        rollback_record = PluginRollback(
            plugin_id=plugin_id,
            from_version=current_version,
            to_version=target_version,
            user_id=user_id,
            reason=reason
        )
        
        db.add(rollback_record)
        db.commit()
        
        return True, f"Rolled back from {current_version} to {target_version}"
    
    @staticmethod
    def deprecate_version(
        db: Session,
        plugin_id: str,
        version: str,
        message: Optional[str] = None
    ) -> PluginVersion:
        """
        Mark a version as deprecated
        
        Args:
            db: Database session
            plugin_id: Plugin ID
            version: Version to deprecate
            message: Deprecation message
        
        Returns:
            PluginVersion: Updated version record
        """
        plugin_version = db.query(PluginVersion).filter(
            PluginVersion.plugin_id == plugin_id,
            PluginVersion.version == version
        ).first()
        
        if not plugin_version:
            raise ValueError(f"Version {version} not found")
        
        plugin_version.is_deprecated = True
        plugin_version.deprecation_message = message
        
        db.commit()
        db.refresh(plugin_version)
        
        return plugin_version
    
    @staticmethod
    def get_update_history(
        db: Session,
        plugin_id: str,
        limit: int = 50
    ) -> List[PluginUpdate]:
        """
        Get plugin update history
        
        Args:
            db: Database session
            plugin_id: Plugin ID
            limit: Maximum records
        
        Returns:
            List[PluginUpdate]: Update history
        """
        return db.query(PluginUpdate).filter(
            PluginUpdate.plugin_id == plugin_id
        ).order_by(
            PluginUpdate.updated_at.desc()
        ).limit(limit).all()
    
    @staticmethod
    def _calculate_checksum(path: str) -> str:
        """Calculate SHA-256 checksum of plugin files"""
        import hashlib
        
        hasher = hashlib.sha256()
        
        if os.path.isfile(path):
            with open(path, 'rb') as f:
                hasher.update(f.read())
        elif os.path.isdir(path):
            for root, dirs, files in os.walk(path):
                for file in sorted(files):
                    file_path = os.path.join(root, file)
                    with open(file_path, 'rb') as f:
                        hasher.update(f.read())
        
        return hasher.hexdigest()
