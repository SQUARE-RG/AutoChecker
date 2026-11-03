struct sData
{
    signed int si01 : 1; // CHECK-MESSAGES: :[[@LINE]]:{{[0-9]+}}: warning: {{.*}} [ucassaat-r-1-1-10]
    signed int si02 : 2;
    unsigned int serv : 29;
};

int main()
{
    sData my_data{};
    my_data.si01 = 0;
    my_data.si02 = -1;
    return 0;
}
