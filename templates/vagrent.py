import os
import textwrap
from pathlib import Path

from models import Config, SamplePair

from gwf import AnonymousTarget


def vagrent_template(
        inputs: dict,
        sample_pair: SamplePair,
        config: Config
    ) -> AnonymousTarget:
    vcf_parent_dir = Path(inputs["vcf"]).parent.absolute()
    annotated_vcf_path = os.path.join(vcf_parent_dir, f"{sample_pair.name}.annot.vcf")

    # OUTPUTS
    outputs = {
        "annotated_vcf": f"{annotated_vcf_path}.gz"
    }

    # OPTIONS
    options = config.options['vagrent'].to_dict()

    # SPEC
    vcf = inputs["vcf"]
    vagrent_cache = inputs["vagrent_cache"]
    image = inputs["image"]
    singularity_flags = config.singularity_flags

    spec = textwrap.dedent(
        rf"""
    {config.pre_script}
    set -euo pipefail
    singularity exec {singularity_flags} {image} bash -c "
        set -euo pipefail
        rm -f {annotated_vcf_path};
        AnnotateVcf.pl \
            --tabix \
            --cache {vagrent_cache} \
            --input {vcf} \
            --output {annotated_vcf_path}

        AnnotateVcf.pl --version > {vcf_parent_dir}/vagrent.version.txt
    "
    {config.post_script}
    """
    )

    return AnonymousTarget(
        inputs=inputs, outputs=outputs, options=options, spec=spec # type: ignore
    )
