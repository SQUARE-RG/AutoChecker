#include <vector>

int main()
{
    std::vector<int> values{1, 2, 3};
    int* data = values.data();

    values = std::vector<int>{4, 5, 6};

    int result = data[0]; // CHECK-MESSAGES: :[[@LINE]]:{{[0-9]+}}: warning: {{.*}} [ucassaat-r-1-6-16]
    (void)result;
    return 0;
}
