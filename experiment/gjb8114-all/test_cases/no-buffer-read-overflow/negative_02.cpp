#include <algorithm>

int main()
{
    int src[3] = {1, 2, 3};
    int des[5] = {0, 0, 0, 0, 0};
    std::copy(src, src + 5, des); // CHECK-MESSAGES: :[[@LINE]]:{{[0-9]+}}: warning: {{.*}} [ucassaat-r-1-6-14]
    return 0;
}
