#include <cstddef>

std::size_t count_digits(char* text) { // CHECK-MESSAGES: :[[@LINE]]:{{[0-9]+}}: warning: {{.*}} [ucassaat-a-2-7-2]
    std::size_t count = 0;
    for (std::size_t i = 0; text[i] != 0; ++i) {
        if (text[i] >= '0' && text[i] <= '9') {
            ++count;
        }
    }
    return count;
}
