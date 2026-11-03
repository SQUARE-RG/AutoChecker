int main(void)
{
    char i; // CHECK-MESSAGES: :[[@LINE]]:{{[0-9]+}}: warning: {{.*}} [ucassaat-r-1-1-20]
    int j;
    i = (char)0xFF;
    j = i + 1;
    return (0);
}
