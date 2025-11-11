from datetime import datetime
from pathlib import Path
from typing import Literal

import numpy as np
from pydantic import BaseModel, Field, ConfigDict
import soundfile as sf


def _parse_sdrpp_filename(path: Path):
    """parse SDR++ file pattern: $t_$f_$h-$m-$s_$d-$M-$y"""
    rec_type, fc, dt = path.stem.split('_', maxsplit=2)

    if not fc.endswith('Hz'):
        raise ValueError(f'Invalid SDR++ filename: {path}')

    fc = int(fc.removesuffix('Hz'))
    dt = datetime.strptime(dt, '%H-%M-%S_%d-%m-%Y')
    return rec_type, fc, dt


class RecordingMetadata(BaseModel):
    path: Path
    rec_type: Literal['baseband', 'audio']
    start_time: datetime
    fc: int = Field(description='Center frequency of recording in Hz')
    n_frames: int = Field(description='Number of frames in recording')
    format: str | None = None
    sample_rate: int | None = None
    channels: int | None = None
    subtype: str | None = Field(description='Subtype of recording, e.g. PCM_16', default=None)

    @property
    def duration(self) -> float:
        return self.n_frames / self.sample_rate

    @classmethod
    def from_file(cls, file: str | Path | sf.SoundFile):
        if isinstance(file, (str, Path)):
            file = sf.SoundFile(file)

        path = Path(file.name)
        rec_type, fc, dt = _parse_sdrpp_filename(path)

        return cls(
            path=Path(file.name),
            start_time=dt,
            rec_type='baseband' if file.samplerate > 1e6 else 'audio',
            fc=fc,
            n_frames=file.frames,
            format=file.format,
            sample_rate=file.samplerate,
            channels=file.channels,
            subtype=file.subtype,
        )


class Recording(BaseModel):
    meta: RecordingMetadata
    data: np.ndarray

    model_config = ConfigDict(arbitrary_types_allowed=True)

    @classmethod
    def load(cls, file: str | Path):
        with sf.SoundFile(str(file)) as f:
            meta = RecordingMetadata.from_file(f)
            data = f.read(dtype='float64', always_2d=True)

        return cls(meta=meta, data=data)
