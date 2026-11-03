#include <cstdlib>

bool allocate_int(int** out)
{
    *out = static_cast<int*>(std::malloc(sizeof(int)));
    return *out != nullptr;
}

int main()
{
    int* value; // CHECK-MESSAGES: :[[@LINE]]:{{[0-9]+}}: warning: {{.*}} [ucassaat-r-1-3-7]
    if (!allocate_int(&value))
    {
        return 1;
    }
    *value = 42;
    int observed = *value;
    std::free(value);
    return observed == 42 ? 0 : 1;
}
