# Data Update Strategies for Docker Backend

## 🏆 Option 1: GitHub Actions Scheduled Workflow (RECOMMENDED)

**Best for:** Cloud-based, automatic, no infrastructure needed

### How It Works:
1. Workflow runs on a schedule (e.g., 2 AM daily)
2. Pulls latest code
3. Runs `nightly_job.py`
4. Updates `matches.txt`, `h2h.txt`, and `probabilities.txt`
5. Auto-commits and pushes changes back to GitHub

### Advantages:
✅ Free (part of GitHub Actions)  
✅ No setup needed  
✅ Automatic - just set it and forget it  
✅ Logs visible in GitHub UI  
✅ Can manually trigger anytime  

### Configuration:
Already created in `.github/workflows/nightly-update.yml`

Edit the cron schedule:
```yaml
# Current: 2 AM UTC daily
- cron: '0 2 * * *'

# Other examples:
- cron: '0 0 * * *'   # Midnight UTC
- cron: '30 1 * * *'  # 1:30 AM UTC
- cron: '0 20 * * *'  # 8 PM UTC
```

### Timezone Reference:
- UTC 2:00 AM = IST 7:30 AM (for India)
- Adjust the hour value in cron accordingly

---

## 🐳 Option 2: Docker Container with Internal Scheduler

**Best for:** Running everything inside Docker, self-contained

### Using APScheduler (Python):

Create `scheduled_job.py`:
```python
from apscheduler.schedulers.background import BackgroundScheduler
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent

def run_nightly_job():
    print("🔄 Running nightly job...")
    result = subprocess.run([sys.executable, ROOT / "nightly_job.py"], 
                          capture_output=True, text=True)
    print(result.stdout)
    if result.returncode != 0:
        print("ERROR:", result.stderr)
    print("✅ Nightly job completed")

def start_scheduler():
    scheduler = BackgroundScheduler()
    # Run at 2 AM UTC daily
    scheduler.add_job(run_nightly_job, 'cron', hour=2, minute=0)
    scheduler.start()
    print("⏰ Scheduler started - will run nightly job at 2 AM UTC")

if __name__ == "__main__":
    start_scheduler()
    try:
        # Keep scheduler running
        while True:
            pass
    except KeyboardInterrupt:
        scheduler.shutdown()
```

Install APScheduler:
```bash
pip install apscheduler
```

Update `docker-compose.yml`:
```yaml
services:
  backend:
    # ... existing config ...
    
  scheduler:
    build:
      context: .
      dockerfile: Dockerfile
    container_name: ipl-scheduler
    volumes:
      - ./matches.txt:/app/matches.txt
      - ./h2h.txt:/app/h2h.txt
      - ./ipl_json:/app/ipl_json
    environment:
      - PORT=8001
    command: ["python", "scheduled_job.py"]
    restart: unless-stopped
```

### Advantages:
✅ Self-contained in Docker  
✅ Always running  
✅ No external dependencies  

### Disadvantages:
❌ Need to keep container always running  
❌ More complex setup  

---

## 💻 Option 3: Linux/Mac Cron Job

**Best for:** Running on your own server (Linux/Mac)

### Set up cron:
```bash
# Edit crontab
crontab -e

# Add this line (runs at 2 AM daily):
0 2 * * * cd /path/to/IPLPlayoffPredictor-backend && docker-compose exec -T backend python nightly_job.py

# For Docker Compose up and running:
0 2 * * * cd /path/to/IPLPlayoffPredictor-backend && docker-compose exec -T backend python nightly_job.py >> /var/log/ipl-nightly.log 2>&1
```

### Test the cron job:
```bash
# Run manually to verify it works
cd /path/to/IPLPlayoffPredictor-backend
docker-compose exec backend python nightly_job.py

# Check cron logs
grep CRON /var/log/syslog  # Linux
log show --predicate 'process == "cron"'  # Mac
```

---

## 🪟 Option 4: Windows Task Scheduler

**Best for:** Running on Windows machine

### Step 1: Create a batch script `run-nightly.bat`:
```batch
@echo off
cd C:\Users\karti\Desktop\IPLPlayoffPredictor\IPLPlayoffPredictor-backend
docker-compose exec -T backend python nightly_job.py
```

### Step 2: Schedule with Task Scheduler:
1. Open Task Scheduler (Press `Win + R`, type `taskschd.msc`)
2. Click "Create Basic Task..."
3. Name: "IPL Nightly Update"
4. Trigger: Daily at 2 AM
5. Action: Run program → `run-nightly.bat`

---

## 🚀 Option 5: GitHub Actions + Docker Hub (Advanced)

**Best for:** Public automated deployments

Create workflow that:
1. Runs nightly job
2. Updates Docker image
3. Pushes new image to registry
4. Notifies deployment system

```yaml
name: Nightly Update + Docker Push

on:
  schedule:
    - cron: '0 2 * * *'

jobs:
  update-and-build:
    runs-on: ubuntu-latest
    
    steps:
      - uses: actions/checkout@v4
      
      - name: Run nightly job
        run: |
          cd IPLPlayoffPredictor-backend
          python nightly_job.py
      
      - name: Commit changes
        run: |
          git config user.email "action@github.com"
          git config user.name "GitHub Action"
          git add -A
          git commit -m "Update data - $(date)" || true
          git push
      
      - name: Rebuild and push Docker image
        uses: docker/build-push-action@v5
        with:
          context: ./IPLPlayoffPredictor-backend
          push: true
          tags: ghcr.io/${{ github.repository }}/backend:latest
```

---

## ✨ Comparison Table

| Method | Setup | Cost | Always Running | Best For |
|--------|-------|------|-----------------|----------|
| **GitHub Actions (Cron)** | Easy | Free | No | 🏆 Recommended |
| **Docker Scheduler** | Medium | Free | Yes | Self-contained |
| **Linux Cron** | Easy | Free | Yes | Linux servers |
| **Windows Task Scheduler** | Medium | Free | Yes | Windows machines |
| **Docker + GitHub Actions** | Complex | Free | Varies | Large deployments |

---

## 📊 How Data Flows in GitHub Actions Option

```
GitHub Actions (2 AM UTC)
        ↓
Checkout code
        ↓
Run nightly_job.py
  - Fetches IPL data
  - Updates matches.txt
  - Updates h2h.txt
  - Generates probabilities.txt
        ↓
Git commit & push
        ↓
Docker image rebuilds (triggered by push)
        ↓
New image pushed to GHCR
        ↓
Your deployment pulls fresh image
```

---

## 🎯 Recommended Setup

**Use GitHub Actions scheduled workflow** because:
1. ✅ No infrastructure to manage
2. ✅ Automatic and reliable
3. ✅ Free
4. ✅ Integrated with your repository
5. ✅ Visible logs and history
6. ✅ Can manually trigger anytime

The data gets updated, committed to GitHub, and your latest Docker image will have the fresh data!

---

## 🔧 Next Steps

1. Commit the nightly-update workflow
2. Test it manually by clicking "Run workflow" in GitHub Actions
3. Verify it successfully runs and updates the data
4. Adjust the cron schedule if needed

---

## ⚠️ Important Notes

- **Credentials**: If your `nightly_job.py` needs authentication, use GitHub Secrets
- **Network**: The action runs on GitHub's servers, so no local machine needed
- **Logs**: Check GitHub Actions → Workflows → Nightly Data Update for logs
- **Data**: Updated files are committed back to your repository automatically
