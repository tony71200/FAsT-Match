### This is my upcoming project: https://plusplusone.herokuapp.com
### Please register your email address if you're interested in it.
------

FAsT-Match
==========

Port of Fast Affine Template Matching algorithm

Reference:

"FAsT-Match: Fast Affine Template Matching"
Simon Korman, Daniel Reichman, Gilad Tsur, Shai Avidan 
CVPR 2013, Portland

You can find the original Matlab code and literature here: http://www.eng.tau.ac.il/~simonk/FastMatch/


One of the example image and template sets are taken from K. Mikolajczyk's dataset which is available here:
http://www.robots.ox.ac.uk/~vgg/research/affine/

## Python package

Project now supports building as a Python library so it can be reused in other Python programs.

### Build wheel

```bash
python -m pip install build
python -m build
```

### Install locally

```bash
python -m pip install .
```

### Example usage

```python
from fast_match import match_template_paths, FastMatch

corners = match_template_paths("image.png", "template.png")
print(corners)

matcher = FastMatch()
matcher.init(epsilon=0.15, delta=0.85, min_scale=0.5, max_scale=2.0)
corners = matcher.match_paths("image.png", "template.png")
```

> Note: OpenCV C++ SDK is required at build-time (headers + libs + `OpenCVConfig.cmake`).


### Test với ảnh mẫu có sẵn

Sau khi đã cài package (`python -m pip install .`), chạy smoke test:

```bash
python tests/test_samples.py
```

Script sẽ thử 2 cặp ảnh:
- `image.png` + `template.png`
- `image2.png` + `template2.png`

Kết quả thành công sẽ in ra 4 góc khớp tìm được cho từng cặp ảnh.


### Build C++ shared library (DLL/SO/DYLIB) cho Python dùng qua ctypes

```bash
cmake -S . -B build -DFAST_MATCH_BUILD_PYTHON=OFF
cmake --build build
```

> Nếu bạn chỉ cần DLL thì đặt `FAST_MATCH_BUILD_PYTHON=OFF` để không cần cài `pybind11`.

Sau khi build xong sẽ có thư viện chia sẻ:
- Linux: `build/libfast_match_capi.so`
- macOS: `build/libfast_match_capi.dylib`
- Windows: `build/Release/fast_match_capi.dll` (hoặc `build/Debug/...`)

Ví dụ gọi từ Python bằng ctypes wrapper:

```python
from fast_match import match_template_paths_via_dll

corners = match_template_paths_via_dll("image.png", "template.png")
print(corners)
```

### Test trường hợp dùng DLL

```bash
python tests/test_samples2.py
```


### Windows build note (OpenCV_DIR)

Nếu gặp lỗi `Could not find OpenCVConfig.cmake`, bạn cần trỏ đúng đường dẫn OpenCV cho CMake:

```bat
set OpenCV_DIR=C:\opencv\build
python -m pip install . --config-settings=cmake.args=-DOpenCV_DIR=%OpenCV_DIR%
```

Hoặc PowerShell:

```powershell
$env:OpenCV_DIR = "C:/opencv/build"
python -m pip install . --config-settings=cmake.args=-DOpenCV_DIR=$env:OpenCV_DIR
```

### Các lỗi đã gặp gần đây, nguyên nhân và cách sửa

1. **Lỗi khi chạy `cmake -S . -B build`: thiếu `pybind11Config.cmake`**
   - **Biểu hiện**: CMake báo không tìm thấy `pybind11Config.cmake` / `pybind11-config.cmake`.
   - **Nguyên nhân**: trước đây CMake luôn yêu cầu `pybind11` dù bạn chỉ muốn build DLL (`fast_match_capi`).
   - **Cách sửa**:
     - Đã cập nhật CMake để hỗ trợ build DLL độc lập với option:
       `-DFAST_MATCH_BUILD_PYTHON=OFF`.
     - Nếu cần build cả Python extension thì cài `pybind11` và để `FAST_MATCH_BUILD_PYTHON=ON` (mặc định).

