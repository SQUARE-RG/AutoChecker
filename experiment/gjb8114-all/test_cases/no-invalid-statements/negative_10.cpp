int main(void)
{
    int values[2] = {1, 2};
    int index = 0;
    values[index]; // CHECK-MESSAGES: :[[@LINE]]:{{[0-9]+}}: warning: {{.*}} [ucassaat-r-1-8-3]
    return (0);
}
