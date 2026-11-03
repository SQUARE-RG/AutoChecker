#include <vector>

int main() {
    std::vector<int> values{1, 2, 3, 4};
    int count = 0;
    for (const auto& unusedValue : values) { // CHECK-MESSAGES: :[[@LINE]]:{{[0-9]+}}: warning: {{.*}} [ucassaat-a-1-8-2]
        count += 1;
    }
    return count;
}
