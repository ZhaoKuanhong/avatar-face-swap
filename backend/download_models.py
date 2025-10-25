import hashlib
import json
import os
import sys
import time
import urllib.error
import urllib.request
from pathlib import Path

# 模型配置
MODELS_CONFIG = {
    # YuNet人脸检测模型
    "face_detection_yunet_2023mar.onnx": {
        "urls": [
            "https://huggingface.co/opencv/face_detection_yunet/resolve/main/face_detection_yunet_2023mar.onnx",
        ],
        "size": "2.8MB",
        "description": "YuNet人脸检测模型 (2023年版本)",
        "sha256": None  # 可选，用于验证文件完整性
    },
    
    # DNN Caffe模型文件
    "deploy.prototxt": {
        "urls": [
            "https://huggingface.co/opencv/face_detection_opencv_dnn/resolve/main/deploy.prototxt",
            "https://raw.githubusercontent.com/opencv/opencv/master/samples/dnn/face_detector/deploy.prototxt",
        ],
        "size": "28KB",
        "description": "OpenCV DNN Caffe配置文件"
    },
    
    "res10_300x300_ssd_iter_140000.caffemodel": {
        "urls": [
            "https://huggingface.co/spaces/liangtian/birthdayCrown/resolve/3db8f1c391e44bd9075b1c2854634f76c2ff46d0/res10_300x300_ssd_iter_140000.caffemodel",
        ],
        "size": "10.7MB", 
        "description": "OpenCV DNN SSD人脸检测模型"
    },
    
    # SCRFD模型（可选，高精度）
    "scrfd_10g_bnkps.onnx": {
        "urls": [
            "https://huggingface.co/typhoon01/aux_models/resolve/main/scrfd_10g_bnkps.onnx",
        ],
        "size": "16.9MB",
        "description": "SCRFD高精度人脸检测模型",
        "optional": True
    }
}

def create_models_dir():
    """创建models目录"""
    models_dir = Path("models")
    models_dir.mkdir(exist_ok=True)
    print(f"[OK]模型目录已创建: {models_dir.absolute()}")
    return models_dir

