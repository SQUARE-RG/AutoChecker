int main()
{
    struct // CHECK-MESSAGES: :[[@LINE]]:5: warning: {{.*}} [ucassaat-r-1-1-8]
    {
        int data1;
        int data2;
    } sData;

    sData.data1 = 2000;
    return 0;
}
