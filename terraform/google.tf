provider "google" {
  project     = "mentionary"
  region      = "us-central1"
  credentials = file("${path.module}/key.json")
}

resource "google_cloud_run_v2_job" "discord_bot" {
  name     = "discord-bot-job"
  location = "us-central1"
  deletion_protection = false


  template {
    template {
      containers {      
        image = "us-central1-docker.pkg.dev/mentionary/bots/discord-bot:latest"
    }
  }
}

  depends_on = [ 
    google_artifact_registry_repository.docker_repo,
    null_resource.docker_push
   ]
}

resource "null_resource" "docker_push" {
  provisioner "local-exec" {
    command = <<EOT
      cd .. 
      gcloud auth print-access-token | docker login -u oauth2accesstoken --password-stdin https://us-central1-docker.pkg.dev
      docker build -t us-central1-docker.pkg.dev/mentionary/bots/discord-bot:latest .
      docker push us-central1-docker.pkg.dev/mentionary/bots/discord-bot:latest
    EOT
  }

  depends_on = [google_artifact_registry_repository.docker_repo]
}

resource "google_artifact_registry_repository" "docker_repo" {
  provider = google

  location      = "us-central1"
  repository_id = "bots"
  description   = "Docker repository for Mentionary bots"
  format        = "DOCKER"

  docker_config {
    immutable_tags = false
  }
}


resource "null_resource" "run_discord_bot_job" {
  depends_on = [google_cloud_run_v2_job.discord_bot]

  provisioner "local-exec" {
    command = "gcloud run jobs execute ${google_cloud_run_v2_job.discord_bot.name} --region=us-central1"
  }
}
