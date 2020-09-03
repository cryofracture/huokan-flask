variable "AWS_REGION" {
    type = string
    default = "us-east-2"
}

variable "AWS_ACCESS_KEY" {
    type = string
    default = "$AWS_ACCESS_KEY"
}

variable "AWS_SECRET_KEY" {
    type = string
    default = "$AWS_SECRET_KEY"
}

variable "AMIS" {
  type = map(string)
  default = {
    us-east-2 = "ami-02ee7191bff040b00"
    us-east-1 = "ami-0580fcddde65b4ace"
    us-west-1 = "ami-05fe528ab5127b0b2"
  }
}

provider "aws" {
    access_key = var.AWS_ACCESS_KEY
    secret_key = var.AWS_SECRET_KEY
    region     = var.AWS_REGION
}

resource "aws_instance" "huokan1" {
    ami             = var.AMIS[var.AWS_REGION]
    instance_type   = "t2.micro"
    provisioner "local-exec" {
        command = "echo ${aws_instance.huokan1.private_ip} >> private_ips.txt"    
    }
    provisioner "file" {
        source      = "./"
        destination = "/app"
    }
    provisioner "file" {
        source = "./ec2-startup.sh"
        destination = "/ec2-startup.sh"    
    }
    provisioner "remote-exec" {
        inline = [
            "chmod +x /ec2-startup.sh",
            "./ec2-startup.sh"
        ]
    }
}