#include <array>

int sum3(std::array<int, 3>& values) { // CHECK-MESSAGES: :[[@LINE]]:{{[0-9]+}}: warning: {{.*}} [ucassaat-a-2-7-2]
    return values[0] + values[1] + values[2];
}

int main() {
    std::array<int, 3> values{1, 2, 3};
    return sum3(values) == 6 ? 0 : 1;
}
