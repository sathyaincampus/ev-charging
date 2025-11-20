# AWS Credentials Setup Guide

## Quick Fix for "Unable to locate credentials" Error

You need to add your AWS credentials to the `.env` file.

### Step 1: Get Your AWS Credentials

1. Log into AWS Console: https://console.aws.amazon.com/
2. Click your username (top right) → Security credentials
3. Scroll to "Access keys" section
4. Click "Create access key"
5. Copy both:
   - Access key ID
   - Secret access key

### Step 2: Add Credentials to .env File

Open `ev-concierge/.env` and replace the placeholder values:

```bash
# AWS Credentials (Required for Bedrock access)
AWS_ACCESS_KEY_ID=AKIAIOSFODNN7EXAMPLE
AWS_SECRET_ACCESS_KEY=wJalrXUtnFEMI/K7MDENG/bPxRfiCYEXAMPLEKEY
AWS_REGION=us-west-2
BEDROCK_MODEL_ID=anthropic.claude-3-5-sonnet-20241022-v2:0
```

### Step 3: Enable Bedrock Access

1. Go to AWS Bedrock Console: https://console.aws.amazon.com/bedrock/
2. Click "Model access" in the left sidebar
3. Click "Manage model access"
4. Enable "Claude 3.5 Sonnet v2"
5. Click "Save changes"

### Step 4: Restart the Application

```bash
cd ev-concierge
bash start.sh
```

## Alternative: Use AWS CLI Configuration

Instead of using .env, you can configure AWS CLI:

```bash
aws configure
```

Enter your:
- AWS Access Key ID
- AWS Secret Access Key
- Default region (us-west-2)
- Default output format (json)

The app will automatically use these credentials.

## Security Best Practices

⚠️ **Never commit your .env file with real credentials to git!**

The `.gitignore` file should already exclude `.env`, but double-check:

```bash
# Make sure .env is in .gitignore
echo ".env" >> .gitignore
```

## Troubleshooting

### Error: "Unable to locate credentials"
- Check that AWS_ACCESS_KEY_ID and AWS_SECRET_ACCESS_KEY are in your .env file
- Make sure there are no extra spaces or quotes around the values
- Restart the application after updating .env

### Error: "Access Denied" or "Not Authorized"
- Your AWS user needs Bedrock permissions
- Add the `AmazonBedrockFullAccess` policy to your IAM user
- Make sure you've enabled Claude 3.5 Sonnet in Bedrock Model Access

### Error: "Model not found"
- Go to Bedrock Console → Model access
- Enable Claude 3.5 Sonnet v2
- Wait a few minutes for access to be granted
