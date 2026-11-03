#include <cstdint>

struct Sample {
    unsigned int value : 16;
};

void store_sample_checked(Sample& sample, std::int64_t input) {
    constexpr std::int64_t kMax = (std::int64_t{1} << 16) - 1;
    if (input < 0 || input > kMax) {
        return;
    }
    sample.value = static_cast<unsigned int>(input);
}
