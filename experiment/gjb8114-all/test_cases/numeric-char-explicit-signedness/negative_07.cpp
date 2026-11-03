#include <vector>

int main()
{
    std::vector<char> values = {10, 20, 30};
    int sum = values[0] + values[1]; // CHECK-MESSAGES: :[[@LINE]]:{{[0-9]+}}: warning: {{.*}} [ucassaat-r-1-1-20]
    return sum;
}
