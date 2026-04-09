# EddieBot

## Backend Setup
- cd Backend
- pip install -r requirements.txt
- python app/main.py

## Frontend Setup
- cd Frontend
- npm install
- npm run dev

---

## Deploying EddieBot as a web application

This guide walks through deploying the **FastAPI backend** and **Vite/React frontend** to a web server, connecting a **new AWS account** to **Amazon Bedrock**, and updating the few places in this repository that must point at your environment.

### Architecture at a glance

| Layer | Role |
|--------|------|
| **Browser** | Serves the built React app (static files or CDN). |
| **Backend** | FastAPI + Uvicorn; calls Bedrock via `boto3` using AWS credentials. |
| **Amazon Bedrock** | Runs the configured foundation model (this project targets **Amazon Nova** via an inference profile or model ID). |

There is **no third-party “chat API key”** in the EddieBot code path: authentication to AWS is handled by the **AWS SDK credential chain** (typically `~/.aws/credentials` on the server, or an **IAM instance role** on EC2).

---

### 1. Create and prepare an AWS account

1. **Sign up** at [AWS](https://aws.amazon.com/) and complete account verification (payment method, support email, etc.).
2. **Choose a Region** where Bedrock and your model are available (this repo defaults to `us-west-2`; keep backend Region and model in the same Region).
3. **Open Amazon Bedrock** in the console: search for **Bedrock** in the services menu.
4. **Models (on demand)**: In current Bedrock, foundation models are generally available **on demand** in supported Regions—you do **not** need to pre-enable each model through a separate **Model access** workflow. For EddieBot, pick **Amazon Nova** in the Bedrock console (check the model list or playground for your Region) and use the **model ID** or **inference profile** AWS shows for Nova when you set `MODEL_ID` in `bedrock_llm.py`. Access is still controlled by **IAM** (and any org policies), so your runtime identity must be allowed to invoke that model.
5. **Note your AWS account ID** (12-digit number in the console top-right / account menu). You will need it for ARNs and IAM policies.

---

### 2. IAM identity for the application

Create an IAM user (or role) the backend will use.

**Recommended for a dedicated server:** create an **IAM user** with **programmatic access** and attach a policy that allows Bedrock inference in your Region.

Example policy (narrow `Resource` to specific model or inference-profile ARNs when your org allows—`*` is shown for simplicity):

```json
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Allow",
      "Action": [
        "bedrock:InvokeModel",
        "bedrock:InvokeModelWithResponseStream"
      ],
      "Resource": "*"
    }
  ]
}
```

For stricter security, restrict `Resource` to the specific foundation model or inference profile ARN Bedrock shows for your account.

**If the backend runs on EC2:** prefer an **IAM instance profile** with the same Bedrock permissions instead of long-lived access keys. `boto3` picks up instance credentials automatically—no `~/.aws/credentials` file required on that instance.

---

### 3. Install the AWS CLI

Install the [AWS CLI v2](https://docs.aws.amazon.com/cli/latest/userguide/getting-started-install.html) on the machine where you will **configure credentials** (your laptop for testing, or the deployment server if you use access keys there).

Verify:

```bash
aws --version
```

Configure a named profile (optional but useful if you have multiple accounts):

```bash
aws configure --profile eddiebot-prod
```

You will be prompted for:

- **AWS Access Key ID** and **Secret Access Key** (from the IAM user’s security credentials).
- **Default region name** (e.g. `us-west-2`).
- **Default output format** (`json` is fine).

This creates/updates files under your AWS config directory (see next section).

---

### 4. The `.aws` folder: credentials and config

The AWS CLI and `boto3` read settings from:

| OS | Typical location |
|----|------------------|
| Linux / macOS | `~/.aws/credentials` and `~/.aws/config` |
| Windows | `%USERPROFILE%\.aws\credentials` and `%USERPROFILE%\.aws\config` |

**`credentials`** (example—use your real keys; never commit this file):

```ini
[default]
aws_access_key_id = AKIA...
aws_secret_access_key = ...

[eddiebot-prod]
aws_access_key_id = AKIA...
aws_secret_access_key = ...
```

**`config`** (example):

```ini
[default]
region = us-west-2
output = json

[profile eddiebot-prod]
region = us-west-2
output = json
```

**On the production server**, either:

- Copy these files to the **same user account** that runs Uvicorn (e.g. `deploy` or `www-data`), **or**
- Set environment variables: `AWS_ACCESS_KEY_ID`, `AWS_SECRET_ACCESS_KEY`, `AWS_DEFAULT_REGION` (and optionally `AWS_PROFILE`), **or**
- Use an **EC2 instance role** and omit static keys.

To use a non-default profile when starting the app:

```bash
export AWS_PROFILE=eddiebot-prod
```

---

### 5. Code changes for your AWS account and Region

These are the **specific lines** clients should update so the app talks to **their** Bedrock resources and so browsers can call the API from the deployed site.

#### 5.1 Bedrock model and Region (`Backend/app/services/bedrock_llm.py`)

**You must change `MODEL_ID` for your AWS account.** An inference-profile ARN looks like `arn:aws:bedrock:REGION:ACCOUNT_ID:inference-profile/...`. The middle **12-digit number is your AWS account ID** (in the repository copy it is `323441263732`, which belongs to the original deployment). If you run the app as-is with another account’s credentials, Bedrock will reject the call—replace the whole string with the **model ID** or **inference profile ARN** Bedrock shows for **your** account (still **Amazon Nova** for this project unless you intentionally switch models).

Align **Region** with where that model lives:

```5:8:Backend/app/services/bedrock_llm.py
# Use your own Bedrock model ID or inference-profile ARN from the console—this ARN embeds a specific AWS account ID and will not work for other accounts.
MODEL_ID = "arn:aws:bedrock:us-west-2:323441263732:inference-profile/us.amazon.nova-pro-v1:0" #amazon.nova-pro-v1:0" 

bedrock = boto3.client("bedrock-runtime", region_name="us-west-2")
```

- Set `MODEL_ID` to the value from **your** console (the `#amazon.nova-pro-v1:0` fragment in the file is a hint for a possible plain model id in some Regions—confirm in Bedrock for your Region).
- Set `region_name` on the `boto3.client("bedrock-runtime", ...)` call to the **same** Region as the model.

#### 5.2 CORS: allow your production frontend origin (`Backend/app/main.py`)

The API only allows local Vite dev origins by default. Add your **public site origin** (scheme + host + port, no trailing slash on the path):

```7:17:Backend/app/main.py
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "http://127.0.0.1:5173",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

Example: for `https://eddiebot.example.edu` served over HTTPS, include that string in `allow_origins`. For multiple environments, list each origin or refactor to read allowed origins from an environment variable (not currently in the repo).

#### 5.3 Frontend API base URL (`Frontend/src/config.js`)

The UI points at the local backend by default:

```1:1:Frontend/src/config.js
export const API_BASE_URL = "http://127.0.0.1:8000";
```

Before building for production, set `API_BASE_URL` to your **public API URL** (e.g. `https://api.eddiebot.example.edu` or `https://eddiebot.example.edu/api` if you reverse-proxy under a path—match whatever your server exposes).

The chat client uses this value here:

```8:8:Frontend/src/services/chatApi.js
  const res = await fetch(`${API_BASE_URL}/chat`, {
```

Rebuild the frontend after changing `API_BASE_URL`:

```bash
cd Frontend
npm install
npm run build
```

Output static assets are written to `Frontend/dist/` by Vite.

---

### 6. Run the backend in production

Install dependencies from **`Backend/requirements.txt`**—that is the canonical environment specification for this project (conda MatchSpec format, as noted in the file header). Example:

```bash
cd Backend
conda create --name eddiebot --file requirements.txt
conda activate eddiebot
uvicorn app.main:app --host 0.0.0.0 --port 8000
```

Use any environment name you prefer for production. If you cannot use conda on the server, reproduce the same packages another way; `requirements-pip.txt` is a separate, pip-oriented list and is **not** the primary lockfile for this repo.

For a long-running server, use **systemd**, **supervisor**, or a **process manager**; put environment variables (`AWS_*`, `AWS_PROFILE`) in the service unit or environment file.

**HTTPS** should be terminated at **nginx**, **Caddy**, **Apache**, or a load balancer in front of Uvicorn—not required for Bedrock itself, but required for a secure public site.

---

### 7. Serve the frontend

**Option A — Same host, nginx:** serve `Frontend/dist/` as static files and proxy `/chat` (and `/fetch` if used) to Uvicorn, **or** serve the SPA from `/` and proxy API paths to the backend.

**Option B — Split hosting:** static site on S3/CloudFront or any static host; API on a subdomain with CORS updated in `main.py` as in §5.2.

Ensure the **production** `API_BASE_URL` uses **HTTPS** if the page is served over HTTPS (mixed content will block requests).

---

### 8. Operational checklist

- [ ] **Amazon Nova** (or the model you configure) is offered in the chosen Region, and IAM allows invoking it.
- [ ] IAM permissions allow `InvokeModel` / streaming if you enable streaming later.
- [ ] `MODEL_ID` and `region_name` in `bedrock_llm.py` match your account and Region.
- [ ] `allow_origins` in `main.py` includes your live frontend origin.
- [ ] `API_BASE_URL` in `config.js` rebuilt into `Frontend/dist/`.
- [ ] AWS credentials available to the process running Uvicorn (files, env vars, or instance role).
- [ ] Firewall / security group allows inbound **only** to the reverse proxy (80/443), not necessarily port 8000 from the public internet.

---

### 9. Troubleshooting

| Symptom | What to check |
|---------|----------------|
| `AccessDeniedException` from Bedrock | IAM policy, `Resource` scope in policy, Region, and that the model ID or inference profile exists in that Region. |
| CORS errors in the browser | `allow_origins` in `main.py` must exactly match the page origin. |
| `Could not connect` / network errors | `API_BASE_URL`, HTTPS vs HTTP, DNS, and reverse proxy paths. |
| Wrong account charged | `MODEL_ID` ARN contains an account ID—confirm it is yours. |

Optional sanity check: the repo includes `Backend/test_bedrock_call.py` for manual boto3 tests; adjust Region/model there if you use it—**it is separate from** `app/services/bedrock_llm.py` and may use different defaults.

---

For local development, continue using the **Backend Setup** and **Frontend Setup** sections at the top of this README.