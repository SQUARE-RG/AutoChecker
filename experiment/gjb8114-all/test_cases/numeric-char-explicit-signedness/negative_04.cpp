int main(void)
{
    char digits[2] = {1, 2}; // CHECK-MESSAGES: :[[@LINE]]:{{[0-9]+}}: warning: {{.*}} [ucassaat-r-1-1-20]
    int sum = digits[0] + digits[1];
    return sum;
}
