typedef struct // CHECK-MESSAGES: :[[@LINE]]:{{[0-9]+}}: warning: {{.*}} [ucassaat-r-1-1-8]
{
    int data1;
    int data2;
} S_Data;

int main()
{
    S_Data sData;
    sData.data1 = 2000;
    return 0;
}
