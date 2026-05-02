# Vercel Deployment Guide - CoughNet Full Stack

## Overview

This guide covers deploying the CoughNet application to Vercel with both React frontend and Python backend.

## Prerequisites

1. **Vercel Account**: Sign up at [vercel.com](https://vercel.com)
2. **GitHub Account**: Repository must be on GitHub (Vercel integrates with GitHub)
3. **Git**: Configured and ready to push

## Deployment Options

### Option 1: Deploy via GitHub (Recommended)

**Step 1: Push to GitHub**
```bash
git add .
git commit -m "Prepare for Vercel deployment"
git push origin main
```

**Step 2: Import to Vercel**
1. Go to [vercel.com/new](https://vercel.com/new)
2. Click "Continue with GitHub"
3. Select your repository
4. Click "Import"

**Step 3: Configure Build Settings**
- **Framework**: Vite
- **Build Command**: `cd ReactFrontend && npm install && npm run build && cd ../backend && pip install -r api/requirements.txt`
- **Output Directory**: `ReactFrontend/dist`
- **Install Command**: (Leave default)

**Step 4: Set Environment Variables**
In Vercel dashboard → Settings → Environment Variables:
```
VITE_API_URL = /api
NODE_ENV = production
```

**Step 5: Deploy**
Click "Deploy" button.

---

### Option 2: Deploy via Vercel CLI

**Step 1: Install Vercel CLI**
```bash
npm i -g vercel
```

**Step 2: Deploy**
```bash
vercel
```

**Step 3: Answer prompts**
- Link to existing project or create new
- Auto-detected settings (usually correct)
- Confirm deployment

---

## File Structure for Deployment

```
project/
├── api/                              # Serverless Python functions
│   ├── predict.py                   # Main prediction endpoint
│   ├── health.py                    # Health check endpoint
│   ├── classes.py                   # Classes endpoint
│   └── requirements.txt             # Python dependencies
├── ReactFrontend/                   # Frontend
│   ├── client/                      # React app
│   ├── server/                      # Express server
│   ├── .env.production              # Production env vars
│   └── package.json
├── backend/                         # Python model code
│   ├── main.py                      # Model definition
│   ├── inference.py                 # Inference logic
│   └── uploads/                     # Temp storage
├── best_cough_classifier.pt         # Trained model (required)
├── vercel.json                      # Vercel configuration
└── .vercelignore                    # Files to exclude
```

---

## API Endpoints

After deployment, your API will be available at:

| Endpoint | Method | Purpose |
|----------|--------|---------|
| `/api/predict` | POST | Classify audio file |
| `/api/health` | GET | Health check |
| `/api/classes` | GET | Available disease classes |

### Example API Call

```bash
curl -X POST https://your-vercel-app.vercel.app/api/predict \
  -F "files=@audio_sample.wav"
```

---

## Model File Deployment

**Important**: The trained model file `best_cough_classifier.pt` must be included in your repository.

If the file is too large for GitHub:

### Option 1: Use Git LFS
```bash
git lfs install
git lfs track "*.pt"
git add .gitattributes best_cough_classifier.pt
git commit -m "Add model with LFS"
git push
```

### Option 2: Download During Build
Add to `vercel.json` build script if needed, or create a deployment-time download script.

### Option 3: Use Vercel Blob Storage
Store the model in Vercel's blob storage and download during serverless function execution.

---

## Environment Variables

Create `.env.production` in `ReactFrontend/`:
```
VITE_API_URL=/api
```

This tells the frontend to call `/api/predict` instead of `localhost:8000/predict`.

---

## Troubleshooting

### Build Failed - Python Dependencies
**Error**: `pip: command not found`
- Solution: Vercel needs Python 3.11. Update `vercel.json` runtime settings.

### 502 Bad Gateway on API Calls
- Check if `best_cough_classifier.pt` exists in root directory
- API falls back to mock classifier if model not found
- Check Vercel Function logs for errors

### Model File Too Large
- Ensure file is under 50MB (free tier limit)
- Use Git LFS if larger
- Or store elsewhere and download at function runtime

### CORS Issues
All API endpoints have `Access-Control-Allow-Origin: *` headers set.

### Port Issues
Vercel automatically assigns ports. Don't hardcode port 8000.

---

## Local Testing

Before deploying, test production build locally:

```bash
cd ReactFrontend
npm install
npm run build

# In another terminal, start a local server
npx serve dist
```

---

## Monitoring & Logs

**View deployment logs**:
1. Go to vercel.com
2. Select project
3. Click "Deployments"
4. Click build to see logs

**View function logs**:
- Vercel Dashboard → Functions → Select function → Logs

---

## Performance Tips

1. **Model Optimization**: Consider quantizing the model to reduce size
2. **Caching**: Configure Vercel cache control in headers
3. **CDN**: Vercel uses global CDN automatically
4. **Lazy Loading**: Frontend already uses Vite code-splitting

---

## Rollback to Previous Deployment

In Vercel dashboard:
1. Go to Deployments
2. Find previous working deployment
3. Click the three dots → Promote to Production

---

## Custom Domain

In Vercel Settings:
1. Go to Domains
2. Add custom domain (requires DNS configuration)
3. Follow Vercel's DNS setup guide

---

## Support

- **Vercel Docs**: https://vercel.com/docs
- **FastAPI to Serverless**: https://vercel.com/docs/functions/serverless-functions/python
- **Project Issues**: Check GitHub issues and Vercel function logs

---

## Next Steps

After successful deployment:
1. Test all endpoints
2. Monitor function performance
3. Set up error notifications
4. Configure analytics (optional)
5. Set up CI/CD for automatic deployments

For questions or issues, refer to the official documentation or GitHub discussions.
