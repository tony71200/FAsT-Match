#include <cstring>
#include <exception>
#include <string>
#include <vector>

#include <opencv2/imgcodecs.hpp>

#include "FAsTMatch.h"

#if defined(_WIN32)
#define FM_EXPORT __declspec(dllexport)
#else
#define FM_EXPORT __attribute__((visibility("default")))
#endif

extern "C" {

FM_EXPORT int fast_match_template_paths(const char* image_path,
                                        const char* template_path,
                                        float epsilon,
                                        float delta,
                                        int photometric_invariance,
                                        float min_scale,
                                        float max_scale,
                                        float* out_corners_xy,
                                        int out_len,
                                        char* err_msg,
                                        int err_msg_len) {
    auto write_error = [&](const std::string& msg) {
        if (err_msg != nullptr && err_msg_len > 0) {
            std::strncpy(err_msg, msg.c_str(), static_cast<size_t>(err_msg_len) - 1);
            err_msg[err_msg_len - 1] = '\0';
        }
        return -1;
    };

    if (image_path == nullptr || template_path == nullptr) {
        return write_error("image_path/template_path must not be null");
    }

    if (out_corners_xy == nullptr || out_len < 8) {
        return write_error("out_corners_xy must have at least 8 floats");
    }

    try {
        cv::Mat image = cv::imread(image_path, cv::IMREAD_COLOR);
        cv::Mat templ = cv::imread(template_path, cv::IMREAD_COLOR);

        if (image.empty()) {
            return write_error(std::string("Unable to read image: ") + image_path);
        }
        if (templ.empty()) {
            return write_error(std::string("Unable to read template: ") + template_path);
        }

        fast_match::FAsTMatch matcher;
        matcher.init(epsilon, delta, photometric_invariance != 0, min_scale, max_scale);
        std::vector<cv::Point2f> corners = matcher.apply(image, templ);

        if (corners.size() != 4) {
            return write_error("Unexpected corner count");
        }

        for (int i = 0; i < 4; ++i) {
            out_corners_xy[2 * i] = corners[static_cast<size_t>(i)].x;
            out_corners_xy[2 * i + 1] = corners[static_cast<size_t>(i)].y;
        }
        return 0;
    } catch (const std::exception& e) {
        return write_error(std::string("Exception: ") + e.what());
    } catch (...) {
        return write_error("Unknown exception");
    }
}

}  // extern "C"
