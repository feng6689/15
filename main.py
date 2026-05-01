import sys
from cli import CLIHandler
from video_processor import VideoProcessor
from config import WatermarkConfig, VideoConfig


def main():
    cli = CLIHandler()
    
    watermark_config, video_config, skip_confirm = cli.parse_args()
    
    if not skip_confirm:
        watermark_config, video_config, confirmed = cli.confirm_and_modify(
            watermark_config, video_config
        )
        if not confirmed:
            print("用户取消操作")
            sys.exit(0)
    
    processor = VideoProcessor(watermark_config, video_config)
    
    try:
        if not processor.open_input():
            sys.exit(1)
        
        if not processor.open_output():
            processor.close()
            sys.exit(1)
        
        processor.process()
        
    except KeyboardInterrupt:
        print("\n用户中断操作")
    except Exception as e:
        print(f"\n处理过程中发生错误: {e}")
        import traceback
        traceback.print_exc()
    finally:
        processor.close()
    
    print("\n程序执行完毕")


if __name__ == "__main__":
    main()
