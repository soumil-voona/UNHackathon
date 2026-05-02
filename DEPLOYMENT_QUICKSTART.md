# CoughNet Vercel Deployment - Quick Reference

## ✅ What's Been Set Up

Your project is now ready for Vercel deployment with both frontend and backend. Here's what has been configured:

### Frontend
- ✅ **React + Vite** build optimized for Vercel
- ✅ **Environment variable** `VITE_API_URL` configured to `/api` in production
- ✅ **Production config** in `ReactFrontend/.env.production`

### Backend
- ✅ **Python serverless functions** in `/api/` directory
  - `api/predict.py` - Main classification endpoint
  - `api/health.py` - Health check
  - `api/classes.py` - Available disease classes
- ✅ **Python dependencies** configured in `api/requirements.txt`

### Configuration Files
- ✅ **vercel.json** - Deployment configuration
- ✅ **.vercelignore** - Files to exclude from deployment
- ✅ **VERCEL_DEPLOYMENT.md** - Full deployment guide
- ✅ **verify-deployment.sh** - Validation script

---

## 🚀 Deploy in 3 Steps

### Step 1: Prepare Your Code
```bash
# From project root
cd /Users/lakshminarayanansanthanam/UNHackathon/UNHackathon

# Verify everything is ready
./verify-deployment.sh

# Commit files to Git
git add -A
git commit -m "Prepare for Vercel deployment"
git push origin main
```

### Step 2: Import to Vercel

Option A: **Via GitHub UI (Easiest)**
1. Go to https://vercel.com/new
2. Click "Continue with GitHub" 
3. Select your repository
4. Click "Import"
5. Vercel auto-detects settings ✅

Option B: **Via Vercel CLI**
```bash
npm install -g vercel
vercel
# Follow prompts
```

### Step 3: Deploy
- Click "Deploy" button in Vercel dashboard
- Wait 2-5 minutes for build to complete
- Your app is live! 🎉

---

## 📋 Critical Files

**Must include in repository:**

| File | Purpose |
|------|---------|
| `best_cough_classifier.pt` | Trained ML model (required for predictions) |
| `api/predict.py` | Prediction endpoint |
| `api/requirements.txt` | Python dependencies |
| `vercel.json` | Build configuration |
| `ReactFrontend/package.json` | Frontend dependencies |

**⚠️ Model File Size:** 
- If model is < 50MB: Include in repository ✅
- If model is > 50MB: Use Git LFS or download at runtime

---

## 🔧 Environment Variables

**In Vercel Dashboard → Settings → Environment Variables:**
(These may already be set from vercel.json)

```
VITE_API_URL = /api
NODE_ENV = production
```

---

## 🧪 Test Your Deployment

Once deployed, test with curl:

```bash
# Health check
curl https://your-vercel-app.vercel.app/api/health

# Get available classes
curl https://your-vercel-app.vercel.app/api/classes

# Test prediction (replace with .wav file)
curl -X POST https://your-vercel-app.vercel.app/api/predict \
  -F "files=@test_audio.wav"
```

---

## 📊 API Endpoints

After deployment:

| Endpoint | Method | Response |
|----------|--------|----------|
| `/api/health` | GET | `{status, model_loaded, device}` |
| `/api/classes` | GET | `{classes, count}` |
| `/api/predict` | POST | `{prediction, confidence, probabilities}` |

---

## 🐛 If Things Go Wrong

### Build Failed
1. Check [Vercel Function logs](https://vercel.com) → Deployments → Logs
2. Verify `api/requirements.txt` has all dependencies
3. Check Python version (should be 3.11+)

### API Returns 500 Error
1. Model file may not be found - API falls back to mock mode
2. Check function logs in Vercel dashboard
3. Verify `best_cough_classifier.pt` exists in root

### frontend shows "Connection error"
1. Verify `VITE_API_URL=/api` is set in environment
2. Check browser console for error messages
3. Ensure build includes `.env.production`

### Model file too large
```bash
# Use Git LFS
git lfs install
git lfs track "*.pt"
git add .gitattributes
git commit -m "Track model with LFS"
git push
```

---

## 📚 Documentation

- **Full Guide**: See [VERCEL_DEPLOYMENT.md](VERCEL_DEPLOYMENT.md)
- **Vercel Docs**: https://vercel.com/docs
- **Python Functions**: https://vercel.com/docs/functions/serverless-functions/python
- **Local Testing**: Run `npm run build` then `npx serve dist` in ReactFrontend/

---

## 💡 Pro Tips

1. **Custom Domain**: Add domain in Vercel Settings after first deployment
2. **Monitoring**: Use Vercel Analytics for performance tracking
3. **Rollback**: Easy rollback to previous deployments in Vercel dashboard
4. **Regional Deployment**: Configure in `vercel.json` for latency optimization
5. **API Caching**: Consider caching predictions for common inputs

---

## Next Steps

- [ ] Push code to GitHub
- [ ] Import project to Vercel
- [ ] Set environment variables (if needed)
- [ ] Deploy
- [ ] Test all endpoints
- [ ] Monitor logs for issues
- [ ] Share your live app!

---

**Ready to deploy? Let's go! 🚀**

For questions or issues, refer to [VERCEL_DEPLOYMENT.md](VERCEL_DEPLOYMENT.md) for detailed troubleshooting.
