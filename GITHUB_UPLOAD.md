# Quick Start: Upload to GitHub

Fast track guide to get your ReliableParts project on GitHub.

## Step 1: Pre-Upload Checklist

**CRITICAL - Verify no sensitive data:**

```bash
cd c:\Users\sidev\reliableparts-project

# Check for .env files (should NOT be in git)
git status | grep ".env"

# Should be empty - .env files excluded by .gitignore
```

**Files that SHOULD be excluded (by .gitignore):**
- `.env`
- `.env.local`
- `backend/database/*.db` (database files)
- `node_modules/`
- `__pycache__/`
- `.next/`

**Files that SHOULD be included:**
- `.env.example` (template without secrets)
- `.env.local.example` (template without secrets)
- `.gitignore` files
- All source code
- README files
- `requirements.txt`, `package.json`

## Step 2: Initialize Git

```bash
cd c:\Users\sidev\reliableparts-project

# Initialize repository
git init

# Add all files
git add .

# Check what will be committed
git status

# Should NOT see:
# - .env files with actual keys
# - .db database files
# - node_modules/
# - __pycache__/

# Create first commit
git commit -m "Initial commit: ReliableParts AI Sales Dashboard

- FastAPI backend with semantic search
- Next.js 14 frontend with TypeScript
- OpenAI GPT-3.5-turbo integration
- 149+ products database
- Complete deployment configuration"
```

## Step 3: Create GitHub Repository

1. Go to https://github.com
2. Click green **New** button (or **+** → New repository)
3. Fill in:
   - **Repository name**: `reliableparts-project`
   - **Description**: `AI-powered sales dashboard for appliance parts with semantic search and GPT chatbot`
   - **Visibility**: Choose Public or Private
   - **DO NOT** check "Initialize with README" (we have one)
   - **DO NOT** add .gitignore (we have one)
   - **DO NOT** add license yet
4. Click **Create repository**

## Step 4: Push to GitHub

GitHub will show you commands. Use these:

```bash
# Add GitHub as remote origin
# Replace YOUR_USERNAME with your actual GitHub username
git remote add origin https://github.com/YOUR_USERNAME/reliableparts-project.git

# Rename branch to main (if needed)
git branch -M main

# Push to GitHub
git push -u origin main
```

**If you have SSH keys set up, use SSH instead:**
```bash
git remote add origin git@github.com:YOUR_USERNAME/reliableparts-project.git
git branch -M main
git push -u origin main
```

## Step 5: Verify Upload

1. Visit your repository: `https://github.com/YOUR_USERNAME/reliableparts-project`
2. Check that you see:
   - ✅ README.md displayed on homepage
   - ✅ `backend/` and `frontend/` directories
   - ✅ `.gitignore` files
   - ✅ `.env.example` files
3. Verify excluded files:
   - ❌ NO `.env` files (with actual secrets)
   - ❌ NO `node_modules/` directory
   - ❌ NO `__pycache__/` directories
   - ❌ NO `.db` database files

## Step 6: Configure Repository Settings

### Add Description and Topics

1. Go to repository settings (top right gear icon)
2. Add **Description**:
   > AI-powered sales dashboard for appliance parts with semantic search and GPT chatbot
3. Add **Topics**:
   - `fastapi`
   - `nextjs`
   - `openai`
   - `semantic-search`
   - `chatbot`
   - `typescript`
   - `python`
   - `ai`
   - `sales-dashboard`

### Add Repository Homepage (Optional)

After deploying to Vercel, add your frontend URL as the repository website.

## Common Issues

### "Permission denied (publickey)"
- Need to set up SSH keys
- Or use HTTPS instead: `https://github.com/YOUR_USERNAME/reliableparts-project.git`
- See: https://docs.github.com/en/authentication

### "Git is not recognized"
- Install Git: https://git-scm.com/download/win
- Restart terminal after installation

### "fatal: 'origin' does not appear to be a git repository"
- Check the remote URL: `git remote -v`
- Make sure you replaced YOUR_USERNAME with your actual username

### Committed sensitive data by accident

**If you accidentally committed .env file:**

```bash
# Remove from git but keep locally
git rm --cached backend/.env
git rm --cached frontend/.env.local

# Add to .gitignore (should already be there)
echo "backend/.env" >> .gitignore
echo "frontend/.env.local" >> .gitignore

# Commit the removal
git commit -m "Remove sensitive environment files"
git push

# IMPORTANT: Rotate all secrets (get new OpenAI API key)
# The old secrets are in git history and should be considered compromised
```

## Next Steps

After pushing to GitHub:

1. **Deploy Backend to Render**
   - See: [DEPLOYMENT.md - Part 2](DEPLOYMENT.md#part-2-deploy-backend-to-render)

2. **Deploy Frontend to Vercel**
   - See: [DEPLOYMENT.md - Part 3](DEPLOYMENT.md#part-3-deploy-frontend-to-vercel)

3. **Update README with Live Links**
   ```bash
   # Edit README.md to add:
   # - Live Demo: https://your-app.vercel.app
   # - API Docs: https://your-backend.onrender.com/docs

   git add README.md
   git commit -m "Add live deployment links"
   git push
   ```

4. **Add GitHub Actions (Optional)**
   - Set up automated testing
   - Add CI/CD workflows

5. **Enable GitHub Features**
   - Issues (for bug tracking)
   - Discussions (for community)
   - Wiki (for extended docs)
   - Security advisories

## Useful Git Commands

```bash
# Check status
git status

# See what changed
git diff

# View commit history
git log --oneline

# Create new branch for features
git checkout -b feature/new-feature

# Switch back to main
git checkout main

# Pull latest changes
git pull origin main

# Push changes
git add .
git commit -m "Description of changes"
git push
```

## Collaboration

If working with a team:

1. **Protect main branch**
   - GitHub Settings → Branches → Add rule
   - Require pull request reviews before merging

2. **Use feature branches**
   ```bash
   git checkout -b feature/search-improvements
   # Make changes
   git push -u origin feature/search-improvements
   # Create pull request on GitHub
   ```

3. **Code review workflow**
   - Create branch → Make changes → Push → Pull Request → Review → Merge

## Resources

- **Git Documentation**: https://git-scm.com/doc
- **GitHub Guides**: https://guides.github.com
- **Git Tutorial**: https://www.atlassian.com/git/tutorials

---

**You're ready to go!** 🚀

Push your code and proceed to deployment following [DEPLOYMENT.md](DEPLOYMENT.md).
