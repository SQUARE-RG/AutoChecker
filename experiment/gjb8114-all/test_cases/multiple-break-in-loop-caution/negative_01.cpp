#include <iostream>

int main() {
    int count = 0;
    for (int i = 0; i < 10; ++i) { if (i == 3) { break; } if (i == 7) { break; } ++count; } // CHECK-MESSAGES: :[[@LINE]]:{{[0-9]+}}: warning: {{.*}} [ucassaat-a-1-9-2]
    std::cout << count << '\n';
    return 0;
}
