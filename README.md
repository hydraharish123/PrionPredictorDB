
# PrionPredictorDB
![Stars](https://img.shields.io/github/stars/hydraharish123/PrionPredictorDB?style=social)
![Forks](https://img.shields.io/github/forks/hydraharish123/PrionPredictorDB?style=social)
![Issues](https://img.shields.io/github/issues/hydraharish123/PrionPredictorDB)
![License](https://img.shields.io/github/license/hydraharish123/PrionPredictorDB)

**PrionPredictorDB** is a scalable and organism-independent pipeline and database for the prediction of prion-like, aggregation-prone proteins using both **sequence** and **structure-based** methods. This project integrates tools like **PLAAC**, **AlphaFold**, **Aggrescan3D**, and **DBSCAN** to identify and cluster potentially pathogenic prion-like domains (PRDs) across any organism's proteome.

---

## Highlights

- Analyzed the complete **human proteome (~20,000 proteins)** using PLAAC to identify **195 PRD-containing proteins**.
- Retrieved **AlphaFold structures** for 188 proteins and computed:
  - **Solvent Accessible Surface Area (SASA)**
  - **Average pLDDT** scores
- Identified aggregation-prone PRDs using:
  - **Aggrescan3D** to score individual residues
  - **DBSCAN** to cluster aggregation-prone residues in 3D
- Developed a **command-line tool** to run the entire pipeline on any FASTA proteome.
- 🖥Built a full-stack **web application** with a ReactJS frontend, NGLViewer for structure rendering, and MongoDB backend.

---

## Workflow Overview

### 1. **PRD Detection (PLAAC)**
- Input: Human proteome FASTA (UniProt)
- Output: 195 proteins with valid prion-like domains (PRDs)

### 2. **Structure Retrieval and Filtering**
- Tool: [AlphaFold Protein Structure Database](https://alphafold.ebi.ac.uk/)
- Filters:
  - **SASA > 1000 Å²**
  - **Average pLDDT < 50**
- Result: 188 proteins passed structure availability and thresholding

Absolutely — here's an updated version of the **DBSCAN-related section** in the README, now including the **biological rationale** for why 3D clustering of aggregation-prone residues matters:


### 3. Aggregation Propensity and 3D Clustering

To identify realistic aggregation hotspots within prion-like domains (PRDs), we implemented a **structure-aware aggregation pipeline**:

#### Steps:

* **Tool:** [Aggrescan3D](http://biocomp.chem.uw.edu.pl/A3D/) computes per-residue aggregation propensity scores using AlphaFold structures.
* For each protein:

  * **Select residues within the PRD** that have **Aggrescan3D score > 0.5**
  * Apply **DBSCAN (Density-Based Spatial Clustering)** to identify **3D clusters** of spatially close, aggregation-prone residues.

#### Biological Rationale for 3D Clustering:

Aggregation is a **structural phenomenon**, not just a sequence-level one. Simply having aggregation-prone residues is not enough — they must be **spatially close in the folded protein** to nucleate aggregation. Here's why clustering is important:

* **Spatial Proximity Matters:**
  Aggregation typically starts at **hotspots** where multiple aggregation-prone residues come **together in 3D**, forming a nucleation seed. These hotspots are more predictive of **actual aggregation** than isolated high-scoring residues.

* **Filters Out False Positives:**
  Some residues may score high individually but be buried inside the protein or far apart. 3D clustering ensures only **physically plausible aggregation regions** are considered.

* **Mimics Real Prion Nucleation:**
  Structural studies of prions (e.g., Tau, α-synuclein) show that **small structured cores** initiate fibril formation. DBSCAN helps emulate this by identifying **compact residue clusters** within PRDs.

* **Therapeutic Relevance:**
  3D clusters can be **targeted** by small molecules or antibodies. Identifying these clusters helps in **rational drug design** aimed at blocking aggregation.

> 📌 In summary: DBSCAN-based 3D clustering enables a **more biologically accurate**, **structurally informed**, and **therapeutically useful** prediction of aggregation hotspots.



### 4. **Annotation & Storage**
- Data stored in MongoDB in the following structure:

```json
{
  "uniprot_id": "Q6P3W7",
  "Protein Name": "SCY1-like protein 2",
  "Organism": "Homo sapiens",
  "Length": 929,
  "Sequence": "MESMLN...",
  "PRDstart": 852,
  "PRDend": 922,
  "PRDlen": 71,
  "PRDaa": "SMNQLSQQKPNQWLN...",
  "AlphaFold Model": "AF-Q6P3W7-F1-model_v4.pdb",
  "SASA": 622.85,
  "Average_pLDDT": 31.81,
  "Aggregating-like": "No",
  "Aggrescan3D Clusters": [
    {"residues": [860, 861, 862], "cluster_id": 1, "score_avg": 0.67},
    ...
  ]
}
````

---

## 💻 Tech Stack

| Component       | Technology                 |
| --------------- | -------------------------- |
| **Backend**     | Node.js + Express          |
| **Database**    | MongoDB                    |
| **Frontend**    | ReactJS, NGLViewer, Plotly |
| **CLI Tool**    | Python                     |
| **Aggregation** | Aggrescan3D, DBSCAN        |
| **Structure**   | AlphaFold + Biopython      |
| **PRD Finder**  | PLAAC                      |

---

## Command Line Tool

A CLI-based standalone pipeline to process **any organism's proteome**.

### Install Requirements

```bash
cd pipeline/
pip install -r requirements.txt
```

### Usage

```bash
python cli.py <sample_fasta> <reference_fasta> -o <output_dir>
```

**Arguments:**

* `sample_fasta`: Proteome FASTA file (multi-sequence)
* `reference_fasta`: Same as sample or a genome reference (for codon bias, if needed)
* `-o, --output`: Output directory to store:

  * Filtered PRD list
  * AlphaFold models
  * Aggregation plots
  * PyMOL visualization scripts

---

## Web Dashboard

### Features:

* Search and browse predicted prion-like proteins
* View AlphaFold structures in 3D using **NGLViewer**
* Interactive aggregation cluster plots with **Plotly.js**
* Export sequences and visualizations

### Screenshots



---

## Biological Relevance

* **Prion-like domains (PLDs)** are disordered regions enriched in Q/N residues and implicated in **neurodegenerative diseases** like ALS and Alzheimer’s.
* Aggregation-prone PLDs are often overlooked due to structural disorder. Combining **PLAAC**, **structure-based filtering**, and **residue clustering** helps refine high-confidence candidates.
* Your dataset and framework can aid in **target discovery** for drug design or genetic studies.

---

## Folder Structure

```
PrionPredictorDB/
├── server/              # Node.js API
├── client/             # React frontend
├── scripts/             # Python scripts (PLAAC, A3D, DBSCAN, AlphaFold parsers)
├── data/               
├── pipeline/                # Command line interface
└── README.md
```

---

## References

* **PLAAC**: Lancaster et al., 2014 – [DOI:10.1016/j.cell.2014.07.046](https://doi.org/10.1016/j.cell.2014.07.046)
* **AlphaFold**: Jumper et al., 2021 – Nature
* **Aggrescan3D**: Kuriata et al., 2019 – [DOI:10.1093/bioinformatics/btz810](https://doi.org/10.1093/bioinformatics/btz810)
* **DBSCAN**: Ester et al., 1996 – KDD


