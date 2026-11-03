int argc = 0;
int count_args(int argc, ...) // CHECK-MESSAGES: :[[@LINE]]:{{[0-9]+}}: warning: {{.*}} [ucassaat-r-1-13-2]
{
    return argc + 1;
}
int main()
{
    return count_args(4);
}
