int main()
{
    int a = 10;
    int b = 5;
    int result = a + b--;  // CHECK-MESSAGES: :[[@LINE]]:{{[0-9]+}}: warning: {{.*}} [ucassaat-r-1-6-5]
    return result;
}
