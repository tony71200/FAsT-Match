# FAsT-Match

Port of **Fast Affine Template Matching** algorithm to C++ with Python bindings.

> **Reference**: "FAsT-Match: Fast Affine Template Matching" — Simon Korman, Daniel Reichman, Gilad Tsur, Shai Avidan, CVPR 2013, Portland.
>
> Original Matlab code: http://www.eng.tau.ac.il/~simonk/FastMatch/

Example image/template sets from K. Mikolajczyk's dataset: http://www.robots.ox.ac.uk/~vgg/research/affine/

---

## Yêu cầu hệ thống

| Phần mềm | Phiên bản | Ghi chú |
|-----------|-----------|---------|
| **Python** | ≥ 3.9 | |
| **OpenCV C++ SDK** | 4.x | Cần headers + libs + `OpenCVConfig.cmake` |
| **CMake** | ≥ 3.18 | |
| **C++ compiler** | MSVC 2019+ (Windows) / GCC / Clang | |
| **pybind11** | ≥ 2.11 | Chỉ cần cho Cách 1 |
| **scikit-build-core** | ≥ 0.10 | Chỉ cần cho Cách 1 |

---

## Bước 0: Thiết lập OpenCV_DIR

Trỏ biến môi trường `OpenCV_DIR` tới thư mục chứa `OpenCVConfig.cmake`:

**PowerShell:**
```powershell
$env:OpenCV_DIR = "C:/Opencv/opencv/build"
```

**CMD:**
```bat
set OpenCV_DIR=C:\Opencv\opencv\build
```

**Linux / macOS:**
```bash
export OpenCV_DIR=/usr/local/lib/cmake/opencv4
```

> **Kiểm tra**: đảm bảo thư mục trên chứa file `OpenCVConfig.cmake`.

---

## Cách 1: Cài Python package (pybind11 extension) — ĐỀ XUẤT

Cách này build C++ thành Python extension (`.pyd` / `.so`) và cài trực tiếp vào Python.

### 1.1. Cài build dependencies

```bash
python -m pip install pybind11 scikit-build-core
```

### 1.2. Build & cài package

**PowerShell (Windows):**
```powershell
python -m pip install . --config-settings="cmake.args=-DOpenCV_DIR=$env:OpenCV_DIR"
```

**CMD (Windows):**
```bat
python -m pip install . --config-settings=cmake.args=-DOpenCV_DIR=%OpenCV_DIR%
```

**Linux / macOS:**
```bash
python -m pip install .
```

### 1.3. Kiểm tra cài đặt

```bash
python -c "from fast_match import match_template_paths; print('OK')"
```

### 1.4. Chạy test

```bash
python tests/test_samples.py
```

Kết quả mong đợi:
```
[OK] image.png + template.png -> [[56.98, 234.14], [32.53, 154.34], [103.40, 102.31], [127.85, 182.11]]
[OK] image2.png + template2.png -> [[177.82, 99.22], [219.54, 87.55], [246.85, 185.20], [205.14, 196.87]]
```

### 1.5. Ví dụ sử dụng

```python
from fast_match import match_template_paths, FastMatch

# --- Cách nhanh: gọi hàm 1 dòng ---
corners = match_template_paths("image.png", "template.png")
print(corners)  # [[x1,y1], [x2,y2], [x3,y3], [x4,y4]]

# --- Cách tuỳ chỉnh: dùng class ---
matcher = FastMatch()
matcher.init(epsilon=0.15, delta=0.85, min_scale=0.5, max_scale=2.0)
corners = matcher.match_paths("image.png", "template.png")
```

---

## Cách 2: Build DLL/SO rồi gọi qua ctypes

Cách này **không cần** `pybind11`. Chỉ cần CMake build ra shared library, rồi gọi qua Python ctypes wrapper có sẵn.

### 2.1. Build

**PowerShell (Windows):**
```powershell
cmake -S . -B build -DFAST_MATCH_BUILD_PYTHON=OFF -DOpenCV_DIR="$env:OpenCV_DIR"
cmake --build build --config Release
```

**CMD (Windows):**
```bat
cmake -S . -B build -DFAST_MATCH_BUILD_PYTHON=OFF -DOpenCV_DIR=%OpenCV_DIR%
cmake --build build --config Release
```

**Linux / macOS:**
```bash
cmake -S . -B build -DFAST_MATCH_BUILD_PYTHON=OFF
cmake --build build
```

Sau khi build, file thư viện nằm tại:

| OS | Đường dẫn |
|----|-----------|
| Windows | `build/Release/fast_match_capi.dll` |
| Linux | `build/libfast_match_capi.so` |
| macOS | `build/libfast_match_capi.dylib` |

### 2.2. Kiểm tra

```bash
python tests/test_samples2.py
```

### 2.3. Ví dụ sử dụng

```python
from fast_match import match_template_paths_via_dll

corners = match_template_paths_via_dll("image.png", "template.png")
print(corners)  # [[x1,y1], [x2,y2], [x3,y3], [x4,y4]]

# Hoặc chỉ định đường dẫn DLL thủ công
corners = match_template_paths_via_dll(
    "image.png", "template.png",
    library_path="build/Release/fast_match_capi.dll",
)
```

> **Windows**: Nếu gặp lỗi thiếu DLL phụ thuộc (`opencv_world*.dll`), set thêm:
> ```powershell
> $env:FAST_MATCH_DLL_DIRS = "C:/Opencv/opencv/build/x64/vc16/bin"
> ```

---

## Build wheel để phân phối

```bash
python -m pip install build
python -m build
```

Wheel sẽ nằm tại `dist/fast_match-0.1.0-*.whl`.

---

## Tham số FAsT-Match

| Tham số | Mặc định | Mô tả |
|---------|----------|-------|
| `epsilon` | 0.15 | Tỷ lệ lấy mẫu ngẫu nhiên (nhỏ hơn → chính xác hơn, chậm hơn) |
| `delta` | 0.25 | Kích thước bước lưới tìm kiếm |
| `photometric_invariance` | `False` | Bật bất biến ánh sáng |
| `min_scale` | 0.5 | Tỷ lệ thu nhỏ tối thiểu |
| `max_scale` | 2.0 | Tỷ lệ phóng to tối đa |

---

## Xử lý lỗi thường gặp

Chi tiết đầy đủ xem file [`FIX_INSTALL.md`](FIX_INSTALL.md).

| Lỗi | Nguyên nhân | Cách sửa |
|-----|-------------|----------|
| `Could not find OpenCVConfig.cmake` | Chưa set `OpenCV_DIR` | Set đúng `OpenCV_DIR` (xem Bước 0) |
| `pybind11Config.cmake` not found | Chưa cài pybind11 hoặc chỉ cần DLL | `pip install pybind11` hoặc thêm `-DFAST_MATCH_BUILD_PYTHON=OFF` |
| `DLL load failed while importing _fast_match` | Thiếu `opencv_world*.dll` trong DLL search path | Set `OpenCV_DIR` đúng, hoặc thêm thư mục vào `PATH` |
| `cv::Mat::at` assertion failed | Build Debug nhưng dùng Release DLLs | Rebuild với `--config Release` |
| `No module named fast_match._fast_match` | Import package source thay vì site-packages | Chạy test từ bên ngoài thư mục repo, hoặc `cd tests && python test_samples.py` |
