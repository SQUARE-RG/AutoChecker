#include <cstdio>

#define ADD_TO(x, v) (x) += (v)  // CHECK-MESSAGES: :[[@LINE]]:{{[0-9]+}}: warning: {{.*}} [ucassaat-r-1-1-7]

int main()
{
    int n = 10;
    int after = (ADD_TO(n, 4), n);
    std::printf("%d %d\n", n, after);
    return 0;
}
