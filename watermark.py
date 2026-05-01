import cv2
import numpy as np
import math
from config import WatermarkConfig


class WatermarkRenderer:
    def __init__(self, config: WatermarkConfig, frame_width: int, frame_height: int):
        self.config = config
        self.frame_width = frame_width
        self.frame_height = frame_height
        self.font = cv2.FONT_HERSHEY_SIMPLEX
        
        if self.config.font_size is None:
            self.font_scale = self._calculate_font_scale()
        else:
            self.font_scale = self.config.font_size / 30.0
    
    def _calculate_font_scale(self) -> float:
        min_dim = min(self.frame_width, self.frame_height)
        if min_dim < 480:
            return 1.0
        elif min_dim < 720:
            return 1.5
        elif min_dim < 1080:
            return 2.0
        else:
            return 3.0
    
    def get_text_size(self) -> tuple:
        text = self.config.text
        font_scale = self.font_scale
        thickness = self.config.stroke_thickness + 1
        
        (text_width, text_height), baseline = cv2.getTextSize(
            text, self.font, font_scale, thickness
        )
        return text_width, text_height, baseline
    
    def render_watermark(self, frame: np.ndarray, x: int, y: int) -> np.ndarray:
        text = self.config.text
        font_scale = self.font_scale
        font_thickness = 2
        stroke_thickness = self.config.stroke_thickness
        alpha = self.config.alpha
        
        text_width, text_height, baseline = self.get_text_size()
        
        overlay = frame.copy()
        
        cv2.putText(
            overlay, text, (x, y), self.font, font_scale,
            self.config.stroke_color, font_thickness + stroke_thickness,
            cv2.LINE_AA
        )
        
        cv2.putText(
            overlay, text, (x, y), self.font, font_scale,
            self.config.font_color, font_thickness,
            cv2.LINE_AA
        )
        
        result = cv2.addWeighted(overlay, alpha, frame, 1 - alpha, 0)
        
        return result


class PositionCalculator:
    def __init__(
        self,
        config: WatermarkConfig,
        frame_width: int,
        frame_height: int,
        total_frames: int
    ):
        self.config = config
        self.frame_width = frame_width
        self.frame_height = frame_height
        self.total_frames = total_frames
        
        self.h_min = int(frame_width * config.h_min_ratio)
        self.h_max = int(frame_width * config.h_max_ratio)
        self.v_min = int(frame_height * config.v_min_ratio)
        self.v_max = int(frame_height * config.v_max_ratio)
        
        self.h_center = (self.h_min + self.h_max) / 2
        self.h_amplitude = (self.h_max - self.h_min) / 2
        
        self.v_center = (self.v_min + self.v_max) / 2
        self.v_amplitude = (self.v_max - self.v_min) / 2
    
    def get_position(self, frame_index: int, text_width: int, text_height: int) -> tuple:
        progress = frame_index / self.total_frames
        
        angle = 2 * math.pi * progress
        
        h_offset = self.h_amplitude * math.sin(angle)
        v_offset = self.v_amplitude * math.sin(angle + math.pi / 2)
        
        center_x = self.h_center + h_offset
        center_y = self.v_center + v_offset
        
        x = int(center_x - text_width / 2)
        y = int(center_y + text_height / 2)
        
        x = max(0, min(x, self.frame_width - text_width))
        y = max(text_height, min(y, self.frame_height))
        
        return x, y
