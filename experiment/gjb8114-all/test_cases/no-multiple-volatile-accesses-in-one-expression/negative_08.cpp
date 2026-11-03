int main()
{
    volatile int v = 1;
    int result = (v, v + 1); // CHECK-MESSAGES: :[[@LINE]]:{{[0-9]+}}: warning: {{.*}} [ucassaat-r-1-13-13]
    return result;
}
