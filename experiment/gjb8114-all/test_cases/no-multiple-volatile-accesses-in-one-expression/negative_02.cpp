int main()
{
    volatile int v = 3;
    bool ok = (v > 0) && (v < 10); // CHECK-MESSAGES: :[[@LINE]]:{{[0-9]+}}: warning: {{.*}} [ucassaat-r-1-13-13]
    return ok ? 0 : 1;
}
