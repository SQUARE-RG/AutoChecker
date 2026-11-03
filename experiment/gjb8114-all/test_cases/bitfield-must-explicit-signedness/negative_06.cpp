struct Flags
{
    int read : 1, write : 1, exec : 2; // CHECK-MESSAGES: :[[@LINE]]:{{[0-9]+}}: warning: {{.*}} [ucassaat-r-1-1-11]
    unsigned int reserved : 26;
};

int main()
{
    Flags f;
    f.read = 1;
    f.write = 0;
    f.exec = 3;
    f.reserved = 0;
    return 0;
}
