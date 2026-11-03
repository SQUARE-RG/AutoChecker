#include <utility>

int combine(int x) {
    int y = x + 1;
    auto [a, b] = std::pair<int, int>{y, y * 2}; // CHECK-MESSAGES: :[[@LINE]]:{{[0-9]+}}: warning: {{.*}} [ucassaat-a-1-1-4]
    return a + b;
}

int main() {
    return combine(3) == 12 ? 0 : 1;
}
