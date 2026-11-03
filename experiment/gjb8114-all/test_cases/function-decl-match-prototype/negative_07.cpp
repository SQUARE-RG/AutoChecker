int compute(int); // CHECK-MESSAGES: :[[@LINE]]:{{[0-9]+}}: warning: {{.*}} [ucassaat-r-1-1-14]

int compute(int value)
{
    return value + 1;
}
