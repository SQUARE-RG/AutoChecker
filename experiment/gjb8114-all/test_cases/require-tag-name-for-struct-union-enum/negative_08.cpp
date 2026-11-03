int main()
{
    union // CHECK-MESSAGES: :[[@LINE]]:5: warning: {{.*}} [ucassaat-r-1-1-8]
    {
        int id;
        unsigned char cd[4];
    } uData;

    uData.id = 7;
    return 0;
}
