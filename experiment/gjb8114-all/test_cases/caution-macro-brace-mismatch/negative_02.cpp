#define ADD_ONE(x) ((x) + 1 // CHECK-MESSAGES: :[[@LINE]]:{{[0-9]+}}: warning: {{.*}} [ucassaat-a-1-1-2]

int main()
{
    int x = 1;
    int y = ADD_ONE(x));
    return y;
}
