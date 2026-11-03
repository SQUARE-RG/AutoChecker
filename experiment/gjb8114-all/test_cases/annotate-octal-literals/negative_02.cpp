int apply_mask(int value)
{
    return value & 0777; // CHECK-MESSAGES: :[[@LINE]]:{{[0-9]+}}: warning: {{.*}} [ucassaat-r-1-8-4]
}

int main()
{
    return apply_mask(10);
}
