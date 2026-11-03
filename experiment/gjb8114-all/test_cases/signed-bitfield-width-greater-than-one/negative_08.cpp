typedef signed int SignedInt;

struct Data
{
    SignedInt value : 1; // CHECK-MESSAGES: :[[@LINE]]:{{[0-9]+}}: warning: {{.*}} [ucassaat-r-1-1-10]
    SignedInt other : 2;
};

int main()
{
    Data d{};
    d.value = -1;
    d.other = -1;
    return 0;
}
