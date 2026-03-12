#include <stdexcept>
#include <string>
#include <vector>

#include <opencv2/imgcodecs.hpp>
#include <pybind11/pybind11.h>
#include <pybind11/stl.h>

#include "FAsTMatch.h"

namespace py = pybind11;

namespace {
std::vector<std::vector<float>> convert_corners(const std::vector<cv::Point2f>& corners) {
    std::vector<std::vector<float>> out;
    out.reserve(corners.size());
    for (const auto& p : corners) {
        out.push_back({p.x, p.y});
    }
    return out;
}

class FastMatchWrapper {
public:
    FastMatchWrapper() = default;

    void init(float epsilon = 0.15f,
              float delta = 0.25f,
              bool photometric_invariance = false,
              float min_scale = 0.5f,
              float max_scale = 2.0f) {
        matcher_.init(epsilon, delta, photometric_invariance, min_scale, max_scale);
    }

    std::vector<std::vector<float>> match_paths(const std::string& image_path,
                                                const std::string& template_path) {
        cv::Mat image = cv::imread(image_path, cv::IMREAD_COLOR);
        cv::Mat templ = cv::imread(template_path, cv::IMREAD_COLOR);

        if (image.empty()) {
            throw std::runtime_error("Unable to read image at path: " + image_path);
        }

        if (templ.empty()) {
            throw std::runtime_error("Unable to read template at path: " + template_path);
        }

        auto corners = matcher_.apply(image, templ);
        return convert_corners(corners);
    }

private:
    fast_match::FAsTMatch matcher_;
};

std::vector<std::vector<float>> match_template_paths(const std::string& image_path,
                                                     const std::string& template_path,
                                                     float epsilon = 0.15f,
                                                     float delta = 0.25f,
                                                     bool photometric_invariance = false,
                                                     float min_scale = 0.5f,
                                                     float max_scale = 2.0f) {
    FastMatchWrapper wrapper;
    wrapper.init(epsilon, delta, photometric_invariance, min_scale, max_scale);
    return wrapper.match_paths(image_path, template_path);
}
}  // namespace

PYBIND11_MODULE(_fast_match, m) {
    m.doc() = "Python bindings for FAsT-Match";

    py::class_<FastMatchWrapper>(m, "FastMatch")
        .def(py::init<>())
        .def("init",
             &FastMatchWrapper::init,
             py::arg("epsilon") = 0.15f,
             py::arg("delta") = 0.25f,
             py::arg("photometric_invariance") = false,
             py::arg("min_scale") = 0.5f,
             py::arg("max_scale") = 2.0f)
        .def("match_paths", &FastMatchWrapper::match_paths, py::arg("image_path"), py::arg("template_path"));

    m.def("match_template_paths",
          &match_template_paths,
          py::arg("image_path"),
          py::arg("template_path"),
          py::arg("epsilon") = 0.15f,
          py::arg("delta") = 0.25f,
          py::arg("photometric_invariance") = false,
          py::arg("min_scale") = 0.5f,
          py::arg("max_scale") = 2.0f,
          "Run FAsT-Match using image file paths and return four transformed corners.");
}
