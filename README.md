# cluster-links

## A Web-Link Clustering Pipeline

This project is a robust, configurable pipeline for extracting, cleaning, embedding, and clustering web links based on their topical content. It aims to help you automatically organize large collections of URLs (such as bookmarks or research links) into semantically meaningful groups.

```mermaid
flowchart TD
    A[Input List of Weblinks] --> B[Extract Textual Semantic Representation]
    B --> C[Compute Embedding per Weblink]
    C --> D[Cluster Weblinks]
```

### Flow

#### High-Level Architecture Diagram
```mermaid
graph TB
    User[User] --> UI[User Interface]
    UI --> API[API Layer]
    API --> OE[Organization Engines]
    API --> CE[Content Extraction]
    API --> DC[Data Collection]
    API --> ES[Evaluation System]
    API --> SL[Storage Layer]
    
    OE --> SL
    CE --> SL
    DC --> SL
    ES --> SL
    
    subgraph "Organization Engines"
        NLP[NLP-Based]
        LLM[LLM-Based]
        Graph[Graph-Based]
        Multi[Multi-Modal]
        RL[Reinforcement Learning]
    end
```

#### Detailed Subsystem Architecture

##### Data Collection Subsystem
```mermaid
graph TD
    LP[Link Provider] --> |URLs| PC[Processing Controller]
    PC --> |URLs| FE[Fetch Engine]
    FE --> |Raw Content| PC
    PC --> |Processed Content| DM[Data Manager]
    
    subgraph "Link Providers"
        TF[Text File]
        BM[Browser Bookmarks]
        HS[History Import]
        Manual[Manual Entry]
    end
    
    subgraph "Fetch Engines"
        HTTP[HTTP Fetcher]
        Sel[Selenium Renderer]
        PDF[PDF Processor]
        YT[YouTube Extractor]
    end
    
    TF --> LP
    BM --> LP
    HS --> LP
    Manual --> LP
    
    HTTP --> FE
    Sel --> FE
    PDF --> FE
    YT --> FE
    
    DM --> |Store| SL[Storage Layer]
```

##### Content Extraction Subsystem
```mermaid
graph TD
    CM[Content Manager] --> TEP[Text Extraction Pipeline]
    CM --> MEP[Metadata Extraction Pipeline]
    CM --> VEP[Visual Extraction Pipeline]
    
    TEP --> |Text Content| SL[Storage Layer]
    MEP --> |Metadata| SL
    VEP --> |Visual Features| SL
    
    subgraph "Text Extraction"
        HTML[HTML Extractor]
        PDF[PDF Extractor]
        YT[Transcript Extractor]
    end
    
    subgraph "Metadata Extraction"
        Title[Title Extractor]
        Date[Date Extractor]
        Author[Author Extractor]
        LLM[LLM Metadata]
    end
    
    subgraph "Visual Extraction"
        SS[Screenshot]
        CV[Computer Vision]
        Layout[Layout Analysis]
    end
    
    HTML --> TEP
    PDF --> TEP
    YT --> TEP
    
    Title --> MEP
    Date --> MEP
    Author --> MEP
    LLM --> MEP
    
    SS --> VEP
    CV --> VEP
    Layout --> VEP
```

##### Organization Engines Subsystem
```mermaid
graph TD
    OC[Organization Controller] --> NLP[NLP Engine]
    OC --> LLM[LLM Engine]
    OC --> GB[Graph-Based Engine]
    OC --> MM[Multi-Modal Engine]
    OC --> RL[Reinforcement Learning Engine]
    
    NLP --> |Organization| SL[Storage Layer]
    LLM --> |Organization| SL
    GB --> |Organization| SL
    MM --> |Organization| SL
    RL --> |Organization| SL
    
    subgraph "NLP Engine"
        Embedding[Embedding Generator]
        Clustering[Clustering]
        TopicModel[Topic Modeling]
    end
    
    subgraph "LLM Engine"
        ZeroShot[Zero-Shot Classification]
        Taxonomy[Taxonomy Generation]
        Relationship[Relationship Extraction]
    end
    
    subgraph "Graph Engine"
        LinkAnalysis[Link Analysis]
        Community[Community Detection]
        Centrality[Centrality Measures]
    end
    
    Embedding --> NLP
    Clustering --> NLP
    TopicModel --> NLP
    
    ZeroShot --> LLM
    Taxonomy --> LLM
    Relationship --> LLM
    
    LinkAnalysis --> GB
    Community --> GB
    Centrality --> GB
```

