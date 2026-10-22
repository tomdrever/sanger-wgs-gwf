import os
import textwrap

from gwf import AnonymousTarget

from models import Config, SingularityImage


def singularity_pull_template(
        name: str,
        image: SingularityImage,
        config: Config
    ) -> AnonymousTarget:
    sif_file_name = f"{name}_{image.version}.sif"

    # OUTPUTS
    outputs = {
        "image": os.path.join(config.image_dir, sif_file_name),
    }

    # SPEC
    spec = textwrap.dedent(
        rf"""
    {config.pre_script}
    mkdir -p {config.image_dir}
    pushd {config.image_dir}
    export SINGULARITY_CACHEDIR="{config.out_dir}/.singularity"
    singularity pull {sif_file_name} {image.version_url}
    popd
    {config.post_script}
    """
    )

    return AnonymousTarget(
        inputs=[], outputs=outputs, options=options, spec=spec, protect=[outputs["image"]] # type: ignore
    )
