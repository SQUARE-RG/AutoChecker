#include <cstddef>

int main() {
    std::size_t n = 4;
    int* data = new int[n];
    for (std::size_t i = 0; i < n; ++i) {
        data[i] = static_cast<int>(i);
    }
    delete data; // CHECK-MESSAGES: :[[@LINE]]:{{[0-9]+}}: warning: {{.*}} [ucassaat-r-2-6-2]
    data = nullptr;
    return 0;
}
