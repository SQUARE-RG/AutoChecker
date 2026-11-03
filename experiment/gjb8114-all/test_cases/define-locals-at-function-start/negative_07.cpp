#include <vector>
#include <cstddef>

int sumPositive(const std::vector<int>& values) {
    int sum = 0;
    std::size_t i = 0;
    do {
        if (values[i] > 0) {
            sum += values[i];
        }
        ++i;
    } while (i < values.size());
    int count = static_cast<int>(i); // CHECK-MESSAGES: :[[@LINE]]:{{[0-9]+}}: warning: {{.*}} [ucassaat-a-1-1-4]
    return sum + count;
}

int main() {
    std::vector<int> values = {1, -2, 3};
    return sumPositive(values);
}
