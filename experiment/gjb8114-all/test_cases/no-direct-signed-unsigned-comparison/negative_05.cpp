bool accept(bool value)
{
    return value;
}

int main()
{
    int signed_value = -2;
    unsigned int unsigned_value = 2U;
    accept(signed_value < unsigned_value); // CHECK-MESSAGES: :[[@LINE]]:{{[0-9]+}}: warning: {{.*}} [ucassaat-r-1-12-5]
    return 0;
}
