#define ADD(x) (x) + 1 // CHECK-MESSAGES: :[[@LINE]]:{{[0-9]+}}: warning: {{.*}} [ucassaat-r-1-1-7]

int main()
{
    int a = 2;
    int result = 2 * ADD(a);
    return result;
}
