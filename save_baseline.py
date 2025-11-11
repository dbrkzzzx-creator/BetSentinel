"""
Save baseline performance metrics before optimization
"""
import json
from pathlib import Path
from datetime import datetime

performance_file = Path('data/performance.json')

if performance_file.exists():
    with open(performance_file, 'r') as f:
        data = json.load(f)
    
    # Save baseline
    baseline = {
        'timestamp': datetime.now().isoformat(),
        'modules': {}
    }
    
    for module_name, metrics in data.get('modules', {}).items():
        baseline['modules'][module_name] = {
            'avg_runtime': metrics.get('avg_runtime', 0),
            'avg_cpu': metrics.get('avg_cpu', 0),
            'avg_memory': metrics.get('avg_memory', 0),
            'avg_api_latency': metrics.get('avg_api_latency', 0),
            'success_count': metrics.get('success_count', 0),
            'error_count': metrics.get('error_count', 0)
        }
    
    # Add baseline to performance data
    data['before_optimization'] = baseline
    
    # Save
    with open(performance_file, 'w') as f:
        json.dump(data, f, indent=2)
    
    print("Baseline performance saved")
    print(f"Collector: runtime={baseline['modules']['collector']['avg_runtime']:.3f}s, memory={baseline['modules']['collector']['avg_memory']:.2f}MB")
    if 'signal_generator' in baseline['modules']:
        print(f"Signal Generator: runtime={baseline['modules']['signal_generator']['avg_runtime']:.3f}s, memory={baseline['modules']['signal_generator']['avg_memory']:.2f}MB")
else:
    print("Performance file not found")

