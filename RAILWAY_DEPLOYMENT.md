# Railway Deployment Guide

This guide explains how to deploy the Headless Telegram Client on Railway.

## Prerequisites

1. **GitHub Personal Access Token (PAT)**
   - Go to [GitHub Settings > Developer settings > Personal access tokens](https://github.com/settings/tokens)
   - Click "Generate new token (classic)"
   - Give it a name like "Railway TDLib Build"
   - Select the `public_repo` scope (or `repo` if your repository is private)
   - Copy the generated token

2. **Railway Account**
   - Sign up at [railway.app](https://railway.app)
   - Connect your GitHub account

## Deployment Steps

### Step 1: Create Railway Project

1. Go to your Railway dashboard
2. Click "New Project"
3. Select "Deploy from GitHub repo"
4. Choose this repository

### Step 2: Configure Build Environment

1. In your Railway project dashboard, go to **Settings**
2. Navigate to **Environment Variables**
3. Add a new variable:
   - **Name:** `GITHUB_TOKEN`
   - **Value:** Your GitHub PAT from the prerequisites
   - **Environment:** Build (important!)

### Step 3: Configure Runtime Environment

Add these environment variables for runtime:

- **Name:** `PORT`
- **Value:** `8000`

### Step 4: Deploy

1. Railway will automatically trigger a build
2. Monitor the build logs to ensure TDLib clones successfully
3. You should see: "Cloning TDLib repository with token authentication"

### Step 5: Access Your Application

1. Once deployed, Railway will provide a public URL
2. Visit the URL to access the web interface
3. Enter your Telegram API credentials to start using the client

## Troubleshooting

### Build Fails with Git Clone Error

If you see:
```
fatal: could not read Username for 'https://github.com';: No such device or address
```

**Solution:** Make sure you've added the `GITHUB_TOKEN` environment variable as a **Build** variable (not Runtime).

### Build Succeeds but App Won't Start

1. Check that the `PORT` environment variable is set to `8000`
2. Verify that `start.sh` has proper permissions
3. Check the runtime logs for Python errors

### TDLib Build Takes Too Long

The TDLib compilation can take 10-15 minutes. This is normal. Railway has generous build timeouts, so be patient.

## Security Notes

- Never commit your GitHub token to the repository
- The token only needs `public_repo` access
- You can revoke the token anytime from GitHub settings
- Railway encrypts environment variables

## Alternative: Using Pre-built TDLib

If you continue having build issues, consider modifying the Dockerfile to use the pre-compiled `tdjson` package instead of building from source. This would eliminate the need for the GitHub token entirely.

To do this, replace the TDLib build section in the Dockerfile with:
```dockerfile
# Use pre-compiled TDLib instead of building from source
# (The tdjson package is already in requirements.txt)
```

However, building from source gives you the latest TDLib version and more control over the build process.
