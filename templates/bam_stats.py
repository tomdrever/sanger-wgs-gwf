import textwrap

from models import Config

from gwf import AnonymousTarget


def bam_stats_template(
        inputs: dict,
        config: Config
    ) -> None:
    """ Produce {bam_path}.bas file with bam_stats """

    # OUTPUTS
    outputs = {
        "bam_stats": inputs["bam_path"] + ".bas",
    }

    # SPEC
    bam_path = inputs["bam_path"]
    image = inputs["image"]
    reference_index = inputs["reference_index"]
    singularity_flags = config.singularity_flags

    bam_stats_file = outputs["bam_stats"]

    spec = textwrap.dedent(
        rf"""
    {config.pre_script}
    set -euo pipefail
    export SINGULARITY_CACHEDIR="{config.out_dir}/.singularity"
    singularity exec {singularity_flags} {image} bash -c "
        set -euo pipefail
        bam_stats -i {bam_path} -r {reference_index} -o {bam_stats_file}
    "
    {config.post_script}
    """
    )

    return AnonymousTarget(
        inputs=inputs, outputs=outputs, options=options, spec=spec # type: ignore
    )
