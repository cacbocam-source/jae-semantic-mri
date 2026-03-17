Computational Pipeline Architecture
Overview

This study implements a computational pipeline designed to analyze the historical corpus of the Journal of Agricultural Education (1960–2026). The system extracts, cleans, segments, and analyzes manuscript text in order to quantify the evolution of disciplinary knowledge structures over time.

The architecture is divided into two layers:

Corpus Processing Layer (Implemented)

Analytical Modeling Layer (Planned)

This separation ensures methodological transparency and reproducibility while allowing the analytical framework to evolve as the corpus processing pipeline stabilizes.

I. Corpus Processing Layer (Implemented)

The current system performs deterministic document extraction, cleaning, segmentation, and ledger tracking for all manuscripts within the corpus.

Data Ingestion

Raw manuscripts are stored on an external NVMe research volume and organized into two acquisition routes:

Route_A_Modern  (digitally-native PDFs)
Route_B_Legacy  (scanned archival PDFs requiring OCR)

Each document is registered within a corpus ledger (jae_master_ledger.csv) which records:

document identifier

source filename

storage path

extraction route

extraction method

page count

raw text length

cleaned text length

processing timestamp

The ledger ensures deterministic corpus tracking and reproducible processing.

Text Extraction

Extraction is implemented through a dual-route architecture.

Route A — Modern Digital Articles

Digitally-native PDFs are processed using the PyMuPDF (fitz) engine, which directly extracts embedded text.

Route B — Legacy Archival Articles

Older scanned manuscripts are processed using an OCR recovery pipeline consisting of:

PDF page rasterization (pdf2image)

Optical character recognition (Tesseract OCR)

Page-by-page reconstruction of manuscript text

This dual-route strategy ensures compatibility across the full historical corpus.

Text Cleaning

After extraction, manuscripts undergo deterministic cleaning.

Processing includes:

whitespace normalization

removal of extraction artifacts

hard-stop truncation at citation boundaries

The pipeline terminates text extraction at the earliest occurrence of:

References
Literature Cited
Acknowledgements
Funding

This step removes bibliographic noise and ensures that analytical sections contain only manuscript content.

Section Segmentation

Following cleaning, manuscripts are segmented into four conceptual sections used for subsequent analysis:

A_TAK      (Theoretical and Analytical Knowledge)
A_Intro    (Introduction / Background)
A_Methods  (Methodology / Approach)
A_Results  (Findings / Results)

Segmentation is performed using an era-aware logic system implemented within the pipeline.

Legacy Manuscripts (Early Eras)

Because early manuscripts lack consistent section headers, segmentation relies on proximity-based slicing of the normalized text.

Heuristic slicing assigns approximate proportions of manuscript text to analytical sections.

Modern Manuscripts

Contemporary articles are segmented using regex-based header detection, identifying standardized structural headings such as:

Introduction
Methods
Results
Findings
Theoretical Framework

The resulting section text is returned to the pipeline for downstream analysis.

Output Artifacts

The corpus processing layer currently produces:

cleaned manuscript text (.txt)
corpus processing ledger (.csv)

Future pipeline stages will export structured section data for analytical modeling.

II. Analytical Modeling Layer (Planned)

The second layer of the system will perform vector-based semantic analysis and statistical modeling of the extracted manuscript sections.

These components are under development and are described here to document the intended analytical architecture.

Vectorization of Manuscript Sections

Relevant manuscript sections will be transformed into numerical embeddings using a transformer-based embedding model.

The planned model is:

Nomic 8K embedding model

The following sections will be embedded:

A_Intro
A_Results

Each section will be converted into a fixed-length vector representation capturing semantic meaning.

Temporal Epoch Construction

Manuscripts will be grouped into five-year historical epochs:

1960–1964
1965–1969
...
2025–2026

This structure enables longitudinal analysis of disciplinary evolution.

Centroid Computation

For each epoch 
𝐸
E, a centroid vector will be calculated:

C_E = mean(vector representations of all manuscripts within epoch E)

This centroid represents the semantic center of disciplinary discourse during that period.

Semantic Dispersion

Semantic dispersion measures the diversity of research discourse within each epoch.

It is calculated as the average cosine distance between each manuscript vector and the epoch centroid.

σ_sem = mean cosine distance (manuscripts → C_E)

Higher values indicate greater conceptual diversity within the discipline.

Innovation Velocity

Innovation velocity measures the rate of conceptual change between adjacent epochs.

This is computed as the cosine distance between successive epoch centroids.

V_innov = cosine distance (C_E , C_E+1)

Larger values indicate faster shifts in disciplinary knowledge structures.

Statistical Testing

Two statistical procedures will be applied to evaluate temporal changes.

Dispersion Analysis

A Kruskal–Wallis H-test will be used to determine whether semantic dispersion differs significantly across historical eras.

Change-Point Detection

A Pettitt Change-Point Test will be applied to the innovation velocity timeline to identify structural shifts in the rate of disciplinary evolution.

Reproducibility and Audit Controls

The pipeline includes several mechanisms to ensure reproducibility:

deterministic file paths on NVMe research storage

corpus ledger tracking

automated environment diagnostics

compliance verification scripts

pipeline audit logging

These controls ensure that corpus processing and analytical outputs can be reproduced and independently verified.

Development Status
Component	Status
Extraction Pipeline	Implemented
OCR Recovery	Implemented
Cleaning Pipeline	Implemented
Section Segmentation	Implemented
Corpus Ledger	Implemented
Regression Benchmark Tests	In Progress
Vector Embedding	Planned
Semantic Metrics	Planned
Statistical Testing	Planned

pipeline now exports persistent structured section JSON files, not just text.

Segmenter → canonical section fields

A_intro
A_methods
A_results

Example description:

The segmentation stage extracts canonical article sections which
are exported in the structured artifact as:

A_intro – Introduction text  
A_methods – Methods text  
A_results – Results text