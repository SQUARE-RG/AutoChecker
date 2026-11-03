#include <cstddef>

int main()
{
    int matrix[][2] = {{1, 2}, {3, 4}}; // CHECK-MESSAGES: :[[@LINE]]:{{[0-9]+}}: warning: {{.*}} [ucassaat-r-1-1-18]
    int sum = 0;
    for (std::size_t i = 0; i < 2; ++i)
    {
        sum += matrix[i][0] + matrix[i][1];
    }
    return sum == 10 ? 0 : 1;
}
