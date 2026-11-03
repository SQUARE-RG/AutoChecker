int combine(int value)
{
    return value;
}
int main()
{
    int a = 0;
    int b = 0;
    int result = combine((a = 1, b = 2)); // CHECK-MESSAGES: :[[@LINE]]:{{[0-9]+}}: warning: {{.*}} [ucassaat-a-1-6-6]
    return result == 2 ? 0 : 1;
}
