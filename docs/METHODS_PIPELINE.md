# Computational Methods Pipeline

## Semantic MRI of Agricultural Education

---

# 1. Computational Environment

All analyses were conducted on an Apple Silicon workstation equipped with an M3 Max processor and 64GB of unified memory.

The computational environment utilized Python and GPU-accelerated embedding computation through Apple's Metal Performance Shaders (MPS).

Primary data storage was provided through an external NVMe solid-state drive.

---

# 2. Corpus Processing Architecture

A modular Python pipeline was constructed to support ingestion, semantic embedding, and longitudinal vector-space analysis of research articles.

The pipeline was organized into three operational phases:

1. Corpus ingestion
2. Text vectorization
3. Vector-space analysis

Each phase was executed through a centralized command interface.

---

# 3. Corpus Ingestion

The ingestion phase collects and inventories research documents within the corpus.

Raw materials are stored within a structured data lake architecture separating modern and legacy sources.

All ingestion procedures generate manifest files documenting document identity, metadata, and processing status.

---

# 4. Semantic Embedding

Document embeddings were generated using the transformer model:

```
nomic-ai/nomic-embed-text-v1.5
```

The model supports extended context windows of up to 8192 tokens, allowing full-article semantic representation without aggressive text segmentation.

Embedding computations were executed using GPU acceleration through Metal Performance Shaders.

Parallel worker execution was limited to eight concurrent processes to maintain stable unified memory usage.

---

# 5. Vector-Space Analysis

Embedded document vectors were used to compute semantic centroids, drift trajectories, and methodological friction across historical time periods.

Temporal segmentation was implemented using five-year epochs spanning 1960–2026.

This approach allows the longitudinal evolution of research paradigms to be modeled as trajectories within a high-dimensional embedding space.

---

# 6. Reproducibility Measures

The computational pipeline incorporates several safeguards to ensure reproducibility.

These include:

* deterministic filesystem architecture
* automated infrastructure validation
* centralized configuration management
* explicit hardware configuration parameters

All pipeline operations are executed through a single orchestrator to prevent inconsistent module execution.

---

# 7. Infrastructure Documentation

A complete infrastructure audit documenting system construction and validation procedures is provided in the supplementary materials.

This audit includes:

* system architecture
* filesystem layout
* build procedures
* validation tests

---

# Status

Methods Draft Version: 1.0
