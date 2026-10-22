import os
import textwrap

from models import Config, SamplePair

from gwf import AnonymousTarget


def ascat_template(
        inputs: dict,
        sample_pair: SamplePair,
        config: Config
    ) -> AnonymousTarget:
    out_dir = os.path.join(config.out_dir, sample_pair.name, "ascat")

    # OUTPUTS
    outputs = {
        "tumor_copynumber": os.path.join(out_dir, "tumor.cn.bed"),
        "normal_copynumber": os.path.join(out_dir, "normal.cn.bed"),
        "sample_stats": os.path.join(
            out_dir, sample_pair.tumour + ".samplestatistics.txt"
        ),
        "done": os.path.join(out_dir, "ascat.done"),
    }

    # OPTIONS
    options = vars(config.options["ascat"])

    # SPEC
    ascat_cn = os.path.join(out_dir, f"{sample_pair.tumour}.copynumber.caveman.csv")

    normal_bam = inputs["normal_path"]
    tumor_bam = inputs["tumor_path"]

    normal_copynumber = outputs["normal_copynumber"]
    tumor_copynumber = outputs["tumor_copynumber"]

    snp_gc = inputs["snp_gc"]
    reference_genome = inputs["reference_genome"]
    locus = inputs["locus"]

    min_base_quality = 20
    gender = "L"
    species = "Human"
    assembly = "GRCh38"
    protocol = "WGS"

    done = outputs["done"]

    image = inputs["image"]
    cores = options["cores"]
    singularity_flags = config.singularity_flags

    spec = textwrap.dedent(rf"""
    {config.pre_script}
    set -euo pipefail
    mkdir -p {out_dir}
    export SINGULARITY_CACHEDIR="{config.out_dir}/.singularity"
    singularity exec {singularity_flags} {image} bash -c "
        set -euo pipefail
        ascat.pl \
            -outdir {out_dir} \
            -tumour {tumor_bam} \
            -normal {normal_bam} \
            -snp_gc {snp_gc} \
            -reference {reference_genome} \
            -minbasequal {min_base_quality} \
            -gender {gender} \
            -locus {locus} \
            -species {species} \
            -assembly {assembly} \
            -protocol {protocol} \
            -cpus {cores} \
            -force
        ascat.pl --version > {out_dir}/ascat.version.txt
    "
    while IFS=',' read -r _ col2 col3 col4 col5 _ _ _; do
        echo -e "${{col2}}\t$((col3-1))\t${{col4}}\t${{col5}}"
    done < "{ascat_cn}" > {normal_copynumber} 
    while IFS=',' read -r _ col2 col3 col4 _ _ col7 _; do
        echo -e "${{col2}}\t$((col3-1))\t${{col4}}\t${{col7}}"
    done < "{ascat_cn}" > {tumor_copynumber}
    touch {done}
    {config.post_script}
    """
    )

    return AnonymousTarget(
        inputs=inputs, outputs=outputs, options=options, spec=spec # type: ignore
    )
