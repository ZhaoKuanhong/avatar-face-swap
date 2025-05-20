import json
import cv2
import dlib
import os

def recognize_and_crop_faces(image_path, output_folder="cropped_faces"):
    """
    识别人脸，截取人脸部分并保存为编号的文件。

    Args:
        image_path (str): 输入图像的路径。
        output_folder (str, optional): 保存截取人脸的文件夹名称。
                                         默认为 "cropped_faces"。
    """
    # 创建输出文件夹（如果不存在）
    if not os.path.exists(output_folder):
        os.makedirs(output_folder)

    # 加载人脸检测器
    detector = dlib.get_frontal_face_detector()

    # 读取图像
    img = cv2.imread(image_path)
    if img is None:
        print(f"无法加载图像: {image_path}")
        return

    # 获取图像尺寸
    height, width = img.shape[:2]

    # 将图像转换为灰度图，以提高检测效率
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

    # 检测图像中的人脸
    faces = detector(gray)

    # 创建包含图像信息的字典
    output_data = {
        "image_info": {
            "width": width,
            "height": height,
            "filename": os.path.basename(image_path)
        },
        "faces": []
    }

    # 遍历检测到的人脸
    for i, face in enumerate(faces):
        # 获取人脸区域的坐标
        x1, y1 = face.left(), face.top()
        x2, y2 = face.right(), face.bottom()

        # 稍微扩大裁剪区域，以包含更多面部信息
        padding = 10
        cropped_x1 = max(0, x1 - padding)
        cropped_y1 = max(0, y1 - padding)
        cropped_x2 = min(width, x2 + padding)
        cropped_y2 = min(height, y2 + padding)

        # 裁剪人脸区域
        cropped_face = img[cropped_y1:cropped_y2, cropped_x1:cropped_x2]

        # 构建输出文件名
        output_filename = os.path.join(output_folder, f"face_{i+1}.jpg")

        # 保存裁剪的人脸图像
        cv2.imwrite(output_filename, cropped_face)
        print(f"检测到人脸 {i+1}，已保存至: {output_filename}")

        face_info = {
            "filename": f"face_{i+1}.jpg",
            "coordinates": {
                "x1": int(cropped_x1),
                "y1": int(cropped_y1),
                "x2": int(cropped_x2),
                "y2": int(cropped_y2)
            }
        }
        output_data["faces"].append(face_info)

    if not faces:
        print(f"在图像 {image_path} 中未检测到人脸。")
    else:
        # 生成JSON文件
        json_filename = os.path.join(output_folder, "faces_info.json")
        with open(json_filename, 'w', encoding='utf-8') as f:
            json.dump(output_data, f, indent=4, ensure_ascii=False)
        print(f"人脸坐标信息已保存至: {json_filename}")


if __name__ == "__main__":
    image_file = "input.jpeg"  # 替换为您的输入图像文件路径
    recognize_and_crop_faces(image_file)
    print("人脸识别和裁剪完成！")