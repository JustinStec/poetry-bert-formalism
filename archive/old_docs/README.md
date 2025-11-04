# Project Documentation

All documentation for the Prosody-Conditioned BERT project.

---

## Quick Start Guides

### For Training
- **[COLAB_SETUP_GUIDE.md](COLAB_SETUP_GUIDE.md)** - How to train BERT on Google Colab Pro
- **[PROSODY_BERT_ARCHITECTURE.md](PROSODY_BERT_ARCHITECTURE.md)** - Complete technical specification of two-phase training

### For Remote Access
- **[REMOTE_ACCESS_GUIDE.md](REMOTE_ACCESS_GUIDE.md)** - SSH and file sharing setup
- **[CORPUS_MANAGEMENT.md](CORPUS_MANAGEMENT.md)** - How to add and manage poems
- **[QUICK_COMMANDS.txt](QUICK_COMMANDS.txt)** - One-page command reference

### For Career Development
- **[JOB_MATERIALS_GUIDE.md](JOB_MATERIALS_GUIDE.md)** - Use this with Claude Chat to update CV, cover letters, research statements
- **[PILOT_STUDY_GUIDE.md](PILOT_STUDY_GUIDE.md)** - Options for writing samples and publications

---

## Document Descriptions

### Technical Documentation

**PROSODY_BERT_ARCHITECTURE.md**
- Two-phase training strategy
- Phase 1: EEBO-BERT (historical language model)
- Phase 2: Prosody-conditioned BERT (novel architecture)
- Implementation details and code examples
- Timeline and expected outputs

**COLAB_SETUP_GUIDE.md**
- Step-by-step Google Colab Pro setup
- Upload corpus to Google Drive
- Configure GPU runtime
- Start training
- Monitor progress
- Download trained model

### Operational Guides

**REMOTE_ACCESS_GUIDE.md**
- Enable Remote Login on Mac
- SSH connection instructions
- File Sharing setup
- Remote poem addition via SSH or Finder

**CORPUS_MANAGEMENT.md**
- How to add poems to corpus
- Metadata management
- Automatic scanning with smart_scan_poems.py
- Batch operations

**QUICK_COMMANDS.txt**
- One-page cheat sheet
- Most common commands
- Quick reference for daily use

### Career Development

**JOB_MATERIALS_GUIDE.md**
- Complete project description for job applications
- CV entries (research, skills)
- Cover letter talking points for different job types
- Research statement framing
- Publication and grant trajectories
- Interview preparation
- **Use with Claude Chat:** Upload this file to AI assistant to update application materials

**PILOT_STUDY_GUIDE.md**
- Writing sample options after model training
- **Recommended:** Sonnet 18 case study (2-3 weeks)
- Alternative options: mini-corpus study, method comparison, pedagogical paper
- Timeline to publication
- Venue recommendations

---

## File Organization

```
docs/
├── README.md                           # This file
├── COLAB_SETUP_GUIDE.md               # Cloud training setup
├── PROSODY_BERT_ARCHITECTURE.md       # Technical specification
├── REMOTE_ACCESS_GUIDE.md             # SSH and file sharing
├── CORPUS_MANAGEMENT.md               # Poem management
├── QUICK_COMMANDS.txt                 # Command reference
├── JOB_MATERIALS_GUIDE.md             # Career development
└── PILOT_STUDY_GUIDE.md               # Writing samples
```

---

## For Specific Tasks

**I want to...**

### ...start training BERT
→ Read **COLAB_SETUP_GUIDE.md**

### ...understand the technical approach
→ Read **PROSODY_BERT_ARCHITECTURE.md**

### ...add poems to the corpus
→ Read **CORPUS_MANAGEMENT.md**

### ...access my Mac remotely
→ Read **REMOTE_ACCESS_GUIDE.md**

### ...update my CV or cover letter
→ Upload **JOB_MATERIALS_GUIDE.md** to Claude Chat

### ...write a paper/writing sample
→ Read **PILOT_STUDY_GUIDE.md**

### ...find a specific command quickly
→ Check **QUICK_COMMANDS.txt**

---

## Related Files in Project Root

- **PROJECT_STATUS.md** - Current project status and timeline
- **FILE_ORGANIZATION.md** - Overall project structure
- **README.md** - Main project README

---

**Last Updated:** October 29, 2024
