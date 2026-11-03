struct Counter
{
    long long ticks : 16; // CHECK-MESSAGES: :[[@LINE]]:{{[0-9]+}}: warning: {{.*}} [ucassaat-r-1-1-11]
    long long limit : 16;
    int id;
};

int main()
{
    Counter c;
    c.ticks = 100;
    c.limit = 50;
    c.id = 1;
    return 0;
}
