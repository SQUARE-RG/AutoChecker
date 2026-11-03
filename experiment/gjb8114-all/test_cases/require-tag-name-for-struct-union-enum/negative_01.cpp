struct { int data1; int data2; } sData; // CHECK-MESSAGES: :[[@LINE]]:{{[0-9]+}}: warning: {{.*}} [ucassaat-r-1-1-8]

int main()
{
    sData.data1 = 2000;
    return 0;
}
