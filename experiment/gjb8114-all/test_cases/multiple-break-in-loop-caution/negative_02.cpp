#include <iostream>
#include <vector>

int main() {
    std::vector<int> values{1, 2, 3, 4, 5};
    int seen = 0;
    for (int x : values) { if (x == 2) { break; } if (x == 4) { break; } ++seen; } // CHECK-MESSAGES: :[[@LINE]]:{{[0-9]+}}: warning: {{.*}} [ucassaat-a-1-9-2]
    std::cout << seen << '\n';
    return 0;
}
