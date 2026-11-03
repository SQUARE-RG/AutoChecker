int main()
{
    float f = 2.5f;
    long l(f); // CHECK-MESSAGES: :[[@LINE]]:{{[0-9]+}}: warning: {{.*}} [ucassaat-r-1-10-1]
    (void)l;
    return 0;
}