##### Storage
```mermaid
graph TD
    SL[Storage Layer] --> RM[Repository Manager]
    RM --> CR[Content Repository]
    RM --> OR[Organization Repository]
    RM --> MR[Metadata Repository]
    
    subgraph "Storage Backends"
        SQLite[SQLite]
        JSON[JSON Files]
        Vector[Vector Database]
    end
    
    SQLite --> CR
    SQLite --> OR
    SQLite --> MR
    
    JSON --> CR
    JSON --> OR
    JSON --> MR
    
    Vector --> CR
```

##### API
```mermaid
graph LR
    Client[Client] --> |REST/GraphQL| API[API Gateway]
    API --> |Requests| RC[Request Controller]
    RC --> DC[Data Collection API]
    RC --> CE[Content Extraction API]
    RC --> OE[Organization API]
    RC --> EA[Evaluation API]
    
    subgraph "API Endpoints"
        Ingest[/ingest/]
        Extract[/extract/]
        Organize[/organize/]
        Compare[/compare/]
        Export[/export/]
    end
    
    Ingest --> DC
    Extract --> CE
    Organize --> OE
    Compare --> EA
    Export --> RC
```

#### Component Interfaces
```mermaid
classDiagram
    class OrganizationEngine {
        <<interface>>
        +organize(content_items[]) Organization
        +getName() string
        +getDescription() string
        +getParameters() Dict
        +setParameters(params) void
    }
    
    class ContentExtractor {
        <<interface>>
        +extract(url) ContentItem
        +extractBatch(urls[]) ContentItem[]
        +getSupportedTypes() string[]
    }
    
    class Organization {
        +id string
        +name string
        +engine string
        +parameters Dict
        +hierarchy Dict
        +getRootCategories() Category[]
        +findItemById(id) ContentItem
        +export(format) string
    }
    
    class ContentItem {
        +id string
        +url string
        +title string
        +content string
        +metadata Dict
        +embeddings Dict
        +visualFeatures Dict
        +getTextContent() string
        +getSummary() string
    }
    
    OrganizationEngine ..> Organization
    ContentExtractor ..> ContentItem
    Organization o-- ContentItem
```

## Key Features

- **Configurable Input:**  
  Reads URLs from a specified file (via `config.json`) and supports domain-based rate limiting and ignore lists (e.g., skip YouTube or problematic PDFs).

- **Robust Content Extraction:**  
  Uses [trafilatura](https://github.com/adbar/trafilatura) to extract the main content from HTML pages (with fallback to BeautifulSoup) and [pdfminer.six](https://github.com/pdfminer/pdfminer.six) to extract text from PDFs (limited to the first 10 pages).  
  Advanced cleaning routines remove common boilerplate and extraneous text.

- **Parallel Processing & Logging:**  
  Extracts text from URLs in parallel using Python’s ThreadPoolExecutor with progress indication. Detailed logs are maintained in separate log files for general extraction, failures, and summary statistics.

- **Embedding & Clustering:**  
  Computes text embeddings with [SentenceTransformers](https://www.sbert.net/) and clusters the links using HDBSCAN and hierarchical clustering methods.

- **Semantic Keyword Extraction:**  
  Generates cluster reports using [KeyBERT](https://github.com/MaartenGr/KeyBERT) to extract meaningful keywords that summarize each cluster’s content.

## How It Works

1. **Read and Clean URLs:**  
   URLs are read from a links file (specified in `config.json`), cleaned, and filtered using `get_links.py`.

2. **Parallel Extraction:**  
   The pipeline fetches each URL, extracts the main content using advanced extraction (with trafilatura and cleaning functions), and logs successes and failures.

3. **Compute Embeddings:**  
   Extracted texts are converted into semantic embeddings using SentenceTransformers.

4. **Clustering & Reporting:**  
   Embeddings are clustered using HDBSCAN (and optionally hierarchical clustering), and a detailed cluster report (with semantic keywords) is generated.

## Getting Started

### Prerequisites

Make sure you have Python 3.8+ installed. Then install dependencies:

```bash
pip install -r requirements.txt
```

### Running the Pipeline


#### Configure the Project

Edit config.json to set your links file (a text file listing weblinks), rate limiting domains, and ignore domains.

#### Run the Project

```bash
python main.py
```

#### View Outputs

**Cluster Report**: See `cluster_report.txt` for grouped links and extracted keywords.

**Logs**: Review `extraction.log`, `extraction_failures.log`, and `extraction_stats.log` for detailed processing information.
