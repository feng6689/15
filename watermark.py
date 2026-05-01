import cv2
import numpy as np
import math
from PIL import Image, ImageDraw, ImageFont
from config import WatermarkConfig


class WatermarkRenderer:
    def __init__(self, config: WatermarkConfig, frame_width: int, frame_height: int):
        self.config = config
        self.frame_width = frame_width
        self.frame_height = frame_height
        
        if self.config.font_size is None:
            self.font_size = self._calculate_font_size()
        else:
            self.font_size = self.config.font_size
        
        self.font = self._load_font(self.font_size)
        self.stroke_font = self._load_font(self.font_size)
    
    def _get_windows_font_paths(self) -> list:
        import os
        font_dirs = [
            r"C:\Windows\Fonts",
            os.path.expandvars(r"%LOCALAPPDATA%\Microsoft\Windows\Fonts"),
            os.path.expandvars(r"%WINDIR%\Fonts"),
        ]
        
        font_files = []
        for font_dir in font_dirs:
            if not os.path.exists(font_dir):
                continue
            for f in os.listdir(font_dir):
                f_lower = f.lower()
                if f_lower.endswith(('.ttf', '.ttc', '.otf')):
                    font_files.append(os.path.join(font_dir, f))
        
        return font_files
    
    def _load_font(self, size: int) -> ImageFont.FreeTypeFont:
        import os
        
        priority_fonts = [
            "msyh.ttc",
            "msyhbd.ttc", 
            "simhei.ttf",
            "simsun.ttc",
            "simkai.ttf",
            "simli.ttf",
            "STZHONGS.TTF",
            "STKAITI.TTF",
            "STSONG.TTF",
            "msyh.ttf",
            "simhei.ttc",
        ]
        
        font_paths = self._get_windows_font_paths()
        
        for priority_name in priority_fonts:
            for font_path in font_paths:
                if os.path.basename(font_path).lower() == priority_name.lower():
                    try:
                        return ImageFont.truetype(font_path, size)
                    except:
                        continue
        
        for font_path in font_paths:
            try:
                return ImageFont.truetype(font_path, size)
            except:
                continue
        
        try:
            return ImageFont.load_default()
        except:
            raise RuntimeError("无法加载任何字体，请确保系统中安装了中文字体")
    
    def _calculate_font_size(self) -> int:
        min_dim = min(self.frame_width, self.frame_height)
        if min_dim < 480:
            return 24
        elif min_dim < 720:
            return 36
        elif min_dim < 1080:
            return 48
        else:
            return 72
    
    def get_text_size(self) -> tuple:
        text = self.config.text
        
        left, top, right, bottom = self.font.getbbox(text)
        text_width = right - left
        text_height = bottom - top
        baseline = 0
        
        return text_width, text_height, baseline
    
    def render_watermark(self, frame: np.ndarray, x: int, y: int) -> np.ndarray:
        text = self.config.text
        alpha = self.config.alpha
        stroke_thickness = self.config.stroke_thickness
        
        text_width, text_height, _ = self.get_text_size()
        
        pil_frame = Image.fromarray(cv2.cvtColor(frame, cv2.COLOR_BGR2RGB))
        
        overlay = Image.new('RGBA', pil_frame.size, (0, 0, 0, 0))
        draw = ImageDraw.Draw(overlay)
        
        font_color_rgba = (
            self.config.font_color[2],
            self.config.font_color[1],
            self.config.font_color[0],
            255
        )
        
        stroke_color_rgba = (
            self.config.stroke_color[2],
            self.config.stroke_color[1],
            self.config.stroke_color[0],
            255
        )
        
        draw.text(
            (x, y - text_height),
            text,
            font=self.font,
            fill=font_color_rgba,
            stroke_fill=stroke_color_rgba,
            stroke_width=stroke_thickness
        )
        
        overlay_rgb = overlay.convert('RGB')
        overlay_np = np.array(overlay_rgb)
        
        alpha_mask = np.array(overlay.split()[-1]) / 255.0
        alpha_mask = alpha_mask * alpha
        
        alpha_mask_3d = np.stack([alpha_mask, alpha_mask, alpha_mask], axis=2)
        
        result_np = (overlay_np * alpha_mask_3d + np.array(pil_frame) * (1 - alpha_mask_3d)).astype(np.uint8)
        
        result = cv2.cvtColor(result_np, cv2.COLOR_RGB2BGR)
        
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
