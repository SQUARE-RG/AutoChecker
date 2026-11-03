#include <vector>

int main() {
    std::vector<int> values;
    double raw = 9.876;
    values.push_back(raw); // CHECK-MESSAGES: :[[@LINE]]:{{[0-9]+}}: warning: {{.*}} [ucassaat-a-1-10-1]
    return values[0];
}
