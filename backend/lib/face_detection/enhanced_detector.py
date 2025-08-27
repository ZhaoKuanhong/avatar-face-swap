import cv2
import numpy as np
import os
import json
import time
from typing import List, Tuple, Dict, Any, Optional
import warnings
warnings.filterwarnings('ignore')

# 延迟导入避免循环导入问题
from ..common.constants import CROPPED_FACES_FOLDER

def _safe_log_activity(*args, **kwargs):
    return True #已弃用


class EnhancedFaceDetector:
    def __init__(self, use_gpu: bool = False):
        self.use_gpu = use_gpu and cv2.cuda.getCudaEnabledDeviceCount() > 0
        self.detectors = {}
        
        # 模型文件路径配置（优先使用预下载的模型）
        self.model_paths = self._get_model_paths()
        
        print("[FaceDetector] 正在初始化增强人脸检测器（服务器优化版）...")
        self._load_detectors()
        print(f"[FaceDetector] 已加载 {len(self.detectors)} 个检测器")
    
    def _get_model_paths(self) -> Dict[str, str]:
        base_dir = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))  # 回到backend目录
        models_dir = os.path.join(base_dir, "models")
        
        paths = {
            "yunet_model": None,
            "dnn_prototxt": None,
            "dnn_model": None,
            "scrfd_model": None
        }
        
        # YuNet模型路径检查
        yunet_candidates = [
            os.path.join(models_dir, "face_detection_yunet_2023mar.onnx"),
            os.path.join(base_dir, "face_detection_yunet_2023mar.onnx"),
            "face_detection_yunet_2023mar.onnx"
        ]
        
        for path in yunet_candidates:
            if os.path.exists(path):
                paths["yunet_model"] = path
                print(f"[FaceDetector] 找到YuNet模型: {path}")
                break
        
        # DNN模型路径检查
        dnn_prototxt_candidates = [
            os.path.join(models_dir, "deploy.prototxt"),
            os.path.join(base_dir, "deploy.prototxt"),
            "deploy.prototxt"
        ]
        
        dnn_model_candidates = [
            os.path.join(models_dir, "res10_300x300_ssd_iter_140000.caffemodel"),
            os.path.join(base_dir, "res10_300x300_ssd_iter_140000.caffemodel"),
            "res10_300x300_ssd_iter_140000.caffemodel"
        ]
        
        for path in dnn_prototxt_candidates:
            if os.path.exists(path):
                paths["dnn_prototxt"] = path
                print(f"[FaceDetector] 找到DNN配置文件: {path}")
                break
        
        for path in dnn_model_candidates:
            if os.path.exists(path):
                paths["dnn_model"] = path
                print(f"[FaceDetector] 找到DNN模型文件: {path}")
                break
        
        # SCRFD模型路径检查
        scrfd_candidates = [
            os.path.join(models_dir, "scrfd_10g_bnkps.onnx"),
            os.path.join(base_dir, "scrfd_10g_bnkps.onnx"),
            "scrfd_10g_bnkps.onnx"
        ]
        
        for path in scrfd_candidates:
            if os.path.exists(path):
                paths["scrfd_model"] = path
                print(f"[FaceDetector] 找到SCRFD模型: {path}")
                break
        
        return paths
    
    def _load_detectors(self):
        """加载各种人脸检测器"""
        # 这个是Mio测试出来的效果，RetinaFace最强，但样本量太少，很难说是不是最实用的
        # 1. 加载RetinaFace检测器（
        self._load_retinaface_detector()
        
        # 2. 加载YuNet检测器
        self._load_yunet_detector()
        
        # 3. 加载MediaPipe检测器
        self._load_mediapipe_detector()
        
        # 4. 加载DNN检测器作为备选
        self._load_dnn_detector()
        
        # 5. 保留传统dlib检测器作为最后备选
        self._load_dlib_detector()
        
        # 6. 级联检测器作为辅助
        self._load_cascade_detector()
    
    def _load_retinaface_detector(self):
        try:
            import insightface
            self.retina_app = insightface.app.FaceAnalysis(providers=['CPUExecutionProvider'])
            self.retina_app.prepare(ctx_id=-1)  # CPU模式
            self.detectors['retinaface'] = self._detect_with_retinaface
            print("[FaceDetector] ✓ RetinaFace检测器加载成功（最强精度）")
        except ImportError:
            print("[FaceDetector] ⚠ RetinaFace需要安装: pip install insightface")
        except Exception as e:
            print(f"[FaceDetector] ⚠ RetinaFace检测器加载失败: {e}")
    
    def _load_mediapipe_detector(self):
        try:
            import mediapipe as mp
            self.mp_face_detection = mp.solutions.face_detection
            self.face_detection = self.mp_face_detection.FaceDetection(
                model_selection=1,  # 1为远距离模式，适合团建照
                min_detection_confidence=0.4  # 降低阈值获得更好的召回率
            )
            self.detectors['mediapipe'] = self._detect_with_mediapipe
            print("[FaceDetector] ✓ MediaPipe检测器加载成功（Google出品）")
        except ImportError:
            print("[FaceDetector] ⚠ MediaPipe需要安装: pip install mediapipe")
        except Exception as e:
            print(f"[FaceDetector] ⚠ MediaPipe检测器加载失败: {e}")
    
    def _load_yunet_detector(self):
        try:
            model_path = self.model_paths["yunet_model"]
            if model_path and os.path.exists(model_path):
                self.yunet = cv2.FaceDetectorYN.create(
                    model_path, "", (0, 0),
                    score_threshold=0.7,
                    nms_threshold=0.3,
                    top_k=20
                )
                self.detectors['yunet'] = self._detect_with_yunet
                print(f"[FaceDetector] ✓ YuNet检测器加载成功（使用预下载模型）")
            else:
                # 如果没有预下载的模型，尝试下载（但不推荐在生产环境）
                print("[FaceDetector] ⚠ YuNet预下载模型未找到，建议运行 python download_models.py")
                self._download_yunet_model()
        except Exception as e:
            print(f"[FaceDetector] ⚠ YuNet检测器加载失败: {e}")
    
    def _load_dnn_detector(self):
        try:
            prototxt_path = self.model_paths["dnn_prototxt"] 
            model_path = self.model_paths["dnn_model"]
            
            if prototxt_path and model_path and os.path.exists(prototxt_path) and os.path.exists(model_path):
                self.dnn_net = cv2.dnn.readNetFromCaffe(prototxt_path, model_path)
                
                if self.use_gpu:
                    self.dnn_net.setPreferableBackend(cv2.dnn.DNN_BACKEND_CUDA)
                    self.dnn_net.setPreferableTarget(cv2.dnn.DNN_TARGET_CUDA)
                
                self.detectors['dnn'] = self._detect_with_dnn
                print("[FaceDetector] ✓ DNN检测器加载成功（使用预下载模型）")
            else:
                print("[FaceDetector] ⚠ DNN预下载模型未找到，建议运行 python download_models.py")
        except Exception as e:
            print(f"[FaceDetector] ⚠ DNN检测器加载失败: {e}")
    
    def _load_dlib_detector(self):
        #飞舞模型
        try:
            import dlib
            self.dlib_detector = dlib.get_frontal_face_detector()
            self.detectors['dlib'] = self._detect_with_dlib
            print("[FaceDetector] ✓ dlib检测器加载成功（兼容模式）")
        except ImportError:
            print("[FaceDetector] ⚠ dlib未安装，跳过dlib检测器")
        except Exception as e:
            print(f"[FaceDetector] ⚠ dlib检测器加载失败: {e}")
    
    def _load_cascade_detector(self):
        """加载级联检测器"""
        try:
            self.cascade = cv2.CascadeClassifier(
                cv2.data.haarcascades + 'haarcascade_frontalface_default.xml'
            )
            self.detectors['cascade'] = self._detect_with_cascade
            print("[FaceDetector] ✓ 级联检测器加载成功")
        except Exception as e:
            print(f"[FaceDetector] ⚠ 级联检测器加载失败: {e}")
    
    def _download_yunet_model(self) -> Optional[str]:
        try:
            import urllib.request
            
            # 确保models目录存在
            models_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), "models")
            os.makedirs(models_dir, exist_ok=True)
            
            model_path = os.path.join(models_dir, "face_detection_yunet_2023mar.onnx")
            
            if os.path.exists(model_path):
                return model_path
            
            # 使用HuggingFace镜像地址
            hf_url = "https://huggingface.co/opencv/face_detection_yunet/resolve/main/face_detection_yunet_2023mar.onnx"
            
            print("[FaceDetector] 正在下载YuNet模型（从HuggingFace）...")
            urllib.request.urlretrieve(hf_url, model_path)
            print("[FaceDetector] ✓ YuNet模型下载完成")
            
            # 更新模型路径
            self.model_paths["yunet_model"] = model_path
            
            # 重新尝试加载YuNet
            self.yunet = cv2.FaceDetectorYN.create(
                model_path, "", (0, 0),
                score_threshold=0.7,
                nms_threshold=0.3,
                top_k=20
            )
            self.detectors['yunet'] = self._detect_with_yunet
            
            return model_path
            
        except Exception as e:
            print(f"[FaceDetector] ⚠ YuNet模型下载失败: {e}")
            return None
    
    def _detect_with_retinaface(self, image: np.ndarray) -> List[Tuple[int, int, int, int, float]]:
        try:
            faces = self.retina_app.get(image)
            results = []
            
            for face in faces:
                bbox = face.bbox.astype(int)
                x1, y1, x2, y2 = bbox
                w, h = x2 - x1, y2 - y1
                confidence = face.det_score
                
                if self._validate_face_region(image, (x1, y1, w, h)):
                    results.append((x1, y1, w, h, confidence))
            
            return results
            
        except Exception as e:
            print(f"[FaceDetector] RetinaFace检测出错: {e}")
            return []
    
    def _detect_with_mediapipe(self, image: np.ndarray) -> List[Tuple[int, int, int, int, float]]:
        """使用MediaPipe检测人脸 - Google出品"""
        try:
            h, w = image.shape[:2]
            rgb_image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
            results = self.face_detection.process(rgb_image)
            
            faces = []
            if results.detections:
                for detection in results.detections:
                    bbox = detection.location_data.relative_bounding_box
                    
                    # 转换为像素坐标
                    x1 = int(bbox.xmin * w)
                    y1 = int(bbox.ymin * h)
                    face_w = int(bbox.width * w)
                    face_h = int(bbox.height * h)
                    
                    confidence = detection.score[0]
                    
                    if self._validate_face_region(image, (x1, y1, face_w, face_h)):
                        faces.append((x1, y1, face_w, face_h, confidence))
            
            return faces
            
        except Exception as e:
            print(f"[FaceDetector] MediaPipe检测出错: {e}")
            return []
    
    def _detect_with_yunet(self, image: np.ndarray) -> List[Tuple[int, int, int, int, float]]:
        """YuNet检测器"""
        try:
            h, w = image.shape[:2]
            self.yunet.setInputSize((w, h))
            
            _, faces = self.yunet.detect(image)
            
            if faces is None:
                return []
            
            results = []
            for face in faces:
                x, y, w, h = face[:4].astype(int)
                confidence = face[14]
                
                if self._validate_face_region(image, (x, y, w, h)):
                    results.append((x, y, w, h, confidence))
            
            return results
            
        except Exception as e:
            print(f"[FaceDetector] YuNet检测出错: {e}")
            return []
    
    def _detect_with_dnn(self, image: np.ndarray) -> List[Tuple[int, int, int, int, float]]:
        try:
            h, w = image.shape[:2]
            
            blob = cv2.dnn.blobFromImage(
                image, 1.0, (300, 300),
                [104, 117, 123], swapRB=False, crop=False
            )
            
            self.dnn_net.setInput(blob)
            detections = self.dnn_net.forward()
            
            results = []
            for i in range(detections.shape[2]):
                confidence = detections[0, 0, i, 2]
                
                if confidence > 0.5:  # 适中的置信度阈值
                    box = detections[0, 0, i, 3:7] * np.array([w, h, w, h])
                    x1, y1, x2, y2 = box.astype(int)
                    
                    # 边界检查
                    x1, y1 = max(0, x1), max(0, y1)
                    x2, y2 = min(w, x2), min(h, y2)
                    
                    if x2 > x1 and y2 > y1:
                        face_w, face_h = x2 - x1, y2 - y1
                        
                        if self._validate_face_region(image, (x1, y1, face_w, face_h)):
                            results.append((x1, y1, face_w, face_h, confidence))
            
            return results
            
        except Exception as e:
            print(f"[FaceDetector] DNN检测出错: {e}")
            return []
    
    def _detect_with_dlib(self, image: np.ndarray) -> List[Tuple[int, int, int, int, float]]:
        """dlib检测器（保持兼容性）"""
        try:
            gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
            faces = self.dlib_detector(gray)
            
            results = []
            for face in faces:
                x, y = face.left(), face.top()
                w, h = face.width(), face.height()
                
                if self._validate_face_region(image, (x, y, w, h)):
                    results.append((x, y, w, h, 0.8))  # dlib没有置信度，给默认值
            
            return results
            
        except Exception as e:
            print(f"[FaceDetector] dlib检测出错: {e}")
            return []
    
    def _detect_with_cascade(self, image: np.ndarray) -> List[Tuple[int, int, int, int, float]]:
        """级联检测器"""
        try:
            gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
            
            faces = self.cascade.detectMultiScale(
                gray,
                scaleFactor=1.05,
                minNeighbors=6,
                minSize=(40, 40),
                maxSize=(400, 400)
            )
            
            results = []
            for (x, y, w, h) in faces:
                if self._validate_face_region(image, (x, y, w, h)):
                    results.append((x, y, w, h, 0.7))
            
            return results
            
        except Exception as e:
            print(f"[FaceDetector] 级联检测出错: {e}")
            return []
    
    def _validate_face_region(self, image: np.ndarray, face_box: Tuple[int, int, int, int]) -> bool:
        """验证人脸区域的有效性"""
        x, y, w, h = face_box
        
        # 基本尺寸检查
        if w < 30 or h < 30 or w > 600 or h > 600:
            return False
        
        # 宽高比检查
        aspect_ratio = w / h
        if aspect_ratio < 0.6 or aspect_ratio > 1.8:
            return False
        
        # 边界检查
        img_h, img_w = image.shape[:2]
        if x < 0 or y < 0 or x + w > img_w or y + h > img_h:
            return False
        
        try:
            # 区域内容检查
            face_roi = image[y:y+h, x:x+w]
            if face_roi.size == 0:
                return False
            
            # 方差检查（避免纯色区域）
            gray_roi = cv2.cvtColor(face_roi, cv2.COLOR_BGR2GRAY)
            variance = np.var(gray_roi)
            if variance < 100:
                return False
            
            return True
            
        except Exception:
            return False
    
    def _enhance_image_for_shadows(self, image: np.ndarray) -> List[Tuple[str, np.ndarray]]:
        """针对阴影优化的图像增强"""
        enhanced_images = [("original", image)]
        
        try:
            # CLAHE增强 - 对阴影最有效
            lab = cv2.cvtColor(image, cv2.COLOR_BGR2LAB)
            clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8, 8))
            lab[:, :, 0] = clahe.apply(lab[:, :, 0])
            clahe_img = cv2.cvtColor(lab, cv2.COLOR_LAB2BGR)
            enhanced_images.append(("clahe", clahe_img))
        except Exception as e:
            print(f"[FaceDetector] CLAHE增强失败: {e}")
        
        return enhanced_images
    
    def _merge_detections(self, all_detections: List[Tuple[int, int, int, int, float]], 
                         iou_threshold: float = 0.3) -> List[Tuple[int, int, int, int, float]]:
        """智能合并检测结果"""
        if len(all_detections) == 0:
            return []
        
        # 按置信度排序
        detections_sorted = sorted(all_detections, key=lambda x: x[4], reverse=True)
        
        keep = []
        while detections_sorted:
            # 取置信度最高的
            current = detections_sorted[0]
            keep.append(current)
            detections_sorted.remove(current)
            
            # 移除与当前检测重叠的其他检测
            remaining = []
            for det in detections_sorted:
                iou = self._calculate_iou(current[:4], det[:4])
                if iou <= iou_threshold:
                    remaining.append(det)
            
            detections_sorted = remaining
        
        return keep
    
    def _calculate_iou(self, box1: Tuple[int, int, int, int], 
                       box2: Tuple[int, int, int, int]) -> float:
        """计算两个边界框的IoU"""
        x1, y1, w1, h1 = box1
        x2, y2, w2, h2 = box2
        
        # 计算交集
        inter_x1 = max(x1, x2)
        inter_y1 = max(y1, y2)
        inter_x2 = min(x1 + w1, x2 + w2)
        inter_y2 = min(y1 + h1, y2 + h2)
        
        if inter_x2 <= inter_x1 or inter_y2 <= inter_y1:
            return 0.0
        
        inter_area = (inter_x2 - inter_x1) * (inter_y2 - inter_y1)
        
        # 计算并集
        area1 = w1 * h1
        area2 = w2 * h2
        union_area = area1 + area2 - inter_area
        
        return inter_area / union_area if union_area > 0 else 0.0
    
    def detect_faces(self, image: np.ndarray, 
                    strategy: str = "balanced") -> List[Dict[str, Any]]:
        if len(self.detectors) == 0:
            print("[FaceDetector] 错误: 没有可用的检测器")
            return []
        
        all_detections = []
        
        # 根据策略选择检测器和参数
        if strategy == "precision":
            # 精确模式：优先使用RetinaFace和现代检测器
            detector_priorities = ['retinaface', 'yunet']
            enhance_images = False
        elif strategy == "recall":
            # 召回模式：使用所有检测器和图像增强
            detector_priorities = ['retinaface', 'yunet', 'mediapipe', 'dnn', 'dlib', 'cascade']
            enhance_images = True
        else:
            # 平衡模式：优先RetinaFace，再使用主力检测器
            detector_priorities = ['retinaface', 'yunet', 'mediapipe']
            enhance_images = True
        
        # 获取增强图像
        if enhance_images:
            image_versions = self._enhance_image_for_shadows(image)
        else:
            image_versions = [("original", image)]
        
        # 对每个图像版本使用选定的检测器
        for version_name, img_version in image_versions:
            for detector_name in detector_priorities:
                if detector_name in self.detectors:
                    try:
                        detections = self.detectors[detector_name](img_version)
                        all_detections.extend(detections)
                    except Exception as e:
                        print(f"[FaceDetector] 检测器 {detector_name} 在 {version_name} 上失败: {e}")
        
        # 合并检测结果
        merged_detections = self._merge_detections(all_detections)
        
        # 转换为标准格式
        results = []
        for i, (x, y, w, h, conf) in enumerate(merged_detections):
            # 添加padding
            padding = 10
            x1 = max(0, x - padding)
            y1 = max(0, y - padding)
            x2 = min(image.shape[1], x + w + padding)
            y2 = min(image.shape[0], y + h + padding)
            
            face_info = {
                "filename": f"face_{i + 1}.jpg",
                "coordinates": {
                    "x1": int(x1),
                    "y1": int(y1), 
                    "x2": int(x2),
                    "y2": int(y2)
                },
                "confidence": float(conf),
                "original_box": (int(x), int(y), int(w), int(h))
            }
            results.append(face_info)
        
        return results
    
    def add_manual_face(self, image: np.ndarray, x1: int, y1: int, x2: int, y2: int, 
                       face_id: Optional[str] = None) -> Dict[str, Any]:
        # 确保坐标在图像范围内
        img_h, img_w = image.shape[:2]
        x1 = max(0, min(x1, img_w))
        y1 = max(0, min(y1, img_h))
        x2 = max(x1, min(x2, img_w))
        y2 = max(y1, min(y2, img_h))
        
        # 基本验证
        if x2 - x1 < 20 or y2 - y1 < 20:
            raise ValueError("人脸区域太小，最小尺寸为20x20像素")
        
        if x2 - x1 > 800 or y2 - y1 > 800:
            raise ValueError("人脸区域太大，最大尺寸为800x800像素")
        
        # 生成face_id
        if not face_id:
            face_id = f"manual_face_{int(time.time())}"
        
        face_info = {
            "filename": f"{face_id}.jpg",
            "coordinates": {
                "x1": int(x1),
                "y1": int(y1),
                "x2": int(x2),
                "y2": int(y2)
            },
            "confidence": 1.0,  # 手动添加的给最高置信度
            "manual": True,  # 标记为手动添加
            "face_id": face_id
        }
        
        # 记录日志
        _safe_log_activity(
            level="INFO",
            module="图片处理",
            action="手动添加人脸",
            details={
                "face_id": face_id,
                "coordinates": face_info["coordinates"]
            }
        )
        
        return face_info


# 全局检测器实例（单例模式，节省内存）
_detector_instance = None

def get_face_detector(use_gpu: bool = False) -> EnhancedFaceDetector:
    """获取人脸检测器实例（单例模式）"""
    global _detector_instance
    
    if _detector_instance is None:
        _detector_instance = EnhancedFaceDetector(use_gpu=use_gpu)
    
    return _detector_instance


def detect_faces_in_image(image: np.ndarray, 
                         strategy: str = "balanced") -> List[Dict[str, Any]]:
    detector = get_face_detector()
    return detector.detect_faces(image, strategy)


def add_manual_face_to_image(image: np.ndarray, x1: int, y1: int, x2: int, y2: int, 
                            face_id: Optional[str] = None) -> Dict[str, Any]:
    detector = get_face_detector()
    return detector.add_manual_face(image, x1, y1, x2, y2, face_id)
