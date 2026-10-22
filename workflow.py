import os
import json
import csv
import sys

from gwf import Workflow

from models import Config, SamplePair
from templates.singularity import singularity_pull_template
from templates.bam_stats import bam_stats_template
from templates.mapping import bwa_mem_template
from templates.ascat import ascat_template
from templates.brass import brass_template
from templates.pindel import pindel_template
from templates.caveman import caveman_template

#region Setup
INPUT_FILE = "input.csv"
CONFIG_FILE = "config.json"

# Load config
if not os.path.exists(CONFIG_FILE):
    sys.exit(f"Config file {CONFIG_FILE} not found!")

with open(CONFIG_FILE) as file:
    try:
        config = Config(**json.load(file))
    except Exception as e:
        print(type(e))
        print(str(e))
        sys.exit(1)

# Initialise workflow
gwf = Workflow(".", defaults=vars(config.options["default"]))

os.makedirs(config.out_dir, exist_ok=True)
os.makedirs(config.ref_dir, exist_ok=True)

#endregion

#region Download images

#endregion

#region Download refs
core_ref_files = {
    "genome": os.path.join(config.ref_dir, "genome.fa"),
    "index": os.path.join(config.ref_dir, "genome.fa.fai"),
    "dict": os.path.join(config.ref_dir, "genome.dict"),
}

get_core_refs = gwf.target(
    "get_core_refs",
    inputs={},
    outputs=core_ref_files,
    protect=core_ref_files.values()
) << rf"""
{config.pre_script}
wget -qO- \
    "ftp://ftp.sanger.ac.uk/pub/cancer/dockstore/human/GRCh38_hla_decoy_ebv/core_ref_GRCh38_hla_decoy_ebv.tar.gz" \
    | tar -C "{config.ref_dir}" -xzv --strip-components=1;
    pushd "{config.ref_dir}"
    ln -fs genome.fa.dict genome.dict
    popd
{config.post_script}
"""

index_ref_files = {
    "genome_alt": os.path.join(config.ref_dir, "genome.fa.alt"),
    "genome_bwt": os.path.join(config.ref_dir, "genome.fa.bwt"),
    "genome_2bit": os.path.join(config.ref_dir, "genome.fa.bwt.2bit.64"),
    "genome_0123": os.path.join(config.ref_dir, "genome.fa.0123"),
    "genome_sa": os.path.join(config.ref_dir, "genome.fa.sa"),
    "genome_ann": os.path.join(config.ref_dir, "genome.fa.ann"),
    "genome_amb": os.path.join(config.ref_dir, "genome.fa.amb"),
    "genome_pac": os.path.join(config.ref_dir, "genome.fa.pac")
}

get_index_refs = gwf.target(
    "get_index_refs",
    inputs={},
    outputs=index_ref_files,
    protect=index_ref_files.values()
) << rf"""
{config.pre_script}
wget -qO- \
    "ftp://ftp.sanger.ac.uk/pub/cancer/dockstore/human/GRCh38_hla_decoy_ebv/bwa_idx_GRCh38_hla_decoy_ebv_bwamem2.tar.gz" \
    | tar -C "{config.ref_dir}" -xzv --strip-components=1;
{config.post_script}
"""

genotype_ref_files = {
    "gender": os.path.join(config.ref_dir, "gender.tsv"),
    "general": os.path.join(config.ref_dir, "general.tsv"),
    "snps": os.path.join(config.ref_dir, "verifyBamID_snps.vcf.gz"),
}

get_genotype_refs =  gwf.target(
    "get_genotype_refs",
    inputs={},
    outputs=genotype_ref_files,
    protect=genotype_ref_files.values()
) << rf"""
{config.pre_script}
wget -qO- \
    "ftp://ftp.sanger.ac.uk/pub/cancer/dockstore/human/GRCh38_hla_decoy_ebv/qcGenotype_GRCh38_hla_decoy_ebv.tar.gz" \
    | tar -C "{config.ref_dir}" -xzv --strip-components=1;
{config.post_script}
"""

