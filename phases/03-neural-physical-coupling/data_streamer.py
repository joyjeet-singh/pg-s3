import mmap
import os
import numpy as np

class DataStreamer:
    """Zero-copy memory mapping for streaming trajectories into OpenVINO graph arena."""
    
    def __init__(self, file_path, buffer_limit_bytes=1024*1024*1024):
        self.file_path = file_path
        self.buffer_limit = buffer_limit_bytes
        
    def stream_trajectory(self):
        """Map file and yield memory-view chunks without copying."""
        size = os.path.getsize(self.file_path)
        if size > self.buffer_limit:
            raise MemoryError(f"Trajectory {size} exceeds buffer limit {self.buffer_limit}")
            
        with open(self.file_path, "rb") as f:
            mmapped_file = mmap.mmap(f.fileno(), 0, access=mmap.ACCESS_READ)
            # Yield memory view chunks (zero-copy)
            yield mmapped_file
            mmapped_file.close()

# Example Usage:
# streamer = DataStreamer("dataset.bin")
# for chunk in streamer.stream_trajectory():
#     # Process chunk directly
