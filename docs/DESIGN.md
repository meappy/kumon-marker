# Kumon Marker - Design Document

## Overview

An automated system for marking Kumon worksheets. Scans handwritten answers from PDF worksheets, verifies correctness, annotates the PDF with marks, and generates detailed reports.

## User Requirements

- **Scanner**: Brother scanner/printer auto-uploads to Google Drive
- **Folder**: `From_BrotherDevice` in My Drive
- **File format**: `YYYYMMDDHHmmss_001.pdf` (timestamp from scanner)
- **Marking style**:
  - All correct on page → Circle entire page (green)
  - Incorrect answers → Tick mark next to wrong answer (red)
- **Output**: Marked PDF + Report with correct solutions
- **Deployment**: Kubernetes (Helm chart), works on OrbStack locally and hosted clusters
- **UI**: Responsive web interface

## Architecture

```
┌────────────────────────────────────────────────────────────────┐
│                         Browser                                 │
│                    (Responsive React UI)                        │
└────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌────────────────────────────────────────────────────────────────┐
│                    Ingress Controller                           │
│              (nginx-ingress / traefik)                          │
└────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌────────────────────────────────────────────────────────────────┐
│                    Kumon Marker Service                         │
│  ┌──────────────────────────────────────────────────────────┐  │
│  │                   FastAPI Backend                         │  │
│  │  POST /api/upload        - Upload scanned PDFs           │  │
│  │  POST /api/process/{id}  - Mark a worksheet              │  │
│  │  GET  /api/reports       - List all reports              │  │
│  │  GET  /api/gdrive/sync   - Sync from Google Drive        │  │
│  │  GET  /api/config        - Get configuration             │  │
│  │  PUT  /api/config        - Update configuration          │  │
│  └──────────────────────────────────────────────────────────┘  │
│  ┌──────────────────────────────────────────────────────────┐  │
│  │              Static React UI (served by FastAPI)          │  │
│  └──────────────────────────────────────────────────────────┘  │
└────────────────────────────────────────────────────────────────┘
                              │
              ┌───────────────┼───────────────┐
              ▼               ▼               ▼
┌──────────────────┐ ┌──────────────┐ ┌──────────────────┐
│  Persistent Vol  │ │  Claude API  │ │ Google Drive API │
│  - scans/        │ │  (Vision)    │ │  (Sync sheets)   │
│  - marked/       │ └──────────────┘ └──────────────────┘
│  - reports/      │
└──────────────────┘
```

## Technology Stack

| Layer | Technology | Rationale |
|-------|------------|-----------|
| **Frontend** | React + Vite + Tailwind CSS | Fast, responsive, modern |
| **Backend** | FastAPI (Python) | Async, great for AI APIs, type-safe |
| **PDF Processing** | PyMuPDF | Fast PDF annotation |
| **Vision/OCR** | Claude API | Best for handwriting recognition |
| **Container** | Docker (multi-stage) | Single image, easy deployment |
| **Orchestration** | Helm 3 | Industry standard, templated configs |
| **Local K8s** | OrbStack | macOS Kubernetes |

## Project Structure

```
~/Projects/kumon-marker/
├── frontend/                    # React application
│   ├── src/
│   │   ├── components/          # UI components
│   │   ├── pages/               # Page views
│   │   ├── hooks/               # Custom hooks
│   │   └── api/                 # API client
│   ├── package.json
│   └── vite.config.ts
│
├── backend/                     # FastAPI application
│   ├── app/
│   │   ├── main.py              # Entry point
│   │   ├── routers/             # API endpoints
│   │   ├── services/            # Business logic
│   │   │   ├── ocr.py           # Claude vision
│   │   │   ├── checker.py       # Answer verification
│   │   │   ├── annotator.py     # PDF marking
│   │   │   ├── reporter.py      # Report generation
│   │   │   └── gdrive.py        # Google Drive sync
│   │   └── models/              # Pydantic schemas
│   └── requirements.txt
│
├── helm/
│   └── kumon-marker/
│       ├── Chart.yaml
│       ├── values.yaml          # Default values
│       ├── values-local.yaml    # OrbStack overrides
│       ├── values-prod.yaml     # Production overrides
│       └── templates/
│           ├── deployment.yaml
│           ├── service.yaml
│           ├── ingress.yaml
│           ├── pvc.yaml
│           ├── configmap.yaml
│           └── secret.yaml
│
├── scripts/                     # Utility scripts
│   └── mark_worksheet.py        # CLI marking tool
│
├── docs/                        # Documentation
│   └── DESIGN.md               # This file
│
├── Dockerfile                   # Multi-stage build
├── docker-compose.yaml          # Quick local dev (no K8s)
│
└── data/                        # Local data (mounted as PV)
    ├── scans/incoming/
    ├── marked/
    └── reports/
```

## Kumon Worksheet Format

