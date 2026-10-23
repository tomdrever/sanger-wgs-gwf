from __future__ import annotations

from dataclasses import dataclass, asdict

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
    memory: str
    queue: str

    def to_dict(self):
        return asdict(self)


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
    caveman_step_jobs: int
    mapping: bool
    images: dict[str, SingularityImage]
    options: dict[str, ResourceConfig]

    @staticmethod
    def load(raw_dict: dict) -> Config:
        """Load a Config instance from a python dict loaded from a config.json file"""
        config = Config(**raw_dict)
        config.images = {image: SingularityImage(**raw_dict["images"][image]) for image in raw_dict["images"]}
        config.options = {option: ResourceConfig(**raw_dict["options"][option]) for option in raw_dict["options"]} 
        return config
