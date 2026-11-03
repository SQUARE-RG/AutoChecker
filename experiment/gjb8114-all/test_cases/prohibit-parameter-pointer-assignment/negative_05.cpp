int choose(int* param, bool first)
{
    static int a = 1;
    static int b = 2;
    param = first ? &a : &b; // CHECK-MESSAGES: :[[@LINE]]:{{[0-9]+}}: warning: {{.*}} [ucassaat-r-1-3-3]
    return *param;
}

int main()
{
    int value = 0;
    return choose(&value, true);
}
