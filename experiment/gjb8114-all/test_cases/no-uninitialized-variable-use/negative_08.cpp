int main()
{
    int cond;
    int r = cond ? 1 : 2; // CHECK-MESSAGES: :[[@LINE]]:{{[0-9]+}}: warning: {{.*}} [ucassaat-r-1-11-1]
    return r;
}
