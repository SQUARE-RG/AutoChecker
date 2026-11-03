#define pabs(x) x >= 0 ? x : -x // CHECK-MESSAGES: :[[@LINE]]:{{[0-9]+}}: warning: {{.*}} [ucassaat-r-1-1-7]

int main()
{
    unsigned int result;
    int a = 6;
    result = pabs(a) + 1;
    return 0;
}
