#include <functional>

int main() {
    auto combine = [](int Count, int count) { return Count + count; }; // CHECK-MESSAGES: :[[@LINE]]:{{[0-9]+}}: warning: {{.*}} [ucassaat-r-1-13-8]
    int result = combine(1, 2);
    return result;
}
