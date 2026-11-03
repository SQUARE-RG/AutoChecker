int add(int lhs, int rhs)
{
    return lhs + rhs;
}

int main()
{
    int result = add(010, 1); // CHECK-MESSAGES: :[[@LINE]]:{{[0-9]+}}: warning: {{.*}} [ucassaat-r-1-8-4]
    return result;
}
