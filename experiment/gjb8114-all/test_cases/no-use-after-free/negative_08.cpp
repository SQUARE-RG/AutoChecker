#include <map>

int main()
{
    std::map<int, int> values;
    values[1] = 10;
    int *pointer = &values[1];
    values.erase(1);
    int result = *pointer; // CHECK-MESSAGES: :[[@LINE]]:{{[0-9]+}}: warning: {{.*}} [ucassaat-r-1-6-16]
    return result;
}