# CaVEMan and Pindel
caveman_pindel_ref_files = {
    "hi_depth_pindel": os.path.join(config.ref_dir, "pindel/HiDepth.bed.gz"),
    "hi_depth_caveman": os.path.join(config.ref_dir, "caveman/HiDepth.tsv"),
    "genome_gap_tab": os.path.join(config.ref_dir, "caveman/genome.gap.tab"),
    "simple_repeats": os.path.join(config.ref_dir, "pindel/simpleRepeats.bed.gz"),
    "unmatched": os.path.join(config.ref_dir, "pindel/pindel_np.gff3.gz"),
    "filter_rules": os.path.join(config.ref_dir, "pindel/WGS_Rules.lst"),
    "flag_bed_files": os.path.join(config.ref_dir, "caveman/flagging"),
    "unmatched_vcf": os.path.join(config.ref_dir, "caveman"),
    "flag_config": os.path.join( config.ref_dir, "caveman/flag.vcf.config.WGS.ini"),
    "flag_to_vcf_config": os.path.join(config.ref_dir, "caveman/flagging/flag.to.vcf.convert.ini"),
    "soft_rules": os.path.join(config.ref_dir, "pindel/softRules.lst"),
    "ignore_contigs": os.path.join(config.ref_dir, "pindel/ignore_contigs_pindel.txt")
}

get_caveman_pindel_refs = gwf.target(
    "get_caveman_pindel_refs",
    inputs={},
    outputs=caveman_pindel_ref_files,
    protect=caveman_pindel_ref_files.values()
) << rf"""
{config.pre_script}
wget -qO- \
    "ftp://ftp.sanger.ac.uk/pub/cancer/dockstore/human/GRCh38_hla_decoy_ebv/SNV_INDEL_ref_GRCh38_hla_decoy_ebv-fragment.tar.gz" \
    | tar -C "{config.ref_dir}" -xzv --strip-components=1;
{config.post_script}
"""

# VAGrENT
vagrent_ref_files = {
    "genes": os.path.join(config.ref_dir, "vagrent/codingexon_regions.indel.bed.gz"),
    "genome_cache": os.path.join(config.ref_dir, "vagrent/vagrent.cache.gz"),
}

get_vagrent_refs = gwf.target(
    "get_vagrent_refs",
    inputs={},
    outputs=vagrent_ref_files,
    protect=vagrent_ref_files.values()
) << rf"""
{config.pre_script}
wget -qO- \
    "ftp://ftp.sanger.ac.uk/pub/cancer/dockstore/human/GRCh38_hla_decoy_ebv/VAGrENT_ref_GRCh38_hla_decoy_ebv_ensembl_91.tar.gz" \
    | tar -C "{config.ref_dir}" -xzv --strip-components=1;
{config.post_script}
"""
#endregion

#region Download singularity images
os.makedirs(config.image_dir, exist_ok=True)

image_targets = {}

for image_name in config.images:
    image = config.images[image_name]

    image_targets[image_name] = gwf.target_from_template(
        name=f"get_{image_name}_image",
        template=singularity_pull_template(
            name=image_name,
            image=image,
            config=config
        )
    )
#endregion

#region Workflows
def _get_sample_info(path: str) -> tuple[str, str]:
    """Given a bam/cram path, return file name and index path"""

    prefix, suffix = os.path.splitext(os.path.basename(path))

    if suffix == ".bam":
        index_path = path + ".bai"
    elif suffix == ".cram":
        index_path = path + ".crai"
    else:
        raise ValueError(f"[Error] Unsupported file type '{suffix}' for path '{path}'")

    if not os.path.exists(index_path):
        raise ValueError(f"[Error] Missing index file for path '{path}'")

    return prefix, index_path

# Dictionaries to hold targets that should be done once per sample 
# (allowing samples e.g. normals to be re-used in a samplesheet)
mapping_targets = {}
bam_stats_targets = {}

