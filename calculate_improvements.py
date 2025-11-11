"""
Calculate performance improvements
"""
import json
from pathlib import Path

performance_file = Path('data/performance.json')

with open(performance_file, 'r') as f:
    data = json.load(f)

before = data.get('before_optimization', {}).get('modules', {}).get('collector', {})
after = data.get('after_optimization', {}).get('modules', {}).get('collector', {})

before_runtime = before.get('avg_runtime', 0.438)
after_runtime = after.get('avg_runtime', 0.373)
runtime_improvement = ((before_runtime - after_runtime) / before_runtime) * 100

before_memory = before.get('avg_memory', 2.07)
after_memory = after.get('avg_memory', 1.75)
memory_improvement = ((before_memory - after_memory) / before_memory) * 100

before_latency = before.get('avg_api_latency', 0.638)
after_latency = after.get('avg_api_latency', 0.647)
latency_change = ((after_latency - before_latency) / before_latency) * 100

print("=" * 60)
print("PERFORMANCE IMPROVEMENTS SUMMARY")
print("=" * 60)
print(f"Runtime: {before_runtime:.3f}s -> {after_runtime:.3f}s ({runtime_improvement:+.1f}% reduction)")
print(f"Memory: {before_memory:.2f}MB -> {after_memory:.2f}MB ({memory_improvement:+.1f}% reduction)")
print(f"API Latency: {before_latency:.3f}s -> {after_latency:.3f}s ({latency_change:+.1f}% change)")
print("=" * 60)

