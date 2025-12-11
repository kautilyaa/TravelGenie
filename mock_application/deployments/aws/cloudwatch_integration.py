"""
CloudWatch Integration for AWS Metrics
Sends metrics to AWS CloudWatch for monitoring and comparison
"""

import boto3
from typing import Dict, Any, Optional
from datetime import datetime
import json


class CloudWatchMetrics:
    """Send metrics to AWS CloudWatch"""
    
    def __init__(self, region: str = "us-east-1", log_group: str = "travel-genie-mock"):
        self.region = region
        self.log_group = log_group
        self.cloudwatch = boto3.client('cloudwatch', region_name=region)
        self.logs = boto3.client('logs', region_name=region)
        
        # Ensure log group exists
        try:
            self.logs.create_log_group(logGroupName=log_group)
        except self.logs.exceptions.ResourceAlreadyExistsException:
            pass
    
    def put_metric(
        self,
        metric_name: str,
        value: float,
        unit: str = "None",
        dimensions: Optional[Dict[str, str]] = None
    ):
        """Put a metric to CloudWatch"""
        metric_data = {
            'MetricName': metric_name,
            'Value': value,
            'Unit': unit,
            'Timestamp': datetime.utcnow()
        }
        
        if dimensions:
            metric_data['Dimensions'] = [
                {'Name': k, 'Value': v} for k, v in dimensions.items()
            ]
        
        try:
            self.cloudwatch.put_metric_data(
                Namespace='TravelGenie/Mock',
                MetricData=[metric_data]
            )
        except Exception as e:
            print(f"Failed to put metric to CloudWatch: {e}")
    
    def put_latency_metrics(self, latency_ms: float, percentile: Optional[str] = None):
        """Put latency metrics"""
        dimensions = {"Platform": "AWS"}
        if percentile:
            dimensions["Percentile"] = percentile
        
        self.put_metric("Latency", latency_ms, "Milliseconds", dimensions)
    
    def put_throughput_metrics(self, rps: float):
        """Put throughput metrics"""
        self.put_metric("Throughput", rps, "Count/Second", {"Platform": "AWS"})
    
    def put_error_metrics(self, error_rate: float):
        """Put error rate metrics"""
        self.put_metric("ErrorRate", error_rate, "Percent", {"Platform": "AWS"})
    
    def put_resource_metrics(self, cpu_percent: float, memory_percent: float):
        """Put resource usage metrics"""
        self.put_metric("CPUUtilization", cpu_percent, "Percent", {"Platform": "AWS"})
        self.put_metric("MemoryUtilization", memory_percent, "Percent", {"Platform": "AWS"})
    
    def send_log_event(self, message: str, level: str = "INFO"):
        """Send log event to CloudWatch Logs"""
        try:
            self.logs.put_log_events(
                logGroupName=self.log_group,
                logStreamName=f"mock-{datetime.now().strftime('%Y%m%d')}",
                logEvents=[{
                    'timestamp': int(datetime.utcnow().timestamp() * 1000),
                    'message': json.dumps({
                        "level": level,
                        "message": message,
                        "timestamp": datetime.utcnow().isoformat()
                    })
                }]
            )
        except Exception as e:
            print(f"Failed to send log to CloudWatch: {e}")
