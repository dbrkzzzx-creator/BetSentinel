"""
Save after-optimization performance metrics
"""
import json
from pathlib import Path
from datetime import datetime

performance_file = Path('data/performance.json')

if performance_file.exists():
    with open(performance_file, 'r') as f:
        data = json.load(f)
    
    # Save after optimization metrics
    after = {
        'timestamp': datetime.now().isoformat(),
        'modules': {}
    }
    
    for module_name, metrics in data.get('modules', {}).items():
        # Get recent metrics (last 3 runs for comparison)
        runtimes = metrics.get('runtimes', [])[-3:]
        memory_usage = metrics.get('memory_usage', [])[-3:]
        api_latency = metrics.get('api_latency', [])[-3:]
        
        if runtimes:
            after['modules'][module_name] = {
                'avg_runtime': sum(runtimes) / len(runtimes) if runtimes else 0,
                'avg_cpu': metrics.get('avg_cpu', 0),
                'avg_memory': sum(memory_usage) / len(memory_usage) if memory_usage else 0,
                'avg_api_latency': sum(api_latency) / len(api_latency) if api_latency else 0,
                'avg_io_wait_time': metrics.get('avg_io_wait_time', 0),
                'success_count': metrics.get('success_count', 0),
                'error_count': metrics.get('error_count', 0)
            }
    
    # Add after optimization to performance data
    data['after_optimization'] = after
    
    # Save
    with open(performance_file, 'w') as f:
        json.dump(data, f, indent=2)
    
    print("After-optimization performance saved")
    if 'collector' in after['modules']:
        print(f"Collector: runtime={after['modules']['collector']['avg_runtime']:.3f}s, memory={after['modules']['collector']['avg_memory']:.2f}MB")
else:
    print("Performance file not found")

