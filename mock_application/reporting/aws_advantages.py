"""
AWS Advantages Documentation
Documents why AWS is superior for production deployments
"""

from typing import List, Dict


def get_aws_advantages() -> List[Dict[str, str]]:
    """Get list of AWS advantages for production deployments"""
    return [
        {
            "title": "Production-Grade Infrastructure",
            "description": (
                "AWS provides enterprise-grade infrastructure designed for production workloads. "
                "Unlike Colab (free tier limitations) or Zaratan (shared academic resources), "
                "AWS offers dedicated, reliable infrastructure with guaranteed uptime SLAs."
            ),
            "details": [
                "99.99% uptime SLA for EC2 instances",
                "Dedicated resources (not shared)",
                "Multiple availability zones for redundancy",
                "Enterprise-grade networking and storage"
            ]
        },
        {
            "title": "Auto-Scaling Capabilities",
            "description": (
                "AWS Auto Scaling automatically adjusts capacity to maintain steady, predictable performance "
                "at the lowest possible cost. This is critical for handling variable traffic loads."
            ),
            "details": [
                "Automatic scaling based on demand",
                "Cost optimization through right-sizing",
                "No manual intervention required",
                "Predictable performance under load"
            ]
        },
        {
            "title": "Comprehensive Monitoring and Observability",
            "description": (
                "AWS CloudWatch provides comprehensive monitoring, logging, and alerting capabilities. "
                "This enables proactive issue detection and performance optimization."
            ),
            "details": [
                "Real-time metrics and dashboards",
                "Centralized logging with CloudWatch Logs",
                "Automated alerting and notifications",
                "Performance insights and recommendations",
                "Integration with third-party tools"
            ]
        },
        {
            "title": "High Availability and Reliability",
            "description": (
                "AWS enables high availability through multi-AZ deployments, load balancing, and "
                "automatic failover. This ensures service continuity even during failures."
            ),
            "details": [
                "Multi-AZ deployment for redundancy",
                "Elastic Load Balancing for traffic distribution",
                "Automatic failover capabilities",
                "Disaster recovery options",
                "Backup and restore capabilities"
            ]
        },
        {
            "title": "Security Features",
            "description": (
                "AWS provides comprehensive security features including IAM, VPC, security groups, "
                "and encryption. These are essential for protecting production applications and data."
            ),
            "details": [
                "Identity and Access Management (IAM)",
                "Virtual Private Cloud (VPC) isolation",
                "Security groups and network ACLs",
                "Encryption at rest and in transit",
                "Secrets Manager for credential management",
                "Compliance certifications (SOC, ISO, etc.)"
            ]
        },
        {
            "title": "Persistent Storage and Databases",
            "description": (
                "AWS offers persistent storage (EBS, EFS) and managed database services (RDS, DynamoDB). "
                "This ensures data persistence and reliability, unlike Colab (ephemeral) or Zaratan (limited)."
            ),
            "details": [
                "Elastic Block Store (EBS) for persistent volumes",
                "Elastic File System (EFS) for shared storage",
                "Managed database services (RDS, DynamoDB)",
                "Automated backups and snapshots",
                "Data durability guarantees"
            ]
        },
        {
            "title": "Load Balancing and CDN Integration",
            "description": (
                "AWS provides Elastic Load Balancing and CloudFront CDN for optimal performance and "
                "global content delivery. This is essential for production applications."
            ),
            "details": [
                "Application Load Balancer (ALB)",
                "Network Load Balancer (NLB)",
                "CloudFront CDN for global content delivery",
                "SSL/TLS termination",
                "Health checks and automatic routing"
            ]
        },
        {
            "title": "Enterprise Support and SLAs",
            "description": (
                "AWS offers enterprise support with SLAs, 24/7 support, and technical account managers. "
                "This ensures production issues are resolved quickly."
            ),
            "details": [
                "24/7 technical support",
                "Service Level Agreements (SLAs)",
                "Technical Account Managers",
                "Proactive guidance and best practices",
                "Infrastructure Event Management"
            ]
        },
        {
            "title": "Cost Management and Optimization",
            "description": (
                "AWS provides tools for cost monitoring, optimization, and budgeting. This enables "
                "predictable costs and optimization opportunities."
            ),
            "details": [
                "Cost Explorer for cost analysis",
                "Reserved Instances for cost savings",
                "Spot Instances for cost optimization",
                "Budget alerts and notifications",
                "Cost allocation tags"
            ]
        },
        {
            "title": "Integration Ecosystem",
            "description": (
                "AWS integrates with a vast ecosystem of services and third-party tools. This enables "
                "building comprehensive solutions without vendor lock-in concerns."
            ),
            "details": [
                "Integration with 200+ AWS services",
                "API Gateway for microservices",
                "Lambda for serverless computing",
                "Container services (ECS, EKS)",
                "Third-party marketplace integrations"
            ]
        },
        {
            "title": "Disaster Recovery and Backup",
            "description": (
                "AWS provides comprehensive disaster recovery and backup solutions. This ensures business "
                "continuity and data protection."
            ),
            "details": [
                "Automated backups and snapshots",
                "Cross-region replication",
                "Disaster recovery solutions",
                "Point-in-time recovery",
                "Data archiving options"
            ]
        },
        {
            "title": "Compliance and Governance",
            "description": (
                "AWS meets various compliance requirements and provides governance tools. This is essential "
                "for regulated industries and enterprise deployments."
            ),
            "details": [
                "SOC 2, ISO 27001, HIPAA compliance",
                "Config for compliance monitoring",
                "CloudTrail for audit logging",
                "Organizations for multi-account management",
                "Control Tower for governance"
            ]
        }
    ]


