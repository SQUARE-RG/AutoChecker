int main()
{
    int accumulator = 0;
    for (int i = 0; i < 4; ++i)
    {
        accumulator += i;
    }
#include <float.h> // CHECK-MESSAGES: :[[@LINE]]:{{[0-9]+}}: warning: {{.*}} [ucassaat-r-1-2-3]
    int result = accumulator + FLT_MANT_DIG;
    return result;
}
