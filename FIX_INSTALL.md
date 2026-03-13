# FAsT-Match — Hướng dẫn cài đặt & Các lỗi đã sửa

## Yêu cầu hệ thống

| Phần mềm | Phiên bản tối thiểu | Ghi chú |
|-----------|---------------------|---------|
| Python | ≥ 3.9 | Đã test trên 3.12.9 |
| OpenCV C++ SDK | 4.x | Cần headers + libs + `OpenCVConfig.cmake` |
| CMake | ≥ 3.18 | Đã test trên 3.30.2 |
| Visual Studio / MSVC | 2019+ | Build tools C++ trên Windows |
| pybind11 | ≥ 2.11 | Chỉ cần cho cách 1 (pybind11 extension) |
| scikit-build-core | ≥ 0.10 | Chỉ cần cho cách 1 |

---

## Hướng dẫn cài đặt chi tiết (Windows)

### Bước 0: Thiết lập biến môi trường OpenCV

Trỏ `OpenCV_DIR` đến thư mục chứa `OpenCVConfig.cmake`:

```powershell
$env:OpenCV_DIR = "C:/Opencv/opencv/build"
```

Hoặc CMD:
```bat
set OpenCV_DIR=C:\Opencv\opencv\build
```

> **Kiểm tra**: thư mục trên phải chứa file `OpenCVConfig.cmake`.

---

### Cách 1: Cài Python package (pybind11 extension) — ĐỀ XUẤT

Đây là cách dùng chính, giúp gọi FAsT-Match trực tiếp từ Python.

```powershell
# 1. Cài build dependencies
python -m pip install pybind11 scikit-build-core

# 2. Build & cài package (truyền OpenCV_DIR qua cmake args)
python -m pip install . --config-settings="cmake.args=-DOpenCV_DIR=$env:OpenCV_DIR"
```

**Kiểm tra cài đặt thành công:**

```powershell
# Test import
python -c "from fast_match import match_template_paths; print('OK')"

# Test chạy matching với ảnh mẫu
python tests/test_samples.py
```

Kết quả mong đợi:
```
[OK] image.png + template.png -> [[...], [...], [...], [...]]
[OK] image2.png + template2.png -> [[...], [...], [...], [...]]
```

---

### Cách 2: Build DLL rồi gọi qua ctypes

Cách này không cần `pybind11`, chỉ cần CMake build DLL.

```powershell
# 1. Configure CMake (tắt pybind11)
cmake -S . -B build -DFAST_MATCH_BUILD_PYTHON=OFF -DOpenCV_DIR="$env:OpenCV_DIR"

# 2. Build Release
cmake --build build --config Release
```

DLL sẽ nằm tại: `build/Release/fast_match_capi.dll`

**Kiểm tra:**

```powershell
python tests/test_samples2.py
```

---

### Ví dụ sử dụng trong Python

```python
# ---- Cách 1: pybind11 (sau khi pip install .) ----
from fast_match import match_template_paths, FastMatch

corners = match_template_paths("image.png", "template.png")
print(corners)  # [[x1,y1], [x2,y2], [x3,y3], [x4,y4]]

# Hoặc dùng class
matcher = FastMatch()
matcher.init(epsilon=0.15, delta=0.85, min_scale=0.5, max_scale=2.0)
corners = matcher.match_paths("image.png", "template.png")

# ---- Cách 2: DLL/ctypes (sau khi cmake build) ----
from fast_match import match_template_paths_via_dll

corners = match_template_paths_via_dll("image.png", "template.png")
```

---

## Các lỗi đã xảy ra, nguyên nhân & cách sửa

### Lỗi 1: DLL build cũ (Debug) gây crash khi chạy test

- **Biểu hiện**: `test_samples2.py` báo `cv::Mat::at` assertion failed (`elemSize() == sizeof(_Tp)`) với cặp ảnh thứ 2.
- **Nguyên nhân**: DLL được build ở chế độ **Debug** với OpenCV 4.10.0d (debug DLL). Khi chạy runtime lại load OpenCV Release DLL → xung đột ABI giữa Debug/Release.
- **Cách sửa**:
  ```powershell
  # Xóa build cũ và rebuild ở Release
  Remove-Item -Recurse -Force build
  cmake -S . -B build -DFAST_MATCH_BUILD_PYTHON=OFF -DOpenCV_DIR="C:/Opencv/opencv/build"
  cmake --build build --config Release
  ```

---

### Lỗi 2: Import `_fast_match.pyd` thất bại — thiếu OpenCV runtime DLL

- **Biểu hiện**: Sau `pip install .` thành công, chạy `python -c "from fast_match import match_template_paths"` báo:
  ```
  ImportError: DLL load failed while importing _fast_match:
  The specified module could not be found.
  ```
- **Nguyên nhân**: File `_fast_match.cp312-win_amd64.pyd` đã có trong site-packages nhưng Windows không tìm thấy `opencv_world4100.dll` (nằm ở `C:\Opencv\opencv\build\x64\vc16\bin`) vì thư mục đó không có trong DLL search path.
- **Cách sửa**: Cập nhật `fast_match/__init__.py` — thêm hàm `_register_opencv_dll_dirs()` gọi `os.add_dll_directory()` để đăng ký thư mục chứa OpenCV DLLs **trước khi** import `_fast_match`:
  ```python
  def _register_opencv_dll_dirs() -> None:
      if os.name != "nt" or not hasattr(os, "add_dll_directory"):
          return
      opencv_dir = os.environ.get("OpenCV_DIR")
      if not opencv_dir:
          return
      base = Path(opencv_dir)
      for d in [base / "x64" / "vc17" / "bin",
                base / "x64" / "vc16" / "bin",
                base / "bin"]:
          if d.is_dir():
              os.add_dll_directory(str(d))

  _register_opencv_dll_dirs()  # gọi TRƯỚC import _fast_match
  ```

---

### Lỗi 3 (tham khảo): pip exit code 1 trên PowerShell

- **Biểu hiện**: `python -m pip install .` báo exit code 1 dù cài thành công.
- **Nguyên nhân**: PowerShell coi bất kỳ output nào đi qua stderr (kể cả warning `libpng`, `[notice]`) là lỗi (`NativeCommandError`).
- **Cách sửa**: Không cần sửa — đây là hành vi của PowerShell, không phải lỗi thật. Kiểm tra thật sự bằng cách import module sau khi cài.

---

## Tóm tắt nhanh — Chạy từ đầu trên Windows

```powershell
# 1. Set OpenCV_DIR
$env:OpenCV_DIR = "C:/Opencv/opencv/build"

# 2. Cài dependencies
python -m pip install pybind11 scikit-build-core

# 3. Cài package
python -m pip install . --config-settings="cmake.args=-DOpenCV_DIR=$env:OpenCV_DIR"

# 4. Test
python tests/test_samples.py
```
