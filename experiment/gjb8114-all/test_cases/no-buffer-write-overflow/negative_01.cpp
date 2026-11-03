#include <cstring>

int main()
{
    int src[4] = {1, 2, 3, 4};
    int des[2] = {0, 0};
    std::memcpy(des, src, sizeof(src)); // CHECK-MESSAGES: :[[@LINE]]:{{[0-9]+}}: warning: {{.*}} [ucassaat-r-1-6-15]
    return 0;
}
