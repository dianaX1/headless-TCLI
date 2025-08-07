# Railway Deployment Checklist

Use this checklist to ensure successful deployment of your Headless Telegram Client on Railway.

## Pre-Deployment Setup

### ✅ GitHub Personal Access Token
- [ ] Go to [GitHub Settings > Developer settings > Personal access tokens](https://github.com/settings/tokens)
- [ ] Create new token (classic)
- [ ] Name: "Railway TDLib Build" (or similar)
- [ ] Scope: Select `public_repo` (minimum required)
- [ ] Copy the generated token (you'll need it for Railway)

### ✅ Railway Account Setup
- [ ] Sign up at [railway.app](https://railway.app)
- [ ] Connect your GitHub account
- [ ] Verify you can access your repositories

## Deployment Steps

### ✅ Step 1: Create Railway Project
- [ ] Click "New Project" in Railway dashboard
- [ ] Select "Deploy from GitHub repo"
- [ ] Choose your telegram client repository
- [ ] Wait for initial project creation

### ✅ Step 2: Configure Build Environment
- [ ] Go to project Settings
- [ ] Navigate to "Environment Variables"
- [ ] Add new variable:
  - **Name:** `GITHUB_TOKEN`
  - **Value:** [Your GitHub PAT from step 1]
  - **Environment:** Build ⚠️ (This is crucial!)
- [ ] Save the environment variable

### ✅ Step 3: Configure Runtime Environment
- [ ] Add runtime environment variable:
  - **Name:** `PORT`
  - **Value:** `8000`
  - **Environment:** Runtime
- [ ] Save the environment variable

### ✅ Step 4: Trigger Deployment
- [ ] Railway should auto-deploy after environment setup
- [ ] If not, click "Deploy" or push a commit to trigger build
- [ ] Monitor build logs for success messages

## Build Verification

### ✅ Check Build Logs
Look for these success indicators in the build logs:

- [ ] `Cloning TDLib repository with token authentication` (confirms token is working)
- [ ] `cmake .. && cmake --build . --target tdjson` (confirms TDLib compilation)
- [ ] `Successfully built` (confirms Docker build completion)
- [ ] No authentication errors or hanging processes

### ✅ Expected Build Time
- [ ] Initial build: 10-15 minutes (TDLib compilation is slow)
- [ ] Subsequent builds: 5-10 minutes (if using Docker layer caching)

## Post-Deployment Verification

### ✅ Application Access
- [ ] Railway provides a public URL (e.g., `https://your-app.railway.app`)
- [ ] Visit the URL in your browser
- [ ] Verify the web interface loads correctly
- [ ] Check for any runtime errors in Railway logs

### ✅ Telegram Client Setup
- [ ] Enter your Telegram API ID and Hash in the web interface
- [ ] Complete phone number verification
- [ ] Test sending a message to verify functionality

## Troubleshooting

### ❌ Build Fails with Git Error
**Error:** `fatal: could not read Username for 'https://github.com'`

**Solution:**
- [ ] Verify `GITHUB_TOKEN` is set as a **Build** environment variable (not Runtime)
- [ ] Check that your GitHub token has `public_repo` scope
- [ ] Ensure the token hasn't expired

### ❌ Build Succeeds but App Won't Start
**Symptoms:** Build completes but app shows startup errors

**Solutions:**
- [ ] Check that `PORT=8000` is set as Runtime environment variable
- [ ] Verify `start.sh` exists and is executable
- [ ] Check Railway runtime logs for Python errors

### ❌ TDLib Compilation Fails
**Symptoms:** Build fails during cmake or compilation steps

**Solutions:**
- [ ] Check if Railway has sufficient build resources
- [ ] Try redeploying (sometimes transient build issues occur)
- [ ] Consider using pre-compiled TDLib option (see RAILWAY_DEPLOYMENT.md)

## Security Reminders

- [ ] Never commit your GitHub token to the repository
- [ ] Your GitHub token only needs `public_repo` access
- [ ] You can revoke/regenerate the token anytime from GitHub
- [ ] Railway encrypts all environment variables

## Success Criteria

✅ **Deployment is successful when:**
- [ ] Build completes without errors
- [ ] Application is accessible via Railway URL
- [ ] Web interface loads and accepts Telegram credentials
- [ ] You can send and receive messages through the interface

---

**Need Help?** 
- Check `RAILWAY_DEPLOYMENT.md` for detailed instructions
- Review `DEPLOYMENT_FIX_SUMMARY.md` for technical details
- Railway has excellent documentation and support
