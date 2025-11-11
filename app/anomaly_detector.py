"""
Anomaly Detector - Detects performance anomalies
"""
import os
import json
import logging
from datetime import datetime
from pathlib import Path

logger = logging.getLogger(__name__)

PERFORMANCE_FILE = Path('data/performance.json')
ANOMALIES_FILE = Path('data/anomalies.log')
ANOMALY_THRESHOLD = 0.25  # 25% deviation
LOOKBACK_RUNS = 5

def detect_anomalies():
    """Detect performance anomalies"""
    anomalies = []
    
    try:
        if not PERFORMANCE_FILE.exists():
            return anomalies
        
        with open(PERFORMANCE_FILE, 'r', encoding='utf-8', errors='replace') as f:
            metrics = json.load(f)
        
        modules = metrics.get('modules', {})
        
        for module_name, module_metrics in modules.items():
            # Check if we have enough data
            runtimes = module_metrics.get('runtimes', [])
            if len(runtimes) < LOOKBACK_RUNS + 1:
                continue
            
            # Get last N runs for baseline
            recent_runs = runtimes[-LOOKBACK_RUNS:]
            baseline_avg = sum(recent_runs) / len(recent_runs)
            
            # Get current run
            current_run = runtimes[-1]
            
            # Check runtime anomaly
            if baseline_avg > 0:
                deviation = abs(current_run - baseline_avg) / baseline_avg
                if deviation > ANOMALY_THRESHOLD:
                    anomaly = {
                        'timestamp': datetime.now().isoformat(),
                        'module': module_name,
                        'metric': 'runtime',
                        'current_value': current_run,
                        'baseline_avg': baseline_avg,
                        'deviation': deviation,
                        'deviation_percent': deviation * 100,
                        'threshold': ANOMALY_THRESHOLD * 100
                    }
                    anomalies.append(anomaly)
                    log_anomaly(anomaly)
            
            # Check CPU usage anomaly
            cpu_usage = module_metrics.get('cpu_usage', [])
            if len(cpu_usage) >= LOOKBACK_RUNS + 1:
                recent_cpu = cpu_usage[-LOOKBACK_RUNS:]
                baseline_cpu = sum(recent_cpu) / len(recent_cpu)
                current_cpu = cpu_usage[-1]
                
                if baseline_cpu > 0:
                    deviation = abs(current_cpu - baseline_cpu) / baseline_cpu
                    if deviation > ANOMALY_THRESHOLD:
                        anomaly = {
                            'timestamp': datetime.now().isoformat(),
                            'module': module_name,
                            'metric': 'cpu_usage',
                            'current_value': current_cpu,
                            'baseline_avg': baseline_cpu,
                            'deviation': deviation,
                            'deviation_percent': deviation * 100,
                            'threshold': ANOMALY_THRESHOLD * 100
                        }
                        anomalies.append(anomaly)
                        log_anomaly(anomaly)
            
            # Check memory usage anomaly
            memory_usage = module_metrics.get('memory_usage', [])
            if len(memory_usage) >= LOOKBACK_RUNS + 1:
                recent_memory = memory_usage[-LOOKBACK_RUNS:]
                baseline_memory = sum(recent_memory) / len(recent_memory)
                current_memory = memory_usage[-1]
                
                if baseline_memory > 0:
                    deviation = abs(current_memory - baseline_memory) / baseline_memory
                    if deviation > ANOMALY_THRESHOLD:
                        anomaly = {
                            'timestamp': datetime.now().isoformat(),
                            'module': module_name,
                            'metric': 'memory_usage',
                            'current_value': current_memory,
                            'baseline_avg': baseline_memory,
                            'deviation': deviation,
                            'deviation_percent': deviation * 100,
                            'threshold': ANOMALY_THRESHOLD * 100
                        }
                        anomalies.append(anomaly)
                        log_anomaly(anomaly)
            
            # Check API latency anomaly
            api_latency = module_metrics.get('api_latency', [])
            if len(api_latency) >= LOOKBACK_RUNS + 1:
                recent_latency = api_latency[-LOOKBACK_RUNS:]
                baseline_latency = sum(recent_latency) / len(recent_latency)
                current_latency = api_latency[-1]
                
                if baseline_latency > 0:
                    deviation = abs(current_latency - baseline_latency) / baseline_latency
                    if deviation > ANOMALY_THRESHOLD:
                        anomaly = {
                            'timestamp': datetime.now().isoformat(),
                            'module': module_name,
                            'metric': 'api_latency',
                            'current_value': current_latency,
                            'baseline_avg': baseline_latency,
                            'deviation': deviation,
                            'deviation_percent': deviation * 100,
                            'threshold': ANOMALY_THRESHOLD * 100
                        }
                        anomalies.append(anomaly)
                        log_anomaly(anomaly)
        
        return anomalies
    
    except Exception as e:
        logger.error(f"Error detecting anomalies: {e}")
        return []

