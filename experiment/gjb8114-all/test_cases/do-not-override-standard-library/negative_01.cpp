int strxfrm(int a, int b) // CHECK-MESSAGES: :[[@LINE]]:{{[0-9]+}}: warning: {{.*}} [ucassaat-r-1-7-1]
{
    return ((a > b) ? a : b);
}

int main()
{
    int ret;
    ret = strxfrm(2, 3);
    return ret;
}
