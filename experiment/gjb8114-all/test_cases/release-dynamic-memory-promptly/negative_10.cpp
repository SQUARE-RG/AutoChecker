#include <iostream>
#include <vector>

int main() {
    std::vector<int*> values;
    for (int i = 0; i < 4; ++i) {
        values.push_back(new int(i * 10)); // CHECK-MESSAGES: :[[@LINE]]:{{[0-9]+}}: warning: {{.*}} [ucassaat-a-1-6-3]
    }
    int sum = 0;
    for (int* value : values) {
        sum += *value;
    }
    std::cout << sum << std::endl;
    return 0;
}
