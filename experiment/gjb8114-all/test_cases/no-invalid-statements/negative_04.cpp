int main()
{
    bool flag = true;
    int left = 1;
    int right = 2;
    flag ? left : right; // CHECK-MESSAGES: :[[@LINE]]:{{[0-9]+}}: warning: {{.*}} [ucassaat-r-1-8-3]
    return 0;
}
