#include <list>

int main()
{
    std::list<int> values{1, 2, 3};
    int *pointer = &values.back();
    values.pop_back();
    int result = *pointer; // CHECK-MESSAGES: :[[@LINE]]:{{[0-9]+}}: warning: {{.*}} [ucassaat-r-1-6-16]
    return result;
}
