int main(void)
{
    int array[] = {0, 1, 2}; // CHECK-MESSAGES: :[[@LINE]]:{{[0-9]+}}: warning: {{.*}} [ucassaat-r-1-1-18]
    int data = 0;
    for (int i = 0; i < 3; ++i)
    {
        data += array[i];
    }
    return data == 3 ? 0 : 1;
}
