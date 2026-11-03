typedef struct
{
    unsigned short a : 10;
    unsigned short b : 7; // CHECK-MESSAGES: :[[@LINE]]:{{[0-9]+}}: warning: {{.*}} [ucassaat-r-1-1-12]
} OverrunShort;

int main()
{
    OverrunShort data;
    return 0;
}
