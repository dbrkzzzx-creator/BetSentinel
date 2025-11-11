"""
Compare performance before and after optimization
"""
import json
from pathlib import Path

performance_file = Path('data/performance.json')

if performance_file.exists():
    with open(performance_file, 'r') as f:
        data = json.load(f)
    
    before = data.get('before_optimization', {}).get('modules', {})
    current = data.get('modules', {})
    
    print("=" * 60)
    print("PERFORMANCE COMPARISON: BEFORE vs AFTER OPTIMIZATION")
    print("=" * 60)
    
    for module_name in ['collector', 'signal_generator', 'backtester']:
        if module_name in before and module_name in current:
            before_metrics = before[module_name]
            current_metrics = current[module_name]
            
            print(f"\n{module_name.upper()}:")
            
            # Runtime
            before_runtime = before_metrics.get('avg_runtime', 0)
            current_runtime = current_metrics.get('avg_runtime', 0)
            if before_runtime > 0:
                runtime_improvement = ((before_runtime - current_runtime) / before_runtime) * 100
                print(f"  Runtime: {before_runtime:.3f}s -> {current_runtime:.3f}s ({runtime_improvement:+.1f}%)")
            
            # Memory
            before_memory = before_metrics.get('avg_memory', 0)
            current_memory = current_metrics.get('avg_memory', 0)
            if before_memory > 0:
                memory_improvement = ((before_memory - current_memory) / before_memory) * 100
                print(f"  Memory: {before_memory:.2f}MB -> {current_memory:.2f}MB ({memory_improvement:+.1f}%)")
            
            # API Latency
            before_latency = before_metrics.get('avg_api_latency', 0)
            current_latency = current_metrics.get('avg_api_latency', 0)
            if before_latency > 0:
                latency_improvement = ((before_latency - current_latency) / before_latency) * 100
                print(f"  API Latency: {before_latency:.3f}s -> {current_latency:.3f}s ({latency_improvement:+.1f}%)")
            
            # I/O Wait Time (new metric)
            if 'avg_io_wait_time' in current_metrics:
                io_wait = current_metrics['avg_io_wait_time']
                print(f"  I/O Wait Time: {io_wait:.3f}s (new metric)")
    
    print("=" * 60)

