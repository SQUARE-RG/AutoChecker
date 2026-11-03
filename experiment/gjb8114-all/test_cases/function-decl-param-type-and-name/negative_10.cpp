class Storage {
public:
    explicit Storage(int); // CHECK-MESSAGES: :[[@LINE]]:{{[0-9]+}}: warning: {{.*}} [ucassaat-r-1-1-13]
};

int main()
{
    return 0;
}
