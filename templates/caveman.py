import os
import textwrap

from gwf import AnonymousTarget

from models import Config, SamplePair


def caveman_template(
        inputs: dict,
        sample_pair: SamplePair,
        config: Config,
        process: str,
        index: int | None = None,
        limit: int | None = None
    ) -> AnonymousTarget:
    out_dir = os.path.join(config.out_dir, sample_pair.name, "caveman")

    # OUTPUTS and additional args (index-specific)
    outputs = {}
    add_args = f"-process {process}"
    if index is not None:
        outputs["done"] = os.path.join(out_dir, f"caveman_{process}_{index}.done")
        add_args += f" -index {index} -limit {limit}"
    else:
        outputs["done"] = os.path.join(out_dir, f"caveman_{process}.done")

    if process != "flag":
        # Only clean during flagging (final step) 
        add_args += " --no-flagging --noclean"
    else:
        # Add vcf output to flagging step
        outputs["vcf"] = os.path.join(
            out_dir, f"{sample_pair.tumour}_vs_{sample_pair.normal}.flagged.muts.vcf.gz"
        )

    # OPTIONS and additional steps (process-specifc)
    add_steps = ""
    match process:
        case "setup" | "split" | "split_concat":
            options = vars(config.options["caveman_small"])
        case "mstep" | "estep":
            options = vars(config.options["caveman_step"])
        case "merge" | "merge_results" | "add_ids": 
            options = vars(config.options["caveman_medium"])
        case "flag":
            options = vars(config.options["caveman_flag"])
            # Print versions after flagging (final step)
            add_steps += f"caveman.pl --version > {out_dir}/caveman.version.txt"
        case _:
            # Error if not a recognised process
            raise ValueError(f"Invalid process {process} for CaVEMan")

    # SPEC
    tumor_bam = inputs["tumor_path"]
    normal_bam = inputs["normal_path"]
    
    normal_copynumber = inputs["normal_copynumber"]
    tumor_copynumber = inputs["tumor_copynumber"]
    sample_stats = inputs["sample_stats"]

    germline_indels = inputs["germline_indels"]
    unmatched_vcf = inputs["unmatched_vcf"]
    reference_index = inputs["reference_index"]
    flag_bed_files = inputs["flag_bed_files"]
    flag_config = inputs["flag_config"]
    flag_to_vcf_config = inputs["flag_to_vcf_config"]
    genome_gap = inputs["genome_gap_tab"]

    tumor_copynumber_def = 5
    normal_copynumber_def = 2
    assembly = "NCBI38"
    protocol = "WGS"
    read_count = 500000
    seq_type = "genome"
    species = "Human"

    image = inputs["image"]
    cores = options["cores"]
    singularity_flags = config.singularity_flags

    done = outputs["done"]

    spec = textwrap.dedent(
        rf"""
    {config.pre_script}
    set -euo pipefail
    mkdir -p {out_dir}
    export SINGULARITY_CACHEDIR="{config.out_dir}/.singularity"
    singularity exec {singularity_flags} {image} bash -c "
        set -euo pipefail
        cd {out_dir}
        caveman.pl \
            -read-count {read_count} \
            -outdir {out_dir} \
            -reference {reference_index} \
            -tumour-bam {tumor_bam} \
            -normal-bam {normal_bam} \
            -ignore-file {genome_gap} \
            -tumour-cn {tumor_copynumber} \
            -normal-cn {normal_copynumber} \
            -germline-indel {germline_indels} \
            -species {species} \
            -species-assembly {assembly} \
            -flag-bed-files {flag_bed_files} \
            -unmatched-vcf {unmatched_vcf} \
            -seqType {seq_type} \
            -normal-contamination {sample_stats} \
            -normal-protocol {protocol} \
            -tumour-protocol {protocol} \
            -flagConfig {flag_config} \
            -flagToVcfConfig {flag_to_vcf_config} \
            -tum-cn-default {tumor_copynumber_def} \
            -norm-cn-default {normal_copynumber_def} \
            -threads {cores} \
            {add_args}
        {add_steps}
        touch {done}
    "
    {config.post_script}
    """
    )

    return AnonymousTarget(
        inputs=inputs, outputs=outputs, options=options, spec=spec # type: ignore
    )