def download_file(url: str, filepath: Path, description: str) -> bool:
    """下载单个文件"""
    try:
        print(f"正在下载: {description}")
        print(f"   URL: {url}")
        print(f"   保存到: {filepath}")
        
        # 添加进度显示
        def progress_hook(block_num, block_size, total_size):
            if total_size > 0:
                percent = min(100, (block_num * block_size * 100) // total_size)
                print(f"\r   进度: {percent}%", end="", flush=True)
        
        urllib.request.urlretrieve(url, filepath, reporthook=progress_hook)
        print(f"\n[OK]下载完成: {filepath.name}")
        return True
        
    except urllib.error.URLError as e:
        print(f"\n[ERROR]下载失败: {e}")
        return False
    except Exception as e:
        print(f"\n[ERROR]下载异常: {e}")
        return False

def download_models():
    """下载所有模型文件"""
    models_dir = create_models_dir()
    
    print("\n开始下载模型文件...")
    print("=" * 60)
    
    success_count = 0
    total_count = 0
    failed_models = []
    
    for filename, config in MODELS_CONFIG.items():
        total_count += 1
        filepath = models_dir / filename
        
        print(f"\n处理模型: {filename}")
        print(f"   描述: {config['description']}")
        print(f"   大小: {config['size']}")
        
        # 如果文件已存在，跳过下载
        if filepath.exists():
            print(f"[OK]文件已存在: {filename}")
            success_count += 1
            continue
        
        # 尝试从多个URL下载
        downloaded = False
        for url in config['urls']:
            if download_file(url, filepath, config['description']):
                # 检查文件是否成功创建
                if filepath.exists():
                    success_count += 1
                    downloaded = True
                    break
                else:
                    print(f"[WARNING]下载失败，尝试下一个源")
        
        if not downloaded:
            failed_models.append(filename)
            # 如果是可选模型，不算作严重错误
            if config.get('optional', False):
                print(f"[WARNING]可选模型下载失败（不影响基本功能）: {filename}")
            else:
                print(f"[ERROR]必需模型下载失败: {filename}")
    
    print("\n" + "=" * 60)
    print("下载总结:")
    print(f"   成功: {success_count}/{total_count}")
    
    if failed_models:
        print(f"   失败: {failed_models}")
        
        # 区分必需和可选模型
        required_failed = [f for f in failed_models 
                          if not MODELS_CONFIG[f].get('optional', False)]
        
        if required_failed:
            print(f"\n[ERROR]必需模型下载失败，可能影响功能: {required_failed}")
            print("建议:")
            print("   1. 检查网络连接")
            print("   2. 手动下载失败的模型文件到models目录")
            print("   3. 联系开发者获取模型文件")
            return False
        else:
            print("\n[OK]所有必需模型已下载完成")
            print("[WARNING]部分可选模型下载失败，不影响基本功能")
            return True
    else:
        print("\n[OK]所有模型文件下载完成！")
        return True

def create_model_info():
    """创建模型信息文件"""
    models_dir = Path("models")
    info_file = models_dir / "model_info.json"
    
    model_info = {
        "download_date": str(Path().absolute()),
        "models": {}
    }
    
    for filename, config in MODELS_CONFIG.items():
        filepath = models_dir / filename
        if filepath.exists():
            model_info["models"][filename] = {
                "description": config["description"],
                "size": config["size"],
                "file_size": filepath.stat().st_size,
                "available": True
            }
        else:
            model_info["models"][filename] = {
                "description": config["description"],
                "size": config["size"],
                "available": False,
                "optional": config.get("optional", False)
            }
    
    with open(info_file, 'w', encoding='utf-8') as f:
        json.dump(model_info, f, indent=4, ensure_ascii=False)
    
    print(f"[OK]模型信息文件已生成: {info_file}")

def main():
    """主函数"""
    print("人脸检测模型下载工具")
    print("适用于服务器部署前的模型预下载")
    print("=" * 60)
    
    try:
        success = download_models()
        create_model_info()
        
        if success:
            print("\n[OK]模型下载完成！现在可以安全部署到服务器了")
            return 0
        else:
            print("\n[ERROR]部分模型下载失败，请检查后重试")
            return 1
            
    except KeyboardInterrupt:
        print("\n\n[CANCEL]用户取消下载")
        return 1
    except Exception as e:
        print(f"\n[ERROR]下载过程中出现异常: {e}")
        return 1

def check_and_download_models_if_needed():
    """
    检查模型是否存在，如果不存在则自动下载
    用于应用启动时的自动检查
    使用文件锁防止多个进程同时下载
    """
    models_dir = Path("models")
    lock_file = models_dir / ".download.lock"
    
    # 创建模型目录
    models_dir.mkdir(exist_ok=True)
    
    # 检查必需的模型文件
    required_models = [f for f, config in MODELS_CONFIG.items() 
                      if not config.get('optional', False)]
    
    missing_models = []
    for filename in required_models:
        filepath = models_dir / filename
        if not filepath.exists():
            missing_models.append(filename)
    
    if not missing_models:
        print("[OK] 所有必需模型文件已存在")
        return True
    
    print(f"[WARNING] 检测到缺失的模型文件: {missing_models}")
    
    # 尝试获取锁
    max_wait = 300  # 最多等待5分钟
    wait_time = 0
    lock_acquired = False
    
    while wait_time < max_wait:
        if not lock_file.exists():
            try:
                # 创建锁文件
                lock_file.touch()
                lock_acquired = True
                print("[INFO] 获取下载锁，开始自动下载模型...")
                break
            except Exception as e:
                print(f"[WARNING] 无法创建锁文件: {e}")
                time.sleep(1)
                wait_time += 1
        else:
            # 检查锁文件的年龄
            lock_age = time.time() - lock_file.stat().st_mtime
            if lock_age > 600:  # 锁文件超过10分钟，认为是死锁
                print("[WARNING] 检测到过期的锁文件，清除并重试...")
                try:
                    lock_file.unlink()
                except:
                    pass
            else:
                print(f"[INFO] 其他进程正在下载模型，等待中... ({wait_time}s/{max_wait}s)")
                time.sleep(5)
                wait_time += 5
                
                # 重新检查模型是否已下载
                missing_models = []
                for filename in required_models:
                    filepath = models_dir / filename
                    if not filepath.exists():
                        missing_models.append(filename)
                
                if not missing_models:
                    print("[OK] 其他进程已完成模型下载")
                    return True
    
    if not lock_acquired:
        print("[ERROR] 无法获取下载锁，超时")
        return False
    
    try:
        # 执行下载
        success = download_models()
        if success:
            print("[OK] 模型下载完成，应用启动继续")
            return True
        else:
            print("[ERROR] 模型下载失败，应用可能无法正常工作")
            return False
    except Exception as e:
        print(f"[ERROR] 模型下载异常: {e}")
        return False
    finally:
        # 释放锁
        try:
            if lock_file.exists():
                lock_file.unlink()
                print("[INFO] 释放下载锁")
        except Exception as e:
            print(f"[WARNING] 无法删除锁文件: {e}")

if __name__ == "__main__":
    sys.exit(main())
