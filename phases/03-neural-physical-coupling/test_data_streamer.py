import os
import mmap
import numpy as np
from data_streamer import DataStreamer

def test_streamer():
    # Create dummy file
    filename = "test_data.bin"
    size = 10 * 1024 * 1024 # 10MB
    with open(filename, "wb") as f:
        f.write(os.urandom(size))
        
    streamer = DataStreamer(filename, buffer_limit_bytes=1024*1024*1024)
    
    # Test streaming
    for chunk in streamer.stream_trajectory():
        assert isinstance(chunk, mmap.mmap)
        assert chunk.size() == size
        print(f"Mapping successful. Size: {chunk.size()}")
        
    os.remove(filename)
    print("Test passed.")

if __name__ == "__main__":
    test_streamer()
