#include <vector>
#include <iostream>

int sum_positive(const std::vector<int>& values) {
    int sum = 0;
    for (auto it = values.begin(); it != values.end(); ++it) {
        if (*it < 0) {
            continue;
        }
        if (*it == 0) {
            continue; // CHECK-MESSAGES: :[[@LINE]]:{{[0-9]+}}: warning: {{.*}} [ucassaat-a-1-9-3]
        }
        sum += *it;
    }
    return sum;
}

int main() {
    std::vector<int> values{1, -2, 0, 3};
    std::cout << sum_positive(values) << std::endl;
    return 0;
}
