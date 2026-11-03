long source = 42L;
int main()
{
    long copy = static_cast<long>(source); // CHECK-MESSAGES: :[[@LINE]]:{{[0-9]+}}: warning: {{.*}} [ucassaat-r-1-10-6]
    return copy == source ? 0 : 1;
}
