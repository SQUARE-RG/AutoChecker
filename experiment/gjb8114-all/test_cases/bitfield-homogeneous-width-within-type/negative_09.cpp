typedef struct
{
    unsigned short a : 3;
    unsigned short b : 3;
    unsigned int c : 3; // CHECK-MESSAGES: :[[@LINE]]:{{[0-9]+}}: warning: {{.*}} [ucassaat-r-1-1-12]
    unsigned int d : 3;
} MixedWidths;

int main()
{
    MixedWidths data;
    return 0;
}
