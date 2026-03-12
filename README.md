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

> Note: C++ dependencies are still required at build-time (OpenCV + TBB).


### Test với ảnh mẫu có sẵn

Sau khi đã cài package (`python -m pip install .`), chạy smoke test:

```bash
python tests/test_samples.py
```

Script sẽ thử 2 cặp ảnh:
- `image.png` + `template.png`
- `image2.png` + `template2.png`

Kết quả thành công sẽ in ra 4 góc khớp tìm được cho từng cặp ảnh.
