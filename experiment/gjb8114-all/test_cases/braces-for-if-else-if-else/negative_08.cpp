int main()
{
    int flag = 0;
    if (flag)
        ; // CHECK-MESSAGES: :[[@LINE]]:{{[0-9]+}}: warning: {{.*}} [ucassaat-r-1-2-2]
    return 0;
}
