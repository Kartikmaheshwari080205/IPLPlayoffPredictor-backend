# IPL Playoff Predictor

This project simulates IPL playoff qualification probabilities for 10 teams based on:

- Current and remaining matches from `matches.txt`
- Head-to-head matrix from `h2h.txt`

Two C++ programs are included:

- `predictor.cpp`: Uses memoization to merge identical point-table end states before computing top-4 probabilities.
- `temp.cpp`: Simulates all branches directly.

Both programs:

- Parse human-editable input files
- Compute pairwise win probabilities using H2H
- Simulate all pending matches
- Print qualification probabilities
- Print total execution time in milliseconds

## Team List

The code expects exactly these teams:

- MI
- CSK
- RCB
- KKR
- RR
- DC
- PBKS
- SRH
- GT
- LSG

## Input Files

### matches.txt

Format per non-comment line:

```text
<team1> <team2> <matchid> <result>
```

Rules:

- `team1` and `team2`: team names (case-insensitive)
- `matchid`: integer
- `result` can be:
  - `PENDING` (match not played)
  - `NR` (no result/draw)
  - winner team name (must be one of `team1` or `team2`)

Notes:

- Lines starting with `#` are ignored.
- Numeric legacy values are also accepted by parser:
  - `-1` -> `PENDING`
  - `0` -> `NR`
  - `1` -> `team1` win
  - `2` -> `team2` win

### h2h.txt

Format is a labeled matrix for easy editing:

```text
TEAM MI CSK RCB KKR RR DC PBKS SRH GT LSG
MI   0  21  19  25  15 17 18   10  5  6
CSK  19 0   21  21  16 20 17   15  4  3
...
```

Rules:

- First row is column header (`TEAM` + 10 team labels)
- Each next row starts with row team label + 10 integers
- Lines starting with `#` are ignored
- Exactly 10 team rows are required

## Build

Use any C++17 compiler.

### Windows (g++)

```powershell
g++ -std=c++17 -O2 predictor.cpp -o predictor.exe
g++ -std=c++17 -O2 temp.cpp -o temp.exe
```

## Run

From project root:

```powershell
./predictor.exe
./temp.exe
```

Each run prints:

- Parsed match list
- Current points table
- Remaining matches
- Pairwise probabilities
- Final playoff qualification probabilities
- `Time taken: <ms> ms`

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
