#define IF0(x) if (0 == (x)) { // CHECK-MESSAGES: :[[@LINE]]:{{[0-9]+}}: warning: {{.*}} [ucassaat-a-1-1-2]

int main(void)
{
    int test = 0;
    IF0(test)
    test = test + 1;
    return 0;
}
}