def get_comparison_table() -> Dict[str, Dict[str, str]]:
    """Get comparison table of features across platforms"""
    return {
        "Feature": {
            "AWS": "Yes",
            "Colab": "No",
            "Zaratan": "No"
        },
        "Auto-Scaling": {
            "AWS": "Yes",
            "Colab": "No",
            "Zaratan": "No"
        },
        "Monitoring": {
            "AWS": "CloudWatch",
            "Colab": "Basic",
            "Zaratan": "SLURM only"
        },
        "High Availability": {
            "AWS": "Multi-AZ",
            "Colab": "Single instance",
            "Zaratan": "Single job"
        },
        "Persistent Storage": {
            "AWS": "EBS/EFS",
            "Colab": "Ephemeral",
            "Zaratan": "Limited"
        },
        "Load Balancing": {
            "AWS": "ALB/NLB",
            "Colab": "No",
            "Zaratan": "No"
        },
        "Enterprise Support": {
            "AWS": "24/7 SLA",
            "Colab": "Community",
            "Zaratan": "Academic"
        },
        "Security": {
            "AWS": "IAM/VPC",
            "Colab": "Basic",
            "Zaratan": "Basic"
        },
        "Cost Predictability": {
            "AWS": "Transparent",
            "Colab": "Free (limited)",
            "Zaratan": "Free (academic)"
        },
        "Production Ready": {
            "AWS": "Yes",
            "Colab": "No",
            "Zaratan": "No"
        }
    }


def get_summary() -> str:
    """Get summary of why AWS is better"""
    return (
        "AWS EC2 provides superior capabilities for production deployments compared to Colab and Zaratan. "
        "While Colab offers a free tier for development and Zaratan provides academic resources, "
        "neither platform is suitable for production workloads. AWS offers:\n\n"
        "1. **Reliability**: 99.99% uptime SLA vs. no guarantees\n"
        "2. **Scalability**: Auto-scaling vs. manual scaling\n"
        "3. **Monitoring**: Comprehensive CloudWatch vs. basic metrics\n"
        "4. **Security**: Enterprise-grade IAM/VPC vs. basic security\n"
        "5. **Support**: 24/7 enterprise support vs. community/academic\n"
        "6. **Persistence**: Reliable storage vs. ephemeral storage\n"
        "7. **High Availability**: Multi-AZ deployment vs. single instance\n"
        "\n"
        "For production deployments, AWS is the clear choice."
    )
