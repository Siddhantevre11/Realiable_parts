# Deployment Guide - ReliableParts AI Sales Dashboard

Complete step-by-step guide for deploying the ReliableParts project to production.

## Overview

- **Backend**: Deploy to [Render](https://render.com) (FastAPI)
- **Frontend**: Deploy to [Vercel](https://vercel.com) (Next.js)
- **Database**: SQLite (included in backend deployment)

---

## Prerequisites

### Required Accounts
- [GitHub](https://github.com) - For code hosting
- [Render](https://render.com) - For backend hosting (free tier available)
- [Vercel](https://vercel.com) - For frontend hosting (free tier available)
- [OpenAI](https://platform.openai.com) - For API key

### Required Local Tools
- Git installed
- OpenAI API key with credits

---

## Part 1: Push to GitHub

### Step 1: Initialize Git Repository

```bash
cd c:\Users\sidev\reliableparts-project

# Initialize git
git init

# Add all files
git add .

# Create first commit
git commit -m "Initial commit: ReliableParts AI Sales Dashboard"
```

### Step 2: Create GitHub Repository

1. Go to [GitHub](https://github.com)
2. Click **New Repository**
3. Repository settings:
   - **Name**: `reliableparts-project`
   - **Description**: AI-powered sales dashboard for appliance parts
   - **Visibility**: Public or Private
   - **DO NOT** initialize with README (we already have one)
4. Click **Create repository**

### Step 3: Push to GitHub

```bash
# Add remote origin (replace YOUR_USERNAME with your GitHub username)
git remote add origin https://github.com/YOUR_USERNAME/reliableparts-project.git

# Push to GitHub
git branch -M main
git push -u origin main
```

### Step 4: Verify Upload

Visit `https://github.com/YOUR_USERNAME/reliableparts-project` and verify all files are uploaded.

**IMPORTANT**: Check that no `.env` files or `.db` files were uploaded (they should be excluded by `.gitignore`)

---

## Part 2: Deploy Backend to Render

### Step 1: Prepare Database

Before deploying, ensure you have the database file:

```bash
# If database doesn't exist in backend/database/, build it:
cd backend
python build_database.py
```

This creates `backend/database/products.db` which will be deployed with the app.

### Step 2: Create Render Web Service

1. Go to [Render Dashboard](https://dashboard.render.com/)
2. Click **New +** → **Web Service**
3. Connect your GitHub repository:
   - Click **Connect GitHub**
   - Authorize Render
   - Select `reliableparts-project` repository

### Step 3: Configure Backend Service

Fill in the following settings:

**Basic Settings:**
- **Name**: `reliableparts-backend` (or your choice)
- **Region**: Choose closest to your users
- **Branch**: `main`
- **Root Directory**: `backend`
- **Runtime**: `Python 3`

**Build Settings:**
- **Build Command**:
  ```
  pip install -r requirements.txt
  ```

**Start Command**:
```
uvicorn api.main:app --host 0.0.0.0 --port 10000
```

**Instance Type:**
- Free tier is sufficient for testing
- Upgrade to paid for production use

### Step 4: Add Environment Variables

In the **Environment** section, add:

| Key | Value | Notes |
|-----|-------|-------|
| `OPENAI_API_KEY` | `sk-your-key-here` | Get from [OpenAI Dashboard](https://platform.openai.com/api-keys) |
| `DATABASE_PATH` | `database/products.db` | Relative path to database |
| `OPENAI_MODEL` | `gpt-3.5-turbo` | GPT model to use |
| `EMBEDDING_MODEL` | `text-embedding-3-small` | Embedding model |

**CRITICAL**: Make sure to use your actual OpenAI API key!

### Step 5: Deploy

1. Click **Create Web Service**
2. Wait for deployment (5-10 minutes for first deploy)
3. Monitor logs for any errors

### Step 6: Verify Backend

Once deployed, you'll get a URL like: `https://reliableparts-backend.onrender.com`

Test the API:

```bash
# Health check
curl https://reliableparts-backend.onrender.com/api/health

# Expected response:
# {"status":"healthy","message":"ReliableParts API is running"}
```

Visit the interactive docs:
- `https://reliableparts-backend.onrender.com/docs`

**IMPORTANT NOTES:**
- First request after inactivity may be slow (free tier spins down)
- Database is stored on disk and persists between deploys
- For production, consider upgrading to paid tier for better performance

---

## Part 3: Deploy Frontend to Vercel

### Step 1: Install Frontend Dependencies Locally (Optional)

Test locally first to ensure everything works:

```bash
cd frontend
npm install
npm run build

# If build succeeds, you're ready to deploy
```

### Step 2: Create Vercel Project

1. Go to [Vercel Dashboard](https://vercel.com/dashboard)
2. Click **Add New...** → **Project**
3. Import your GitHub repository:
   - Click **Import Git Repository**
   - Select `reliableparts-project`
   - Click **Import**

### Step 3: Configure Frontend Deployment

**Configure Project:**
- **Framework Preset**: Next.js (should auto-detect)
- **Root Directory**: `frontend` (IMPORTANT!)
- **Build Command**: `npm run build` (auto-detected)
- **Output Directory**: `.next` (auto-detected)
- **Install Command**: `npm install` (auto-detected)

### Step 4: Add Environment Variables

Click **Environment Variables** and add:

| Key | Value | Notes |
|-----|-------|-------|
| `NEXT_PUBLIC_API_URL` | `https://reliableparts-backend.onrender.com/api` | Your Render backend URL |

**IMPORTANT**:
- Use the full URL from your Render deployment
- Must include `/api` at the end
- Must start with `NEXT_PUBLIC_` to be exposed to browser

### Step 5: Deploy

1. Click **Deploy**
2. Wait for build and deployment (2-5 minutes)
3. Monitor build logs for errors

### Step 6: Verify Frontend

Once deployed, you'll get a URL like: `https://reliableparts-project.vercel.app`

**Test the application:**
1. Visit your Vercel URL
2. Try the search feature
3. Try the chat feature
4. Check analytics dashboard

**If you get CORS errors:**
- Check that `NEXT_PUBLIC_API_URL` in Vercel matches your Render URL exactly
- Verify backend API is running (visit `/docs` endpoint)
- Check browser console for specific error messages

---

## Part 4: Post-Deployment Configuration

### Update CORS Settings (If Needed)

If frontend can't connect to backend, update CORS in `backend/api/main.py`:

```python
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",
        "https://reliableparts-project.vercel.app",  # Add your Vercel URL
        "https://*.vercel.app"
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

Commit and push changes:

```bash
git add backend/api/main.py
git commit -m "Update CORS for production frontend"
git push
```

Render will auto-deploy the update.

### Set Up Custom Domains (Optional)

**Backend (Render):**
1. Go to Render dashboard → Your service → Settings
2. Click **Custom Domains**
3. Add your domain (e.g., `api.reliableparts.com`)
4. Follow DNS configuration instructions

**Frontend (Vercel):**
1. Go to Vercel dashboard → Your project → Settings → Domains
2. Add your domain (e.g., `reliableparts.com`)
3. Follow DNS configuration instructions

---

## Part 5: Monitoring and Maintenance

### Monitor Backend Performance

**Render Dashboard:**
- View logs: Dashboard → Your service → Logs
- Monitor metrics: CPU, memory usage
- Check for errors in deployment logs

**Render Logs:**
```bash
# API request logs appear in Render dashboard
# Look for:
# - 200 responses (success)
# - 500 responses (errors)
# - OpenAI API call latency
```

### Monitor Frontend Performance

**Vercel Dashboard:**
- View deployment logs
- Check build status
- Monitor function invocations

### Update Database

To update products database:

1. **Local:**
   ```bash
   cd backend
   python build_database.py  # Rebuild with new data
   ```

2. **Commit and push:**
   ```bash
   git add backend/database/products.db
   git commit -m "Update products database"
   git push
   ```

3. Render will auto-deploy with updated database

### Cost Monitoring

**OpenAI API:**
- Visit [OpenAI Usage](https://platform.openai.com/usage)
- Monitor costs per day
- Expected costs:
  - Search: ~$0.0001 per query
  - Chat: ~$0.001-0.003 per message
  - Embeddings: ~$0.00002 per product

**Render:**
- Free tier: Spins down after inactivity
- Paid tier: Starts at $7/month

**Vercel:**
- Free tier: 100GB bandwidth, generous limits
- Paid tier: $20/month per member

---

## Troubleshooting

### Backend Issues

**"Chat service unavailable"**
- Check `OPENAI_API_KEY` in Render environment variables
- Verify API key is valid at [OpenAI Dashboard](https://platform.openai.com/api-keys)
- Check Render logs for specific error

**"No embeddings found"**
- Ensure `backend/database/products.db` was deployed
- Check database file size in Render (shouldn't be 0 bytes)
- Rebuild database locally and redeploy

**"Module not found" errors**
- Check `requirements.txt` includes all dependencies
- Verify build command ran successfully in Render logs

**Slow API responses**
- Free tier spins down after inactivity (first request slow)
- Upgrade to paid tier for always-on service
- Check OpenAI API latency in logs

### Frontend Issues

**"Failed to fetch" or CORS errors**
- Verify `NEXT_PUBLIC_API_URL` in Vercel settings
- Check backend CORS configuration includes Vercel URL
- Test backend directly: visit `https://your-backend.onrender.com/docs`

**Build failures**
- Check build logs in Vercel
- Verify `package.json` has correct dependencies
- Test build locally: `npm run build`

**Environment variables not working**
- Ensure variable names start with `NEXT_PUBLIC_`
- Redeploy after adding new environment variables
- Check browser Network tab to see what URL is being called

### Database Issues

**Products not showing**
- Verify database file exists and has data
- Check Render logs for database connection errors
- Test locally: `python db_queries.py`

**Search returns no results**
- Check if embeddings were generated
- Verify OpenAI API key has credits
- Test semantic search locally first

---

## Performance Optimization

### Backend Optimizations

1. **Enable API response caching:**
   - Cache search results for common queries
   - Use Redis for session storage

2. **Database indexing:**
   - Already implemented in `db_loader.py`
   - Indexes on SKU, brand, category, price

3. **Upgrade instance type:**
   - Move from free tier to paid for better performance
   - Consider 2GB RAM instance for production

### Frontend Optimizations

1. **Image optimization:**
   - Use Next.js Image component
   - Configure image domains in `next.config.mjs`

2. **Code splitting:**
   - Already implemented with Next.js App Router
   - Lazy load heavy components

3. **Edge caching:**
   - Vercel automatically caches static assets
   - Configure `stale-while-revalidate` for API calls

---

## Security Checklist

- [ ] `.env` files not committed to GitHub
- [ ] `.gitignore` properly configured
- [ ] OpenAI API key stored only in environment variables
- [ ] CORS configured to allow only your frontend domain
- [ ] Database file permissions properly set
- [ ] No sensitive data in logs
- [ ] HTTPS enabled (automatic with Vercel/Render)
- [ ] API rate limiting considered for production

---

## Scaling Considerations

### When to Scale Backend

**Indicators:**
- API response times > 5 seconds
- High CPU/memory usage (>80%)
- Frequent 503 errors
- High concurrent users

**Solutions:**
- Upgrade Render instance type
- Implement Redis caching
- Add CDN for static assets
- Consider horizontal scaling with load balancer

### When to Scale Frontend

**Indicators:**
- Slow page loads (>3 seconds)
- High bandwidth usage
- Build times too long

**Solutions:**
- Optimize images and assets
- Enable Vercel edge functions
- Implement incremental static regeneration
- Use Vercel Analytics to identify bottlenecks

### When to Migrate Database

**Move from SQLite to PostgreSQL when:**
- Concurrent writes needed (>10 simultaneous)
- Database size > 1GB
- Need advanced features (full-text search, JSON queries)
- Multi-region deployment required

**Migration path:**
1. Export SQLite data
2. Create PostgreSQL database (e.g., on Render or Supabase)
3. Import data
4. Update connection strings
5. Test thoroughly before switching

---

## Backup Strategy

### Database Backups

**Manual backup:**
```bash
# Download from Render
# Or commit to git periodically
git add backend/database/products.db
git commit -m "Backup: $(date)"
git push
```

**Automated backups:**
- Use Render Disk backups (paid feature)
- Or set up scheduled job to upload to S3/Google Cloud Storage

### Code Backups

- GitHub is your primary backup
- Consider enabling branch protection
- Tag releases: `git tag v1.0.0 && git push --tags`

---

## Continuous Deployment (CD)

Both Render and Vercel support automatic deployments:

**Automatic deployments on push:**
1. Push to `main` branch
2. Render rebuilds backend automatically
3. Vercel rebuilds frontend automatically
4. Both deploy if builds succeed

**Branch deployments:**
- Vercel creates preview deployments for every branch/PR
- Test changes before merging to main
- Preview URL: `https://reliableparts-project-git-feature.vercel.app`

---

## Getting Help

### Resources

- **FastAPI Docs**: https://fastapi.tiangolo.com
- **Next.js Docs**: https://nextjs.org/docs
- **Render Docs**: https://render.com/docs
- **Vercel Docs**: https://vercel.com/docs
- **OpenAI Docs**: https://platform.openai.com/docs

### Support Channels

- **Render**: support@render.com
- **Vercel**: https://vercel.com/support
- **OpenAI**: help.openai.com

---

## Summary

You now have:
- ✅ Backend deployed on Render with FastAPI
- ✅ Frontend deployed on Vercel with Next.js
- ✅ Database included in deployment
- ✅ OpenAI integration configured
- ✅ Automatic deployments on git push
- ✅ HTTPS enabled
- ✅ Production-ready infrastructure

**Your URLs:**
- Backend API: `https://your-service.onrender.com`
- Frontend: `https://your-project.vercel.app`
- API Docs: `https://your-service.onrender.com/docs`

**Next steps:**
1. Test all features in production
2. Monitor costs and performance
3. Set up custom domains (optional)
4. Implement analytics tracking
5. Add monitoring/alerting tools
