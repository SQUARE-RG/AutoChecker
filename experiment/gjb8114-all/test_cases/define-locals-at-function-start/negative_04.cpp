#include <iostream>
#include <vector>
#include <algorithm>

int main() {
    std::vector<int> values{1, 2, 3, 4};
    int sum = 0;
    std::for_each(values.begin(), values.end(), [&sum](int v) {
        sum += v;
        int localCopy = v; // CHECK-MESSAGES: :[[@LINE]]:{{[0-9]+}}: warning: {{.*}} [ucassaat-a-1-1-4]
        sum += localCopy * 0;
    });
    std::cout << sum << '\n';
    return 0;
}
