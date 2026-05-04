# IPL Playoff Predictor - Backend

A high-performance IPL playoff qualification probability predictor with REST API and automated data updates.

This project simulates IPL playoff qualification probabilities for 10 teams based on:

- Current and remaining matches from `matches.txt`
- Head-to-head matrix from `h2h.txt`

## ⚡ Quick Start (Recommended)

### Using Docker Compose

```bash
# Build and start the container
docker-compose up -d

# Check if it's running
curl http://localhost:8000/health

# Get probabilities
curl http://localhost:8000/probabilities
```

See [DOCKER_GUIDE.md](DOCKER_GUIDE.md) for more details.

### Manual Build & Run

```bash
# Build C++ binaries
g++ -std=c++17 -O2 predictor.cpp -o predictor
g++ -std=c++17 -O2 temp.cpp -o temp

# Run API server
python api_server.py

# Server runs on http://localhost:8000
```

## 🐳 Docker Deployment

Everything is containerized and ready to deploy:

```bash
# Build the image
docker build -t ipl-predictor:latest .

# Push to GitHub Container Registry
docker push ghcr.io/your-username/ipl-predictor-backend:latest
```

**Automated CI/CD**: GitHub Actions automatically builds and pushes the image on every push to main.

See [DOCKER_GUIDE.md](DOCKER_GUIDE.md) for complete Docker documentation.

## 📡 API Endpoints

### Health Check
```bash
GET http://localhost:8000/health
```

Response:
```json
{"status": "ok"}
```

### Get Probabilities
```bash
GET http://localhost:8000/probabilities
```

Response:
```json
{
  "status": "computed",
  "lastUpdated": "2026-05-04 12:30:00",
  "remainingMatches": 15,
  "teamOrder": ["MI", "CSK", "RCB", "KKR", "RR", "DC", "PBKS", "SRH", "GT", "LSG"],
  "probabilities": [0.85, 0.72, 0.65, 0.58, 0.42, 0.35, 0.28, 0.15, 0.08, 0.02],
  "mappedProbabilities": {
    "MI": 0.85,
    "CSK": 0.72,
    ...
  },
  "lastCompletedMatch": {
    "matchId": 1082591,
    "team1": "MI",
    "team2": "CSK"
  }
}
```

## 🔄 Automated Data Updates

The system automatically updates match data **4 times daily** during IPL season:

- **8:00 AM IST** - Morning update
- **2:00 PM IST** - Afternoon refresh
- **6:00 PM IST** - Evening update (before matches)
- **11:00 PM IST** - Night update (after matches)

**Smart Logic**: Only runs when there are pending matches. Stops automatically when tournament ends.

See [DATA_UPDATE_GUIDE.md](DATA_UPDATE_GUIDE.md) for implementation details.

## 🚀 CI/CD Workflows

Two GitHub Actions workflows are configured:

### 1. Docker Build & Push (`.github/workflows/docker-build.yml`)
- Triggers on every push to `main`
- Builds Docker image
- Pushes to GitHub Container Registry

### 2. Data Update (`.github/workflows/nightly-update.yml`)
- Runs 4 times daily on schedule
- Checks for pending matches
- Updates probabilities
- Auto-commits changes

## 📁 Project Structure

```
IPLPlayoffPredictor-backend/
├── predictor.cpp          # Main C++ predictor (memoization-based)
├── temp.cpp               # Alternative C++ predictor (brute-force)
├── api_server.py          # REST API server
├── nightly_job.py         # Data refresh job
├── refresh_ipl_data.py    # Refresh script for JSON data
├── matches.txt            # Match results and pending matches
├── h2h.txt                # Head-to-head win matrix
├── ipl_json/              # Match data (JSON files)
├── Dockerfile             # Docker image definition
├── docker-compose.yml     # Docker Compose configuration
├── .github/workflows/     # GitHub Actions workflows
├── DOCKER_GUIDE.md        # Docker setup guide
└── DATA_UPDATE_GUIDE.md   # Data update strategies
```

## 🔧 Build & Compilation

### Prerequisites

- **C++17** compiler (g++, clang, or MSVC)
- **Python 3.11+**