def log_anomaly(anomaly):
    """Log anomaly to file"""
    try:
        os.makedirs(ANOMALIES_FILE.parent, exist_ok=True)
        with open(ANOMALIES_FILE, 'a', encoding='utf-8', errors='replace') as f:
            f.write(f"{anomaly['timestamp']} | {anomaly['module']} | {anomaly['metric']} | "
                   f"Current: {anomaly['current_value']:.3f} | Baseline: {anomaly['baseline_avg']:.3f} | "
                   f"Deviation: {anomaly['deviation_percent']:.2f}% | Threshold: {anomaly['threshold']:.2f}%\n")
        
        logger.warning(f"Anomaly detected: {anomaly['module']} - {anomaly['metric']} deviation: {anomaly['deviation_percent']:.2f}%")
    
    except Exception as e:
        logger.error(f"Error logging anomaly: {e}")

def get_recent_anomalies(hours=24):
    """Get recent anomalies from log file"""
    anomalies = []
    
    try:
        if not ANOMALIES_FILE.exists():
            return anomalies
        
        cutoff_time = datetime.now().timestamp() - (hours * 3600)
        
        with open(ANOMALIES_FILE, 'r', encoding='utf-8', errors='replace') as f:
            for line in f:
                if line.strip():
                    parts = line.split(' | ')
                    if len(parts) >= 6:
                        try:
                            timestamp_str = parts[0]
                            timestamp = datetime.fromisoformat(timestamp_str).timestamp()
                            if timestamp >= cutoff_time:
                                anomalies.append(line.strip())
                        except:
                            continue
        
        return anomalies
    
    except Exception as e:
        logger.error(f"Error getting recent anomalies: {e}")
        return []

def check_anomaly_recovery(module_name, metric_name, runs_to_check=3):
    """Check if an anomaly has recovered within N runs"""
    try:
        if not PERFORMANCE_FILE.exists():
            return False
        
        with open(PERFORMANCE_FILE, 'r', encoding='utf-8', errors='replace') as f:
            metrics = json.load(f)
        
        module_metrics = metrics.get('modules', {}).get(module_name)
        if not module_metrics:
            return False
        
        # Get metric values
        if metric_name == 'runtime':
            values = module_metrics.get('runtimes', [])
        elif metric_name == 'cpu_usage':
            values = module_metrics.get('cpu_usage', [])
        elif metric_name == 'memory_usage':
            values = module_metrics.get('memory_usage', [])
        elif metric_name == 'api_latency':
            values = module_metrics.get('api_latency', [])
        else:
            return False
        
        if len(values) < LOOKBACK_RUNS + runs_to_check:
            return False
        
        # Get baseline
        baseline_start = -(LOOKBACK_RUNS + runs_to_check)
        baseline_values = values[baseline_start:-runs_to_check]
        baseline_avg = sum(baseline_values) / len(baseline_values)
        
        # Check recent runs
        recent_values = values[-runs_to_check:]
        all_within_threshold = True
        
        for value in recent_values:
            if baseline_avg > 0:
                deviation = abs(value - baseline_avg) / baseline_avg
                if deviation > ANOMALY_THRESHOLD:
                    all_within_threshold = False
                    break
        
        return all_within_threshold
    
    except Exception as e:
        logger.error(f"Error checking anomaly recovery: {e}")
        return False

