typedef struct
{
    short d01 : 2; // CHECK-MESSAGES: :[[@LINE]]:{{[0-9]+}}: warning: {{.*}} [ucassaat-r-1-1-11]
} sData;

int main(void)
{
    sData my_data{};
    my_data.d01 = 1;
    return my_data.d01;
}
