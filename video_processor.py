import cv2
import sys
from typing import Optional
from config import WatermarkConfig, VideoConfig
from watermark import WatermarkRenderer, PositionCalculator


class VideoProcessor:
    def __init__(self, watermark_config: WatermarkConfig, video_config: VideoConfig):
        self.watermark_config = watermark_config
        self.video_config = video_config
        self.cap: Optional[cv2.VideoCapture] = None
        self.out: Optional[cv2.VideoWriter] = None
        self.frame_width: int = 0
        self.frame_height: int = 0
        self.fps: float = 0.0
        self.total_frames: int = 0
    
    def open_input(self) -> bool:
        self.cap = cv2.VideoCapture(self.video_config.input_path)
        if not self.cap.isOpened():
            print(f"无法打开视频文件: {self.video_config.input_path}")
            return False
        
        self.frame_width = int(self.cap.get(cv2.CAP_PROP_FRAME_WIDTH))
        self.frame_height = int(self.cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
        self.fps = self.cap.get(cv2.CAP_PROP_FPS)
        self.total_frames = int(self.cap.get(cv2.CAP_PROP_FRAME_COUNT))
        
        print(f"视频信息:")
        print(f"  分辨率: {self.frame_width} x {self.frame_height}")
        print(f"  帧率: {self.fps:.2f} FPS")
        print(f"  总帧数: {self.total_frames}")
        print(f"  时长: {self.total_frames / self.fps:.2f} 秒")
        
        return True
    
    def open_output(self) -> bool:
        fourcc = cv2.VideoWriter_fourcc(*'mp4v')
        
        self.out = cv2.VideoWriter(
            self.video_config.output_path,
            fourcc,
            self.fps,
            (self.frame_width, self.frame_height)
        )
        
        if not self.out.isOpened():
            print(f"无法创建输出视频文件: {self.video_config.output_path}")
            return False
        
        return True
    
    def process(self):
        if self.cap is None or self.out is None:
            print("视频未正确初始化")
            return
        
        renderer = WatermarkRenderer(self.watermark_config, self.frame_width, self.frame_height)
        position_calc = PositionCalculator(
            self.watermark_config,
            self.frame_width,
            self.frame_height,
            self.total_frames
        )
        
        text_width, text_height, _ = renderer.get_text_size()
        
        print(f"\n开始处理视频...")
        print(f"水印文字: '{self.watermark_config.text}'")
        print(f"水印透明度: {self.watermark_config.alpha}")
        print(f"水印尺寸: {text_width} x {text_height}")
        print(f"水平移动范围: {position_calc.h_min} - {position_calc.h_max} (像素)")
        print(f"垂直移动范围: {position_calc.v_min} - {position_calc.v_max} (像素)")
        print("-" * 50)
        
        frame_index = 0
        
        while True:
            ret, frame = self.cap.read()
            if not ret:
                break
            
            x, y = position_calc.get_position(frame_index, text_width, text_height)
            
            frame = renderer.render_watermark(frame, x, y)
            
            self.out.write(frame)
            
            frame_index += 1
            
            if frame_index % 30 == 0:
                progress = frame_index / self.total_frames * 100
                sys.stdout.write(f"\r处理进度: {progress:.1f}% ({frame_index}/{self.total_frames})")
                sys.stdout.flush()
        
        print(f"\n处理完成! 输出视频: {self.video_config.output_path}")
    
    def close(self):
        if self.cap is not None:
            self.cap.release()
        if self.out is not None:
            self.out.release()
        cv2.destroyAllWindows()
