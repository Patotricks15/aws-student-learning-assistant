output "alb_dns_name" {
  description = "Public DNS name of the traffic-distribution load balancer."
  value       = aws_lb.main.dns_name
}

output "ecs_cluster_name" {
  description = "Name of the ECS cluster running the containerized application."
  value       = aws_ecs_cluster.main.name
}

output "ecs_service_name" {
  description = "Name of the ECS service running the containerized application."
  value       = aws_ecs_service.app.name
}

output "dynamodb_table_name" {
  description = "Name of the DynamoDB table storing Q&A pairs and scores."
  value       = aws_dynamodb_table.qa_scores.name
}

output "generated_images_bucket" {
  description = "Name of the S3 bucket storing generated assignment images."
  value       = aws_s3_bucket.generated_images.bucket
}
