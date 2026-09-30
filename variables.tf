variable "project_name" {
  description = "Project name used as prefix for all resources."
  type        = string
  default     = "floci-learning-assistant"
}

variable "aws_region" {
  description = "AWS region (simulated by floci)."
  type        = string
  default     = "us-east-1"
}

variable "vpc_cidr" {
  description = "CIDR block for the VPC hosting the containerized application."
  type        = string
  default     = "10.0.0.0/16"
}

variable "public_subnet_cidrs" {
  description = "CIDR blocks for the two public subnets used by the ALB and the Fargate tasks."
  type        = list(string)
  default     = ["10.0.1.0/24", "10.0.2.0/24"]
}

variable "container_port" {
  description = "Port the containerized application listens on."
  type        = number
  default     = 8080
}

variable "service_desired_count" {
  description = "Desired task count for the ECS service."
  type        = number
  default     = 2
}

variable "container_image" {
  description = "Container image for the Student Learning Assistant application."
  type        = string
  default     = "public.ecr.aws/docker/library/python:3.12-slim"
}

variable "qa_scores_table_name" {
  description = "Name of the DynamoDB table storing Q&A pairs and scores."
  type        = string
  default     = "qa-scores"
}

variable "generated_images_bucket_name" {
  description = "Name of the S3 bucket storing images generated for assignments."
  type        = string
  default     = "generated-images"
}

variable "bedrock_text_model_id" {
  description = "Bedrock foundation model id used to create assignments and Q&A."
  type        = string
  default     = "amazon.titan-text-express-v1"
}

variable "bedrock_image_model_id" {
  description = "Bedrock foundation model id used to create assignment images."
  type        = string
  default     = "stability.stable-diffusion-xl-v1"
}
