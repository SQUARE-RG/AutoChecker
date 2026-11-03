int add_one(int l) // CHECK-MESSAGES: :[[@LINE]]:{{[0-9]+}}: warning: {{.*}} [ucassaat-r-1-13-11]
{
    return l + 1;
}

int main()
{
    return add_one(0);
}
