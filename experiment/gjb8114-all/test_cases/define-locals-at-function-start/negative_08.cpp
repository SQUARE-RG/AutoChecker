#include <vector>

int totalEven(const std::vector<int>& data) {
    int total = 0;
    for (int value : data) {
        if (value % 2 == 0) {
            total += value;
        }
    }
    int offset = total / 2; // CHECK-MESSAGES: :[[@LINE]]:{{[0-9]+}}: warning: {{.*}} [ucassaat-a-1-1-4]
    return total + offset;
}

int main() {
    std::vector<int> data = {2, 4, 5, 6};
    return totalEven(data);
}
