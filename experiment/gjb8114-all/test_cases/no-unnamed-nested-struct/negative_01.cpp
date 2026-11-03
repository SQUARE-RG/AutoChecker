struct Sdata
{
    unsigned char id;
    struct Scoor { unsigned char xs; unsigned char ys; unsigned char zs; }; // CHECK-MESSAGES: :[[@LINE]]:{{[0-9]+}}: warning: {{.*}} [ucassaat-r-1-1-9]
};

int main()
{
    Sdata data{};
    data.id = 1;
    return 0;
}
