#define NEGATE(x) (0 - x) // CHECK-MESSAGES: :[[@LINE]]:{{[0-9]+}}: warning: {{.*}} [ucassaat-r-1-1-7]

int main()
{
    int result = NEGATE(1 - 2);
    return result == 1 ? 0 : 1;
}
