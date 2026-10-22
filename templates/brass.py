import os
import textwrap

from models import Config, SamplePair

from gwf import AnonymousTarget


def brass_template(
        inputs: dict,
        sample_pair: SamplePair,
        config: Config,
        process: str | None = None
    ) -> AnonymousTarget:
    out_dir = os.path.join(config.out_dir, sample_pair.name, "brass")

    if process is None:
        process = "main"

    # OUTPUTS
    outputs = {}
    if process != "main":
        outputs["done"] = os.path.join(out_dir, process + ".done")
    else:
        outputs["done"] = os.path.join(out_dir, "brass.done")

    # OPTIONS
    brass_step_options = {
        "brass_input": vars(config.options["brass_input"]),
        "brass_cover": vars(config.options["brass_cover"]),
        "brass_main": vars(config.options["brass_main"])
    }

    if f"brass_{process}" not in brass_step_options:
        raise ValueError(f"Invalid process {process} for brass for config.json")
    options = brass_step_options[f"brass_{process}"]

    # SPEC
    tumor_bam = inputs["tumor_path"]
    normal_bam = inputs["normal_path"]

    reference_genome = inputs["reference_genome"]
    hi_depth = inputs["hi_depth"]
    brass_filter = inputs["brass_filter"]
    genome_cache = inputs["genome_cache"]
    virus_sequences = inputs["virus_sequences"]
    microbe_sequences = inputs["microbe_sequences"]
    gc_bin = inputs["gc_bin"]
    cent_telo = inputs["cent_telo"]
    cytoband = inputs["cytoband"]
    sample_stats = inputs["sample_stats"]

    min_group = 4
    protocol = "WGS"
    assembly = "GRCh38"
    species = "Human"

    image = inputs["image"]
    cores = options["cores"]
    singularity_flags = config.singularity_flags

    done = outputs["done"]

    add_args = ""
    add_steps = ""

    if process != "main":
        add_args += f"-process {process}"
    else:
        add_steps += f"brass.pl --version > {out_dir}/brass.version.txt"

    spec = textwrap.dedent(
        rf"""
    {config.pre_script}
    set -euo pipefail
    mkdir -p {out_dir}
    export SINGULARITY_CACHEDIR="{config.out_dir}/.singularity"
    singularity exec {singularity_flags} {image} bash -c "
        set -euo pipefail
        brass.pl \
            -k {min_group} \
            -mingroup {min_group} \
            -cpus {cores} \
            -tum_name {sample_pair.tumour} \
            -norm_name {sample_pair.normal} \
            -depth {hi_depth} \
            -filter {brass_filter} \
            -genome {reference_genome} \
            -species {species} \
            -assembly {assembly} \
            -protocol {protocol} \
            -sampstat {sample_stats} \
            -g_cache {genome_cache} \
            -viral {virus_sequences} \
            -microbe {microbe_sequences}/all_ncbi_bacteria \
            -gcbin {gc_bin} \
            -centtel {cent_telo} \
            -cytoband {cytoband} \
            -tumour {tumor_bam} \
            -normal {normal_bam} \
            -outdir {out_dir} \
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
