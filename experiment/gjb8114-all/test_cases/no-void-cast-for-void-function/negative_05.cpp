template <typename T>
void consume(T)
{
}

int main()
{
    (void)consume(42); // CHECK-MESSAGES: :[[@LINE]]:{{[0-9]+}}: warning: {{.*}} [ucassaat-r-1-7-12]
    return 0;
}
