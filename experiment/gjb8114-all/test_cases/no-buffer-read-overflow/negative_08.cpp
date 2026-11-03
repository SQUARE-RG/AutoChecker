#include <vector>
#include <iostream>

int main()
{
    int src[2] = {1, 2};
    std::vector<int> values;
    values.insert(values.end(), src, src + 3); // CHECK-MESSAGES: :[[@LINE]]:{{[0-9]+}}: warning: {{.*}} [ucassaat-r-1-6-14]
    std::cout << values.size();
    return 0;
}
