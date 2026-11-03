typedef struct
{
    long long d01 : 32;
    long long d02 : 32;
    long long d03 : 1; // CHECK-MESSAGES: :[[@LINE]]:{{[0-9]+}}: warning: {{.*}} [ucassaat-r-1-1-12]
} stData;

int main()
{
    stData my_data;
    return 0;
}
