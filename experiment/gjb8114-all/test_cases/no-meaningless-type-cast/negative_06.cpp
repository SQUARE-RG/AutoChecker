double source = 3.5;
int main()
{
    double copy = double(source); // CHECK-MESSAGES: :[[@LINE]]:{{[0-9]+}}: warning: {{.*}} [ucassaat-r-1-10-6]
    return copy == source ? 0 : 1;
}
