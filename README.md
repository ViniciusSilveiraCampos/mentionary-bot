
---

<div align="center">

```shell
___  ___           _   _                              
|  \/  |          | | (_)                             
| .  . | ___ _ __ | |_ _  ___  _ __   __ _ _ __ _   _ 
| |\/| |/ _ \ '_ \| __| |/ _ \| '_ \ / _` | '__| | | |
| |  | |  __/ | | | |_| | (_) | | | | (_| | |  | |_| |
\_|  |_/\___|_| |_|\__|_|\___/|_| |_|\__,_|_|   \__, |
                                                 __/ |
                                                |___/ 
```

</p>
<div align="center">
    <img src="https://img.shields.io/badge/Python-3776AB.svg?style=for-the-badge&logo=Python&logoColor=white" >
    <img src="https://img.shields.io/badge/LangChain-1C3C3C.svg?style=for-the-badge&logo=LangChain&logoColor=white" >
    <img src="https://img.shields.io/badge/Discord-5865F2.svg?style=for-the-badge&logo=Discord&logoColor=white" >
    <img src="https://img.shields.io/badge/Google%20Gemini-8E75B2.svg?style=for-the-badge&logo=Google-Gemini&logoColor=white" >

</div>
<br>

Mentionary is a Discord bot powered by Gemini AI (via Langchain) designed to interact with server members. It responds to mentions, assists with questions, engages in playful interactions, and brings intelligent conversation to your Discord server.


</div>

<br>

- [Technologies](#technologies)
- [How the bot works](#how-the-bot-works)
- [Technical Details](#technical-details)
- [Running Locally](#running-locally)
- [How to deploy on google cloud](#how-to-deploy-on-google-cloud-platform-gcp-using-terraform)
- [Notes](#notes)


The main goal was to test the integration between:
- Google Gemini (text and image generation).
- LangChain + LangGraph (for flow control).
- Discord.py (as a chat interface).




## Technologies
- Python
- Poetry
- discord.py
- Langchain
- Gemini (Google Generative AI)
- dotenv





## How the Bot Works

1. **Message Responses**  
When the bot is mentioned in any conversation:
- It checks whether the message is a reply or a direct mention.
- Builds a minimal chat history (who said what).
- Sends this history to the Gemini model via LangChain.
- Awaits the model's response and posts it directly to the channel.

2. **Image Generation**  
Using the command:
```bash
!create_image <prompt>
````

* The bot sends the prompt to Google's image generation model (`gemini-2.0-flash-preview-image-generation`).
* Receives a base64 image from the model.
* Converts the base64 into a file and sends it to the Discord channel.

3. **Flow Control**

* Conversation flow and streaming are handled using **LangGraph**.
* Message IDs are tracked to avoid duplicate replies.


## Technical Details

* The bot reads the Discord token and Gemini API key from a `.env` file.
* The `agent.py` module (not included here) defines the message graph and the language model interaction.
* Images returned by the Gemini API are processed from base64 to binary files before sending them to Discord.


## Running Locally

1. Install dependencies:

```bash
poetry install
```

2. Configure your `.env` file:

```
DISCORD_BOT_TOKEN=your_token_here
GOOGLE_API_KEY=your_api_key_here
```

3. Run the bot:

```bash
poetry run python app.py
```




## How to Deploy on Google Cloud Platform (GCP) using Terraform

This project can be deployed as a **Cloud Run Job** using **Google Cloud Platform** and **Terraform**.

### Prerequisites

- Google Cloud project with billing enabled.
- Artifact Registry repository created (or let Terraform create it automatically).
- Service account with permissions:
  - Cloud Run Admin
  - Artifact Registry Admin
  - Service Account User
- Terraform installed locally.
- Docker installed locally.
- `gcloud` CLI installed and authenticated.

---

### Steps to Deploy

1. **Configure Environment Variables**

Ensure you have a `key.json` file from your service account in the Terraform folder.

2. **Initialize Terraform**

```bash
terraform init
````

3. **Apply the Infrastructure**

This will:

* Create the Docker Artifact Registry repository (if not exists).
* Build and push the Docker image of your bot.
* Deploy the Cloud Run Job.

```bash
terraform apply
```

4. **Execute the Bot Job**

After deploying, the Terraform script automatically executes the Cloud Run Job once via:

```bash
gcloud run jobs execute discord-bot-job --region=us-central1
```

You can manually rerun the bot later using the same command.

---

### Terraform Flow Summary

* **google\_artifact\_registry\_repository** – Creates (or manages) your Docker repository.
* **null\_resource.docker\_push** – Automates Docker build & push using `gcloud` authentication.
* **google\_cloud\_run\_v2\_job** – Defines the Cloud Run Job pointing to your Docker image.
* **null\_resource.run\_discord\_bot\_job** – Triggers the job execution via `gcloud`.


## Notes
* Each execution of the Cloud Run Job runs your bot container once.
* Logs can be viewed via Google Cloud Console (`Operations > Logs Explorer`).
* This setup uses `null_resource` for Docker automation. Adjust paths if needed.
* This is a **test project / technical experiment**, not intended as a production-ready solution.
* Some parts (like image response handling) are basic and could be improved.
* You’ll need to configure or implement `agent.py` based on your own LangGraph pipeline.

