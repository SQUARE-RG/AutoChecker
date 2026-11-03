int main()
{
    volatile int v = 1;
    int result = (v > 0) ? v + 1 : 0; // CHECK-MESSAGES: :[[@LINE]]:{{[0-9]+}}: warning: {{.*}} [ucassaat-r-1-13-13]
    return result;
}
