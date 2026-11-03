int mode = 0;
extern "C" int set_mode(int mode) // CHECK-MESSAGES: :[[@LINE]]:{{[0-9]+}}: warning: {{.*}} [ucassaat-r-1-13-2]
{
    return mode + 1;
}
int main()
{
    return set_mode(3);
}
