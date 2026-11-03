int negative_08(int value)
{
    value += 1; // CHECK-MESSAGES: :[[@LINE]]:{{[0-9]+}}: warning: {{.*}} [ucassaat-r-1-8-3]
    return value;
}

int main()
{
    return negative_08(0);
}
