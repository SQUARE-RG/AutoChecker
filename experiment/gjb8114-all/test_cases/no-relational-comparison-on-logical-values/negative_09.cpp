int main()
{
    bool lhs = true;
    bool rhs = false;
    int data[2] = {3, 7};
    int value = data[lhs < rhs]; // CHECK-MESSAGES: :[[@LINE]]:{{[0-9]+}}: warning: {{.*}} [ucassaat-r-1-12-1]
    return value;
}
