int comp(float data1, float data2);

int main()
{
    return 0;
}

int comp(int data1, int data2) // CHECK-MESSAGES: :[[@LINE]]:{{[0-9]+}}: warning: {{.*}} [ucassaat-r-1-7-5]
{
    return 2 * data1 + data2;
}
