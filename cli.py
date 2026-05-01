import argparse
from config import WatermarkConfig, VideoConfig


class CLIHandler:
    def __init__(self):
        self.parser = self._create_parser()
    
    def _create_parser(self) -> argparse.ArgumentParser:
        parser = argparse.ArgumentParser(
            description="视频水印添加工具 - 添加半透明移动文字水印"
        )
        
        parser.add_argument(
            "-i", "--input",
            default="1.mp4",
            help="输入视频文件路径 (默认: 1.mp4)"
        )
        
        parser.add_argument(
            "-o", "--output",
            default="2.mp4",
            help="输出视频文件路径 (默认: 2.mp4)"
        )
        
        parser.add_argument(
            "-t", "--text",
            default="AI生成",
            help="水印文字 (默认: AI生成)"
        )
        
        parser.add_argument(
            "-a", "--alpha",
            type=float,
            default=0.4,
            help="水印透明度 (0.0-1.0, 默认: 0.4)"
        )
        
        parser.add_argument(
            "--h-min",
            type=float,
            default=0.4,
            help="水平移动最小比例 (默认: 0.4, 即40%)"
        )
        
        parser.add_argument(
            "--h-max",
            type=float,
            default=0.6,
            help="水平移动最大比例 (默认: 0.6, 即60%)"
        )
        
        parser.add_argument(
            "--v-min",
            type=float,
            default=0.3,
            help="垂直移动最小比例 (默认: 0.3, 即30%)"
        )
        
        parser.add_argument(
            "--v-max",
            type=float,
            default=0.7,
            help="垂直移动最大比例 (默认: 0.7, 即70%)"
        )
        
        parser.add_argument(
            "-y", "--yes",
            action="store_true",
            help="跳过确认提示直接处理"
        )
        
        return parser
    
    def parse_args(self) -> tuple:
        args = self.parser.parse_args()
        
        watermark_config = WatermarkConfig(
            text=args.text,
            alpha=max(0.0, min(1.0, args.alpha)),
            h_min_ratio=max(0.0, min(1.0, args.h_min)),
            h_max_ratio=max(0.0, min(1.0, args.h_max)),
            v_min_ratio=max(0.0, min(1.0, args.v_min)),
            v_max_ratio=max(0.0, min(1.0, args.v_max))
        )
        
        video_config = VideoConfig(
            input_path=args.input,
            output_path=args.output
        )
        
        return watermark_config, video_config, args.yes
    
    def display_config(self, watermark_config: WatermarkConfig, video_config: VideoConfig):
        print("=" * 60)
        print("当前配置:")
        print("=" * 60)
        print(f"  输入视频: {video_config.input_path}")
        print(f"  输出视频: {video_config.output_path}")
        print(f"  水印文字: '{watermark_config.text}'")
        print(f"  水印透明度: {watermark_config.alpha}")
        print(f"  水平移动范围: {watermark_config.h_min_ratio*100:.0f}% - {watermark_config.h_max_ratio*100:.0f}%")
        print(f"  垂直移动范围: {watermark_config.v_min_ratio*100:.0f}% - {watermark_config.v_max_ratio*100:.0f}%")
        print("=" * 60)
    
    def confirm_and_modify(self, watermark_config: WatermarkConfig, video_config: VideoConfig) -> tuple:
        while True:
            self.display_config(watermark_config, video_config)
            
            choice = input("\n确认以上配置? (y=确认, m=修改, q=退出): ").strip().lower()
            
            if choice == 'y':
                return watermark_config, video_config, True
            elif choice == 'q':
                return watermark_config, video_config, False
            elif choice == 'm':
                watermark_config, video_config = self._modify_config(watermark_config, video_config)
            else:
                print("无效输入，请输入 y, m 或 q")
        
        return watermark_config, video_config, False
    
    def _modify_config(self, watermark_config: WatermarkConfig, video_config: VideoConfig) -> tuple:
        while True:
            print("\n请选择要修改的项:")
            print("  1. 水印文字")
            print("  2. 水印透明度")
            print("  3. 水平移动范围")
            print("  4. 垂直移动范围")
            print("  5. 输入视频路径")
            print("  6. 输出视频路径")
            print("  0. 返回确认界面")
            
            choice = input("\n请输入选项编号: ").strip()
            
            if choice == '0':
                break
            elif choice == '1':
                new_text = input(f"请输入新的水印文字 (当前: {watermark_config.text}): ").strip()
                if new_text:
                    watermark_config.text = new_text
            elif choice == '2':
                new_alpha = input(f"请输入新的透明度 (0.0-1.0, 当前: {watermark_config.alpha}): ").strip()
                try:
                    alpha = float(new_alpha)
                    if 0.0 <= alpha <= 1.0:
                        watermark_config.alpha = alpha
                    else:
                        print("透明度需在 0.0-1.0 之间")
                except ValueError:
                    print("请输入有效的数字")
            elif choice == '3':
                print(f"当前水平范围: {watermark_config.h_min_ratio*100:.0f}% - {watermark_config.h_max_ratio*100:.0f}%")
                new_hmin = input("请输入新的最小比例 (如 0.4 表示 40%): ").strip()
                new_hmax = input("请输入新的最大比例 (如 0.6 表示 60%): ").strip()
                try:
                    hmin = float(new_hmin)
                    hmax = float(new_hmax)
                    if 0.0 <= hmin < hmax <= 1.0:
                        watermark_config.h_min_ratio = hmin
                        watermark_config.h_max_ratio = hmax
                    else:
                        print("范围无效，请确保 0.0 <= min < max <= 1.0")
                except ValueError:
                    print("请输入有效的数字")
            elif choice == '4':
                print(f"当前垂直范围: {watermark_config.v_min_ratio*100:.0f}% - {watermark_config.v_max_ratio*100:.0f}%")
                new_vmin = input("请输入新的最小比例 (如 0.3 表示 30%): ").strip()
                new_vmax = input("请输入新的最大比例 (如 0.7 表示 70%): ").strip()
                try:
                    vmin = float(new_vmin)
                    vmax = float(new_vmax)
                    if 0.0 <= vmin < vmax <= 1.0:
                        watermark_config.v_min_ratio = vmin
                        watermark_config.v_max_ratio = vmax
                    else:
                        print("范围无效，请确保 0.0 <= min < max <= 1.0")
                except ValueError:
                    print("请输入有效的数字")
            elif choice == '5':
                new_input = input(f"请输入新的输入视频路径 (当前: {video_config.input_path}): ").strip()
                if new_input:
                    video_config.input_path = new_input
            elif choice == '6':
                new_output = input(f"请输入新的输出视频路径 (当前: {video_config.output_path}): ").strip()
                if new_output:
                    video_config.output_path = new_output
            else:
                print("无效选项，请重新选择")
        
        return watermark_config, video_config
