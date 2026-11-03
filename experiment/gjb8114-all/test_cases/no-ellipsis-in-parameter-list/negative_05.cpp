template <typename T>
T accumulate(T initial, ...) // CHECK-MESSAGES: :[[@LINE]]:{{[0-9]+}}: warning: {{.*}} [ucassaat-r-1-7-15]
{
    return initial;
}

int main()
{
    return accumulate(0);
}
