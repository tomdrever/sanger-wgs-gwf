import os
import textwrap

from models import Config, SamplePair

from gwf import AnonymousTarget


def pindel_template(
        inputs: dict,
        sample_pair: SamplePair,
        config: Config
    ) -> AnonymousTarget:
    out_dir = os.path.join(config.out_dir, sample_pair.name, "pindel")

    # OUTPUTS
    outputs = {
        "done": os.path.join(out_dir, "pindel.done"),
        "vcf": os.path.join(
            out_dir, f"{sample_pair.tumour}_vs_{sample_pair.normal}.flagged.vcf.gz"
        ),
        "germline_bed": os.path.join(
            out_dir, f"{sample_pair.tumour}_vs_{sample_pair.normal}.germline.bed.gz"
        )
    }

    # OPTIONS
    options = vars(config.options["pindel"])

    # SPEC
    tumor_bam = inputs["tumor_path"]
    normal_bam = inputs["normal_path"]
    reference_genome = inputs["reference_genome"]
    simple_repeats = inputs["simple_repeats"]
    unmatched = inputs["unmatched"]
    filter_rules = inputs["filter_rules"]
    genes = inputs["genes"]
    hi_depth = inputs["hi_depth"]
    soft_rules = inputs["soft_rules"]
    image = inputs["image"]

    protocol = "WGS"
    assembly = "NCBI38"
    species = "Human"
    cores = options["cores"]
    contig_exclude = inputs["ignore_contigs"]
    singularity_flags = config.singularity_flags

    spec = textwrap.dedent(
        rf"""
    {config.pre_script}
    set -euo pipefail
    mkdir -p {out_dir}
    export SINGULARITY_CACHEDIR="{config.out_dir}/.singularity"
    singularity exec {singularity_flags} {image} bash -c "
        set -euo pipefail
        pindel.pl \
            -outdir {out_dir} \
            -reference {reference_genome} \
            -tumour {tumor_bam} \
            -normal {normal_bam} \
            -simrep {simple_repeats} \
            -unmatched {unmatched} \
            -filter {filter_rules} \
            -genes {genes} \
            -seqtype {protocol} \
            -assembly {assembly} \
            -species {species} \
            -exclude {contig_exclude} \
            -badloci {hi_depth} \
            -cpus {cores} \
            -softfil {soft_rules}
        pindel.pl --version > {out_dir}/pindel.version.txt
        touch {outputs['done']}
        GERMLINE_BED=\$(find '{out_dir}' -maxdepth 1 -type f -name '*germline.bed' -print -quit)
        if [ -f \$GERMLINE_BED ]; then
            sort -k1,1 -k2,2n -k3,3n \$GERMLINE_BED | bgzip -c > \$GERMLINE_BED.gz
            tabix -p bed \$GERMLINE_BED.gz
            rm -f \$GERMLINE_BED
        fi
    "
    {config.post_script}
    """
    )

    return AnonymousTarget(
        inputs=inputs, outputs=outputs, options=options, spec=spec # type: ignore
    )
