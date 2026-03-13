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
