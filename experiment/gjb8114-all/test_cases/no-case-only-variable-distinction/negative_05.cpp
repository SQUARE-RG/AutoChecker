#include <tuple>

int main() {
    int data = 0;
    auto [Data, other] = std::make_tuple(1, 2); // CHECK-MESSAGES: :[[@LINE]]:{{[0-9]+}}: warning: {{.*}} [ucassaat-r-1-13-8]
    return data + Data + other;
}
