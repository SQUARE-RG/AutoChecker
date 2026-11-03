#include <vector>

int accumulate_positive(const std::vector<int>& values, int ignored) {
    int total = 0;
    for (int value : values) {
        while (value > 0) {
            if (value == ignored) {
                --value;
                continue;
            }
            if (value % 2 == 0) {
                --value;
                continue; // CHECK-MESSAGES: :[[@LINE]]:{{[0-9]+}}: warning: {{.*}} [ucassaat-a-1-9-3]
            }
            total += value;
            --value;
        }
    }
    return total;
}
