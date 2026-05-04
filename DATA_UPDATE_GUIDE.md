# Data Update Strategies for Docker Backend

## 🏆 Option 1: GitHub Actions Scheduled Workflow (RECOMMENDED)

**Best for:** Cloud-based, automatic, no infrastructure needed

### How It Works:
1. Workflow runs **4 times daily** during IPL season
2. Checks if there are pending matches
3. If pending matches exist:
   - Pulls latest code
   - Runs `nightly_job.py`
   - Updates match data and probabilities
   - Auto-commits and pushes changes
4. If no pending matches: Skips the update (tournament over)

### Schedule (4 Times Daily):
- **8:00 AM IST** - Morning update (2:30 AM UTC)
- **2:00 PM IST** - Afternoon update (8:30 AM UTC)
- **6:00 PM IST** - Evening update before matches (12:30 PM UTC)
- **11:00 PM IST** - Night update after matches (5:30 PM UTC)

### Advantages:
✅ Free (part of GitHub Actions)  
✅ Smart - only runs when matches are pending  
✅ No setup needed  
✅ Automatic - just set it and forget it  
✅ Logs visible in GitHub UI  
✅ Can manually trigger anytime  
✅ Stops automatically when tournament ends  

### Configuration:
Already created in `.github/workflows/nightly-update.yml`

Edit the cron schedule if needed:
```yaml
# Current schedule (4 times daily in IST):
- cron: '30 2 * * *'   # 8:00 AM IST
- cron: '30 8 * * *'   # 2:00 PM IST
- cron: '30 12 * * *'  # 6:00 PM IST
- cron: '30 17 * * *'  # 11:00 PM IST
```

**Cron Format**: `minute hour * * *` (in UTC)
**IST to UTC**: Subtract 5:30 hours

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
GitHub Actions (4 Times Daily - During IPL Season)
   8 AM | 2 PM | 6 PM | 11 PM IST
        ↓
Checkout code
        ↓
Check for pending matches in matches.txt
        ↓
    ┌───────────────────────────┐
    │ Pending matches found?    │
    └───────────────────────────┘
          ↙             ↖
        YES             NO
        ↓               ↓
   Run job          Skip update
   - Fetch IPL     (Tournament
   - Update data      over)
   - Commit & push
        ↓
Docker image rebuilds
        ↓
New image pushed to GHCR
        ↓
✅ Fresh data available
```

---

## 🎯 Recommended Setup

**Use GitHub Actions scheduled workflow** because:
1. ✅ Runs 4 times daily throughout IPL season
2. ✅ Smart - stops when all matches are done
3. ✅ No infrastructure to manage
4. ✅ Automatic and reliable
5. ✅ Free
6. ✅ Integrated with your repository
7. ✅ Visible logs and history
8. ✅ Can manually trigger anytime

The data gets updated **4 times daily** automatically:
- **Morning (8 AM IST)**: Pre-day update
- **Afternoon (2 PM IST)**: Midday refresh  
- **Evening (6 PM IST)**: Before match time
- **Night (11 PM IST)**: After matches

Your latest Docker image will have the freshest data!

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
