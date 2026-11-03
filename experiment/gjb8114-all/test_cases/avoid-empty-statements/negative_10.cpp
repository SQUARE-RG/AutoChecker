#include <vector>

int main() {
    std::vector<int> values{1, 2, 3};
    int sum = 0;
    for (int value : values)
        ; // CHECK-MESSAGES: :[[@LINE]]:{{[0-9]+}}: warning: {{.*}} [ucassaat-a-1-8-1]
    return sum;
}
