#define BOOL bool // CHECK-MESSAGES: :[[@LINE]]:{{[0-9]+}}: warning: {{.*}} [ucassaat-r-1-1-2]

int main()
{
    BOOL flag = true;
    return flag ? 0 : 1;
}
