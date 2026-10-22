import os
import textwrap

from models import Config, SamplePair

from gwf import AnonymousTarget


def bwa_mem_template(
        inputs: dict,
        sample_name: str,
        sample_inputs: list[str],
        config: Config
    ) -> AnonymousTarget:
    out_dir = os.path.join(config.out_dir, "mapping", sample_name)

    # INPUTS
    for i, in_file in enumerate(sample_inputs):
        inputs[f"in_file_{i}"] = in_file

    # OUTPUTS
    outputs = {
        "cram": os.path.join(out_dir, sample_name + ".cram"),
        "crai": os.path.join(out_dir, sample_name + ".cram.crai")
    }

    # OPTIONS
    options = vars(config.options["bwa_mem"])

    # SPEC
    sample_inputs = inputs["sample"]
    genome = inputs["genome"]
    image = inputs["image"]
    cores = options["cores"]
    singularity_flags = config.singularity_flags

    spec = textwrap.dedent(
        rf"""
    {config.pre_script}
    set -euo pipefail
    mkdir -p {out_dir}
    export SINGULARITY_CACHEDIR="{config.out_dir}/.singularity"
    singularity exec {singularity_flags} {image} bash -c "
        set -euo pipefail
        bwa_mem.pl \
            -o {out_dir} \
            -r {genome} \
            -s {sample_name} \
            -f 10000000 \
            -t {cores} \
            -mt {cores} \
            -cram \
            -bwamem2 \
            -bwakit \
            {" ".join(sample_inputs)}
        "
    {config.post_script}
    """
    )

    return AnonymousTarget(
        inputs=inputs, outputs=outputs, options=options, spec=spec # type: ignore
    )
