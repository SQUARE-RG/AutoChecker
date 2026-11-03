#define CHECK if // CHECK-MESSAGES: :[[@LINE]]:{{[0-9]+}}: warning: {{.*}} [ucassaat-r-1-1-2]

int main()
{
    int value = 3;
    CHECK (value > 0)
    {
        value = 0;
    }
    return value;
}
