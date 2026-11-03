typedef int (*VarargHandler)(int, ...); // CHECK-MESSAGES: :[[@LINE]]:{{[0-9]+}}: warning: {{.*}} [ucassaat-r-1-7-15]

int main()
{
    return 0;
}
