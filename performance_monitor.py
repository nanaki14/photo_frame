#!/usr/bin/env python3
"""
Performance Monitor for Digital Photo Frame
Monitors system performance and provides optimization recommendations for Pi Zero 2 WH
"""

import time
import psutil
import json
import os
import logging
from pathlib import Path

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class PerformanceMonitor:
    def __init__(self):
        self.baseline_memory = psutil.virtual_memory().available
        self.start_time = time.time()
        
    def get_system_metrics(self):
        """Get current system performance metrics"""
        cpu_percent = psutil.cpu_percent(interval=1)
        memory = psutil.virtual_memory()
        disk = psutil.disk_usage('/')
        
        # Get temperature if available (Pi specific)
        temperature = None
        try:
            if os.path.exists('/sys/class/thermal/thermal_zone0/temp'):
                with open('/sys/class/thermal/thermal_zone0/temp', 'r') as f:
                    temp_raw = int(f.read().strip())
                    temperature = temp_raw / 1000.0  # Convert to Celsius
        except:
            pass
        
        return {
            'timestamp': time.time(),
            'cpu': {
                'percent': cpu_percent,
                'count': psutil.cpu_count(),
                'freq': psutil.cpu_freq()._asdict() if psutil.cpu_freq() else None
            },
            'memory': {
                'total_mb': memory.total // (1024 * 1024),
                'available_mb': memory.available // (1024 * 1024),
                'used_mb': memory.used // (1024 * 1024),
                'percent': memory.percent
            },
            'disk': {
                'total_gb': disk.total // (1024 * 1024 * 1024),
                'free_gb': disk.free // (1024 * 1024 * 1024),
                'used_gb': disk.used // (1024 * 1024 * 1024),
                'percent': (disk.used / disk.total) * 100
            },
            'temperature_c': temperature,
            'uptime_hours': (time.time() - self.start_time) / 3600
        }
    
    def analyze_performance(self, metrics):
        """Analyze metrics and provide recommendations"""
        recommendations = []
        warnings = []
        
        # CPU Analysis
        if metrics['cpu']['percent'] > 80:
            warnings.append(f"High CPU usage: {metrics['cpu']['percent']:.1f}%")
            recommendations.append("Consider reducing image processing quality or concurrent operations")
        
        # Memory Analysis
        if metrics['memory']['percent'] > 85:
            warnings.append(f"High memory usage: {metrics['memory']['percent']:.1f}%")
            recommendations.append("Enable low-memory optimizations in display manager")
        
        if metrics['memory']['available_mb'] < 50:
            warnings.append("Very low available memory")
            recommendations.append("Restart the service to free up memory")
        
        # Temperature Analysis (Pi specific)
        if metrics['temperature_c']:
            if metrics['temperature_c'] > 70:
                warnings.append(f"High temperature: {metrics['temperature_c']:.1f}°C")
                recommendations.append("Improve cooling or reduce CPU load")
            elif metrics['temperature_c'] > 60:
                warnings.append(f"Elevated temperature: {metrics['temperature_c']:.1f}°C")
        
        # Disk Analysis
        if metrics['disk']['percent'] > 90:
            warnings.append(f"High disk usage: {metrics['disk']['percent']:.1f}%")
            recommendations.append("Clean up old photos or expand storage")
        
        return {
            'status': 'warning' if warnings else 'healthy',
            'warnings': warnings,
            'recommendations': recommendations
        }
    
    def benchmark_image_processing(self):
        """Benchmark image processing performance"""
        try:
            from PIL import Image
            import tempfile
            
            logger.info("Running image processing benchmark...")
            
            # Create test image
            test_image = Image.new('RGB', (2000, 1500), color='red')
            
            with tempfile.NamedTemporaryFile(suffix='.jpg', delete=False) as tmp:
                test_image.save(tmp.name, 'JPEG')
                tmp_path = tmp.name
            
            start_time = time.time()
            
            # Simulate photo frame processing
            img = Image.open(tmp_path)
            img = img.resize((800, 480), Image.Resampling.LANCZOS)
            img = img.convert('L')
            
            # Apply contrast enhancement
            pixels = img.load()
            for y in range(img.height):
                for x in range(img.width):
                    pixel = pixels[x, y]
                    enhanced = min(255, max(0, int((pixel - 128) * 1.2 + 128)))
                    pixels[x, y] = enhanced
            
            processing_time = time.time() - start_time
            
            # Cleanup
            os.unlink(tmp_path)
            
            logger.info(f"Image processing benchmark completed in {processing_time:.2f} seconds")
            
            return {
                'processing_time_seconds': processing_time,
                'performance_rating': 'excellent' if processing_time < 2 else 
                                    'good' if processing_time < 5 else 
                                    'slow' if processing_time < 10 else 'very_slow'
            }
            
        except Exception as e:
            logger.error(f"Benchmark failed: {e}")
            return {'error': str(e)}
    
    def monitor_service(self, duration_minutes=5):
        """Monitor service performance over time"""
        logger.info(f"Monitoring performance for {duration_minutes} minutes...")
        
        metrics_history = []
        start_time = time.time()
        
        while (time.time() - start_time) < (duration_minutes * 60):
            metrics = self.get_system_metrics()
            analysis = self.analyze_performance(metrics)
            
            metrics_history.append({
                'metrics': metrics,
                'analysis': analysis
            })
            
            # Print current status
            print(f"CPU: {metrics['cpu']['percent']:5.1f}% | "
                  f"RAM: {metrics['memory']['percent']:5.1f}% | "
                  f"Temp: {metrics['temperature_c']:5.1f}°C | "
                  f"Status: {analysis['status']}")
            
            if analysis['warnings']:
                for warning in analysis['warnings']:
                    print(f"  ⚠️  {warning}")
            
            time.sleep(10)  # Monitor every 10 seconds
        
        return metrics_history
    
    def generate_report(self):
        """Generate comprehensive performance report"""
        metrics = self.get_system_metrics()
        analysis = self.analyze_performance(metrics)
        benchmark = self.benchmark_image_processing()
        
        report = {
            'timestamp': time.strftime('%Y-%m-%d %H:%M:%S'),
            'system_info': {
                'platform': os.uname()._asdict(),
                'python_version': os.sys.version
            },
            'current_metrics': metrics,
            'analysis': analysis,
            'benchmark': benchmark,
            'optimization_status': {
                'low_memory_detected': metrics['memory']['total_mb'] < 1024,
                'pi_detected': 'arm' in os.uname().machine.lower(),
                'recommended_settings': self._get_recommended_settings(metrics)
            }
        }
        
        return report
    
    def _get_recommended_settings(self, metrics):
        """Get recommended settings based on system capabilities"""
        settings = {
            'sharp_concurrency': 1 if metrics['memory']['total_mb'] < 1024 else 2,
            'sharp_cache_memory': 16 if metrics['memory']['total_mb'] < 1024 else 50,
            'image_quality': 85 if metrics['cpu']['count'] == 1 else 90,
            'use_nearest_neighbor': metrics['memory']['total_mb'] < 512,
            'chunk_processing': metrics['memory']['total_mb'] < 1024
        }
        
        return settings

def main():
    import argparse
    
    parser = argparse.ArgumentParser(description='Photo Frame Performance Monitor')
    parser.add_argument('--report', action='store_true', help='Generate performance report')
    parser.add_argument('--monitor', type=int, default=5, help='Monitor for N minutes')
    parser.add_argument('--benchmark', action='store_true', help='Run image processing benchmark')
    parser.add_argument('--output', type=str, help='Output file for report (JSON)')
    
    args = parser.parse_args()
    
    monitor = PerformanceMonitor()
    
    if args.benchmark:
        benchmark = monitor.benchmark_image_processing()
        print(json.dumps(benchmark, indent=2))
    elif args.report:
        report = monitor.generate_report()
        
        if args.output:
            with open(args.output, 'w') as f:
                json.dump(report, f, indent=2)
            print(f"Report saved to {args.output}")
        else:
            print(json.dumps(report, indent=2))
    else:
        monitor.monitor_service(args.monitor)

if __name__ == "__main__":
    main()