### Windows (g++)

```powershell
g++ -std=c++17 -O2 predictor.cpp -o predictor.exe
g++ -std=c++17 -O2 temp.cpp -o temp.exe
```

### Linux/Mac

```bash
g++ -std=c++17 -O2 predictor.cpp -o predictor
g++ -std=c++17 -O2 temp.cpp -o temp
```

## 📊 Algorithm Comparison

### predictor.cpp
- **Strategy**: Memoization with state merging
- **Best for**: Large number of remaining matches
- **Speed**: Faster for consolidated states
- **Memory**: Higher memory usage

### temp.cpp
- **Strategy**: Brute-force simulation
- **Best for**: Small number of remaining matches
- **Speed**: Slower but comprehensive
- **Memory**: Lower memory usage

## 📋 Input Files

## 📋 Input Files

### Supported Teams

The system expects exactly these 10 teams:

```
MI    - Mumbai Indians
CSK   - Chennai Super Kings
RCB   - Royal Challengers Bangalore
KKR   - Kolkata Knight Riders
RR    - Rajasthan Royals
DC    - Delhi Capitals
PBKS  - Punjab Kings
SRH   - Sunrisers Hyderabad
GT    - Gujarat Titans
LSG   - Lucknow Super Giants
```

### matches.txt

Format per non-comment line:

```text
<team1> <team2> <matchid> <result>
```

**Rules**:
- `team1` and `team2`: team names (case-insensitive)
- `matchid`: integer (match identifier)
- `result` can be:
  - `PENDING` - match not yet played
  - `NR` - no result / draw
  - winner team name - must be `team1` or `team2`

**Example**:
```text
# 2026 IPL Season
MI CSK 1082591 MI
RCB KKR 1082592 PENDING
LSG GT 1082593 NR
```

**Notes**:
- Lines starting with `#` are ignored
- Numeric legacy values also supported:
  - `-1` → `PENDING`
  - `0` → `NR`
  - `1` → `team1` win
  - `2` → `team2` win

### h2h.txt

Head-to-head win matrix in labeled format:

```text
TEAM  MI  CSK  RCB  KKR  RR  DC  PBKS  SRH  GT  LSG
MI    0   21   19   25   15  17  18    10   5   6
CSK   19  0    21   21   16  20  17    15   4   3
RCB   21  19   0    18   14  16  15    12   8   7
...
```

**Rules**:
- First row: column headers (`TEAM` + 10 team names)
- Each row: row team name + 10 integers (head-to-head wins)
- Integer at [i][j] = times team i has beaten team j
- Diagonal should be 0 (team vs itself)
- Lines starting with `#` are ignored
- Exactly 10 team rows required

## 📊 Performance Notes

- Both algorithms compute probabilities using Monte Carlo simulation
- Remaining matches threshold: Default is 27 (configurable in code)
- If remaining matches > threshold: Returns "unfeasible" status
- Execution time depends on:
  - Number of remaining matches
  - Algorithm choice (predictor.cpp vs temp.cpp)
  - System performance

## 🧪 Testing the API

### Using curl

```bash
# Health check
curl http://localhost:8000/health

# Get current probabilities
curl http://localhost:8000/probabilities

# Pretty print JSON
curl http://localhost:8000/probabilities | python -m json.tool
```

### Using Python

```python
import requests
import json

# Health check
response = requests.get('http://localhost:8000/health')
print(response.json())

# Get probabilities
response = requests.get('http://localhost:8000/probabilities')
data = response.json()
print(json.dumps(data, indent=2))
```

## 📚 Documentation

- **[DOCKER_GUIDE.md](DOCKER_GUIDE.md)** - Complete Docker setup and deployment
- **[DATA_UPDATE_GUIDE.md](DATA_UPDATE_GUIDE.md)** - Automated data update strategies

## 🔄 Workflow

### Local Development

```
Edit matches.txt / h2h.txt
    ↓
Run: python nightly_job.py
    ↓
View: python api_server.py
    ↓
Access: http://localhost:8000/probabilities
```

### Production (Docker + GitHub Actions)

