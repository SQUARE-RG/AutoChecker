#define REAL double // CHECK-MESSAGES: :[[@LINE]]:{{[0-9]+}}: warning: {{.*}} [ucassaat-r-1-1-2]

int main()
{
    REAL value = 2.5;
    return static_cast<int>(value);
}