2. **Lỗi sau khi `python -m pip install .` thành công nhưng chạy `python tests/test_samples.py` báo extension không có**
   - **Biểu hiện**: `Details: fast_match extension is not available`.
   - **Nguyên nhân**: `fast_match/__init__.py` cũ bắt mọi exception khi import `._fast_match` rồi gán `None`, làm mất lỗi gốc và gây khó chẩn đoán.
   - **Cách sửa**:
     - Đã đổi `__init__.py` để ném `ImportError` rõ ràng kèm lỗi gốc khi extension không load được.
     - Nhờ đó biết chính xác lỗi thật (thiếu file `.pyd/.so`, thiếu runtime DLL, sai môi trường, ...).

3. **Lỗi compile trên Windows/MSVC (OpenCV 4.x)**
   - **Biểu hiện**:
     - `M_PI` undeclared
     - `std::accumulate` không nhận đúng hàm, đụng `cv::accumulate`
     - syntax error do dấu đóng ngoặc
     - `CV_BGR2GRAY` undeclared
   - **Nguyên nhân**:
     - Khác biệt tương thích giữa compiler/platform và API OpenCV cũ.
   - **Cách sửa**:
     - thay `M_PI` -> `CV_PI`
     - thêm header `<numeric>` và dùng `std::accumulate(..., 0.0)`
     - sửa lỗi đóng ngoặc trong `FAsTMatch.cpp`
     - thay `CV_BGR2GRAY` -> `cv::COLOR_BGR2GRAY`

4. **Lỗi không tìm thấy OpenCVConfig.cmake**
   - **Biểu hiện**: CMake dừng ở `find_package(OpenCV ...)`.
   - **Nguyên nhân**: chưa trỏ đúng `OpenCV_DIR` (thư mục chứa `OpenCVConfig.cmake`).
   - **Cách sửa**:
     - set `OpenCV_DIR` đúng và truyền qua pip/cmake như hướng dẫn ở mục **Windows build note (OpenCV_DIR)** phía trên.

5. **Lỗi môi trường mạng/proxy khi cài dependency build**
   - **Biểu hiện**: pip không tải được `scikit-build-core` (403/proxy).
   - **Nguyên nhân**: môi trường mạng chặn truy cập index package.
   - **Cách sửa**:
     - cấu hình mirror/proxy nội bộ hoặc cài dependency offline trước khi chạy `python -m pip install .`.


6. **`python tests/test_samples.py` báo `No module named fast_match._fast_match` dù đã cài thành công**
   - **Nguyên nhân**:
     - Script test trước đây chèn root repo vào `sys.path`, khiến Python ưu tiên import package source trong repo (không có file extension đã build) thay vì package đã cài trong site-packages.
   - **Cách sửa**:
     - Đã bỏ `sys.path.insert(0, ROOT)` trong `tests/test_samples.py` và `tests/test_samples2.py` để test dùng đúng package đã cài.

7. **`python tests/test_samples2.py` báo `Could not find module ... fast_match_capi.dll (or one of its dependencies)`**
   - **Nguyên nhân**:
     - DLL chính có thể tồn tại, nhưng thiếu DLL phụ thuộc runtime (thường là OpenCV `opencv_world*.dll`) trong `PATH`/DLL search path.
   - **Cách sửa**:
     - `fast_match/dll_api.py` đã được cập nhật để:
       - tự thêm thư mục chứa `fast_match_capi.dll` vào DLL search path,
       - tự dò các thư mục OpenCV runtime từ `OpenCV_DIR` (ví dụ `x64/vc17/bin`, `bin`),
       - cho phép thêm thủ công qua biến môi trường `FAST_MATCH_DLL_DIRS`.
     - Nếu vẫn lỗi, set thêm:
       - `set FAST_MATCH_DLL_DIRS=C:\opencv\build\x64\vc17\bin`
