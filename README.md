# sanger-wgs-gwf

[GWF](https://github.com/gwforg/gwf) workflows orchestrating the standard Sanger / [CGP](https://github.com/cancerit) WGS mapping and analysis tools.

Requires [singularity](https://sylabs.io/singularity) >= 3.11.0.

## Quickstart

### Installation
GWF and other Python dependencies can be installed with:
```sh
python3 -m venv .venv
. .venv/bin/activate
pip install -r requirements.txt
```

### Setup
Create an `input.csv` and `config.json`, which drive the pipeline
```sh
cp input.csv.template input.csv 
# Edit input.csv to point to input files 
cp config.json.lsf.template config.json
# Edit config.json to contain valid configuration
```

### Running
```sh
gwf status
# Confirm expected targets are generated before launching jobs:
gwf run
```

## Overview

This pipeline will run the standard CGP processing tools.

```mermaid
flowchart TB

subgraph download [Download]
    direction TB
    get_core_refs
    get_index_refs
    get_genotype_refs
    get_caveman_pindel_refs 
    get_ascat_brass_refs 
    get_vagrent_refs
    get_N_image 
end

subgraph mapping [Mapping]
    direction TB
    tumour_bam_stats
    normal_bam_stats
    tumour_map
    normal_map
end


subgraph analysis [Analysis]
    direction TB
    sample_pair_ascat --> sample_pair_caveman
    sample_pair_pindel --> sample_pair_caveman
    sample_pair_caveman
    sample_pair_ascat --> sample_pair_brass
end

download --> mapping
mapping --> analysis

class tumour_bam_stats,normal_bam_stats,tumour_map,normal_map,mapping opt
class get_core_refs,get_index_refs,get_genotype_refs,get_caveman_pindel_refs,get_vagrent_refs,get_N_image,sample_pair_ascat,sample_pair_caveman,sample_pair_pindel,sample_pair_brass node
classDef opt stroke-dasharray: 5 5
classDef node fill:#fff,stroke:#333
```

### Mapping

If `"mapping": true` is enabled in `config.json`, samples will be mapped using `bwa_mem.pl`.

Otherwise, if .bas files are not already present, `bam_stats` from pcap-core will run.

### Analysis

| Tool | Analysis type |
| - | - |
| ASCAT | CNVs |
| CaVEMan | SNVs |
| Pindel | Indels |
| BRASS | SVs |

# Acknowledgements

This repository is built directly on the GWF workflows used in the [PanProstate hg38 workflows](https://github.com/panprostate/panprostate_workflows) (currently a private repo), with significant contributions from Philippe Lamy and Gregory Leeman.
