from dataclasses import dataclass
from typing import Optional


@dataclass
class WatermarkConfig:
    text: str = "AI生成"
    alpha: float = 0.4
    font_color: tuple = (255, 255, 255)
    stroke_color: tuple = (0, 0, 0)
    stroke_thickness: int = 2
    font_size: Optional[int] = None
    
    h_min_ratio: float = 0.4
    h_max_ratio: float = 0.6
    v_min_ratio: float = 0.3
    v_max_ratio: float = 0.7


@dataclass
class VideoConfig:
    input_path: str = "1.mp4"
    output_path: str = "2.mp4"
