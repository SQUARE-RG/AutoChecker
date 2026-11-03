int scale(const int height); // CHECK-MESSAGES: :[[@LINE]]:{{[0-9]+}}: warning: {{.*}} [ucassaat-r-1-1-14]

int scale(const int amount)
{
    return amount * 2;
}
