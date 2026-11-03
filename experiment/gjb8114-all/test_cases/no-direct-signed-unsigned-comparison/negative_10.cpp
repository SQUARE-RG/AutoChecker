int main()
{
    long index = 0;
    unsigned long limit = 1;
    int values[2] = { 10, 20 };
    int result = values[index < limit]; // CHECK-MESSAGES: :[[@LINE]]:{{[0-9]+}}: warning: {{.*}} [ucassaat-r-1-12-5]
    return result;
}
