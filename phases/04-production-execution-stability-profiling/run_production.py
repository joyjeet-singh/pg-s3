import subprocess
import resource
import time
import os

def run_simulation():
    print("[PY] Starting production orchestration...")
    
    # Compile the core (ensure mfma and avx2 are used)
    cpp_source = "GPD/phases/04-production-execution-stability-profiling/production_core.cpp"
    cpp_exec = "GPD/phases/04-production-execution-stability-profiling/production_core"
    
    print(f"[PY] Compiling {cpp_source}...")
    compile_cmd = ["g++", "-mavx2", "-mfma", "-O3", cpp_source, "-o", cpp_exec]
    subprocess.run(compile_cmd, check=True)
    
    # Environment pinning as per Phase 04 plan
    env = os.environ.copy()
    env["OV_CPU_DISPATCH_ARCH"] = "AVX2"
    env["OPENVINO_CPU_EXTENSION_LIST"] = "avx2"
    
    print(f"[PY] Executing {cpp_exec}...")
    start_time = time.time()
    
    # Run the compiled binary
    process = subprocess.Popen([cpp_exec], env=env, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
    
    stdout, stderr = process.communicate()
    end_time = time.time()
    
    print("[PY] Simulation Output:")
    print(stdout)
    if stderr:
        print("[PY] Simulation Errors:")
        print(stderr)
        
    # Profile children
    usage_self = resource.getrusage(resource.RUSAGE_SELF)
    usage_children = resource.getrusage(resource.RUSAGE_CHILDREN)
    
    # On Darwin, ru_maxrss is in bytes.
    peak_rss_self_mb = usage_self.ru_maxrss / (1024 * 1024)
    peak_rss_children_mb = usage_children.ru_maxrss / (1024 * 1024)
    
    print(f"[PY] Orchestrator Peak RSS: {peak_rss_self_mb:.2f} MB")
    print(f"[PY] Worker (Child) Peak RSS: {peak_rss_children_mb:.2f} MB")
    print(f"[PY] Total Runtime: {end_time - start_time:.2f} seconds")
    
    # Validate against 5GB limit
    if peak_rss_children_mb > 5120:
        print("[PY] ALERT: RSS limit of 5GB exceeded!")
    else:
        print("[PY] SUCCESS: RSS within 5GB limit.")

if __name__ == "__main__":
    run_simulation()
