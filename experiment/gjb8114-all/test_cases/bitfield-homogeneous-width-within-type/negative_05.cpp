typedef struct
{
    unsigned int d01 : 4;
    unsigned int d02 : 4;
    unsigned long long d03 : 8; // CHECK-MESSAGES: :[[@LINE]]:{{[0-9]+}}: warning: {{.*}} [ucassaat-r-1-1-12]
} stData;

int main(void)
{
    stData my_data;
    return (0);
}
