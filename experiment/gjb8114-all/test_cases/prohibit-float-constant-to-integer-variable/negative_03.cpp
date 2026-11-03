int main()
{
    int value = 8;
    value += 1.75; // CHECK-MESSAGES: :[[@LINE]]:{{[0-9]+}}: warning: {{.*}} [ucassaat-r-1-6-1]
    return 0;
}
