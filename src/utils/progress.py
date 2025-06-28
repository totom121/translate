"""
Progress tracking utilities.
"""

import sys
import time
from typing import Optional

class ProgressTracker:
    """
    Simple progress tracker for long-running operations.
    """
    
    def __init__(self, total: int, description: str = "Processing", 
                 show_percentage: bool = True, show_rate: bool = True):
        """
        Initialize progress tracker.
        
        Args:
            total: Total number of items to process
            description: Description of the operation
            show_percentage: Whether to show percentage complete
            show_rate: Whether to show processing rate
        """
        self.total = total
        self.description = description
        self.show_percentage = show_percentage
        self.show_rate = show_rate
        
        self.current = 0
        self.start_time = time.time()
        self.last_update = 0
        
        # Only show progress for substantial operations
        self.enabled = total > 10
    
    def update(self, increment: int = 1) -> None:
        """
        Update progress by the specified increment.
        
        Args:
            increment: Number of items processed
        """
        if not self.enabled:
            return
        
        self.current += increment
        current_time = time.time()
        
        # Only update display every 0.5 seconds to avoid spam
        if current_time - self.last_update < 0.5 and self.current < self.total:
            return
        
        self.last_update = current_time
        self._display_progress()
    
    def finish(self) -> None:
        """Mark progress as complete."""
        if not self.enabled:
            return
        
        self.current = self.total
        self._display_progress()
        print()  # New line after completion
    
    def _display_progress(self) -> None:
        """Display current progress."""
        if not self.enabled:
            return
        
        # Calculate progress
        percentage = (self.current / self.total) * 100 if self.total > 0 else 0
        elapsed_time = time.time() - self.start_time
        
        # Build progress string
        progress_parts = [f"\r{self.description}: {self.current}/{self.total}"]
        
        if self.show_percentage:
            progress_parts.append(f"({percentage:.1f}%)")
        
        if self.show_rate and elapsed_time > 0:
            rate = self.current / elapsed_time
            progress_parts.append(f"[{rate:.1f} items/s]")
        
        # Add progress bar
        bar_width = 30
        filled_width = int(bar_width * percentage / 100)
        bar = "█" * filled_width + "░" * (bar_width - filled_width)
        progress_parts.append(f"[{bar}]")
        
        # Print progress (overwrite previous line)
        progress_string = " ".join(progress_parts)
        sys.stdout.write(progress_string)
        sys.stdout.flush()

