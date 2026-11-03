#include <cstring>

int main()
{
    int src[2] = {1, 2};
    int des[4] = {0, 0, 0, 0};
    std::memcpy(des, src, sizeof(des)); // CHECK-MESSAGES: :[[@LINE]]:{{[0-9]+}}: warning: {{.*}} [ucassaat-r-1-6-14]
    return 0;
}
