int main()
{
    long double a = 1.0L;
    long double b = 1.0L;
    if (a != b) { // CHECK-MESSAGES: :[[@LINE]]:{{[0-9]+}}: warning: {{.*}} [ucassaat-r-1-12-3]
        return 1;
    }
    return 0;
}
