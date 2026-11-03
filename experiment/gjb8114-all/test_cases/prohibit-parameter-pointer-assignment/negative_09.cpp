#include <cstddef>

static int g_values[3] = {1, 2, 3};

void advance(int* p, bool continue_loop)
{
    for (int i = 0; continue_loop && i < 1; ++i, p = &g_values[i]) // CHECK-MESSAGES: :[[@LINE]]:{{[0-9]+}}: warning: {{.*}} [ucassaat-r-1-3-3]
    {
        (void)p;
    }
}

int main()
{
    int value = 0;
    advance(&value, true);
    return 0;
}
