"""
Plugin Marketplace for OmniScope AI
Provides plugin discovery, ratings, and reviews
"""

from sqlalchemy.orm import Session
from sqlalchemy import Column, String, Text, DateTime, Integer, Float, Boolean, ForeignKey, and_, or_
from sqlalchemy.sql import func
from typing import List, Dict, Any, Optional
from datetime import datetime
import uuid

from .models import Base


class MarketplacePlugin(Base):
    """Model for marketplace plugin listings"""
    __tablename__ = "marketplace_plugins"
    
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    name = Column(String(255), nullable=False, unique=True, index=True)
    version = Column(String(50), nullable=False)
    author = Column(String(255), nullable=False)
    author_email = Column(String(255))
    description = Column(Text, nullable=False)
    long_description = Column(Text)
    language = Column(String(20), nullable=False)
    category = Column(String(100), nullable=False, index=True)
    tags = Column(String(500))  # Comma-separated tags
    extension_points = Column(String(500))  # Comma-separated extension points
    
    # Marketplace metadata
    downloads = Column(Integer, default=0)
    rating_average = Column(Float, default=0.0)
    rating_count = Column(Integer, default=0)
    verified = Column(Boolean, default=False)
    featured = Column(Boolean, default=False)
    
    # Version info
    latest_version = Column(String(50))
    changelog = Column(Text)
    
    # Links
    homepage_url = Column(String(500))
    repository_url = Column(String(500))
    documentation_url = Column(String(500))
    
    # Requirements
    min_platform_version = Column(String(50))
    dependencies = Column(Text)  # JSON string
    
    # Status
    status = Column(String(50), default='pending')  # pending, approved, rejected
    published_at = Column(DateTime)
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())


class PluginRating(Base):
    """Model for plugin ratings"""
    __tablename__ = "plugin_ratings"
    
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    plugin_id = Column(String, ForeignKey('marketplace_plugins.id'), nullable=False, index=True)
    user_id = Column(String, nullable=False, index=True)
    rating = Column(Integer, nullable=False)  # 1-5 stars
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())


class PluginReview(Base):
    """Model for plugin reviews"""
    __tablename__ = "plugin_reviews"
    
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    plugin_id = Column(String, ForeignKey('marketplace_plugins.id'), nullable=False, index=True)
    user_id = Column(String, nullable=False, index=True)
    rating = Column(Integer, nullable=False)  # 1-5 stars
    title = Column(String(255))
    review_text = Column(Text, nullable=False)
    helpful_count = Column(Integer, default=0)
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())


class PluginDownload(Base):
    """Model for tracking plugin downloads"""
    __tablename__ = "plugin_downloads"
    
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    plugin_id = Column(String, ForeignKey('marketplace_plugins.id'), nullable=False, index=True)
    user_id = Column(String, index=True)
    version = Column(String(50))
    downloaded_at = Column(DateTime, default=func.now(), index=True)


