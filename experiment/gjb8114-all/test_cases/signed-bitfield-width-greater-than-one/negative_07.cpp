struct Data
{
    signed flag : 1; // CHECK-MESSAGES: :[[@LINE]]:{{[0-9]+}}: warning: {{.*}} [ucassaat-r-1-1-10]
    signed other : 2;
};

int main()
{
    Data d{};
    d.flag = -1;
    d.other = -1;
    return 0;
}
