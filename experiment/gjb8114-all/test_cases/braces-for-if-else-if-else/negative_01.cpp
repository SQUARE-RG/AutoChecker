int main()
{
    int i = 0;
    int j = 0;
    if (i == 0)
        j = 1; // CHECK-MESSAGES: :[[@LINE]]:{{[0-9]+}}: warning: {{.*}} [ucassaat-r-1-2-2]
    return 0;
}
