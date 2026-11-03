// negative_06.cpp
#include <iostream>
#include <vector>

#define INIT_VALUES { 1, 2, 3 // CHECK-MESSAGES: :[[@LINE]]:{{[0-9]+}}: warning: {{.*}} [ucassaat-a-1-1-2]

int main()
{
    std::vector<int> values = INIT_VALUES };
    for (int value : values)
    {
        std::cout << value << '\n';
    }
    return 0;
}
