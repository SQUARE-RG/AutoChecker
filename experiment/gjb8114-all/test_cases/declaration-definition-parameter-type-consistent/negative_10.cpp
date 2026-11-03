void inspect(int* ptr);

void inspect(const int* ptr) // CHECK-MESSAGES: :[[@LINE]]:{{[0-9]+}}: warning: {{.*}} [ucassaat-r-1-7-5]
{
    (void)ptr;
}

int main()
{
    return 0;
}
