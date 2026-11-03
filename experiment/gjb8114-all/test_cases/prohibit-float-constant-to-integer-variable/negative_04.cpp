int main()
{
    int values[3] = {1, 2, 3};
    values[1] = 4.5; // CHECK-MESSAGES: :[[@LINE]]:{{[0-9]+}}: warning: {{.*}} [ucassaat-r-1-6-1]
    return 0;
}
