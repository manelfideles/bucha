module "ecr" {
  source = "terraform-aws-modules/ecr/aws"

  repository_name         = var.repository_name
  repository_force_delete = true

  repository_image_tag_mutability = "MUTABLE"

  # By default, it will use root access
  # repository_read_write_access_arns = ["arn:aws:iam::992382607343:role/terraform"]

  repository_lifecycle_policy = jsonencode({
    rules = [
      {
        rulePriority = 1,
        description  = "Keep last N images",
        selection = {
          tagStatus     = "tagged",
          tagPrefixList = ["v"],
          countType     = "imageCountMoreThan",
          countNumber   = var.keep_last_N
        },
        action = {
          type = "expire"
        }
      }
    ]
  })

  tags = {
    Terraform   = "true"
    Environment = "dev"
  }
}
