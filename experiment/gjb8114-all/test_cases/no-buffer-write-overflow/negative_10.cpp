#include <algorithm>

int main() {
    int src[4] = {1, 2, 3, 4};
    int dst[2] = {0, 0};
    std::transform(src, src + 4, dst, [](int v) { return v; });  // CHECK-MESSAGES: :[[@LINE]]:{{[0-9]+}}: warning: {{.*}} [ucassaat-r-1-6-15]
    return 0;
}
