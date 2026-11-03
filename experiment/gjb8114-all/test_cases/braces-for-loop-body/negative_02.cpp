#include <iostream>
#include <vector>

int main() {
    std::vector<int> values{1, 2, 3};
    for (int value : values)
        std::cout << value << ' '; // CHECK-MESSAGES: :[[@LINE]]:{{[0-9]+}}: warning: {{.*}} [ucassaat-r-1-2-1]
    std::cout << '\n';
    return 0;
}
