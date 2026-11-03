int main()
{
    int a = 1;
    int b = 2;
    int result = ++a * b;  // CHECK-MESSAGES: :[[@LINE]]:{{[0-9]+}}: warning: {{.*}} [ucassaat-r-1-6-5]
    return result;
}