with open(INPUT_FILE, "r") as file:
    for row in csv.reader(file):
        row = [field.strip() for field in row]

        if row[0].startswith("#"):
            continue

        tumour_name = row[0]
        tumour_files = row[1].split(";")
        normal_name = row[2]
        normal_files = row[3].split(";")

        sample_pair = SamplePair(tumour_name, normal_name)

        #region Process BAM - mapping or bam stats
        if not config.mapping:
            # Not remapping - check we have a single pair of BAM files per input row
            if len(tumour_files) > 1 or len(normal_files) > 1:
                raise ValueError(f"[Error] mapping: false configuration requires 1 BAM/CRAM file per sample")

            tumour_path = tumour_files[0]
            normal_path = normal_files[0]

            tumour_file_name, tumour_index_path = _get_sample_info(tumour_path)
            normal_file_name, normal_index_path = _get_sample_info(normal_path)
    
            # Run bam_stats
            bam_stats_inputs = {
                "image": image_targets["pcap-core"].outputs["image"],
                "reference_index": get_core_refs.outputs["index"],
            }

            for sample_name, sample_path in [(tumour_name, tumour_path), (normal_name, normal_path)]:
                if sample_name not in bam_stats_targets:
                    bam_stats_targets[sample_name] = gwf.target_from_template(
                        name=f"{sample_name}_bam_stats",
                        template=bam_stats_template(
                            inputs={
                                **bam_stats_inputs,
                                "bam_path": sample_path
                            },
                            config=config
                        )
                    )
            
            sample_pair_inputs = {
                "tumour_path": tumour_path,
                "tumour_index_path": tumour_index_path,
                "tumour_bas_path": bam_stats_targets[tumour_name].outputs["bas"],
                "normal_path": normal_path,
                "normal_index_path": normal_index_path,
                "normal_bas_path": bam_stats_targets[normal_name].outputs["bas"],
            }
        else:
            # Remapping
            map_inputs = {
                "genome":       get_core_refs.outputs["genome"],
                "index":        get_core_refs.outputs["index"],
                "dict":         get_core_refs.outputs["dict"],
                "genome_alt":   get_index_refs.outputs["genome_alt"],
                "genome_bwt":   get_index_refs.outputs["genome_bwt"],
                "genome_2bit":  get_index_refs.outputs["genome_2bit"],
                "genome_0123":  get_index_refs.outputs["genome_0123"],
                "genome_sa":    get_index_refs.outputs["genome_sa"],
                "genome_ann":   get_index_refs.outputs["genome_ann"],
                "genome_amb":   get_index_refs.outputs["genome_amb"],
                "genome_pac":   get_index_refs.outputs["genome_pac"],
                "image":        image_targets["pcap-core"].outputs["image"],
            }
            
            for sample_name, sample_inputs in [(tumour_name, tumour_files), (normal_name, normal_files)]:
                if not sample_name in mapping_targets:
                    mapping_targets[sample_name] = gwf.target_from_template(
                        name=f"{sample_name}_map",
                        template=bwa_mem_template(
                            inputs=map_inputs,
                            sample_name=sample_name,
                            sample_inputs=sample_inputs,
                            config=config
                        )
                    )

            sample_pair = SamplePair(tumour_name, normal_name)
            
            sample_pair_inputs = {
                "tumour_path":          mapping_targets[tumour_name].outputs["cram"],
                "tumour_index_path":    mapping_targets[tumour_name].outputs["crai"],
                "tumour_bas_path":      mapping_targets[tumour_name].outputs["bas"],
                "normal_path":          mapping_targets[normal_name].outputs["cram"],
                "normal_index_path":    mapping_targets[normal_name].outputs["crai"],
                "normal_bas_path":      mapping_targets[normal_name].outputs["bas"]
            }

        sample_pair_out_dir = os.path.join(config.out_dir, sample_pair.name)
        #endregion

        # ASCAT
        ascat_inputs = {
            **sample_pair_inputs,
            "reference_genome": get_core_refs.outputs["genome"],
            "snp_gc": get_ascat_brass_refs.outputs["snp_gc"],
            "locus": get_genotype_refs.outputs["gender"],
            "image": image_targets["ascat"].outputs["image"]
        }

        ascat = gwf.target_from_template(
            name=f"{sample_pair.name}_ascat", template=ascat_template(
                inputs=ascat_inputs,
                sample_pair=sample_pair,
                config=config
            )
        )

        # BRASS
        brass_inputs = {
            **sample_pair_inputs,
            "reference_genome": get_core_refs.outputs["genome"],
            "hi_depth": get_caveman_pindel_refs.outputs["hi_depth_pindel"],
            "brass_filter": get_ascat_brass_refs.outputs["brass_filter"],
            "genome_cache": get_vagrent_refs.outputs["genome_cache"],
            "virus_sequences": get_ascat_brass_refs.outputs["virus_sequences"],
            "microbe_sequences": get_ascat_brass_refs.outputs["microbe_sequences"],
            "gc_bin": get_ascat_brass_refs.outputs["gc_bin"],
            "cent_telo": get_ascat_brass_refs.outputs["cent_telo"],
            "cytoband": get_ascat_brass_refs.outputs["cytoband"],
            "sample_stats": ascat.outputs["sample_stats"], 
            "image": image_targets["brass"].outputs["image"]
        }

        brass_input = gwf.target_from_template(
            name=f"{sample_pair.name}_brass_input",
            template=brass_template(
                inputs=brass_inputs,
                sample_pair=sample_pair,
                config=config,
                process="input"
            )
        )

        brass_cover = gwf.target_from_template(
            name=f"{sample_pair.name}_brass_cover",
            template=brass_template(
                inputs={
                    **brass_inputs,
                    "ready": brass_input.outputs["done"]
                },
                sample_pair=sample_pair,
                config=config,
                process="cover"
            ),
        )

        brass = gwf.target_from_template(
            name=f"{sample_pair.name}_brass",
            template=brass_template(
                inputs={
                    **brass_inputs,
                    "ready": brass_cover.outputs["done"]
                },
                sample_pair=sample_pair,
                config=config
            )
        )

        # PINDEL
        pindel_inputs = {
            **sample_pair_inputs,
            "reference_genome": get_core_refs.outputs["genome"],
            "simple_repeats": get_caveman_pindel_refs.outputs["simple_repeats"],
            "unmatched": get_caveman_pindel_refs.outputs["unmatched"],
            "filter_rules": get_caveman_pindel_refs.outputs["filter_rules"],
            "genes": get_vagrent_refs.outputs["genes"],
            "hi_depth": get_caveman_pindel_refs.outputs["hi_depth_pindel"],
            "soft_rules": get_caveman_pindel_refs.outputs["soft_rules"],
            "ignore_contigs": get_caveman_pindel_refs.outputs["ignore_contigs"],
            "image": image_targets["pindel"].outputs["image"],
        }

        pindel = gwf.target_from_template(
            name=f"{sample_pair.name}_pindel",
            template=pindel_template(
                inputs = pindel_inputs,
                sample_pair=sample_pair,
                config=config
            )
        )

        # ANNOTATE PINDEL
        annotate_pindel_inputs = {
            "vcf": pindel.outputs["vcf"],
            "vagrent_cache": get_vagrent_refs.outputs["genome_cache"],
            "image": image_targets["vagrent"].outputs["image"],
        }

        annotate_pindel = gwf.target_from_template(
            name=f"{sample_pair.name}_annotate_pindel",
            template=vagrent_template(
                inputs=annotate_pindel_inputs,
                sample_pair=sample_pair,
                config=config
            ),
        )

        # CAVEMAN
        caveman_inputs = {
            **sample_pair_inputs,
            "tumor_copynumber": ascat.outputs["tumor_copynumber"],
            "normal_copynumber": ascat.outputs["normal_copynumber"],
            "sample_stats": ascat.outputs["sample_stats"],
            "germline_indels": pindel.outputs["germline_bed"],
            "reference_index": get_core_refs.outputs["index"],
            "hi_depth": get_caveman_pindel_refs.outputs["hi_depth_caveman"],
            "genome_gap_tab": get_caveman_pindel_refs.outputs["genome_gap_tab"],
            "flag_bed_files": get_caveman_pindel_refs.outputs["flag_bed_files"],
            "unmatched_vcf": get_caveman_pindel_refs.outputs["unmatched_vcf"],
            "flag_config": get_caveman_pindel_refs.outputs["flag_config"],
            "flag_to_vcf_config": get_caveman_pindel_refs.outputs["flag_to_vcf_config"],
            "image": image_targets["caveman"].outputs["image"],
        }

        # setup
        caveman_setup = gwf.target_from_template(
            name=f"{sample_pair.name}_caveman_setup", 
            template=caveman_template(
                inputs=caveman_inputs,
                sample_pair=sample_pair,
                config=config,
                process="setup"
            )
        )

        # split [1-24] (canonical chromosomes only)
        caveman_split_jobs = 24
        caveman_split_array = [
            gwf.target_from_template(
                name=f"{sample_pair.name}_caveman_split_{i}", 
                template=caveman_template(
                    inputs={
                        **caveman_inputs,
                        "ready": caveman_setup.outputs["done"]
                    },
                    sample_pair=sample_pair,
                    config=config,
                    process="split",
                    index=i,
                    limit=caveman_split_jobs 
                )
            )
            for i in range(1, caveman_split_jobs+1)
        ]

        # split_concat
        caveman_split_concat = gwf.target_from_template(
            name=f"{sample_pair.name}_caveman_split_concat", 
            template=caveman_template(
                inputs={
                    **caveman_inputs,
                    **{f"ready_{i}": caveman_split_target.outputs["done"] for i, caveman_split_target in enumerate(caveman_split_array, 1)}
                },
                sample_pair=sample_pair,
                config=config,
                process="split_concat"
            )
        )

        # mstep [1-N]
        caveman_mstep_array = [
            gwf.target_from_template(
                name=f"{sample_pair.name}_caveman_mstep_{i}", 
                template=caveman_template(
                    inputs={
                        **caveman_inputs,
                        "ready": caveman_split_concat.outputs["done"]
                    },
                    sample_pair=sample_pair,
                    config=config,
                    process="mstep",
                    index=i,
                    limit=config.caveman_step_jobs 
                )
            )
            for i in range(1, config.caveman_step_jobs+1)
        ]

        # merge
        caveman_merge = gwf.target_from_template(
            name=f"{sample_pair.name}_caveman_merge", 
            template=caveman_template(
                inputs={
                    **caveman_inputs,
                    **{f"ready_{i}": caveman_mstep_target.outputs["done"] for i, caveman_mstep_target in enumerate(caveman_mstep_array, 1)}
                },
                sample_pair=sample_pair,
                config=config,
                process="merge"
            )
        )

        # estep [1-N]
        caveman_estep_array = [
            gwf.target_from_template(
                name=f"{sample_pair.name}_caveman_estep_{i}", 
                template=caveman_template(
                    inputs={
                        **caveman_inputs,
                        "ready": caveman_merge.outputs["done"]
                    },
                    sample_pair=sample_pair,
                    config=config,
                    process="estep",
                    index=i,
                    limit=config.caveman_step_jobs 
                )
            )
            for i in range(1, config.caveman_step_jobs+1)
        ]

        # merge
        caveman_merge_results= gwf.target_from_template(
            name=f"{sample_pair.name}_caveman_merge_results", 
            template=caveman_template(
                inputs={
                    **caveman_inputs,
                    **{f"ready_{i}": caveman_estep_target.outputs["done"] for i, caveman_estep_target in enumerate(caveman_estep_array, 1)}
                },
                sample_pair=sample_pair,
                config=config,
                process="merge_results"
            )
        )

        # add_ids
        caveman_add_ids= gwf.target_from_template(
            name=f"{sample_pair.name}_caveman_add_ids", 
            template=caveman_template(
                inputs={
                    **caveman_inputs,
                    "ready": caveman_merge_results.outputs["done"]
                },
                sample_pair=sample_pair,
                config=config,
                process="add_ids"
            )
        )

        # flag
        caveman_flag = gwf.target_from_template(
            name=f"{sample_pair.name}_caveman_flag", 
            template=caveman_template(
                inputs={
                    **caveman_inputs,
                    "ready": caveman_add_ids.outputs["done"]
                },
                sample_pair=sample_pair,
                config=config,
                process="flag"
            )
        )
        
        # ANNOTATE CAVEMAN
        annotate_caveman_inputs = {
            "vcf": caveman_flag.outputs["vcf"],
            "vagrent_cache": get_vagrent_refs.outputs["genome_cache"],
            "image": image_targets["vagrent"].outputs["image"],
        }

        annotate_caveman = gwf.target_from_template(
            name=f"{sample_pair.name}_annotate_caveman",
            template=vagrent_template(
                inputs=annotate_caveman_inputs,
                sample_pair=sample_pair,
                config=config
            ),
        )
#endregion
