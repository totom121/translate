"""
Translation caching system for improved performance.
"""

import time
import threading
from typing import Dict, Optional, Any
from dataclasses import dataclass
from collections import OrderedDict

@dataclass
class CacheEntry:
    """Cache entry with timestamp and data."""
    data: Any
    timestamp: float
    access_count: int = 0
    
    def is_expired(self, ttl_hours: float) -> bool:
        """Check if the cache entry has expired."""
        return time.time() - self.timestamp > (ttl_hours * 3600)
    
    def touch(self):
        """Update access count and timestamp."""
        self.access_count += 1
        self.timestamp = time.time()

class TranslationCache:
    """
    Thread-safe LRU cache with TTL for translation results.
    
    Features:
    - Least Recently Used (LRU) eviction policy
    - Time-to-Live (TTL) expiration
    - Thread-safe operations
    - Cache statistics
    - Memory-efficient storage
    """
    
    def __init__(self, max_size: int = 10000, ttl_hours: float = 24):
        """
        Initialize the translation cache.
        
        Args:
            max_size: Maximum number of entries to store
            ttl_hours: Time-to-live in hours for cache entries
        """
        self.max_size = max_size
        self.ttl_hours = ttl_hours
        self._cache: OrderedDict[str, CacheEntry] = OrderedDict()
        self._lock = threading.RLock()
        
        # Statistics
        self._stats = {
            'hits': 0,
            'misses': 0,
            'evictions': 0,
            'expirations': 0,
            'total_size': 0
        }
    
    def get(self, key: str) -> Optional[Any]:
        """
        Get a value from the cache.
        
        Args:
            key: Cache key
            
        Returns:
            Cached value or None if not found/expired
        """
        with self._lock:
            if key not in self._cache:
                self._stats['misses'] += 1
                return None
            
            entry = self._cache[key]
            
            # Check if expired
            if entry.is_expired(self.ttl_hours):
                del self._cache[key]
                self._stats['expirations'] += 1
                self._stats['misses'] += 1
                return None
            
            # Move to end (most recently used)
            self._cache.move_to_end(key)
            entry.touch()
            
            self._stats['hits'] += 1
            return entry.data
    
    def set(self, key: str, value: Any) -> None:
        """
        Set a value in the cache.
        
        Args:
            key: Cache key
            value: Value to cache
        """
        with self._lock:
            # If key exists, update it
            if key in self._cache:
                self._cache[key].data = value
                self._cache[key].touch()
                self._cache.move_to_end(key)
                return
            
            # Add new entry
            entry = CacheEntry(data=value, timestamp=time.time())
            self._cache[key] = entry
            
            # Evict oldest entries if over capacity
            while len(self._cache) > self.max_size:
                oldest_key = next(iter(self._cache))
                del self._cache[oldest_key]
                self._stats['evictions'] += 1
            
            self._stats['total_size'] = len(self._cache)
    
    def delete(self, key: str) -> bool:
        """
        Delete a key from the cache.
        
        Args:
            key: Cache key to delete
            
        Returns:
            True if key was deleted, False if not found
        """
        with self._lock:
            if key in self._cache:
                del self._cache[key]
                self._stats['total_size'] = len(self._cache)
                return True
            return False
    
    def clear(self) -> None:
        """Clear all entries from the cache."""
        with self._lock:
            self._cache.clear()
            self._stats['total_size'] = 0
    
    def cleanup_expired(self) -> int:
        """
        Remove all expired entries from the cache.
        
        Returns:
            Number of entries removed
        """
        with self._lock:
            expired_keys = []
            
            for key, entry in self._cache.items():
                if entry.is_expired(self.ttl_hours):
                    expired_keys.append(key)
            
            for key in expired_keys:
                del self._cache[key]
                self._stats['expirations'] += 1
            
            self._stats['total_size'] = len(self._cache)
            return len(expired_keys)
    
    def get_statistics(self) -> Dict[str, Any]:
        """
        Get cache statistics.
        
        Returns:
            Dictionary with cache statistics
        """
        with self._lock:
            stats = self._stats.copy()
            stats['current_size'] = len(self._cache)
            stats['max_size'] = self.max_size
            stats['ttl_hours'] = self.ttl_hours
            
            total_requests = stats['hits'] + stats['misses']
            if total_requests > 0:
                stats['hit_rate'] = (stats['hits'] / total_requests) * 100
                stats['miss_rate'] = (stats['misses'] / total_requests) * 100
            else:
                stats['hit_rate'] = 0.0
                stats['miss_rate'] = 0.0
            
            # Memory usage estimation (rough)
            if self._cache:
                avg_entry_size = sum(
                    len(str(entry.data)) + len(key) 
                    for key, entry in list(self._cache.items())[:min(100, len(self._cache))]
                ) / min(100, len(self._cache))
                stats['estimated_memory_bytes'] = avg_entry_size * len(self._cache)
            else:
                stats['estimated_memory_bytes'] = 0
            
            return stats
    
    def get_top_accessed(self, limit: int = 10) -> Dict[str, int]:
        """
        Get the most frequently accessed cache entries.
        
        Args:
            limit: Maximum number of entries to return
            
        Returns:
            Dictionary mapping keys to access counts
        """
        with self._lock:
            sorted_entries = sorted(
                self._cache.items(),
                key=lambda x: x[1].access_count,
                reverse=True
            )
            
            return {
                key: entry.access_count 
                for key, entry in sorted_entries[:limit]
            }
    
    def resize(self, new_max_size: int) -> None:
        """
        Resize the cache to a new maximum size.
        
        Args:
            new_max_size: New maximum cache size
        """
        with self._lock:
            self.max_size = new_max_size
            
            # Evict entries if current size exceeds new max size
            while len(self._cache) > self.max_size:
                oldest_key = next(iter(self._cache))
                del self._cache[oldest_key]
                self._stats['evictions'] += 1
            
            self._stats['total_size'] = len(self._cache)
    
    def __len__(self) -> int:
        """Get the current number of entries in the cache."""
        with self._lock:
            return len(self._cache)
    
    def __contains__(self, key: str) -> bool:
        """Check if a key exists in the cache (without updating access)."""
        with self._lock:
            if key not in self._cache:
                return False
            
            entry = self._cache[key]
            return not entry.is_expired(self.ttl_hours)

