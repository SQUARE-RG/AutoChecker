typedef struct
{
    unsigned int d01 : 16;
    unsigned int d02 : 16;
    unsigned int d03 : 1; // CHECK-MESSAGES: :[[@LINE]]:{{[0-9]+}}: warning: {{.*}} [ucassaat-r-1-1-12]
} stData;

int main()
{
    stData my_data;
    return 0;
}
