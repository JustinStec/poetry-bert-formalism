# Academic Application Composer - For Job Materials

## Project Overview
**Academic Application Composer** - A full-stack AI-powered web application for managing academic job applications, specializing in philosophy positions. Built to streamline the creation of cover letters, teaching philosophies, research statements, and diversity statements through intelligent content recommendations.

**Status:** Production-ready, actively used for 2024-2025 job cycle
**Repository:** ~/Repos/coverletter_tagger
**Integration:** MCP (Model Context Protocol) enabled for Claude Desktop integration

---

## Technical Achievement Summary

### Full-Stack Architecture
- **Frontend:** React + TypeScript, Vite build system, TipTap rich text editor
- **Backend:** FastAPI (Python), RESTful API design
- **Database:** SQLite for application tracking and storage
- **AI Integration:** OpenAI API + Sentence Transformers for semantic search
- **Configuration:** YAML-based rule system (210+ tagging rules)
- **Data Processing:** PyPDF2 for CV parsing, custom NLP pipeline

### Key Technical Features

#### 1. AI-Powered Semantic Matching
- Implemented hybrid ranking system combining:
  - OpenAI embeddings for semantic similarity
  - Tag-based filtering with 210+ comprehensive rules
  - Contextual scoring algorithm
- Achieves high-precision paragraph recommendations from library of 500+ curated texts

#### 2. Intelligent Document Generation
- Dynamic template synthesis from job posting analysis
- Slot-based architecture for modular content composition
- Auto-save and caching system using local storage
- Export pipeline to formatted Word documents (.docx)

#### 3. Application Management Dashboard
- Full CRUD operations for job applications
- Deadline tracking and status management
- Teaching materials library integration
- SQLite-backed persistence layer

#### 4. AI Refinement Pipeline
Three-mode refinement system:
- **Content refinement:** Clarity and flow improvement
- **Institutionalization:** Context-specific adaptation with institutional references
- **Research context integration:** Web search + AI synthesis for institutional priorities

#### 5. MCP Protocol Implementation
- Built custom MCP server bridging Claude Desktop ↔ FastAPI backend
- Exposes tools: `parse_cover_letter`, `get_paragraph_suggestions`, `check_style`, `health_check`
- Enables natural language interaction with application system

---

## For CV / Job Materials

### Technical Skills Demonstrated

**Programming Languages:**
- Python (FastAPI, async/await, type hints)
- TypeScript/JavaScript (React, modern ES6+)
- SQL (SQLite queries and schema design)

**Frameworks & Libraries:**
- **Backend:** FastAPI, OpenAI SDK, Sentence Transformers, PyPDF2, YAML parsing
- **Frontend:** React, React Router, TipTap, Vite
- **AI/ML:** OpenAI GPT models, sentence-transformers, semantic search

**Software Engineering:**
- RESTful API design and implementation
- Full-stack application architecture
- Database schema design and optimization
- Version control (Git)
- Development tools (virtual environments, package management)

**AI/ML Integration:**
- Prompt engineering for content refinement
- Semantic similarity scoring
- Hybrid ranking algorithms (AI + rule-based)
- Embedding-based search systems

**Modern Development Practices:**
- TypeScript for type-safe frontend development
- Async Python for performant backend
- Component-based UI architecture
- Auto-save and state management
- Error handling and validation

---

## Potential Talking Points

### For Cover Letters (Technical Skills)
> "I developed a full-stack AI-powered application management system using React, TypeScript, and FastAPI to streamline academic job applications. The system uses OpenAI's embedding models and a custom hybrid ranking algorithm to recommend contextually appropriate content from a curated paragraph library. The application features a sophisticated tagging system with 210+ rules, CV parsing capabilities, and institutional research integration. I recently extended the system with MCP (Model Context Protocol) integration, enabling seamless interaction with Claude Desktop."

### For Research Statement (Computational Methods)
> "My technical skills complement my research in digital humanities. I built a production-ready web application demonstrating proficiency in modern full-stack development, AI/ML integration, and natural language processing. This experience positions me well to lead DH initiatives and mentor students in computational methods for humanities research."

### For Teaching Philosophy (Pedagogy + Technology)
> "I bring practical experience in educational technology development. In building an academic application management system, I designed intuitive interfaces for complex workflows, implemented intelligent recommendation algorithms, and created tools that reduce cognitive load. These principles—user-centered design, progressive disclosure, and intelligent assistance—inform my approach to course design and learning platforms."

---

## Relevant CV Entries

### Under "Digital Projects" or "Technical Skills"

**Academic Application Composer** (2024)
Full-stack web application for AI-powered academic job application management
- Built with React/TypeScript frontend and FastAPI/Python backend
- Implemented semantic search using OpenAI embeddings and Sentence Transformers
- Designed hybrid ranking algorithm combining AI matching with rule-based filtering (210+ tags)
- Integrated CV parsing, institutional research context, and document export pipeline
- Extended with MCP protocol for Claude Desktop integration

### Under "Technical Skills" Section

**Programming:** Python, TypeScript/JavaScript, SQL
**Frameworks:** FastAPI, React, OpenAI API, Sentence Transformers
**Tools:** Git, Vite, SQLite, YAML, Docker
**Specializations:** Full-stack web development, AI/ML integration, RESTful API design, semantic search systems

---

## Project Context

**Purpose:** Built to solve a real workflow problem during the academic job cycle—managing hundreds of customized application materials across 50+ applications.

**Scale:**
- 500+ paragraph library with semantic tagging
- 210+ tagging rules across 8 content categories
- 4 document types (cover letters, teaching philosophy, research statements, diversity statements)
- Complete application lifecycle management (tracking, drafting, refinement, export)

**Innovation:**
- Novel hybrid ranking combining AI semantic matching with structured rule-based filtering
- Dynamic template generation from job posting analysis
- Three-mode AI refinement pipeline (clarity, institutionalization, research integration)
- MCP protocol implementation for LLM tool integration

**Impact:**
- Reduced application drafting time from 2-3 hours to 30-45 minutes per application
- Maintained consistency across materials while enabling customization
- Enabled data-driven insights into paragraph effectiveness

---

## For Claude Chat

When updating job materials, use this project to demonstrate:

1. **Technical competency** in modern web development and AI integration
2. **Problem-solving skills** through building practical research tools
3. **DH readiness** for positions emphasizing computational methods
4. **Pedagogical innovation** in educational technology
5. **Research tool development** experience

**Positioning:** This is NOT a side hobby—it's a production research tool demonstrating the technical skills you bring to DH research and teaching.

**When to emphasize:**
- Digital Humanities positions (technical skills + tool building)
- Teaching-focused positions (educational technology)
- Research positions with computational methods component
- Liberal arts colleges emphasizing innovation

**When to de-emphasize:**
- Traditional philosophy positions with no DH component
- Senior positions where tool-building might seem off-brand
- Use judgment based on department priorities

---

## Related Projects

This tool complements your **Prosody-Conditioned BERT** project (in progress):
- Both demonstrate AI/ML integration skills
- Both involve building research tools from scratch
- Together they show range: production web apps + research-grade ML models
- Shared technical foundations: Python, transformers, semantic analysis

**Narrative:** "I build the tools I need for my research—whether that's a web application to manage job applications or a custom BERT model to analyze poetic form."
