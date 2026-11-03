typedef struct
{
    unsigned long long d01 : 40;
    unsigned long long d02 : 25; // CHECK-MESSAGES: :[[@LINE]]:{{[0-9]+}}: warning: {{.*}} [ucassaat-r-1-1-12]
} stData;

int main(void)
{
    stData my_data;
    return (0);
}
