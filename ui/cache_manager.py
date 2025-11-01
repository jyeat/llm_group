"""
Analysis Cache Manager

Manages caching of trading analysis results to avoid redundant API calls.
For historical dates, cached results are永久有效 (permanently valid).
"""

import json
from pathlib import Path
from datetime import datetime
from typing import Dict, Any, List, Optional


class CacheManager:
    """Manages analysis result caching"""
    
    def __init__(self, cache_dir: str = "analysis_cache"):
        self.cache_dir = Path(cache_dir)
        self.cache_dir.mkdir(exist_ok=True)
        self.index_file = self.cache_dir / "index.json"
        self.index = self._load_index()
    
    def _load_index(self) -> Dict[str, Any]:
        """Load the cache index"""
        if self.index_file.exists():
            try:
                with open(self.index_file, 'r') as f:
                    return json.load(f)
            except Exception as e:
                print(f"Error loading cache index: {e}")
                return {}
        return {}
    
    def _save_index(self):
        """Save the cache index"""
        try:
            with open(self.index_file, 'w') as f:
                json.dump(self.index, f, indent=2)
        except Exception as e:
            print(f"Error saving cache index: {e}")
    
    def _get_cache_key(self, ticker: str, date: str) -> str:
        """Generate cache key from ticker and date"""
        return f"{ticker}_{date}"
    
    def _get_cache_file(self, cache_key: str) -> Path:
        """Get cache file path for a given key"""
        return self.cache_dir / f"{cache_key}.json"
    
    def has_cache(self, ticker: str, date: str) -> bool:
        """Check if cache exists for ticker and date"""
        cache_key = self._get_cache_key(ticker, date)
        cache_file = self._get_cache_file(cache_key)
        return cache_file.exists()
    
    def get_cache(self, ticker: str, date: str) -> Optional[Dict[str, Any]]:
        """Get cached analysis result"""
        cache_key = self._get_cache_key(ticker, date)
        cache_file = self._get_cache_file(cache_key)
        
        if not cache_file.exists():
            return None
        
        try:
            with open(cache_file, 'r') as f:
                data = json.load(f)
                # Add cache metadata
                data['from_cache'] = True
                data['cached_at'] = self.index.get(cache_key, {}).get('cached_at', 'unknown')
                return data
        except Exception as e:
            print(f"Error loading cache for {cache_key}: {e}")
            return None
    
    def save_cache(self, ticker: str, date: str, result: Dict[str, Any]):
        """Save analysis result to cache"""
        cache_key = self._get_cache_key(ticker, date)
        cache_file = self._get_cache_file(cache_key)
        
        try:
            # Remove messages field if present (contains non-serializable objects)
            result_to_save = {k: v for k, v in result.items() if k != 'messages'}
            
            # Save the result
            with open(cache_file, 'w') as f:
                json.dump(result_to_save, f, indent=2)
            
            # Update index
            self.index[cache_key] = {
                'ticker': ticker,
                'date': date,
                'cached_at': datetime.now().isoformat(),
                'decision': result.get('decision', 'unknown'),
                'confidence': result.get('confidence', 0),
                'file': cache_file.name
            }
            self._save_index()
            
            print(f"✅ Cached analysis for {ticker} on {date}")
            
        except Exception as e:
            print(f"Error saving cache for {cache_key}: {e}")
    
    def get_all_cached(self) -> List[Dict[str, Any]]:
        """Get list of all cached analyses"""
        cached_list = []
        
        for cache_key, metadata in self.index.items():
            cached_list.append({
                'cache_key': cache_key,
                'ticker': metadata.get('ticker'),
                'date': metadata.get('date'),
                'cached_at': metadata.get('cached_at'),
                'decision': metadata.get('decision'),
                'confidence': metadata.get('confidence'),
            })
        
        # Sort by cached_at descending (most recent first)
        cached_list.sort(key=lambda x: x.get('cached_at', ''), reverse=True)
        
        return cached_list
    
    def delete_cache(self, ticker: str, date: str) -> bool:
        """Delete a specific cache entry"""
        cache_key = self._get_cache_key(ticker, date)
        cache_file = self._get_cache_file(cache_key)
        
        try:
            if cache_file.exists():
                cache_file.unlink()
            
            if cache_key in self.index:
                del self.index[cache_key]
                self._save_index()
            
            print(f"🗑️  Deleted cache for {ticker} on {date}")
            return True
            
        except Exception as e:
            print(f"Error deleting cache for {cache_key}: {e}")
            return False
    
    def clear_all_cache(self) -> bool:
        """Clear all cached analyses"""
        try:
            for cache_file in self.cache_dir.glob("*.json"):
                if cache_file.name != "index.json":
                    cache_file.unlink()
            
            self.index = {}
            self._save_index()
            
            print("🗑️  Cleared all cache")
            return True
            
        except Exception as e:
            print(f"Error clearing cache: {e}")
            return False
    
    def get_cache_stats(self) -> Dict[str, Any]:
        """Get cache statistics"""
        total_cached = len(self.index)
        cache_size = sum(f.stat().st_size for f in self.cache_dir.glob("*.json"))
        
        return {
            'total_analyses': total_cached,
            'cache_size_bytes': cache_size,
            'cache_size_mb': round(cache_size / (1024 * 1024), 2),
            'cache_directory': str(self.cache_dir.absolute())
        }


# Global cache manager instance
cache_manager = CacheManager()


