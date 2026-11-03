void inspect(int& value);

void inspect(const int& value) // CHECK-MESSAGES: :[[@LINE]]:{{[0-9]+}}: warning: {{.*}} [ucassaat-r-1-7-5]
{
    (void)value;
}

int main()
{
    const int value = 7;
    inspect(value);
    return 0;
}
