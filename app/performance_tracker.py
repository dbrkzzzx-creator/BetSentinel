"""
Performance Tracker - Monitors system performance metrics
"""
import os
import json
import time
import psutil
import logging
from datetime import datetime
from pathlib import Path
from functools import wraps

logger = logging.getLogger(__name__)

PERFORMANCE_FILE = Path('data/performance.json')
METRICS_HISTORY_SIZE = 100

def track_performance(module_name):
    """Decorator to track performance of a function"""
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            start_time = time.time()
            process = psutil.Process()
            start_cpu = process.cpu_percent(interval=0.1)
            start_memory = process.memory_info().rss / 1024 / 1024  # MB
            
            try:
                result = func(*args, **kwargs)
                success = True
                error = None
            except Exception as e:
                result = None
                success = False
                error = str(e)
                raise
            finally:
                end_time = time.time()
                end_cpu = process.cpu_percent(interval=0.1)
                end_memory = process.memory_info().rss / 1024 / 1024  # MB
                
                runtime = end_time - start_time
                cpu_usage = max(0, end_cpu - start_cpu)  # Ensure non-negative
                memory_usage = end_memory - start_memory
                
                # Record metrics
                record_metrics(
                    module_name=module_name,
                    function_name=func.__name__,
                    runtime=runtime,
                    cpu_usage=cpu_usage,
                    memory_usage=memory_usage,
                    success=success,
                    error=error
                )
            
            return result
        return wrapper
    return decorator

def record_metrics(module_name, function_name, runtime, cpu_usage, memory_usage, success=True, error=None, api_latency=None, io_wait_time=None, thread_efficiency=None):
    """Record performance metrics with I/O wait time and thread efficiency"""
    try:
        # Load existing metrics
        if PERFORMANCE_FILE.exists():
            with open(PERFORMANCE_FILE, 'r', encoding='utf-8', errors='replace') as f:
                metrics = json.load(f)
        else:
            metrics = {
                'modules': {},
                'history': [],
                'before_optimization': {},
                'after_optimization': {}
            }
        
        # Initialize module if not exists
        if module_name not in metrics['modules']:
            metrics['modules'][module_name] = {
                'runtimes': [],
                'cpu_usage': [],
                'memory_usage': [],
                'api_latency': [],
                'io_wait_time': [],
                'thread_efficiency': [],
                'success_count': 0,
                'error_count': 0,
                'last_update': None
            }
        
        # Record metrics
        module_metrics = metrics['modules'][module_name]
        
        # Ensure all required keys exist (for backward compatibility)
        if 'io_wait_time' not in module_metrics:
            module_metrics['io_wait_time'] = []
        if 'thread_efficiency' not in module_metrics:
            module_metrics['thread_efficiency'] = []
        
        module_metrics['runtimes'].append(runtime)
        module_metrics['cpu_usage'].append(cpu_usage)
        module_metrics['memory_usage'].append(memory_usage)
        
        if api_latency is not None:
            module_metrics['api_latency'].append(api_latency)
        
        if io_wait_time is not None:
            module_metrics['io_wait_time'].append(io_wait_time)
        
        if thread_efficiency is not None:
            module_metrics['thread_efficiency'].append(thread_efficiency)
        
        if success:
            module_metrics['success_count'] += 1
        else:
            module_metrics['error_count'] += 1
        
        # Keep only last N metrics
        if len(module_metrics['runtimes']) > METRICS_HISTORY_SIZE:
            module_metrics['runtimes'] = module_metrics['runtimes'][-METRICS_HISTORY_SIZE:]
            module_metrics['cpu_usage'] = module_metrics['cpu_usage'][-METRICS_HISTORY_SIZE:]
            module_metrics['memory_usage'] = module_metrics['memory_usage'][-METRICS_HISTORY_SIZE:]
            if module_metrics['api_latency']:
                module_metrics['api_latency'] = module_metrics['api_latency'][-METRICS_HISTORY_SIZE:]
            if module_metrics['io_wait_time']:
                module_metrics['io_wait_time'] = module_metrics['io_wait_time'][-METRICS_HISTORY_SIZE:]
            if module_metrics['thread_efficiency']:
                module_metrics['thread_efficiency'] = module_metrics['thread_efficiency'][-METRICS_HISTORY_SIZE:]
        
        module_metrics['last_update'] = datetime.now().isoformat()
        
        # Calculate averages
        module_metrics['avg_runtime'] = sum(module_metrics['runtimes']) / len(module_metrics['runtimes'])
        module_metrics['avg_cpu'] = sum(module_metrics['cpu_usage']) / len(module_metrics['cpu_usage'])
        module_metrics['avg_memory'] = sum(module_metrics['memory_usage']) / len(module_metrics['memory_usage'])
        
        if module_metrics['api_latency']:
            module_metrics['avg_api_latency'] = sum(module_metrics['api_latency']) / len(module_metrics['api_latency'])
        
        if module_metrics['io_wait_time']:
            module_metrics['avg_io_wait_time'] = sum(module_metrics['io_wait_time']) / len(module_metrics['io_wait_time'])
        
        if module_metrics['thread_efficiency']:
            module_metrics['avg_thread_efficiency'] = sum(module_metrics['thread_efficiency']) / len(module_metrics['thread_efficiency'])
        
        # Add to history
        history_entry = {
            'timestamp': datetime.now().isoformat(),
            'module': module_name,
            'function': function_name,
            'runtime': runtime,
            'cpu_usage': cpu_usage,
            'memory_usage': memory_usage,
            'api_latency': api_latency,
            'success': success,
            'error': error
        }
        metrics['history'].append(history_entry)
        
        # Keep only last N history entries
        if len(metrics['history']) > METRICS_HISTORY_SIZE:
            metrics['history'] = metrics['history'][-METRICS_HISTORY_SIZE:]
        
        # Save metrics
        os.makedirs(PERFORMANCE_FILE.parent, exist_ok=True)
        with open(PERFORMANCE_FILE, 'w', encoding='utf-8', errors='replace') as f:
            json.dump(metrics, f, indent=2)
        
        logger.debug(f"Recorded metrics for {module_name}: runtime={runtime:.3f}s, cpu={cpu_usage:.2f}%, memory={memory_usage:.2f}MB")
    
    except Exception as e:
        logger.error(f"Error recording metrics: {e}")

def get_module_metrics(module_name):
    """Get metrics for a specific module"""
    try:
        if not PERFORMANCE_FILE.exists():
            return None
        
        with open(PERFORMANCE_FILE, 'r', encoding='utf-8', errors='replace') as f:
            metrics = json.load(f)
        
        return metrics.get('modules', {}).get(module_name)
    except Exception as e:
        logger.error(f"Error getting module metrics: {e}")
        return None

def get_all_metrics():
    """Get all performance metrics"""
    try:
        if not PERFORMANCE_FILE.exists():
            return {}
        
        with open(PERFORMANCE_FILE, 'r', encoding='utf-8', errors='replace') as f:
            return json.load(f)
    except Exception as e:
        logger.error(f"Error getting all metrics: {e}")
        return {}

def record_api_latency(module_name, latency):
    """Record API latency for a module"""
    record_metrics(
        module_name=module_name,
        function_name='api_request',
        runtime=0,
        cpu_usage=0,
        memory_usage=0,
        api_latency=latency
    )

