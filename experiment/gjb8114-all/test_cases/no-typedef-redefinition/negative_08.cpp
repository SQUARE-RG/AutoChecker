typedef int GlobalInt;

union Storage
{
    typedef double GlobalInt; // CHECK-MESSAGES: :[[@LINE]]:{{[0-9]+}}: warning: {{.*}} [ucassaat-r-1-1-3]
    GlobalInt realPart;
};

int main()
{
    Storage s;
    s.realPart = 1.5;
    return 0;
}