### Sheet Structure
- Sheet ID: `B161a`, `B161b`, `B162a`, etc. (a = front, b = back)
- Title: "Subtraction of 3-Digit Numbers 1"
- Grade scale printed on each sheet
- 8-10 questions per side, 18-20 per sheet
- Name, Date, Time fields

### Grading Scale (varies by sheet)
```
Grade A: ~90% (1-2 mistakes)
Grade B: ~70% (3-6 mistakes)
Grade C: ~50% (7-10 mistakes)
Grade D: 49%~ (11-20 mistakes)
```

### Question Format
- Vertical subtraction: 3-digit minus 2-digit
- Handwritten answers below the line
- Some sheets include word problems and number sequences

## Marking Logic

### Correct Answers
- If ALL answers on a page are correct → Draw large circle around entire page
- Circle colour: Green (#22c55e)

### Incorrect Answers
- Place a tick (✓) next to each wrong answer
- Optionally show correct answer nearby
- Tick colour: Red (#ef4444)

### Grade Assignment
- Count total mistakes across both sides (a + b)
- Apply grade scale from sheet header
- Fill in grade box on the worksheet

## Google Drive Integration

### Source Folder
- Path: `My Drive/From_BrotherDevice`
- Auto-populated by Brother scanner

### File Naming
```
Format: YYYYMMDDHHmmss_001.pdf

Examples:
├── 20260114130247_001.pdf  →  2026-01-14 13:02:47
├── 20260113224351_001.pdf  →  2026-01-13 22:43:51
└── 20260107232454_001.pdf  →  2026-01-07 23:24:54
```

### Sync Strategy
- **Primary**: Manual sync button in UI
- **Secondary**: Auto-poll every N minutes (configurable)
- Track processed files to avoid duplicates

### Output Folder
- Path: `My Drive/Kumon_Marked`
- Marked PDFs uploaded here after processing

## Configuration

### Helm Values (Source of Truth)

```yaml
config:
  anthropic:
    apiKey: ""
    model: "claude-sonnet-4-20250514"
    maxTokens: 4096

  googleDrive:
    enabled: true
    folderName: "From_BrotherDevice"
    syncIntervalMinutes: 5
    autoSync: true
    uploadMarked: true
    markedFolderName: "Kumon_Marked"
    oauth:
      clientId: ""
      clientSecret: ""

  marking:
    correctMark: "circle_page"
    incorrectMark: "tick"
    showCorrectAnswer: true
    colours:
      correct: "#22c55e"
      incorrect: "#ef4444"

  grading:
    useSheetScale: true
    customScale: null
```

### Generated config.json

Helm templates generate `config.json` stored as Kubernetes Secret, mounted at `/app/config/config.json`.

### Runtime Updates

UI Settings page can modify config at runtime:
1. Backend reads current Secret
2. Merges user changes
3. Updates Secret
4. App reloads config

## Deployment

### Local (OrbStack)

```bash
helm install kumon-marker ./helm/kumon-marker \
  -f ./helm/kumon-marker/values-local.yaml \
  --set config.anthropic.apiKey="sk-ant-..."

# Access at http://kumon.localhost
```

### Production

```bash
helm install kumon-marker ./helm/kumon-marker \
  -f ./helm/kumon-marker/values-prod.yaml \
  --set config.anthropic.apiKey="${ANTHROPIC_API_KEY}"
```

## API Cost Estimate

- Claude Vision: ~$3 per 1000 pages (Sonnet)
- 20-page Kumon PDF: ~$0.06 per marking session
- Google Drive API: Free tier sufficient

## UI Wireframes

### Main Dashboard
```
┌─────────────────────────────────────────────────────────────┐
│  🎯 Kumon Marker                    [Sync Drive] [Settings] │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  ┌─────────────────────────────────────────────────────┐   │
│  │  📤 Drop PDF here or click to upload                │   │
│  └─────────────────────────────────────────────────────┘   │
│                                                             │
│  Recent Worksheets                                          │
│  ┌─────────────┬─────────────┬─────────────┬────────────┐  │
│  │ B161-B170   │ 14 Jan 2026 │ Grade: B    │ [View] [📥]│  │
│  │ Gemma       │ 156/164     │ 8 mistakes  │            │  │
│  └─────────────┴─────────────┴─────────────┴────────────┘  │
└─────────────────────────────────────────────────────────────┘
```

### Settings Page
```
┌─────────────────────────────────────────────────────────────────┐
│  ⚙️ Settings                                      [Save] [Reset]│
├─────────────────────────────────────────────────────────────────┤
│  🔑 API Configuration                                           │
│  📁 Google Drive                                                │
│  ✏️ Marking Style                                               │
│  📊 Advanced                                                    │
└─────────────────────────────────────────────────────────────────┘
```

## Future Enhancements

- Email reports to parents
- Progress tracking over time
- Multiple student profiles
- Support for other Kumon subjects (reading, etc.)
- Mobile app companion
