from dataclasses import dataclass


@dataclass(slots=True, frozen=True)
class SingularityImage:
    """Source information for a singularity image"""
    url: str
    version: str

    @property
    def version_url(self):
        return f"{self.url}:{self.version}"


@dataclass(slots=True, frozen=True)
class ResourceConfig:
    """HPC scheduler job configuration"""
    cores: int
    memory: int
    queue: int


@dataclass(slots=True)
class SamplePair:
    """A tumour-normal pair of samples"""
    tumour: str
    normal: str

    @property
    def name(self):
        """tumour_vs_normal-format pair name"""
        return f"{self.tumour}_vs_{self.normal}"


@dataclass(slots=True)
class Config:
    """Workflow configuration"""
    out_dir: str
    ref_dir: str
    image_dir: str
    pre_script: str
    post_script: str
    singularity_flags: str
    build: str
    mapping: bool
    images: dict[str, SingularityImage]
    options: dict[str, ResourceConfig]
