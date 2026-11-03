int abs(int value) // CHECK-MESSAGES: :[[@LINE]]:{{[0-9]+}}: warning: {{.*}} [ucassaat-r-1-7-1]
{
    return value < 0 ? -value : value;
}

int main()
{
    int number = -5;
    int result = abs(number);
    return result == 5 ? 0 : 1;
}
