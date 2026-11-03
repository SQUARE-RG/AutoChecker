#include <array>
#include <cstddef>

template <typename T, std::size_t N>
int locate(const std::array<T, N>& values, const T& target) {
    for (std::size_t i = 0; i < N; ++i) {
        if (values[i] == target) {
            if constexpr (N > 0) {
                break;
            }
        }
        if (i + 1 == N) {
            break; // CHECK-MESSAGES: :[[@LINE]]:{{[0-9]+}}: warning: {{.*}} [ucassaat-a-1-9-2]
        }
    }
    return -1;
}
