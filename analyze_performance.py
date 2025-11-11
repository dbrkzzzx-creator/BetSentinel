"""
Analyze performance.json to identify optimization targets
"""
import json
from pathlib import Path

performance_file = Path('data/performance.json')

if performance_file.exists():
    with open(performance_file, 'r') as f:
        data = json.load(f)
    
    modules = data.get('modules', {})
    print("Performance Analysis:")
    print("=" * 60)
    
    for module_name, metrics in modules.items():
        avg_runtime = metrics.get('avg_runtime', 0)
        avg_memory = metrics.get('avg_memory', 0)
        avg_api_latency = metrics.get('avg_api_latency', 0)
        runtimes = metrics.get('runtimes', [])
        
        # Count anomalies (runs >1s, memory >10MB)
        high_runtime = sum(1 for r in runtimes if r > 1.0)
        high_memory_runs = [m for m in metrics.get('memory_usage', []) if m > 10]
        
        print(f"\n{module_name.upper()}:")
        print(f"  Avg Runtime: {avg_runtime:.3f}s {'[HIGH]' if avg_runtime > 1.0 else '[OK]'}")
        print(f"  Avg Memory: {avg_memory:.2f}MB {'[HIGH]' if avg_memory > 10 else '[OK]'}")
        if avg_api_latency:
            print(f"  Avg API Latency: {avg_api_latency:.3f}s")
        print(f"  High Runtime Runs (>1s): {high_runtime}")
        print(f"  High Memory Runs (>10MB): {len(high_memory_runs)}")
        
        if avg_runtime > 1.0 or avg_memory > 10 or high_runtime >= 3:
            print(f"  [OPTIMIZATION NEEDED]")
else:
    print("Performance file not found")

