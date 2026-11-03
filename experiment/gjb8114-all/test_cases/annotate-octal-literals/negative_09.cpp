int get_mask(int mode = 0777) // CHECK-MESSAGES: :[[@LINE]]:{{[0-9]+}}: warning: {{.*}} [ucassaat-r-1-8-4]
{
    return mode;
}

int main(void)
{
    return 0;
}
