int main()
{
    int data[4] = {0, 0, 0, 0};
    int index = -2;
    data[index] = 5; // CHECK-MESSAGES: :[[@LINE]]:{{[0-9]+}}: warning: {{.*}} [ucassaat-r-1-6-9]
    return 0;
}
