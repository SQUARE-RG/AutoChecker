#include <vector>

std::vector<int> g_values(5, 0);

int main()
{
    int sum = 0;
    for (g_values[0] = 0; g_values[0] < 5; ++g_values[0]) // CHECK-MESSAGES: :[[@LINE]]:{{[0-9]+}}: warning: {{.*}} [ucassaat-r-1-9-1]
    {
        sum += g_values[0];
    }
    return 0;
}
