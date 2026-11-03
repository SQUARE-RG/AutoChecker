#include <iostream>
#include <vector>

int main() {
    std::vector<int> values{1, 2, 3};
    int sum = 0;
    for (int value : values) // CHECK-MESSAGES: :[[@LINE]]:{{[0-9]+}}: warning: {{.*}} [ucassaat-r-1-2-1]
        sum += value;
    std::cout << sum << std::endl;
    return 0;
}
