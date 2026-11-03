int accumulate(const int &value); // CHECK-MESSAGES: :[[@LINE]]:{{[0-9]+}}: warning: {{.*}} [ucassaat-r-1-1-14]

int accumulate(int &value)
{
    return value + 1;
}
