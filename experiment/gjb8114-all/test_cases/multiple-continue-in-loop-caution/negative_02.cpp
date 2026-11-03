#include <iostream>

int main() {
    int values[] = {5, 0, -1, 7};
    int i = 0;
    int sum = 0;
    while (i < 4) { int v = values[i++]; if (v == 0) continue; if (v == -1) continue; sum += v; } // CHECK-MESSAGES: :[[@LINE]]:{{[0-9]+}}: warning: {{.*}} [ucassaat-a-1-9-3]
    std::cout << sum << '\n';
    return 0;
}
