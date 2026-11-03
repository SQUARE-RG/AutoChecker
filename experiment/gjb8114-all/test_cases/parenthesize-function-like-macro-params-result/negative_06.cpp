#define SELECT_OR_ZERO(flag, value) (flag) ? (value) : 0 // CHECK-MESSAGES: :[[@LINE]]:{{[0-9]+}}: warning: {{.*}} [ucassaat-r-1-1-7]

int main()
{
    int flag = 1;
    int value = 7;
    int result = 2 + SELECT_OR_ZERO(flag, value);
    return result;
}