class MarketplaceService:
    """Service for plugin marketplace operations"""
    
    @staticmethod
    def publish_plugin(
        db: Session,
        name: str,
        version: str,
        author: str,
        description: str,
        language: str,
        category: str,
        author_email: Optional[str] = None,
        long_description: Optional[str] = None,
        tags: List[str] = None,
        extension_points: List[str] = None,
        homepage_url: Optional[str] = None,
        repository_url: Optional[str] = None,
        documentation_url: Optional[str] = None,
        dependencies: Optional[str] = None,
        min_platform_version: Optional[str] = None
    ) -> MarketplacePlugin:
        """
        Publish a plugin to the marketplace
        
        Args:
            db: Database session
            name: Plugin name
            version: Plugin version
            author: Author name
            description: Short description
            language: Programming language
            category: Plugin category
            ... (other optional parameters)
        
        Returns:
            MarketplacePlugin: Published plugin
        """
        # Check if plugin already exists
        existing = db.query(MarketplacePlugin).filter(
            MarketplacePlugin.name == name
        ).first()
        
        if existing:
            raise ValueError(f"Plugin '{name}' already exists in marketplace")
        
        plugin = MarketplacePlugin(
            name=name,
            version=version,
            latest_version=version,
            author=author,
            author_email=author_email,
            description=description,
            long_description=long_description,
            language=language,
            category=category,
            tags=','.join(tags) if tags else '',
            extension_points=','.join(extension_points) if extension_points else '',
            homepage_url=homepage_url,
            repository_url=repository_url,
            documentation_url=documentation_url,
            dependencies=dependencies,
            min_platform_version=min_platform_version,
            status='pending'
        )
        
        db.add(plugin)
        db.commit()
        db.refresh(plugin)
        
        return plugin
    
    @staticmethod
    def search_plugins(
        db: Session,
        query: Optional[str] = None,
        category: Optional[str] = None,
        language: Optional[str] = None,
        tags: List[str] = None,
        extension_point: Optional[str] = None,
        verified_only: bool = False,
        sort_by: str = 'downloads',  # downloads, rating, recent
        limit: int = 50,
        offset: int = 0
    ) -> List[MarketplacePlugin]:
        """
        Search for plugins in marketplace
        
        Args:
            db: Database session
            query: Search query
            category: Filter by category
            language: Filter by language
            tags: Filter by tags
            extension_point: Filter by extension point
            verified_only: Only show verified plugins
            sort_by: Sort order
            limit: Maximum results
            offset: Result offset
        
        Returns:
            List[MarketplacePlugin]: Matching plugins
        """
        q = db.query(MarketplacePlugin).filter(
            MarketplacePlugin.status == 'approved'
        )
        
        # Apply filters
        if query:
            search_pattern = f"%{query}%"
            q = q.filter(
                or_(
                    MarketplacePlugin.name.ilike(search_pattern),
                    MarketplacePlugin.description.ilike(search_pattern),
                    MarketplacePlugin.tags.ilike(search_pattern)
                )
            )
        
        if category:
            q = q.filter(MarketplacePlugin.category == category)
        
        if language:
            q = q.filter(MarketplacePlugin.language == language)
        
        if tags:
            for tag in tags:
                q = q.filter(MarketplacePlugin.tags.ilike(f"%{tag}%"))
        
        if extension_point:
            q = q.filter(
                MarketplacePlugin.extension_points.ilike(f"%{extension_point}%")
            )
        
        if verified_only:
            q = q.filter(MarketplacePlugin.verified == True)
        
        # Apply sorting
        if sort_by == 'downloads':
            q = q.order_by(MarketplacePlugin.downloads.desc())
        elif sort_by == 'rating':
            q = q.order_by(MarketplacePlugin.rating_average.desc())
        elif sort_by == 'recent':
            q = q.order_by(MarketplacePlugin.published_at.desc())
        else:
            q = q.order_by(MarketplacePlugin.name)
        
        return q.limit(limit).offset(offset).all()
    
    @staticmethod
    def get_plugin_details(
        db: Session,
        plugin_id: str
    ) -> Optional[Dict[str, Any]]:
        """
        Get detailed plugin information
        
        Args:
            db: Database session
            plugin_id: Plugin ID
        
        Returns:
            Dict: Plugin details with ratings and reviews
        """
        plugin = db.query(MarketplacePlugin).filter(
            MarketplacePlugin.id == plugin_id
        ).first()
        
        if not plugin:
            return None
        
        # Get recent reviews
        reviews = db.query(PluginReview).filter(
            PluginReview.plugin_id == plugin_id
        ).order_by(
            PluginReview.created_at.desc()
        ).limit(10).all()
        
        return {
            'plugin': plugin,
            'reviews': reviews,
            'total_reviews': db.query(PluginReview).filter(
                PluginReview.plugin_id == plugin_id
            ).count()
        }
    
    @staticmethod
    def rate_plugin(
        db: Session,
        plugin_id: str,
        user_id: str,
        rating: int
    ) -> PluginRating:
        """
        Rate a plugin
        
        Args:
            db: Database session
            plugin_id: Plugin ID
            user_id: User ID
            rating: Rating (1-5)
        
        Returns:
            PluginRating: Rating record
        """
        if not 1 <= rating <= 5:
            raise ValueError("Rating must be between 1 and 5")
        
        # Check if user already rated
        existing = db.query(PluginRating).filter(
            and_(
                PluginRating.plugin_id == plugin_id,
                PluginRating.user_id == user_id
            )
        ).first()
        
        if existing:
            # Update existing rating
            existing.rating = rating
            existing.updated_at = datetime.utcnow()
            rating_record = existing
        else:
            # Create new rating
            rating_record = PluginRating(
                plugin_id=plugin_id,
                user_id=user_id,
                rating=rating
            )
            db.add(rating_record)
        
        # Update plugin average rating
        MarketplaceService._update_plugin_rating(db, plugin_id)
        
        db.commit()
        db.refresh(rating_record)
        
        return rating_record
    
    @staticmethod
    def add_review(
        db: Session,
        plugin_id: str,
        user_id: str,
        rating: int,
        title: str,
        review_text: str
    ) -> PluginReview:
        """
        Add a plugin review
        
        Args:
            db: Database session
            plugin_id: Plugin ID
            user_id: User ID
            rating: Rating (1-5)
            title: Review title
            review_text: Review text
        
        Returns:
            PluginReview: Review record
        """
        if not 1 <= rating <= 5:
            raise ValueError("Rating must be between 1 and 5")
        
        # Check if user already reviewed
        existing = db.query(PluginReview).filter(
            and_(
                PluginReview.plugin_id == plugin_id,
                PluginReview.user_id == user_id
            )
        ).first()
        
        if existing:
            raise ValueError("User has already reviewed this plugin")
        
        review = PluginReview(
            plugin_id=plugin_id,
            user_id=user_id,
            rating=rating,
            title=title,
            review_text=review_text
        )
        
        db.add(review)
        
        # Also add/update rating
        MarketplaceService.rate_plugin(db, plugin_id, user_id, rating)
        
        db.commit()
        db.refresh(review)
        
        return review
    
    @staticmethod
    def record_download(
        db: Session,
        plugin_id: str,
        user_id: Optional[str],
        version: str
    ) -> PluginDownload:
        """
        Record a plugin download
        
        Args:
            db: Database session
            plugin_id: Plugin ID
            user_id: User ID (optional)
            version: Downloaded version
        
        Returns:
            PluginDownload: Download record
        """
        download = PluginDownload(
            plugin_id=plugin_id,
            user_id=user_id,
            version=version
        )
        
        db.add(download)
        
        # Update plugin download count
        plugin = db.query(MarketplacePlugin).filter(
            MarketplacePlugin.id == plugin_id
        ).first()
        
        if plugin:
            plugin.downloads += 1
        
        db.commit()
        db.refresh(download)
        
        return download
    
    @staticmethod
    def get_featured_plugins(
        db: Session,
        limit: int = 10
    ) -> List[MarketplacePlugin]:
        """
        Get featured plugins
        
        Args:
            db: Database session
            limit: Maximum results
        
        Returns:
            List[MarketplacePlugin]: Featured plugins
        """
        return db.query(MarketplacePlugin).filter(
            and_(
                MarketplacePlugin.status == 'approved',
                MarketplacePlugin.featured == True
            )
        ).order_by(
            MarketplacePlugin.rating_average.desc()
        ).limit(limit).all()
    
    @staticmethod
    def get_popular_plugins(
        db: Session,
        limit: int = 10
    ) -> List[MarketplacePlugin]:
        """
        Get most popular plugins
        
        Args:
            db: Database session
            limit: Maximum results
        
        Returns:
            List[MarketplacePlugin]: Popular plugins
        """
        return db.query(MarketplacePlugin).filter(
            MarketplacePlugin.status == 'approved'
        ).order_by(
            MarketplacePlugin.downloads.desc()
        ).limit(limit).all()
    
    @staticmethod
    def get_categories(db: Session) -> List[Dict[str, Any]]:
        """
        Get all plugin categories with counts
        
        Args:
            db: Database session
        
        Returns:
            List[Dict]: Categories with plugin counts
        """
        from sqlalchemy import func
        
        results = db.query(
            MarketplacePlugin.category,
            func.count(MarketplacePlugin.id).label('count')
        ).filter(
            MarketplacePlugin.status == 'approved'
        ).group_by(
            MarketplacePlugin.category
        ).all()
        
        return [
            {'category': cat, 'count': count}
            for cat, count in results
        ]
    
    @staticmethod
    def _update_plugin_rating(db: Session, plugin_id: str):
        """Update plugin average rating"""
        from sqlalchemy import func
        
        result = db.query(
            func.avg(PluginRating.rating).label('avg'),
            func.count(PluginRating.id).label('count')
        ).filter(
            PluginRating.plugin_id == plugin_id
        ).first()
        
        plugin = db.query(MarketplacePlugin).filter(
            MarketplacePlugin.id == plugin_id
        ).first()
        
        if plugin and result:
            plugin.rating_average = float(result.avg) if result.avg else 0.0
            plugin.rating_count = result.count
