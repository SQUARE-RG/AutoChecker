int main()
{
    int i = 0;
    for (; i < 10; ++i); // CHECK-MESSAGES: :[[@LINE]]:{{[0-9]+}}: warning: {{.*}} [ucassaat-r-1-2-1]
    return i;
}
