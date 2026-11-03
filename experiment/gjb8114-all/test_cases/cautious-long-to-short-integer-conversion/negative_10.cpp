#include <cstdint>

struct Sample {
    unsigned int value : 16;
};

void store_sample(Sample& sample, std::int64_t input) {
    sample.value = input; // CHECK-MESSAGES: :[[@LINE]]:{{[0-9]+}}: warning: {{.*}} [ucassaat-a-1-10-3]
}
