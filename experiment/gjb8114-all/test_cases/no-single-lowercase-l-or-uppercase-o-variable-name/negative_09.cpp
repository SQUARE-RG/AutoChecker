int main()
{
    if (int l = 1; l > 0) // CHECK-MESSAGES: :[[@LINE]]:{{[0-9]+}}: warning: {{.*}} [ucassaat-r-1-13-11]
    {
        return 0;
    }
    return 1;
}