```
Push code to main branch
    ↓
GitHub Actions builds Docker image
    ↓
Image pushed to GitHub Container Registry
    ↓
4x daily: Data update workflow runs
    ↓
New probabilities committed & pushed
    ↓
Docker image rebuilt with fresh data
    ↓
Deployment pulls latest image
```

## 📦 Deployment Options

1. **Local Docker**: `docker-compose up -d`
2. **GitHub Container Registry**: Pull and deploy anywhere
3. **Kubernetes**: Use the Docker image with K8s manifests
4. **Azure Container Instances**: Deploy the image directly
5. **Cloud Platforms**: Use with any container runtime

## 🤝 Contributing

To update match data:

1. Edit `matches.txt` with new results
2. Update `h2h.txt` if needed
3. Commit and push (triggers Docker build + data update)

Or run manually:
```bash
python nightly_job.py
```

## 📝 License

[Add your license information here]

## ✨ Summary

**IPL Playoff Predictor Backend** provides:
- ✅ High-performance C++ probability engine
- ✅ REST API for easy integration
- ✅ Docker containerization for portability
- ✅ Automated daily updates via GitHub Actions
- ✅ Ready for production deployment
- ✅ Scalable and maintainable codebase

Each run prints:

- Parsed match list
- Current points table
- Remaining matches
- Pairwise probabilities
- Final playoff qualification probabilities
- `Time taken: <ms> ms`

## API Endpoint

A lightweight API server is available in `api_server.py`.

Start it from project root:

```powershell
python api_server.py
```

The server listens on port `8000` by default (override with environment variable `PORT`).

Available endpoints:

- `GET /health` -> simple health check
- `GET /probabilities` -> returns latest snapshot from `probabilities.txt`

`/probabilities` behavior:

- If `remainingMatches > 27`, returns status `unfeasible` with message `unfeasible to compute at the moment`
- Otherwise returns:
  - `teamOrder`
  - `probabilities` (same fixed order as predictor/temp)
  - `mappedProbabilities` (team -> probability)
  - `lastUpdated`, `remainingMatches`, `status`

## Nightly Orchestration

Use `nightly_job.py` to run backend workflow in one step:

1. Run `refresh_ipl_data.py`
2. Count remaining matches from `matches.txt`
3. If `remainingMatches > 27`, write unfeasible snapshot to `probabilities.txt`
4. Otherwise run predictor executable to compute and store probabilities

Run manually:

```powershell
python nightly_job.py
```

Optional threshold override:

```powershell
python nightly_job.py --threshold 27
```

For deployment, schedule this script at 1am server time (Task Scheduler on Windows or cron/systemd timer on Linux).

## GitHub Actions Nightly Publish

You can run the nightly backend flow on GitHub Actions and publish the latest snapshot directly into your frontend repo.

Workflow file:

- `.github/workflows/nightly-publish-frontend.yml`

What it does nightly:

1. Builds `predictor.cpp` on Ubuntu runner
2. Runs `nightly_job.py`
3. Builds frontend payload JSON via `build_frontend_payload.py`
4. Clones frontend repo and updates payload file
5. Commits and pushes only if content changed

Required GitHub Secrets (in backend repo):

- `FRONTEND_REPO`: `<owner>/<repo>` for frontend repository
- `FRONTEND_REPO_PAT`: Personal access token with repo write permission to frontend repository

Optional GitHub Variables (in backend repo):

- `FRONTEND_BRANCH` (default: `main`)
- `FRONTEND_DATA_PATH` (default: `src/data/playoff_snapshot.json`)

Schedule:

- Default cron is `30 19 * * *` (1:00 AM IST)
- Adjust cron if your timezone differs

## How Probability Is Computed

For team A vs team B:

```text
P(A beats B) = (H2H[A][B] + 1) / (H2H[A][B] + H2H[B][A] + 2)
```

This is Laplace smoothing on H2H outcomes.

## Troubleshooting

If input parsing fails:

- Verify team labels are valid
- Verify each `matches.txt` row has 4 tokens
- Verify `h2h.txt` has header + 10 complete rows
- Ensure winner team in a row matches one of the two teams in that row

The programs print line-specific validation errors to help fix formatting issues quickly.
